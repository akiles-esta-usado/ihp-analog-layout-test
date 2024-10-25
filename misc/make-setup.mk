# Disable make's implicit rules
MAKEFLAGS += --no-builtin-rules
.SUFFIXES:

#-------------------------------------------------------------------------------
# Default target when invoking without specific target.
.DEFAULT_GOAL := print

#-------------------------------------------------------------------------------
# Proper way to initiate SHELL for make
SHELL          := /usr/bin/env bash
.SHELLFLAGS    := -o pipefail -c


#-------------------------------------------------------------------------------
# Add execution rules
