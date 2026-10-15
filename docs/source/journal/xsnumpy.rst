.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: 01 March 2025
.. Last updated on: 13 October 2026

:km-pg-title: Rebuilding NumPy to understand it
:km-pg-description: Journey of building a lightweight, pure-python
    implementation of NumPy's core features
:km-pg-type: article
:km-pg-image: https://i.imgur.com/BPxkNzC.jpeg
:km-pg-image-alt: How writing a simplified NumPy in pure-Python taught me more
    about numerical computing than using the real thing.
:km-fb-title: Have you rebuilt something just to learn?
:km-fb-description: If you've cracked open an industry standard to truly master
    it, I'd love to hear your experiences.
:km-fb-button: Share your "aha" moment

.. _journal-building-xsnumpy:

===============================================================================
:far-icon:`screwdriver-wrench` Rebuilding NumPy to understand it
===============================================================================

.. rst-class:: km-lead

    How writing a simplified NumPy in pure-Python taught me more about
    numerical computing than using the real thing.

.. author:: @xames3
    :avatar: https://avatars.githubusercontent.com/u/90549089?v=4
    :url: https://github.com/xames3

I'm a wee bit fuzzy on the exact timelines, but it all started around
mid-November of 2024. I was still at the uni and in my second-to-last quarter.
I was working on an assignment that required me to use
`NumPy`_.

I multiplied some matrices; NumPy did its thing, as it always does and made
all the computations look super easy. But, under this "simplicity", a few
questions began to gnaw at me.

So, I thought of experimenting with a simple code, nothing fancy:

.. code-block:: python
    :linenos:

    a = np.array([[1, 2], [3, 4]])
    b = np.array([[5, 6], [7, 8]])
    np.dot(a, b)

The result popped out instantly. But this time, instead of just accepting the
answer, I asked myself a bunch of questions. Like, why was I even using
:func:`np.dot(a, b) <numpy.dot>` when I could've used
:py:data:`np.matmul(a, b) <numpy.matmul>`, which feels more appropriate?

And if :func:`np.dot(a, b) <numpy.dot>` indeed performs matrix multiplication,
then what's the deal with the :python:`a @ b` (:meth:`@ <object.__matmul__>`
operator)? Why are there three different ways to perform matrix multiplication,
and if so, which one's the best?

.. _building-with-a-purpose:

-------------------------------------------------------------------------------
Building with a purpose.
-------------------------------------------------------------------------------

With all these questions in mind, I was motivated enough to learn the actual
implementation details of NumPy. I was ready to build my own scrappy version. I
didn't set out to create something that'd rival NumPy; I mean, NumPy's a bloody
powerhouse, built over decades of work by incredibly talented minds in maths
and science, plus loads of optimisations.

I couldn't possibly compete with that.

I wanted to stop treating these libraries (starting with NumPy) as black boxes
and truly understand the "whys" and "hows". This realisation hit me so hard, I
challenged myself.

Could I build a dinky version of NumPy from scratch? Because if I'm going to
teach these concepts one day, I have to go **deeper**. If I were going to learn
this properly, I needed discipline and some rules to follow.

.. admonition:: :fas-icon:`badge-check km-green` Rules of engagement
    :class: km-unusual-one note

    - No use of LLMs or any AI usage of anything.
    - Every line of code and every solution had to come from my own
      understanding and experimentation.
    - Pure Python only. No external dependencies, just the standard library.
    - It should be clean, maintainable, statically typed and well-documented
      code that mirrors NumPy's public APIs, aiming to be a drop-in replacement
      where sensible.

.. _writing-my-first-array:

-------------------------------------------------------------------------------
Writing my first array.
-------------------------------------------------------------------------------

Now that I have set my rules, I started experimenting with NumPy's core APIs,
trying to understand their core behaviours and functionality. As I read through
more and more `documentation`_ and Stack Overflow answers, it quickly became
clear that most of NumPy's APIs are heavily relying on a single core construct,
the :func:`np.array <numpy.array>` function.

It's also worth noting that this function is a cheeky little wrapper for the
:class:`np.ndarray <numpy.ndarray>` class. That's where I decided to start,
implementing my own |xp.ndarray|_ data structure.

.. admonition:: :fas-icon:`lightbulb` Quick analogy
    :class: km-unusual-one seealso

    If you're new to arrays, think of them as egg cartons, each slot holds an
    egg and the shape of the carton tells you how many eggs you've got.

    Where your hand moves from one slot to the next are the strides; the type
    of eggs is the dtype; the carton itself is the buffer or the actual
    storage.

Now, by this point in time, I had a basic understanding of arrays and how they
worked. But, as I looked deeper and deeper, I discovered heaps of concepts,
including `memory allocation`_, `shape`_ calculations, `strides`_ and various
optimisation techniques for data storage.

It felt like opening Pandora's box; I wasn't ready. After a few days of
head-scratching, I managed to create a primitive, albeit minimal, working
version using Python's built-in :py:mod:`ctypes` module.

It worked poorly. But it worked!

Looking back, that was the easy bit. A constructor that takes five things,
``shape``, ``dtype``, ``buffer``, ``offset`` and ``strides``, looks harmless
until you realise each of them is a small rabbit hole and they all have to
agree with one another.

What finally helped was a change in how I pictured the thing. I'd been
thinking of an array as its data. It isn't. The data is just a strip of
memory, numbers sitting back to back with no idea they're supposed to be a
grid. The array is a **way of looking at that strip** and the shape, the
``dtype`` and the strides are the pair of glasses you read it through. Swap the
glasses and the very same memory becomes a different array.

That sounds a bit grand for a few dozen lines of Python, so let's watch it
happen instead.

.. rubric:: Making sense of shapes.
.. rubric::
    A shape of an array is a tuple of integers that represents the number of
    elements along **each dimension** (axis) of the array.
    :class: km-subtitle-text

I'll build a **3x4** array of floats in front of you, a line at a time, so just
keep scrolling. One warning first. I've intentionally removed loads of details
to keep things simple, like the check for unsupported memory orders and a fair
bit of type juggling. If you'd rather read the lot in one go, the complete
implementation of **ndarray** is on GitHub.

.. button:: https://github.com/xames3/xsnumpy/blob/main/xsnumpy/_core.py
    :fa-icon: fab fa-github

    See full implementation

.. walkthrough:: python
    :caption: `xsnumpy/_core.py`_
    :linenos:
    :watch: shape, dtype, itemsize, strides, buffersize

    .. setup::

        import ctypes
        from collections import namedtuple
        from collections.abc import Iterable

        _BaseDType = namedtuple("_BaseDType", "short, numpy, ctypes, value")
        _BaseDType.__repr__ = lambda self: f"dtype({self.numpy!r})"

        _supported_dtypes = (
            (int32 := _BaseDType("i4", "int32", ctypes.c_int32, 0)),
            (float32 := _BaseDType("f4", "float32", ctypes.c_float, 0.0)),
            (float64 := _BaseDType("f8", "float64", ctypes.c_double, 0.0)),
        )

        for dtype in _supported_dtypes:
            globals()[dtype] = dtype
        del dtype

        def _convert_dtype(dtype, to):
            return getattr(dtype, to)

        def calc_strides(shape, itemsize):
            strides = []
            stride = itemsize
            for dim in reversed(shape):
                strides.append(stride)
                stride *= dim
            return tuple(reversed(strides))

    .. code::

        class ndarray:

            def __init__(
                self,
                shape,
                dtype=float64,
                buffer=None,
                offset=0,
                strides=None,
            ):
                if not isinstance(shape, Iterable):
                    shape = (shape,)
                shape = tuple(int(dim) for dim in shape)
                if dtype is None:
                    dtype = float64
                elif isinstance(dtype, type):
                    dtype = globals()[f"{dtype.__name__}32"]
                else:
                    dtype = globals()[dtype]
                itemsize = int(_convert_dtype(dtype, "short")[-1])
                if buffer is None:
                    if offset != 0:
                        raise ValueError(
                            "Offset must be 0 when buffer is None"
                        )
                    if strides is not None:
                        raise ValueError(
                            "Strides must be None when buffer is None"
                        )
                    strides = calc_strides(shape, itemsize)
                else:
                    if (
                        isinstance(buffer, ndarray)
                        and buffer.base is not None
                    ):
                        buffer = buffer.base
                    if isinstance(buffer, ndarray):
                        buffer = buffer.data
                    if strides is None:
                        strides = calc_strides(shape, itemsize)
                buffersize = strides[0] * shape[0] // itemsize
                buffersize += offset
                Buffer = _convert_dtype(dtype, "ctypes") * buffersize
                if buffer is None:
                    data = Buffer()
                elif isinstance(buffer, ctypes.Array):
                    data = Buffer.from_address(ctypes.addressof(buffer))
                else:
                    data = Buffer.from_buffer(buffer)
                self._shape, self._dtype = shape, dtype
                self._strides, self._data = strides, data

        ndarray((3, 4), dtype=float)

    .. lines:: 11-13

        I started by checking if the provided shape can be
        :py:class:`iterated <collections.abc.Iterable>`. If it wasn't, I
        wrapped it in a :py:class:`tuple`, so ``5`` becomes ``(5,)``. Ours
        already is one.

        Then, I converted the shape into a tuple of :py:class:`integers
        <int>`, because you can't have non-integer dimensions in an array.

    .. lines:: 14-19

        Next up, the ``dtype`` (short for data type). If you didn't provide
        one, the constructor falls back to ``float64``. If you hand it a
        :py:class:`float` or an :py:class:`int`, it looks the appropriate data
        type up in the :func:`globals` namespace.

        This nifty trick meant I could dynamically fetch whatever data type I
        fancied. We passed ``float``, so ``dtype`` lands on ``float32``.

    .. lines:: 20

        Every data type knows how wide it is. ``float32``'s short code is
        ``f4``, whose last character is the number of bytes, so that's our
        ``itemsize``, 4.

    .. lines:: 21-29

        Right, on to the ``buffer``. If none was provided, the array is
        initialised without an external memory buffer. In this case, the
        ``offset`` must be zero and the ``strides`` must be
        :py:obj:`None`, which is all these two checks are for. Nothing gets
        raised this time.

    .. lines:: 30

        The constructor then calculates the `strides`_, which, put simply, are
        just the number of bytes between consecutive elements in memory.

        I've tucked ``calc_strides`` out of sight. It walks the shape
        **backwards**, multiplying up by each dimension as it goes, because the
        last axis is the one that's contiguous in memory. Step along a row and
        you move 4 bytes, step down a column and you move 16.

    .. lines:: 41-42

        Finally, calculating the total ``buffer`` size. This is worked out
        using the strides, shape and the size. ``16 * 3 // 4`` is 12 items,
        plus whatever ``offset`` there is, which is none.

    .. lines:: 43

        The ``buffer`` itself is a type derived from the data type and its
        size. A ``float32`` is a :py:class:`ctypes.c_float`, so this is twelve
        of those, back to back. It's only the *type* so far. Nothing has been
        allocated.

    .. lines:: 44-49

        Depending on whether a buffer was passed or not, the constructor
        handles the data accordingly, either creating a new buffer or using
        the existing one. We passed none, so ``Buffer()`` allocates a fresh
        one, zeroed.

    .. lines:: 50-51

        Store the lot and that's an array.

Have a look at what that actually made. Forty-eight bytes of zeros, a shape, a
``dtype`` and a pair of strides. Nothing in those bytes knows it's a grid.
That's the glasses again and it's why I stopped finding reshaping and
transposing so mysterious a while later. They don't touch the bytes at all.
They just hand you a different pair of glasses.

But that was the easy case, the one where the array makes its own memory. What
if the memory is already there?

That's the other half of the ``if`` and it's the half I understood last. Every
time you slice an array, you don't want a copy, you want to look at the same
memory again through new glasses. So a slice calls the constructor and hands it
the original array's memory as the ``buffer``. Here's the very same constructor
again, this time handed some memory that somebody else already allocated.

.. walkthrough:: python
    :caption: `xsnumpy/_core.py`_
    :linenos:
    :watch: shape, dtype, itemsize, strides, buffersize

    .. setup::

        import ctypes
        from collections import namedtuple
        from collections.abc import Iterable

        _BaseDType = namedtuple("_BaseDType", "short, numpy, ctypes, value")
        _BaseDType.__repr__ = lambda self: f"dtype({self.numpy!r})"

        _supported_dtypes = (
            (int32 := _BaseDType("i4", "int32", ctypes.c_int32, 0)),
            (float32 := _BaseDType("f4", "float32", ctypes.c_float, 0.0)),
            (float64 := _BaseDType("f8", "float64", ctypes.c_double, 0.0)),
        )

        for dtype in _supported_dtypes:
            globals()[dtype] = dtype
        del dtype

        def _convert_dtype(dtype, to):
            return getattr(dtype, to)

        def calc_strides(shape, itemsize):
            strides = []
            stride = itemsize
            for dim in reversed(shape):
                strides.append(stride)
                stride *= dim
            return tuple(reversed(strides))

    .. code::

        class ndarray:

            def __init__(
                self,
                shape,
                dtype=float64,
                buffer=None,
                offset=0,
                strides=None,
            ):
                if not isinstance(shape, Iterable):
                    shape = (shape,)
                shape = tuple(int(dim) for dim in shape)
                if dtype is None:
                    dtype = float64
                elif isinstance(dtype, type):
                    dtype = globals()[f"{dtype.__name__}32"]
                else:
                    dtype = globals()[dtype]
                itemsize = int(_convert_dtype(dtype, "short")[-1])
                if buffer is None:
                    if offset != 0:
                        raise ValueError(
                            "Offset must be 0 when buffer is None"
                        )
                    if strides is not None:
                        raise ValueError(
                            "Strides must be None when buffer is None"
                        )
                    strides = calc_strides(shape, itemsize)
                else:
                    if (
                        isinstance(buffer, ndarray)
                        and buffer.base is not None
                    ):
                        buffer = buffer.base
                    if isinstance(buffer, ndarray):
                        buffer = buffer.data
                    if strides is None:
                        strides = calc_strides(shape, itemsize)
                buffersize = strides[0] * shape[0] // itemsize
                buffersize += offset
                Buffer = _convert_dtype(dtype, "ctypes") * buffersize
                if buffer is None:
                    data = Buffer()
                elif isinstance(buffer, ctypes.Array):
                    data = Buffer.from_address(ctypes.addressof(buffer))
                else:
                    data = Buffer.from_buffer(buffer)
                self._shape, self._dtype = shape, dtype
                self._strides, self._data = strides, data

        raw = (ctypes.c_float * 12)()
        ndarray((3, 4), dtype=float, buffer=raw)

    .. lines:: 1-10

        The very same constructor, not a character changed. The only
        difference is the last two lines.

    .. lines:: 53

        Twelve floats' worth of memory that already exists, made with plain
        :py:mod:`ctypes` and not by me.

    .. lines:: 54

        And now an ``ndarray`` that's handed it as the ``buffer``. Everything
        up to the ``if`` runs exactly as before, so I'll skip along.

    .. lines:: 31-40

        This time ``buffer`` isn't :py:obj:`None`, so the other branch runs.
        If the buffer is itself an ``ndarray``, I swap it for the memory it
        looks at, so a slice of a slice still points at the original. Ours is
        a plain ctypes array, so both of those checks wave it through.

        Then the strides are either given, which a slice would do, or
        calculated the usual way, which is what happens here.

    .. lines:: 41-43

        The same sum as before, 12 items, and the same type to hold them.

    .. lines:: 44-49

        And here's what the three-way ``if`` was for. No buffer, allocate a
        fresh one. Already a ctypes array, point :py:meth:`from_address
        <ctypes._CData.from_address>` straight at it. Anything else that
        supports the buffer protocol goes through ``from_buffer``.

    .. lines:: 50-51

        Store it. ``self._data`` is ``raw``'s very own memory, not a copy of
        it.

That's why slicing in NumPy is so cheap and why it is in xsNumPy as well.
``a[1:]`` copies nothing. It makes another ``ndarray`` that looks at the same
memory, which is also why writing into a slice writes into the original.

That's a lot of work, innit?

.. _illusion-of-simplicity:

-------------------------------------------------------------------------------
Illusion of simplicity.
-------------------------------------------------------------------------------

After all that hard work, I thought of giving myself a break. I remembered
telling myself

.. epigraph::

    Let's start with something dead easy... perhaps just display
    the array. That couldn't be hard, right? All I've to do is print the
    content of my array in a readable format, just like NumPy does

    -- silly me, *2025*

Little did I know, I was shooting myself in the foot. At its core, a
:meth:`__repr__ <object.__repr__>` is an object's internal data representation.
Here's every version I wrote on the way there, one after another and what each
one printed when I tried it.

.. attempts:: python
    :caption: `xsnumpy/_core.py`_
    :code-position: left
    :linenos:

    .. attempt::

        .. code::

            def __repr__(self):
                return f"array({self._data}, dtype={str(self.dtype)})"

        .. output:: broke

            >>> xp.array([[1, 2], [3, 4]])
            array([1, 2, 3, 4], dtype=int64)

        I started with something simple and it worked for scalars and 1D
        arrays. Feeling quite pleased and a bit cocky, I tried a 2D array, but
        it unexpectedly printed everything as a flat list. I hadn't accounted
        for the rows and columns.

    .. attempt::

        No problem, I updated the code and it worked.

        .. code::

            def __repr__(self):
                if self.ndim == 1:
                    return f"array({self._data}, dtype={str(self.dtype)})"
                elif self.ndim > 1:
                    rows = ",\n       ".join(
                        [f"[{', '.join(map(str, row))}]" for row in self._data]
                    )
                    return f"array([{rows}], dtype={str(self.dtype)})"

        .. lines:: 2-3

            A 1D array keeps what already worked.

        .. lines:: 4-8

            Anything bigger gets its rows joined with a newline and seven
            spaces, so each one lines up under ``array([``.

        Then the 3D arrays... It broke again.

        .. output:: broke

            >>> xp.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])
            array([[[1, 2], [3, 4]],
                   [[5, 6], [7, 8]]], dtype=int64)

    .. attempt::

        That's when it hit me, this wasn't just about formatting strings. I
        needed a general solution that would work with any number of
        dimensions. A few days later, I found myself neck-deep in recursive
        logic and multidimensional `indexing`_, all for what I believed was an
        "easy" print function.

        .. code::

            def __repr__(self):
                def _extended_repr(s, axis, offset):
                    indent = min(2, max(0, (self.ndim - axis - 1)))
                    if axis < len(self.shape):
                        step = self.strides[axis] // self.itemsize
                        s += "["
                        for idx in range(self.shape[axis]):
                            if idx > 0:
                                s += ("\n       " + " " * axis) * indent
                            _oset = offset + idx * step
                            s = _extended_repr(s, axis + 1, _oset)
                            if idx < self.shape[axis] - 1:
                                s += ", "
                        s += "]"
                    else:
                        s += repr(self.data[offset])
                    return s

                s = _extended_repr("", 0, self._offset)
                if self.dtype not in (float64, int64, bool):
                    return f"array({s}, dtype={self.dtype})"
                return f"array({s})"

        .. lines:: 5

            This is where the strides finally pay off. ``step`` is how many
            items one step along this axis moves through the flat buffer.

        .. lines:: 8-9

            Between the items of an axis goes a newline and seven spaces, so
            each one lines up under ``array([``, and one more space for every
            level of nesting. The outer levels of a bigger array get a blank
            line as well.

        .. lines:: 10-11

            Then do the very same thing one axis down, from wherever this
            item starts in the buffer.

        .. lines:: 16

            At the bottom there are no axes left, only a number, so print it.

        .. lines:: 19-22

            The ``dtype`` only gets a mention when it isn't one of the usual
            suspects, just like NumPy.

        .. output:: worked

            >>> xp.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])
            array([[[1, 2],
                    [3, 4]],

                   [[5, 6],
                    [7, 8]]])

What started as a chilled attempt to rework :meth:`__repr__ <object.__repr__>`
turned out to be a masterclass in designing for generality. This struggle
taught me something fundamental. What seemingly appears simple on the surface
often hides massive complexity underneath.

And so, I realised, printing a NumPy array from scratch was a rabbit hole.

.. seealso::

    Complete implementation of |xp.ndarray.repr|_ with helper functions.

.. rubric:: More than meets the eye.

After wrestling with the "simple" things, I naively believed the hardest part
was behind me. I was excited for the fun stuff: element-wise arithmetic,
`broadcasting`_, transposing and other random functions. However, I didn't
realise my journey was about to get even more challenging.

Basic arithmetic operations like addition, subtraction and scalar
multiplication seemed straightforward. I figured I could just iterate through
my flattened data and perform operations element-wise.

And it worked for the first few test cases. But, as always, the test cases
failed almost immediately for higher-dimensional vectors. Here's
:meth:`__add__ <object.__add__>`, before and after.

.. attempts:: python
    :caption: `xsnumpy/_core.py`_
    :linenos:

    .. attempt::

        .. code::

            def __add__(self, other):
                arr = ndarray(self.shape, self.dtype)
                if isinstance(other, (int, float)):
                    arr[:] = [x + other for x in self._data]
                elif isinstance(other, ndarray):
                    if self.shape != other.shape:
                        raise ValueError(
                            "Operands couldn't broadcast together with shapes "
                            f"{self.shape} {other.shape}"
                        )
                    arr[:] = [x + y for x, y in zip(self.flat, other.flat)]
                else:
                    raise TypeError(
                        "Unsupported operand type(s) for +: "
                        f"{type(self).__name__!r} and "
                        f"{type(other).__name__!r}"
                    )
                return arr

        .. lines:: 3-4

            A number gets added to every element of the flat data.

        .. lines:: 5-11

            Another array has to be the very same shape, otherwise I turn it
            away. If it is, the two get added element by element.

        .. lines:: 12-17

            Anything else is turned away at the door.

        Looks sensible, doesn't it? But what about a ``(3,)`` array and a
        ``(3, 3)`` matrix?

        .. output:: broke

            >>> matrix = xp.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
            >>> vector = xp.array([1, 2, 3])
            >>> matrix + vector
            Traceback (most recent call last):
              ...
            ValueError: Operands couldn't broadcast together with shapes (3, 3) (3,)

        NumPy adds those two without blinking.

    .. attempt::

        So I stopped turning shapes away and started working out what they
        could become.

        .. code::

            def __add__(self, other):
                if isinstance(other, (int, float)):
                    out = ndarray(self.shape, self.dtype)
                    out[:] = [data + other for data in self._data]
                elif isinstance(other, ndarray):
                    shape = broadcast_shape(self.shape, other.shape)
                    self = self.broadcast_to(shape)
                    other = other.broadcast_to(shape)
                    out = ndarray(shape, self.dtype)
                    out[:] = [x + y for x, y in zip(self.flat, other.flat)]
                else:
                    raise TypeError(
                        "Unsupported operand type(s) for +: "
                        f"{type(self).__name__!r} and "
                        f"{type(other).__name__!r}"
                    )
                return out

        .. lines:: 6

            Work out the shape both sides agree on first. That's the resolver
            in the next bit and it took me longer than the rest of this put
            together.

        .. lines:: 7-8

            Then stretch each side out to that shape, so the two line up
            number for number.

        .. lines:: 9-10

            And from there it's the same element-by-element sum as before.

        .. output:: worked

            >>> matrix + vector
            array([[ 2,  4,  6],
                   [ 5,  7,  9],
                   [ 8, 10, 12]])
            >>> matrix + 10
            array([[11, 12, 13],
                   [14, 15, 16],
                   [17, 18, 19]])

What if I added a scalar to a matrix or a ``(3,)`` array to a ``(3, 3)``
matrix? Could I add a :py:class:`float` to an :py:class:`int`? Each of those
experiments brought new challenges and I was absolutely frustrated!

That's when I realised I wasn't just adding or multiplying numbers, but
learning and simultaneously recreating NumPy's broadcasting rules.

.. rubric:: The shape both sides agree on.
.. rubric::
    Here's the resolver, running. This one's worth watching the values on
    rather than the code.
    :class: km-subtitle-text

.. walkthrough:: python
    :caption: `xsnumpy/_utils.py`_
    :code-position: left
    :linenos:
    :watch: input, other, r_input, r_other, maximum, idx, jdx, buffer

    .. code::

        def broadcast_shape(input, other):
            buffer = []
            r_input = list(reversed(input))
            r_other = list(reversed(other))
            maximum = max(len(r_input), len(r_other))
            r_input.extend([1] * (maximum - len(r_input)))
            r_other.extend([1] * (maximum - len(r_other)))
            for idx, jdx in zip(r_input, r_other):
                if idx == jdx or idx == 1 or jdx == 1:
                    buffer.append(max(idx, jdx))
                else:
                    raise ValueError(
                        "Operands couldn't broadcast together with shapes "
                        f"{input} and {other}"
                    )
            return tuple(reversed(buffer))

        broadcast_shape((3, 3), (3,))

    .. lines:: 1

        The shape resolver on its own, with nothing else in the way.

    .. lines:: 18

        A ``(3, 3)`` matrix and a bare ``(3,)`` vector. NumPy does this
        without blinking. I very much did blink.

    .. lines:: 2-4

        ``buffer`` is where the answer gets built. Both shapes are turned
        back to front first, because broadcasting lines the shapes up from
        the **right**. The last dimensions meet first.

    .. lines:: 5-7

        The thing that finally made it click, the shorter shape gets padded
        out with ones. That's it. That's the rule I'd been dancing around for
        days. ``(3,)`` quietly becomes ``(3, 1)`` back to front, which is
        ``(1, 3)`` the right way round, and suddenly both shapes are the same
        length.

    .. lines:: 8

        Now walk them in step, one pair of dimensions at a time.

    .. lines:: 9-15

        If the two dimensions match or either one is a ``1``, take the bigger
        of the two and move on. A ``1`` stretches to meet the other side.
        Nothing is actually copied, mind, that's the whole point of it, but
        the *shape* maths behaves as though it were.

        The ``else`` is the branch we never get to here. If neither side is a
        ``1`` and they don't match, the shapes are genuinely incompatible and
        there's nothing clever to be done about it.

    .. lines:: 16

        ``(3, 3)``, once it's turned back the right way round. Which is
        obvious in hindsight and obvious things in hindsight are the entire
        reason I built this library.

NumPy raises on that last branch too. It took me an unreasonable amount of time
to accept that "just error" was the correct answer.

.. rubric:: Final boss, Matrix Multiplication.
.. rubric:: Matrix multiplication was another **beast** entirely.
    :class: km-subtitle-text

I thought it would be just a matter of looping through rows and columns,
summing them element-wise, high school maths, if you ask me. Here's roughly
that, on the very same matrices from the start of this story.

.. walkthrough:: python
    :caption: `xsnumpy/_numeric.py`_
    :code-position: left
    :linenos:
    :watch: idx, jdx, out

    .. code::

        def matmul(a, b):
            out = [[0] * len(b[0]) for _ in range(len(a))]
            for idx in range(len(a)):
                for jdx in range(len(b[0])):
                    out[idx][jdx] = sum(
                        a[idx][kdx] * b[kdx][jdx] for kdx in range(len(b))
                    )
            return out

        matmul([[1, 2], [3, 4]], [[5, 6], [7, 8]])

    .. lines:: 1

        A plain function on plain nested lists. No NumPy, no ``ndarray``, just
        what I'd have written in the first week of any programming course.

    .. lines:: 10

        The matrices from the very first snippet. NumPy handed the answer back
        in a blink. Let's see how long it takes me.

    .. lines:: 2

        The answer has as many rows as ``a`` and as many columns as ``b``. It
        starts out as nothing but zeros.

    .. lines:: 3-4

        One row of the answer at a time and one cell of it at a time.

    .. lines:: 5-7

        Each cell is a row of ``a`` against a column of ``b``, multiplied pair
        by pair and added up, so the first is ``1 * 5 + 2 * 7``, which is 19.

    .. lines:: 8

        ``[[19, 22], [43, 50]]``. The very matrix that popped out of
        :func:`np.dot(a, b) <numpy.dot>` at the start.

And it worked as well until I tried with higher-dimensional arrays.

This is where I realised that matrix multiplication isn't just about rows and
columns, but about correctly handling batch dimensions for higher-order
tensors.

I found myself diving into NVIDIA's documentation, reading about the
`Generalised Matrix Multiplication (GEMM)`_ routines and how broadcasting
affects the output shapes.

.. seealso::

    Complete implementation of `arithmetic operations
    <https://github.com/xames3/xsnumpy/blob/main/xsnumpy/_core.py>`_ on GitHub.

Which, finally, answered the question that started all of this. For two
dimensions, :func:`np.dot(a, b) <numpy.dot>`,
:py:data:`np.matmul(a, b) <numpy.matmul>` and :python:`a @ b` give the very
same answer, which is exactly why it took me so long to spot that there was a
difference. The :meth:`@ <object.__matmul__>` operator is just ``matmul`` in a
nicer coat.

Above two dimensions, they part ways. ``matmul`` treats the leading axes as a
stack of matrices and multiplies them pair by pair, while ``dot`` multiplies
every matrix in the first against every matrix in the second.

.. code-block:: python

    >>> a = np.ones((2, 2, 2))
    >>> (a @ a).shape
    (2, 2, 2)
    >>> np.dot(a, a).shape
    (2, 2, 2, 2)

So, which one's the best? For matrices, :python:`@`, every time. It says what
it means.

.. rubric:: Small victories, big lessons.
.. rubric::
    Here comes December. By now, I wasn't just rebuilding a scrappy numerical
    computing **doppelganger** like I thought I was.
    :class: km-subtitle-text

I was on my winter break. I was fully committed to this project because I
didn't have to attend uni or work on any assignments. After days of debugging,
I realised that my vector operations weren't just about getting the "maths"
right.

They were about thinking like NumPy:

- How can I minimise unnecessary data duplication?
- How can I broadcast arrays?
- How can I infer the correct output shape?

I was creating a flexible and extensible system that could handle both
intuitive and weird edge cases. With each iteration, every commit I made, I
explored even more ways to optimise it, reducing redundant calculations.

Every bug, every unexpected result, every failure, every new piece of answer
and advice that I received on Stack Overflow and every small achievement
taught me something new about NumPy. As time passed, xsNumPy evolved into more
than just a project and a scrappy experiment.

It became a weird, obsessive mentality. A belief that the best way to learn is
by rolling up your sleeves, taking things apart, trying to understand the
problem and putting it back together, piece by piece.

.. _so-what-can-xsnumpy-do:

-------------------------------------------------------------------------------
So, what can xsNumPy do?
-------------------------------------------------------------------------------

Like I said, xsNumPy started off as a learning exercise and has since grown
into a small but cheeky, reliable companion that I can use to demonstrate the
underlying mechanics of some of the implementations of NumPy.

It was not about speed but about clarity. Below are some things that xsNumPy
does quite well.

.. tab-set::

    .. tab-item:: :far-icon:`empty-set` Creations

        xsNumPy provides familiar ways to create arrays. These creation
        routines are consistent, predictable and designed to slot neatly into
        later operations.

        - ``array()``

          Like NumPy, the |xp.array|_ function is the bread and butter of
          xsNumPy as well. It's the most flexible way to create arrays from
          Python lists or tuples with sensible ``dtype`` inference and the
          option to set one explicitly.

          .. code-block:: python

              >>> import xsnumpy as xp
              >>> xp.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])
              array([[[1, 2],
                      [3, 4]],

                     [[5, 6],
                      [7, 8]]])
              >>> xp.array([1, 0, 2], dtype=xp.bool)
              array([True, False, True])

        - ``zeros()``, ``ones()`` and ``full()``

          xsNumPy support |xp.zeros|_, |xp.ones|_ and |xp.full|_ functions for
          repeatable initialisation of arrays filled with, zeros, ones and any
          ``fill_value`` respectively.

          .. code-block:: python

              >>> xp.zeros(3)
              array([0. , 0. , 0. ])
              >>> xp.ones([3, 2], dtype=xp.int32)
              array([[1, 1],
                     [1, 1],
                     [1, 1]])
              >>> xp.full(2, 3, fill_value=3.14159)
              array([[3.14159, 3.14159, 3.14159],
                     [3.14159, 3.14159, 3.14159]])

        - ``arange()``

          Inspired by Python's :py:class:`range`, |xp.arange|_ generates arrays
          with evenly spaced values.

          .. code-block:: python

              >>> xp.arange(0, 5, 0.5)
              array([0. , 0.5, 1. , 1.5, 2. , 2.5, 3. , 3.5, 4. , 4.5])

        .. seealso::

            Check out all of array `creation <https://github.com/xames3/
            xsnumpy?tab=readme-ov-file#array-creation-routines>`_ methods
            supported by xsNumPy on GitHub.

    .. tab-item:: :far-icon:`plus-minus` Operations

        xsNumPy provides a range of arithmetic operations, carefully adhering
        to NumPy's rules for broadcasting and type coercion. The emphasis is on
        correctness and clear behaviour across dimensions.

        - **Element-wise arithmetic**

          xsNumPy supports element-wise addition, subtraction, multiplication,
          and division along with other basic arithmetics.

          .. code-block:: python

              >>> a = xp.array([[1, 0], [0, 1]])
              >>> b = xp.array([[4, 1], [2, 2]])
              >>> a + b
              array([[5, 1],
                     [2, 3]])

        - **Broadcasting arithmetic**

          xsNumPy matches shapes, stretches smaller arrays and makes sure the
          output shape followed NumPy's exact logic. Just like NumPy, these
          operations are broadcasted.

          .. code-block:: python

              >>> matrix = xp.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
              >>> vector = xp.array([[1], [2], [3]])
              >>> matrix + vector
              array([[ 2,  4,  6],
                     [ 5,  7,  9],
                     [ 8, 10, 12]])

        - **Linear algebraic helper functions**

          To mirror NumPy's API, xsNumPy supports explicit arithmetic
          functions. These are useful when you want to be very clear about the
          operation being performed or when you need more control over the
          parameters.

          .. code-block:: python

              >>> a = xp.array([[1, 0], [0, 1]])
              >>> b = xp.array([[4, 1], [2, 2]])
              >>> xp.dot(a, b)
              array([[4, 1],
                     [2, 2]])

        - **Scalar operations**

          xsNumPy supports scalar operations as well so you're not just
          limited to array-to-array operations.

          .. code-block:: python

              >>> xp.array([3, 4]) + 10
              array([13, 14])

        .. seealso::

            Check out examples of the arithmetic
            `operations <https://github.com/xames3/xsnumpy?
            tab=readme-ov-file#linear-algebra>`_ supported by xsNumPy on
            GitHub.

    .. tab-item:: :far-icon:`diagram-predecessor` Transforms

        xsNumPy provides essential shape manipulation APIs that are predictable
        and memory-aware. The emphasis is on clarity of intent and avoiding
        unnecessary data duplication. Think of this as learning to fold and
        unfold the same fabric without tearing it.

        .. tip::

            Read more about `NumPy internals`_ here.

        - ``.reshape()``

          The |xp.ndarray.reshape|_ method changes the view of data when
          possible, preserving the total element count.

          .. code-block:: python

              >>> a = xp.array([1, 2, 3, 4, 5, 6])
              >>> a.reshape((2, 3))
              array([[1, 2, 3],
                     [4, 5, 6]])

        - ``.transpose()``

          Transposing is more than just flipping rows and columns; for
          higher-dimensional arrays, it's about permuting the axes. The
          |xp.ndarray.transpose|_ method does just that.

          .. code-block:: python

              >>> a = xp.array([[1, 2, 3], [4, 5, 6]])
              >>> a.transpose()
              array([[1, 4],
                     [2, 5],
                     [3, 6]])

        - ``.flatten()``

          The |xp.ndarray.flatten|_ method returns a tidy 1D copy.

          .. code-block:: python

              >>> a = xp.array([[1, 2, 3], [4, 5, 6]])
              >>> a.flatten()
              array([1, 2, 3, 4, 5, 6])

    .. tab-item:: :far-icon:`brackets-square` Indexing

        Indexing is expressive and disciplined in xsNumPy, just like NumPy. The
        goal is to provide intuitive access to elements and subarrays while
        maintaining clarity about the underlying data structure.

        .. attention::

            Indexing and slicing were implemented by overridding the standard
            :meth:`__getitem__ <object.__getitem__>`  and
            :meth:`__setitem__ <object.__setitem__>`  protocols.

        - **Basic indexing**

          At its core, basic indexing in xsNumPy works similarly to NumPy,
          using zero-based indices to access elements. You can fetch single
          elements or entire subarrays. You can also use negative indices to
          count from the end of an array.

          .. code-block:: python

              >>> a = xp.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
              >>> a[1, 2]
              6
              >>> a[-1, -2]
              8

        - **Slicing**

          Slicing allows you to extract subarrays using a
          :python:`a[start:stop:step]` format. Just like NumPy, xsNumPy
          supports almost all the classic slicing mechanics.

          .. code-block:: python

              >>> a = xp.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
              >>> a[::2]
              array([[1, 2, 3],
                     [7, 8, 9]])
              >>> a[:2, 1:]
              array([[2, 3],
                     [5, 6]])

        - **Boolean masking**

          Boolean masking lets you select elements based on a condition.

          .. code-block:: python

              >>> a[a % 2 == 0]
              array([2, 4, 6, 8])

        .. seealso::

            Check out the complete implementation
            `here <https://github.com/xames3/xsnumpy/blob/
            69c302ccdd594f1d8f0c51dbe16346232c39047f/xsnumpy/_core.py>`_
            on GitHub.

    .. tab-item:: :far-icon:`sigma` Reductions

        Reductions condense information carefully, preserving the essence of
        the data. xsNumPy provides a few key reduction operations that are
        predictable and consistent.

        - ``.sum()``

          The |xp.sum|_ method computes the sum of elements along a given
          axis.

          .. code-block:: python

              >>> a = xp.array([[1, 2, 3], [4, 5, 6]])
              >>> a.sum()
              21
              >>> a.sum(axis=0)
              array([5, 7, 9])

        - ``.prod()``

          The |xp.prod|_ (product) method computes the multiplication of
          elements along a given axis.

          .. code-block:: python

              >>> a = xp.array([[1, 2, 3], [4, 5, 6]])
              >>> a.prod()
              720
              >>> a.prod(axis=0)
              array([ 4, 10, 18])

        - ``.any()`` and ``.all()``

          The |xp.all|_ method checks if all elements are :py:obj:`True`, while
          |xp.any|_ checks if at least one is.

          .. code-block:: python

              >>> b = xp.array([[True, False, True], [True, True, False]])
              >>> b.all()
              False
              >>> b.any(axis=1)
              array([True, True])


.. rubric:: Sharing notes with the community.
.. rubric::
    I gave a talk at `ChiPy`_ titled **"xsNumPy: Curiosity to Code"**, walking
    through the decisions, the missteps and the insights that stayed with me.
    :class: km-subtitle-text

.. youtube:: https://www.youtube.com/watch?v=QIhyix3oEns
    :caption: The presentation covered the technical challenges, mathematical
        discoveries and most importantly, the mindset shift from viewing
        libraries as opaque entities to understanding them as collections of
        elegant algorithms waiting to be explored.

.. _looking-back-moving-forward:

-------------------------------------------------------------------------------
Looking back, moving forward.
-------------------------------------------------------------------------------

xsNumPy didn't aim for performance; that wasn't the plan anyway. It was to
learn and understand, build intuition. It taught me to replace awe with
attention, trusting libraries while still learning and understanding their
core concepts with care.

Most importantly, it reminded me that doing something by yourself is perhaps
the best teaching and learning experience.

I intend to work on this project in small, respectful steps whenever I get
time. However, the larger work is already done. I re-learnt the essentials by
making them and that learning will travel with me far beyond this code.

.. _NumPy: https://numpy.org
.. _Generalised Matrix Multiplication (GEMM): https://docs.nvidia.com/
    deeplearning/performance/dl-performance-matrix-multiplication/index.html
.. _multiplying matrices: https://www.mathsisfun.com/algebra/
    matrix-multiplying.html
.. _memory allocation: https://numpy.org/doc/stable/reference/
    c-api/data_memory.html
.. _shape: https://numpy.org/doc/stable/reference/generated/numpy.ndarray.
    shape.html
.. _strides: https://numpy.org/doc/stable/reference/generated/numpy.ndarray.
    strides.html
.. _broadcasting: https://numpy.org/doc/stable/user/basics.broadcasting.html
.. _indexing: https://numpy.org/doc/stable/user/basics.indexing.html
.. _NumPy internals: https://numpy.org/doc/stable/dev/internals.html
.. _ChiPy: https://www.chipy.org/
.. _documentation: https://numpy.org/doc/stable/reference/index.html#reference

.. _xsnumpy/_core.py: https://github.com/xames3/xsnumpy/blob/main/xsnumpy/
    _core.py
.. _xsnumpy/_utils.py: https://github.com/xames3/xsnumpy/blob/main/xsnumpy/
    _utils.py
.. _xsnumpy/_numeric.py: https://github.com/xames3/xsnumpy/blob/main/xsnumpy/
    _numeric.py

.. |xp.ndarray| replace:: ``ndarray``
.. _xp.ndarray: https://github.com/xames3/xsnumpy/blob/
    69c302ccdd594f1d8f0c51dbe16346232c39047f/xsnumpy/_core.py
.. |xp.ndarray.repr| replace:: ``__repr__``
.. _xp.ndarray.repr: https://github.com/xames3/xsnumpy/blob/
    69c302ccdd594f1d8f0c51dbe16346232c39047f/xsnumpy/_core.py
.. |xp.array| replace:: ``array``
.. _xp.array: https://github.com/xames3/xsnumpy/blob/
    69c302ccdd594f1d8f0c51dbe16346232c39047f/xsnumpy/_numeric.py
.. |xp.zeros| replace:: ``zeros``
.. _xp.zeros: https://github.com/xames3/xsnumpy/blob/
    69c302ccdd594f1d8f0c51dbe16346232c39047f/xsnumpy/_numeric.py
.. |xp.ones| replace:: ``ones``
.. _xp.ones: https://github.com/xames3/xsnumpy/blob/
    69c302ccdd594f1d8f0c51dbe16346232c39047f/xsnumpy/_numeric.py
.. |xp.full| replace:: ``full``
.. _xp.full: https://github.com/xames3/xsnumpy/blob/
    69c302ccdd594f1d8f0c51dbe16346232c39047f/xsnumpy/_numeric.py
.. |xp.arange| replace:: ``arange``
.. _xp.arange: https://github.com/xames3/xsnumpy/blob/
    69c302ccdd594f1d8f0c51dbe16346232c39047f/xsnumpy/_numeric.py
.. |xp.ndarray.reshape| replace:: ``reshape``
.. _xp.ndarray.reshape: https://github.com/xames3/xsnumpy/blob/
    69c302ccdd594f1d8f0c51dbe16346232c39047f/xsnumpy/_core.py
.. |xp.ndarray.transpose| replace:: ``transpose``
.. _xp.ndarray.transpose: https://github.com/xames3/xsnumpy/blob/
    69c302ccdd594f1d8f0c51dbe16346232c39047f/xsnumpy/_core.py
.. |xp.ndarray.flatten| replace:: ``flatten``
.. _xp.ndarray.flatten: https://github.com/xames3/xsnumpy/blob/
    69c302ccdd594f1d8f0c51dbe16346232c39047f/xsnumpy/_core.py
.. |xp.sum| replace:: ``sum``
.. _xp.sum: https://github.com/xames3/xsnumpy/blob/
    69c302ccdd594f1d8f0c51dbe16346232c39047f/xsnumpy/_numeric.py
.. |xp.prod| replace:: ``prod``
.. _xp.prod: https://github.com/xames3/xsnumpy/blob/
    69c302ccdd594f1d8f0c51dbe16346232c39047f/xsnumpy/_numeric.py
.. |xp.all| replace:: ``all``
.. _xp.all: https://github.com/xames3/xsnumpy/blob/
    69c302ccdd594f1d8f0c51dbe16346232c39047f/xsnumpy/_numeric.py
.. |xp.any| replace:: ``any``
.. _xp.any: https://github.com/xames3/xsnumpy/blob/
    69c302ccdd594f1d8f0c51dbe16346232c39047f/xsnumpy/_numeric.py
