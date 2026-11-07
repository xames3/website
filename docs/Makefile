# =============================================================================
# Makefile for Akshay Mestry's website
#
# Author: Akshay Mestry <xa@mes3.dev>
# Created on: 22 February 2025
# Last updated on: 02 November 2026
#
# The commands I use to build, check and serve the site. Run make for the list.
# =============================================================================

COLOUR_DIM      := \033[2m
COLOUR_RESET    := \033[0m

COLOUR_RED      := \033[38;5;160m
COLOUR_GREEN    := \033[38;5;34m
COLOUR_ORANGE   := \033[38;5;220m
COLOUR_YELLOW   := \033[38;5;214m
COLOUR_BLUE     := \033[38;5;75m

TARGET_PADDING  := 12
SPINNER_FRAMES  := "" "." ".." "..."
SPINNER_DELAY   := 0.25

SOURCE_DIR      := source
OUTPUT_DIR      := build
CACHE_DIR       := .cache
DOCTREE_DIR     := $(CACHE_DIR)/doctrees
INVENTORY_DIR   := $(CACHE_DIR)/intersphinx
LINKCHECK_DIR   := $(CACHE_DIR)/linkcheck
LINKCHECK_FILE  := $(LINKCHECK_DIR)/output.txt
LOG_FILE        := $(CACHE_DIR)/last.log

INVENTORIES     := \
	numpy=https://numpy.org/doc/stable/objects.inv \
	python=https://docs.python.org/3/objects.inv \
	sphinx=https://www.sphinx-doc.org/en/master/objects.inv \
	torch=https://docs.pytorch.org/docs/2.11/objects.inv

PROTOCOL        := http
LOCALHOST       := localhost
PORT            := 5500
URL             := $(PROTOCOL)://$(LOCALHOST):$(PORT)

SPHINX_BUILD    ?= sphinx-build
CHECK           ?= check
LOCAL           ?=
HTTP_SERVER     ?= python3 -m http.server
TOX             ?= tox
CURL            ?= curl

SPHINX_BUILD_FLAGS := \
	--builder dirhtml \
	--doctree-dir $(DOCTREE_DIR) \
	--fail-on-warning \
	--show-traceback \
	--fresh-env \
	--quiet \
	--color

CURL_FLAGS := \
	--fail \
	--location \
	--silent \
	--show-error \
	--retry 3 \
	--retry-all-errors \
	--connect-timeout 10 \
	--max-time 30

SPHINX_LINKCHECK_FLAGS := \
	--builder linkcheck \
	--show-traceback \
	--fresh-env \
	--quiet \
	--color

TOX_FLAGS := \
	--quiet

HTTP_SERVER_FLAGS := \
	$(PORT) \
	--bind 0.0.0.0 \
	--directory $(OUTPUT_DIR)

define spin
	@mkdir -p $(CACHE_DIR); \
	[ -n "$(4)" ] && rm -f "$(4)"; \
	prefix="$(1) $(2)"; \
	if [ -t 1 ]; then \
		printf '%b' "$$prefix"; \
	else \
		printf '%b... ' "$$prefix"; \
	fi; \
	( $(3) ) >$(LOG_FILE) 2>&1 & \
	pid=$$!; \
	if [ -t 1 ]; then \
		while kill -0 $$pid 2>/dev/null; do \
			for dots in $(SPINNER_FRAMES); do \
				printf '\r%b%-3s' "$$prefix" "$$dots"; \
				sleep $(SPINNER_DELAY); \
				kill -0 $$pid 2>/dev/null || break; \
			done; \
		done; \
		printf '\r%b... ' "$$prefix"; \
	fi; \
	if wait $$pid; then \
		printf '$(COLOUR_GREEN)OK!$(COLOUR_RESET)\n'; \
		status=0; \
	else \
		printf '$(COLOUR_RED)FAILED!$(COLOUR_RESET)\n'; \
		status=1; \
	fi; \
	if [ -n "$(4)" ] && [ -s "$(4)" ]; then \
		sed 's/^/    /' "$(4)"; \
	elif [ $$status -ne 0 ] && [ -s $(LOG_FILE) ]; then \
		sed 's/^/    /' $(LOG_FILE); \
	fi; \
	exit $$status
endef

define fetch
mkdir -p $(INVENTORY_DIR); \
missing=0; \
for pair in $(INVENTORIES); do \
	name=$${pair%%=*}; \
	if $(CURL) $(CURL_FLAGS) --output $(INVENTORY_DIR)/$$name.part \
		$${pair#*=}; then \
		mv $(INVENTORY_DIR)/$$name.part $(INVENTORY_DIR)/$$name.inv; \
	else \
		rm -f $(INVENTORY_DIR)/$$name.part; \
		[ -s $(INVENTORY_DIR)/$$name.inv ] || { \
			echo "no inventory for $$name" >&2; \
			missing=1; \
		}; \
	fi; \
done; \
exit $$missing
endef

.DEFAULT_GOAL := help
.PHONY: help clean check lint format reformat typecheck tox html \
	linkcheck rebuild serve start stop devserver inventories all

# Improvement based on: https://stackoverflow.com/a/64394417
help: ## Show this help and list available targets.
	@printf "Usage:\n"
	@printf "  $(COLOUR_GREEN)make$(COLOUR_RESET) "
	@printf "$(COLOUR_YELLOW)<target>$(COLOUR_RESET)\n\n"
	@printf "Targets:\n"
	@grep -E '^[a-zA-Z_-]+:.*##' $(firstword $(MAKEFILE_LIST)) | \
		sort | \
		awk 'BEGIN {FS = ":.*## *"} \
		{printf "  $(COLOUR_BLUE)%-$(TARGET_PADDING)s$(COLOUR_RESET) %s\n", \
		$$1, $$2}'
	@printf "\n$(COLOUR_DIM)For executing a particular target, run "
	@printf "'make <target>'.$(COLOUR_RESET)\n"
	@printf "$(COLOUR_DIM)Documentation: https://xa.mes3.dev/docs/kaamiki/"
	@printf "$(COLOUR_RESET)\n"

clean: ## Remove the build output, egg-info folders and temporary directories.
	$(call spin,[  CLEAN],Removing the build output,\
		rm -rf $(OUTPUT_DIR) $(DOCTREE_DIR) \
		$(LINKCHECK_DIR) ../build ../*.egg-info)

check: ## Lint the rST with sphinx-lint.
	$(call spin,[ SPHINX],Running sphinx linter,\
		$(TOX) $(TOX_FLAGS) -e sphinxlint)

html: ## Build HTML files from the source directory.
	@$(if $(CHECK),$(MAKE) $(CHECK) --no-print-directory)
	$(call spin,[  BUILD],Building HTML pages,\
		$(SPHINX_BUILD) $(SPHINX_BUILD_FLAGS) $(if $(LOCAL),--tag local) \
		$(SOURCE_DIR) $(OUTPUT_DIR))

inventories: ## Fetch the intersphinx inventories the build falls back on.
	$(call spin,[  FETCH],Fetching intersphinx inventories,$(fetch))

linkcheck: ## Check every external link and report the dead ones.
	$(call spin,[  CHECK],Checking for broken external links,\
		$(SPHINX_BUILD) $(SPHINX_LINKCHECK_FLAGS) \
		$(SOURCE_DIR) $(LINKCHECK_DIR),$(LINKCHECK_FILE))

lint: ## Lint Python code with ruff, through tox.
	$(call spin,[   LINT],Linting python code,$(TOX) $(TOX_FLAGS) -e lint)

format: ## Check Python formatting with ruff, through tox.
	$(call spin,[  STYLE],Checking code format,$(TOX) $(TOX_FLAGS) -e format)

reformat: ## Fix lint and reformat Python, TOML, HTML and Jinja, through tox.
	$(call spin,[ REFORM],Reformatting sources,$(TOX) $(TOX_FLAGS) -e reformat)

typecheck: ## Typecheck Python code with mypy, through tox.
	$(call spin,[   TYPE],Checking types,$(TOX) $(TOX_FLAGS) -e typecheck)

tox: ## Run every tox check in parallel.
	$(call spin,[    TOX],Running every tox check,$(TOX) $(TOX_FLAGS) -p)

rebuild: ## Rebuild HTML files after cleaning the build directory.
	@$(MAKE) clean --no-print-directory
	@$(MAKE) inventories --no-print-directory
	@$(MAKE) html LOCAL=1 --no-print-directory

serve: ## Start a development web server, if not running already and serve.
	@if lsof -nP -i :$(PORT) 2>/dev/null | grep -q LISTEN; then \
		printf "[  EXIST] Development server already running at $(URL)... "; \
		printf "$(COLOUR_ORANGE)SKIPPED!$(COLOUR_RESET)\n"; \
	else \
		$(MAKE) devserver --no-print-directory; \
	fi

start: ## Rebuild HTML files, start a development web server and serve.
	@$(MAKE) stop --no-print-directory
	@$(MAKE) rebuild --no-print-directory
	@$(MAKE) serve --no-print-directory

stop: ## Stop the development web server.
	@pids=$$(lsof -nP -i :$(PORT) 2>/dev/null \
		| awk '/LISTEN/ {print $$2}' | sort -u); \
	if [ -z "$$pids" ]; then \
		printf "[  CLOSE] No development server on port $(PORT)... "; \
		printf "$(COLOUR_ORANGE)SKIPPED!$(COLOUR_RESET)\n"; \
	else \
		printf "[  CLOSE] Stopping any development server... "; \
		if kill $$pids 2>/dev/null; then \
			printf "$(COLOUR_GREEN)OK!$(COLOUR_RESET)\n"; \
		else \
			printf "$(COLOUR_RED)FAILED!$(COLOUR_RESET)\n"; \
			exit 1; \
		fi; \
	fi

devserver:
	@printf "[  START] Starting development server at $(URL)... "
	@($(HTTP_SERVER) $(HTTP_SERVER_FLAGS) >/dev/null 2>&1 &); \
	for _ in 1 2 3 4 5 6 7 8 9 10; do \
		lsof -nP -i :$(PORT) 2>/dev/null | grep -q LISTEN && break; \
		sleep 0.2; \
	done; \
	if lsof -nP -i :$(PORT) 2>/dev/null | grep -q LISTEN; then \
		printf "$(COLOUR_GREEN)OK!$(COLOUR_RESET)\n\n"; \
		open "$(URL)" >/dev/null 2>&1 || \
			xdg-open "$(URL)" >/dev/null 2>&1 || { \
				printf "$(COLOUR_DIM)Open $(URL) in your browser."; \
				printf "$(COLOUR_RESET)\n"; \
			}; \
	else \
		printf "$(COLOUR_RED)FAILED!$(COLOUR_RESET)\n"; \
		exit 1; \
	fi

all: ## Rebuild, run the tox checks and serve the site.
	@$(MAKE) stop --no-print-directory
	@$(MAKE) rebuild --no-print-directory
	@$(MAKE) tox --no-print-directory
	@$(MAKE) serve --no-print-directory
