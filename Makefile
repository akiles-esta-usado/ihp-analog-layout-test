KLAYOUT_EXE		= $(shell command -v klayout)
KLAYOUT_ARGS	= -c misc/klayoutrc -t -e

KLAYOUT			= $(KLAYOUT_EXE) $(KLAYOUT_ARGS)


klayout:
	$(KLAYOUT) $(TOP)