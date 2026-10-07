.DEFAULT_GOAL := help
# DEPRECATED: task logic moved to justfile; forwarding shim for one sprint (BK-025 / TSK-066).
# Remove in a later cleanup sprint once muscle-memory + any stale callers have moved to `just`.
Makefile: ;
help:
	@just --list
%:
	@just $@
.PHONY: help
