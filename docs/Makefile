# =============================================================================
# Makefile for testing Akshay's Corner
#
# Author: Akshay Mestry <xa@mes3.dev>
# Created on: 22 February, 2025
# Last updated on: 15 February, 2026
#
# This Makefile provides a comprehensive set of commands (targets) for building
# and testing my website.
# =============================================================================

# === CONFIGURATIONS ==========================================================
COLOUR_BOLD     := \033[1m
COLOUR_DIM      := \033[2m
COLOUR_RESET    := \033[0m

COLOUR_RED      := \033[31;5;160m
COLOUR_GREEN    := \033[38;5;34m
COLOUR_ORANGE   := \033[38;5;220m
COLOUR_YELLOW   := \033[38;5;214m
COLOUR_BLUE     := \033[38;5;75m
COLOUR_MAGENTA  := \033[38;5;90m
COLOUR_CYAN     := \033[38;5;45m
COLOUR_WHITE    := \033[38;5;15m
COLOUR_OLIVE    := \033[38;5;112m

TARGET_PADDING  := 12

SOURCE_DIR      := source
OUTPUT_DIR      := build

PROTOCOL        := http
LOCALHOST       := localhost
PORT            := 5500

# === TOOLS ===================================================================
SPHINX_BUILD    ?= sphinx-build
SPHINX_LINT     ?= sphinx-lint
HTTP_SERVER     ?= python3 -m http.server

# === FLAGS ===================================================================
SPHINX_BUILD_FLAGS := \
	--builder dirhtml \
	--fail-on-warning \
	--show-traceback \
	--fresh-env \
	--write-all \
	--quiet \
	--color

SPHINX_LINT_FLAGS := \
	--disable role-with-double-backticks,role-without-backticks \
	--max-line-length 79

HTTP_SERVER_FLAGS := \
	$(PORT) \
	--directory $(OUTPUT_DIR)

# === TARGETS =================================================================
.DEFAULT_GOAL := help
.PHONY: help clean check html rebuild serve start stop

# Improvement based on: https://stackoverflow.com/a/64394417
help: ## Show this help and list available targets.
	@echo "Usage:"
	@echo "  $(COLOUR_GREEN)make$(COLOUR_RESET) $(COLOUR_YELLOW)<target>$(COLOUR_RESET)\n"
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*##' $(firstword $(MAKEFILE_LIST)) | \
		sort | \
		awk 'BEGIN {FS = ":.*## *"} {printf "  $(COLOUR_BLUE)%-$(TARGET_PADDING)s$(COLOUR_RESET) %s\n", $$1, $$2}'
	@echo "\n$(COLOUR_DIM)For executing a particular target, run 'make <target>'.$(COLOUR_RESET)"
	@echo "$(COLOUR_DIM)Read complete documentation at: https://github.com/xames3/website.$(COLOUR_RESET)"

clean: ## Remove build artifacts and temporary directories.
	@printf "$(COLOUR_YELLOW)[CLEAN]$(COLOUR_RESET) Removing $(OUTPUT_DIR) directory... "
	@rm -rf $(OUTPUT_DIR) && \
		printf "$(COLOUR_GREEN)OK!$(COLOUR_RESET)\n" || \
		(printf "$(COLOUR_RED)FAILED!$(COLOUR_RESET)\n" && exit 1)

check: ## Perform linting checks and report issues, if any.
	@printf "$(COLOUR_ORANGE)[CHECK]$(COLOUR_RESET) Running linter... "
	@$(SPHINX_LINT) $(SPHINX_LINT_FLAGS) $(SOURCE_DIR) >/dev/null && \
		printf "$(COLOUR_GREEN)OK!$(COLOUR_RESET)\n" || \
		(printf "$(COLOUR_RED)FAILED!$(COLOUR_RESET)\n" && exit 1)

html: ## Build HTML files from the source directory.
	@$(MAKE) check --no-print-directory
	@printf "$(COLOUR_BLUE)[BUILD]$(COLOUR_RESET) Building HTML output... "
	@$(SPHINX_BUILD) $(SPHINX_BUILD_FLAGS) $(SOURCE_DIR) $(OUTPUT_DIR) && \
		printf "$(COLOUR_GREEN)OK!$(COLOUR_RESET)\n" || \
		(printf "$(COLOUR_RED)FAILED!$(COLOUR_RESET)\n" && exit 1)

rebuild: ## Rebuild HTML files after cleaning the build directory.
	@$(MAKE) clean --no-print-directory
	@$(MAKE) html --no-print-directory

serve: ## Start a development web server, if not running already and serve.
	@if ps -ef | grep "$(HTTP_SERVER)" | grep $(PORT) | grep -v grep | grep -v xargs | grep -v awk | grep -v make > /dev/null; then \
		printf "$(COLOUR_GREEN)[EXIST]$(COLOUR_RESET) Development server already running at $(PROTOCOL)://$(LOCALHOST):$(PORT)... $(COLOUR_CYAN)SKIPPED!$(COLOUR_RESET)\n"; \
	else \
		$(MAKE) devserver --no-print-directory; \
	fi

start: ## Rebuild HTML files, start a development web server and serve.
	@$(MAKE) rebuild --no-print-directory
	@$(MAKE) serve --no-print-directory

stop: ## Stop the development web server.
	@printf "$(COLOUR_RED)[CLOSE]$(COLOUR_RESET) Stopping development server... "
	@lsof -i :$(PORT) | tail -n +2 | awk '{print $$2}' | xargs -r kill && \
		printf "$(COLOUR_GREEN)OK!$(COLOUR_RESET)\n" || \
		(printf "$(COLOUR_RED)FAILED!$(COLOUR_RESET)\n" && exit 1)

devserver:
	@printf "$(COLOUR_OLIVE)[START]$(COLOUR_RESET) Starting development server at $(PROTOCOL)://$(LOCALHOST):$(PORT)... "
	@($(HTTP_SERVER) $(HTTP_SERVER_FLAGS) &) >/dev/null && \
		sleep 1 && \
		(open "$(PROTOCOL)://$(LOCALHOST):$(PORT)" 2>/dev/null || \
		xdg-open "$(PROTOCOL)://$(LOCALHOST):$(PORT)" 2>/dev/null || \
		echo "Open $(PROTOCOL)://$(LOCALHOST):$(PORT) in your browser.") && \
		printf "$(COLOUR_GREEN)OK!$(COLOUR_RESET)\n" || \
		(printf "$(COLOUR_RED)FAILED!$(COLOUR_RESET)\n" && exit 1)
