# =============================================================================
# Makefile for testing Akshay's Corner
#
# Author: Akshay Mestry <xa@mes3.dev>
# Created on: 22 February, 2025
# Last updated on: 13 September, 2026
#
# This Makefile provides a comprehensive set of commands (targets) for building
# and testing my website.
# =============================================================================

# === CONFIGURATIONS ==========================================================
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
LINKCHECK_DIR   := $(CACHE_DIR)/linkcheck
LINKCHECK_FILE  := $(LINKCHECK_DIR)/output.txt
LOG_FILE        := $(CACHE_DIR)/last.log

PROTOCOL        := http
LOCALHOST       := localhost
PORT            := 5500

# === TOOLS ===================================================================
SPHINX_BUILD    ?= sphinx-build
SPHINX_LINT     ?= sphinx-lint
HTTP_SERVER     ?= python3 -m http.server
TOX             ?= tox

# === FLAGS ===================================================================
SPHINX_BUILD_FLAGS := \
	--builder dirhtml \
	--fail-on-warning \
	--show-traceback \
	--fresh-env \
	--quiet \
	--color

SPHINX_LINKCHECK_FLAGS := \
	--builder linkcheck \
	--show-traceback \
	--fresh-env \
	--quiet \
	--color

# Quiet drops tox's own env-setup chatter. The command output it wraps
# is kept, which is the half worth reading when a run goes red.
TOX_FLAGS := \
	--quiet

SPHINX_LINT_FLAGS := \
	--disable role-with-double-backticks,role-without-backticks \
	--max-line-length 79

HTTP_SERVER_FLAGS := \
	$(PORT) \
	--directory $(OUTPUT_DIR)

define spin
	@mkdir -p $(CACHE_DIR); \
	[ -n "$(4)" ] && rm -f "$(4)"; \
	prefix="$(1) $(2)"; \
	if [ -t 1 ]; then printf '%b' "$$prefix"; else printf '%b... ' "$$prefix"; fi; \
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

# === TARGETS =================================================================
.DEFAULT_GOAL := help
.PHONY: help clean check lint format typecheck tox html linkcheck test \
	rebuild serve start stop devserver

# Improvement based on: https://stackoverflow.com/a/64394417
help: ## Show this help and list available targets.
	@printf "Usage:\n"
	@printf "  $(COLOUR_GREEN)make$(COLOUR_RESET) $(COLOUR_YELLOW)<target>$(COLOUR_RESET)\n\n"
	@printf "Targets:\n"
	@grep -E '^[a-zA-Z_-]+:.*##' $(firstword $(MAKEFILE_LIST)) | \
		sort | \
		awk 'BEGIN {FS = ":.*## *"} {printf "  $(COLOUR_BLUE)%-$(TARGET_PADDING)s$(COLOUR_RESET) %s\n", $$1, $$2}'
	@printf "\n$(COLOUR_DIM)For executing a particular target, run 'make <target>'.$(COLOUR_RESET)\n"
	@printf "$(COLOUR_DIM)Read complete documentation at: https://github.com/xames3/website.$(COLOUR_RESET)\n"

clean: ## Remove build artifacts and temporary directories.
	$(call spin,[  CLEAN],Removing build artifacts,rm -rf $(OUTPUT_DIR) $(CACHE_DIR))

check: ## Perform linting checks and report issues, if any.
	$(call spin,[ SPHINX],Running sphinx linter,$(SPHINX_LINT) $(SPHINX_LINT_FLAGS) $(SOURCE_DIR))

html: ## Build HTML files from the source directory.
	@$(MAKE) check --no-print-directory
	$(call spin,[  BUILD],Building HTML pages,$(SPHINX_BUILD) $(SPHINX_BUILD_FLAGS) $(SOURCE_DIR) $(OUTPUT_DIR))

linkcheck: ## Check every external link and report the dead ones.
	$(call spin,[  CHECK],Checking for broken external links,$(SPHINX_BUILD) $(SPHINX_LINKCHECK_FLAGS) $(SOURCE_DIR) $(LINKCHECK_DIR),$(LINKCHECK_FILE))

lint: ## Lint Python code with ruff, through tox.
	$(call spin,[   LINT],Linting python code,$(TOX) $(TOX_FLAGS) -e lint)

format: ## Check Python formatting with ruff, through tox.
	$(call spin,[  STYLE],Checking code format,$(TOX) $(TOX_FLAGS) -e format)

typecheck: ## Typecheck Python code with mypy, through tox.
	$(call spin,[   TYPE],Checking types,$(TOX) $(TOX_FLAGS) -e typecheck)

tox: ## Run every tox environment in parallel.
	$(call spin,[    TOX],Running every tox environment,$(TOX) $(TOX_FLAGS) -p)

test: ## Lint, build and check every link in one go.
	@$(MAKE) html --no-print-directory
	@$(MAKE) linkcheck --no-print-directory

rebuild: ## Rebuild HTML files after cleaning the build directory.
	@$(MAKE) clean --no-print-directory
	@$(MAKE) html --no-print-directory

serve: ## Start a development web server, if not running already and serve.
	@if lsof -nP -i :$(PORT) 2>/dev/null | grep -q LISTEN; then \
		printf "[  EXIST] Development server already running at $(PROTOCOL)://$(LOCALHOST):$(PORT)... $(COLOUR_ORANGE)SKIPPED!$(COLOUR_RESET)\n"; \
	else \
		$(MAKE) devserver --no-print-directory; \
	fi

start: ## Rebuild HTML files, start a development web server and serve.
	@$(MAKE) stop --no-print-directory
	@$(MAKE) rebuild --no-print-directory
	@$(MAKE) serve --no-print-directory

stop: ## Stop the development web server.
	@pids=$$(lsof -nP -i :$(PORT) 2>/dev/null | awk '/LISTEN/ {print $$2}' | sort -u); \
	if [ -z "$$pids" ]; then \
		printf "[  CLOSE] No development server on port $(PORT)... $(COLOUR_ORANGE)SKIPPED!$(COLOUR_RESET)\n"; \
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
	@printf "[  START] Starting development server at $(PROTOCOL)://$(LOCALHOST):$(PORT)... "
	@($(HTTP_SERVER) $(HTTP_SERVER_FLAGS) >/dev/null &); \
	for _ in 1 2 3 4 5 6 7 8 9 10; do \
		lsof -nP -i :$(PORT) 2>/dev/null | grep -q LISTEN && break; \
		sleep 0.2; \
	done; \
	if lsof -nP -i :$(PORT) 2>/dev/null | grep -q LISTEN; then \
		printf "$(COLOUR_GREEN)OK!$(COLOUR_RESET)\n\n"; \
		open "$(PROTOCOL)://$(LOCALHOST):$(PORT)" >/dev/null 2>&1 || \
			xdg-open "$(PROTOCOL)://$(LOCALHOST):$(PORT)" >/dev/null 2>&1 || \
			printf "$(COLOUR_DIM)Open $(PROTOCOL)://$(LOCALHOST):$(PORT) in your browser.$(COLOUR_RESET)\n"; \
	else \
		printf "$(COLOUR_RED)FAILED!$(COLOUR_RESET)\n"; \
		exit 1; \
	fi

all: ## Run all targets except linkcheck and start the development server
	@$(MAKE) stop --no-print-directory
	@$(MAKE) rebuild --no-print-directory
	@$(MAKE) tox --no-print-directory
	@$(MAKE) lint --no-print-directory
	@$(MAKE) typecheck --no-print-directory
	@$(MAKE) format --no-print-directory
	@$(MAKE) serve --no-print-directory
