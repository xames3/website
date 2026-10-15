"""\
Explainer Tracer
================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 12 September 2026
Last updated on: 15 October 2026

Running a snippet and writing down what it did, one line at a time.
"""

import functools
import hashlib
import json
import os
import signal
import subprocess
import sys
import tempfile
import typing as t

short: t.Final[int] = 28
full: t.Final[int] = 480
kinds: t.Final[frozenset[str]] = frozenset({"call", "line", "return"})
exhausted: t.Final[frozenset[int]] = frozenset(
    -getattr(signal, _) for _ in ("SIGXCPU",) if hasattr(signal, _)
)
killed: t.Final[frozenset[int]] = frozenset(
    -getattr(signal, _) for _ in ("SIGKILL",) if hasattr(signal, _)
)
oversized: t.Final[frozenset[int]] = frozenset(
    -getattr(signal, _) for _ in ("SIGXFSZ",) if hasattr(signal, _)
)


class Trace(t.TypedDict):
    """What the tracer saw, before any of it's turned into steps."""

    events: list[dict[str, t.Any]]
    error: dict[str, t.Any] | None
    tail: str
    truncated: bool
    seen: list[str]
    deps: list[str]


# NOTE(xames3): The runner is a script of its own, run with `-s -P`
# so neither the user site nor the working directory is on its path.
# https://docs.python.org/3/library/sys.html#sys.settrace
# https://docs.python.org/3/library/resource.html#resource.setrlimit
# Comprehensions are inlined since 3.12, which is why `co_positions`
# is used to tell their lines apart: https://peps.python.org/pep-0709/
RUNNER: t.Final[str] = r"""
import ast
import builtins
import io
import json
import os
import re
import sys
import sysconfig

with open(sys.argv[1]) as fd:
    job = json.load(fd)

try:
    import resource
except ImportError:
    resource = None
for limit_name, value in (
    ("RLIMIT_AS", job["memory"]),
    ("RLIMIT_CPU", job["cpu"]),
    ("RLIMIT_FSIZE", job["written"]),
):
    if resource is not None and hasattr(resource, limit_name):
        try:
            resource.setrlimit(getattr(resource, limit_name), (value, value))
        except (ValueError, OSError):
            pass

for entry in job["pythonpath"]:
    sys.path.insert(0, entry)

filename = "<walkthrough>"
watch = job["watch"]
limit = job["limit"]
events = []
seen = set()
state = {"frames": 0, "truncated": False}
last = {}
spans = []
positions = {}
addresses = {}
buffer = io.StringIO()
ADDRESS = re.compile(r" at 0x[0-9a-fA-F]+")
HIDDEN = ("<genexpr>",)
INLINED = (ast.ListComp, ast.SetComp, ast.DictComp)
SHORT = job["short"]
FULL = job["full"]
ITEMS = 4
SHELLS = {
    list: "[%s]",
    tuple: "(%s)",
    set: "{%s}",
    frozenset: "frozenset({%s})",
    dict: "{%s}",
}


def steady(text):
    def label(match):
        found = addresses.setdefault(match.group(0), len(addresses) + 1)
        return " at 0x%x" % found

    return ADDRESS.sub(label, text)


def flat(text):
    return " ".join(steady(text).split())


def clip(text, width):
    if len(text) <= width:
        return text
    head = width // 2
    tail = max(0, width - head - 3)
    return text[:head] + "..." + (text[-tail:] if tail else "")


def abridge(value, text):
    kind = type(value)
    if kind in SHELLS and len(value) > ITEMS:
        if kind is dict:
            pairs = (next(iter(value.items())), next(reversed(value.items())))
            ends = [
                clip(flat(repr(key)), 10) + ": " + clip(flat(repr(item)), 10)
                for key, item in pairs
            ]
        else:
            items = list(value) if kind in (set, frozenset) else value
            ends = [clip(flat(repr(_)), 12) for _ in (items[0], items[-1])]
        return SHELLS[kind] % (ends[0] + ", ..., " + ends[1])
    return clip(text, SHORT)


def show(value):
    try:
        text = flat(repr(value))
    except Exception as exc:
        return ["<unrepresentable %s>" % exc.__class__.__name__, None]
    try:
        short = abridge(value, text)
    except Exception:
        short = clip(text, SHORT)
    full = clip(text, FULL)
    return [full, None if short == full else short]


def describe(exc):
    text = flat(str(exc))
    return exc.__class__.__name__ + (": " + text if text else "")


def snapshot(frame):
    scope = frame.f_locals
    rows = []
    for key in watch:
        if key in scope:
            seen.add(key)
            value = scope[key]
            rows.append([key] + show(value) + [id(value)])
    return rows


def drain():
    written = buffer.getvalue()
    if written:
        buffer.seek(0)
        buffer.truncate(0)
    return steady(written)


def imported():
    skip = {
        os.path.join(os.path.realpath(path), "")
        for key, path in sysconfig.get_paths().items()
        if key in ("stdlib", "platstdlib", "purelib", "platlib")
    }
    found = set()
    for module in list(sys.modules.values()):
        path = getattr(module, "__file__", None)
        if not path or not os.path.isfile(path):
            continue
        path = os.path.realpath(path)
        if not any(path.startswith(_) for _ in skip):
            found.add(path)
    return sorted(found)


def finish(error):
    with open(sys.argv[2], "w") as fd:
        json.dump(
            {
                "events": events,
                "error": error,
                "tail": drain(),
                "truncated": state["truncated"],
                "seen": sorted(seen),
                "deps": imported(),
            },
            fd,
        )


def ask(prompt=""):
    sys.stdout.write(str(prompt))
    line = sys.stdin.readline()
    if not line:
        raise EOFError("EOF when reading a line")
    sys.stdout.write(line if line.endswith("\n") else line + "\n")
    return line.removesuffix("\n")


def inlined(frame, ident):
    if not spans or ident not in last:
        return False
    code = frame.f_code
    if code not in positions:
        positions[code] = list(code.co_positions())
    index = frame.f_lasti // 2
    if index >= len(positions[code]):
        return False
    line, end, col, stop = positions[code][index]
    if None in (line, end, col, stop):
        return False
    for top, left, bottom, right in spans:
        if (top, left) <= (line, col) and (end, stop) <= (bottom, right):
            return top <= last[ident] <= bottom
    return False


def record(frame, event, arg, ident, resumed=False):
    if len(events) >= limit:
        sys.settrace(None)
        state["truncated"] = True
        finish(None)
        os._exit(0)
    last[ident] = frame.f_lineno
    row = {
        "event": event,
        "line": frame.f_lineno,
        "frame": ident,
        "vars": snapshot(frame),
        "out": drain(),
    }
    # NOTE(xames3): A class body runs once, as its class is defined, so it
    # gets the same treatment as a module: no step for its call or return.
    scope = frame.f_locals
    if frame.f_code.co_name == "<module>" or (
        "__qualname__" in scope and "__module__" in scope
    ):
        row["module"] = True
    if resumed:
        row["resumed"] = True
    if event == "return":
        row["ret"] = show(arg)
    events.append(row)


def follow(ident):
    def local(frame, event, arg):
        if event == "line" and inlined(frame, ident):
            return local
        if event in ("line", "return"):
            record(frame, event, arg, ident)
        return local

    local.ident = ident
    return local


def tracer(frame, event, arg):
    code = frame.f_code
    if code.co_filename != filename:
        return None
    if code.co_name in HIDDEN and not job["comprehensions"]:
        return None
    ident = getattr(frame.f_trace, "ident", None)
    resumed = ident is not None
    if not resumed:
        state["frames"] += 1
        ident = state["frames"]
    record(frame, event, arg, ident, resumed)
    return follow(ident)


if not job["comprehensions"]:
    try:
        tree = ast.parse(job["code"])
    except SyntaxError:
        tree = None
    for node in ast.walk(tree) if tree is not None else ():
        if isinstance(node, INLINED):
            start = (node.lineno, node.col_offset)
            spans.append((*start, node.end_lineno, node.end_col_offset))

sys.stdin = io.StringIO(job["stdin"])
builtins.input = ask
scope = {"__name__": "__main__"}
error = None
if job["setup"]:
    try:
        exec(compile(job["setup"], "<setup>", "exec"), scope)
    except BaseException as exc:
        error = {"text": "setup failed, " + describe(exc), "line": None}

if error is None:
    stdout, stderr = sys.stdout, sys.stderr
    sys.stdout = sys.stderr = buffer
    try:
        code = compile(job["code"], filename, "exec")
        sys.settrace(tracer)
        exec(code, scope)
    except BaseException as exc:
        error = {"text": describe(exc), "line": None}
        tb = exc.__traceback__
        while tb is not None:
            if tb.tb_frame.f_code.co_filename == filename:
                error["line"] = tb.tb_lineno
                error["frame"] = getattr(tb.tb_frame.f_trace, "ident", None)
                error["vars"] = snapshot(tb.tb_frame)
            tb = tb.tb_next
    finally:
        sys.settrace(None)
        sys.stdout, sys.stderr = stdout, stderr

finish(error)
"""


def clip(text: str, width: int) -> str:
    """Cut a value down to its two ends.

    :param text: The value, as it would be printed.
    :param width: How many characters it may take, ellipsis included.
    :return: The value, whole when it fits and cut when it doesn't.
    """
    if len(text) <= width:
        return text
    head = width // 2
    tail = max(0, width - head - 3)
    return text[:head] + "..." + (text[-tail:] if tail else "")


def show(text: str) -> tuple[str, str | None]:
    """Give a value in its two lengths, the way the runner does.

    :param text: The value, as it would be printed.
    :return: The value whole, clipped to `full` and cut down to
        `short` or `None` when it didn't need cutting.
    """
    whole = clip(" ".join(text.split()), full)
    cut = clip(whole, short)
    return whole, None if cut == whole else cut


def failed(reason: str) -> Trace:
    """Give back a trace that saw nothing and why.

    :param reason: What went wrong.
    :return: An empty trace carrying the reason as its error.
    """
    return {
        "events": [],
        "error": {"text": reason, "line": None},
        "tail": "",
        "truncated": False,
        "seen": [],
        "deps": [],
    }


def execute(
    code: str,
    setup: str,
    stdin: str,
    watch: list[str],
    limit: int,
    timeout: int,
    pythonpath: list[str],
    *,
    comprehensions: bool,
    memory_limit: int,
    output_limit: int,
    python: str | None = None,
    cache: str | None = None,
) -> Trace:
    """Run the snippet under a tracer and collect what it did.

    It runs in a subprocess of its own, so a snippet that leaks state,
    rebinds `sys.stdout` or runs away can't hurt the main build. The
    answer comes back through a file, which leaves `stdout` to the
    snippet.

    :param code: The snippet to trace.
    :param setup: Code to run first, untraced.
    :param stdin: What `input()` reads, a line at a time.
    :param watch: The names to keep, in the order they're shown.
        Empty keeps none.
    :param limit: How many events to collect before stopping.
    :param timeout: How long the snippet may run, in seconds.
    :param pythonpath: Directories to put on `sys.path` first.
    :param comprehensions: Whether to step into comprehensions, which
        each carry a frame of their own.
    :param python: The interpreter to run it with, the one the build
        runs on when unset.
    :param memory_limit: Bytes of memory it may use.
    :param output_limit: Bytes of files it may write.
    :param cache: A folder to keep the trace in. The same snippet,
        options, interpreter and packages get it back from there, so
        long as the files it imported are as they were. A snippet that
        raised is never kept.
    :return: The trace, with whatever went wrong on it.
    """
    job: dict[str, t.Any] = {
        "code": code,
        "setup": setup,
        "stdin": stdin,
        "watch": watch,
        "limit": limit,
        "pythonpath": pythonpath,
        "comprehensions": comprehensions,
        "short": short,
        "full": full,
        "memory": memory_limit,
        "cpu": timeout,
        "written": output_limit,
    }
    key = ""
    if cache:
        seen = fingerprint(python)
        if seen:
            blob = json.dumps([job, RUNNER, seen], sort_keys=True)
            key = hashlib.sha256(blob.encode()).hexdigest()
            kept = recall(cache, key)
            if kept is not None:
                return kept
    with tempfile.TemporaryDirectory(prefix="kaamiki-") as here:
        path = os.path.join(here, "job.json")
        answer = os.path.join(here, "answer.json")
        with open(path, "w") as fd:
            json.dump(job, fd)
        try:
            finished = subprocess.run(  # noqa: S603
                [
                    python or sys.executable,
                    "-s",
                    "-P",
                    "-c",
                    RUNNER,
                    path,
                    answer,
                ],
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
                cwd=here,
                env=sandbox(here),
                stdin=subprocess.DEVNULL,
            )
        except subprocess.TimeoutExpired:
            return failed(f"ran past its {timeout}s")
        except OSError as exc:
            return failed(f"could not start {python or sys.executable}: {exc}")
        try:
            with open(answer) as fd:
                result = t.cast("Trace", json.load(fd))
        except OSError, json.JSONDecodeError:
            return failed(verdict(finished, timeout, output_limit))
    if cache and key and result["error"] is None:
        remember(cache, key, result)
    return result


@functools.cache
def fingerprint(python: str | None) -> str:
    """Describe the interpreter and the packages a snippet runs with.

    :param python: The interpreter, the one the build runs on when
        unset.
    :return: A digest of its version and every package installed for it
        or an empty string when it couldn't be asked.
    """
    code = (
        "import importlib.metadata as m, sys\n"
        "print(sys.version)\n"
        "print(*sorted(f'{d.metadata[\"Name\"]}=={d.version}'"
        " for d in m.distributions()), sep='\\n')\n"
    )
    try:
        done = subprocess.run(  # noqa: S603
            [python or sys.executable, "-s", "-P", "-c", code],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
            env=sandbox(tempfile.gettempdir()),
            stdin=subprocess.DEVNULL,
        )
    except OSError, subprocess.TimeoutExpired:
        return ""
    if done.returncode:
        return ""
    return hashlib.sha256(done.stdout.encode()).hexdigest()


def digest(path: str) -> str | None:
    """Hash a file's contents.

    :param path: The file.
    :return: The digest or `None` when the file can't be read.
    """
    try:
        with open(path, "rb") as fd:
            return hashlib.sha256(fd.read()).hexdigest()
    except OSError:
        return None


def recall(folder: str, key: str) -> Trace | None:
    """Fetch a kept trace, if the files it imported are as they were.

    :param folder: The cache folder.
    :param key: What the trace was kept under.
    :return: `Trace` or `None` when there's none or it has gone stale.
    """
    try:
        with open(os.path.join(folder, f"{key}.json")) as fd:
            kept = json.load(fd)
        for path, was in kept["deps"].items():
            if digest(path) != was:
                return None
        return t.cast("Trace", kept["trace"])
    except OSError, ValueError, KeyError, TypeError, AttributeError:
        return None


def remember(folder: str, key: str, trace: Trace) -> None:
    """Keep a trace along with the digests of the files it imported.

    :param folder: The cache folder, made if it isn't there.
    :param key: What to keep the trace under.
    :param trace: The trace.
    """
    deps: dict[str, str] = {}
    for path in trace["deps"]:
        was = digest(path)
        if was is None:
            return
        deps[path] = was
    try:
        os.makedirs(folder, exist_ok=True)
        fd, temp = tempfile.mkstemp(dir=folder, suffix=".tmp")
        with os.fdopen(fd, "w") as out:
            json.dump({"trace": trace, "deps": deps}, out)
        os.replace(temp, os.path.join(folder, f"{key}.json"))
    except OSError:
        return


def sandbox(home: str) -> dict[str, str]:
    """Build the little environment a snippet runs in.

    :param home: The temporary directory.
    :return: The environment.
    """
    return {
        "HOME": home,
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "MKL_NUM_THREADS": "1",
        "OMP_NUM_THREADS": "1",
        "OPENBLAS_NUM_THREADS": "1",
        "PATH": os.defpath,
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "PYTHONIOENCODING": "utf-8",
        "TMPDIR": home,
    }


def verdict(
    finished: subprocess.CompletedProcess[str], timeout: int, output_limit: int
) -> str:
    """Say why a snippet left no answer behind.

    :param finished: The runner's process.
    :param timeout: How long it was allowed, in seconds.
    :param output_limit: Bytes of files it was allowed to write.
    :return: The reason, in a line.
    """
    code = finished.returncode
    if code in exhausted:
        return f"used more than its {timeout}s of processor time"
    if code in oversized:
        return f"wrote a file past {output_limit >> 20} MB"
    if code in killed:
        return "was killed, most likely for running out of memory"
    detail = (finished.stderr or finished.stdout).strip()
    return detail[-400:] or "the snippet produced nothing"


def replay(trace: Trace, wanted: frozenset[str]) -> list[dict[str, t.Any]]:
    """Turn what the tracer saw into the steps a reader walks through.

    :param trace: What `execute` gave back.
    :param wanted: The events to make steps of.
    :return: The steps, in the order they ran.
    """
    events = list(trace["events"])
    error = trace["error"]
    raised = error is not None and error.get("line") is not None
    unwound = ""
    while raised and events and events[-1]["event"] == "return":
        unwound = events.pop()["out"] + unwound
    frames: dict[int, dict[str, t.Any]] = {}
    fresh: dict[int, set[str]] = {}
    steps: list[dict[str, t.Any]] = []
    out = ""
    for event in events:
        ident = event["frame"]
        rows = {row[0]: row for row in event["vars"]}
        frame = frames.setdefault(
            ident, {"line": event["line"], "values": {}, "where": {}}
        )
        if event["event"] == "call" and not event.get("resumed"):
            changed = set(rows)
            frame["where"].update(dict.fromkeys(rows, event["line"]))
        else:
            changed = {
                name
                for name, row in rows.items()
                if frame["values"].get(name) != (row[1], row[3])
            }
            frame["where"].update(dict.fromkeys(changed, frame["line"]))
        for name in set(frame["where"]) - set(rows):
            del frame["where"][name]
        frame["values"] = {name: (row[1], row[3]) for name, row in rows.items()}
        frame["line"] = event["line"]
        fresh.setdefault(ident, set()).update(changed)
        out += event["out"]
        kind = event["event"]
        module = event.get("module", False)
        if kind not in wanted or (module and kind == "call"):
            continue
        if module and kind == "return" and not (out or fresh.get(ident)):
            continue
        taken = fresh.pop(ident, set())
        returned = kind == "return" and not module
        steps.append(
            {
                "line": event["line"],
                "frame": ident,
                "vars": [
                    [name, frame["where"][name], row[1], row[2], name in taken]
                    for name, row in rows.items()
                ],
                "out": out,
                "ret": event["ret"] if returned else None,
                "error": None,
            }
        )
        out = ""
    if error is not None and raised:
        steps.append(fault(error, frames, fresh, out + unwound))
        out = ""
    if steps and not trace["truncated"]:
        steps[-1]["out"] += out + trace["tail"]
    return steps


def fault(
    error: dict[str, t.Any],
    frames: dict[int, dict[str, t.Any]],
    fresh: dict[int, set[str]],
    out: str,
) -> dict[str, t.Any]:
    """Write the step a snippet dies on.

    :param error: The exception, as the runner reported it.
    :param frames: Where every frame's values were last set.
    :param fresh: The changes not yet shown, by frame.
    :param out: Whatever was printed on the way down.
    :return: The step.
    """
    ident: int | None = error.get("frame")
    frame: dict[str, t.Any] = {"line": error["line"], "values": {}, "where": {}}
    taken: set[str] = set()
    if ident is not None:
        frame = frames.get(ident, frame)
        taken = fresh.pop(ident, set())
    rows = {row[0]: row for row in error.get("vars") or []}
    taken |= {
        name
        for name, row in rows.items()
        if frame["values"].get(name) != (row[1], row[3])
    }
    text = error["text"]
    short = clip(text, 60)
    return {
        "line": error["line"],
        "frame": ident,
        "vars": [
            [
                name,
                frame["where"].get(name, frame["line"]),
                row[1],
                row[2],
                name in taken,
            ]
            for name, row in rows.items()
        ],
        "out": out,
        "ret": None,
        "error": [clip(text, 480), None if short == text else short],
    }


def collapse(steps: list[dict[str, t.Any]]) -> list[dict[str, t.Any]]:
    """Drop the steps that wouldn't change the page.

    A step that only moves the highlight within a note that's already
    showing, or that no note covers, has nothing new to say, so the step
    before it stands for it.

    :param steps: The steps as replayed, in order.
    :return: The steps worth stepping through.
    """
    kept: list[dict[str, t.Any]] = []
    for step in steps:
        if kept:
            last = kept[-1]
            before = [_[:4] for _ in last["vars"]]
            if (
                [_[:4] for _ in step["vars"]] == before
                and step["note"] in (None, last["note"])
                and not step["out"]
                and step["ret"] is None
                and step["error"] is None
            ):
                continue
        kept.append(step)
    return kept
