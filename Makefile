PYTHON ?= python3
export PYTHONPATH := src
export PYTHONDONTWRITEBYTECODE := 1

.PHONY: help hooks-install phase-start check syntax

help:
	@printf '%s\n' 'Sillage source repository commands:' \
	  '  make help           Show available commands' \
	  '  make check          Check P0 files and JSON Schema (read-only)' \
	  '  make syntax         Check Python source syntax (read-only)' \
	  '  make hooks-install  Set Git local hooksPath (owner action)' \
	  '  make phase-start BUNDLE=... FRENCH_SMART=... APPROVAL_RECORD=...' \
	  '                    Read-only plan; use CLI apply for authorized effects'

check:
	$(PYTHON) -m sillage_dev.repo_check structure

syntax:
	$(PYTHON) -m sillage_dev.repo_check syntax

hooks-install:
	git config --local core.hooksPath .githooks

phase-start:
	$(PYTHON) -m sillage_dev.phase_cli plan --bundle "$(BUNDLE)" --french-smart "$(FRENCH_SMART)" --approval-record "$(APPROVAL_RECORD)"
