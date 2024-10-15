PDK=ihp-sg13g2

KLAYOUT_EXE		= $(shell command -v klayout)
KLAYOUT_ARGS	= -c misc/klayoutrc -t -e
KLAYOUT			= $(KLAYOUT_EXE) $(KLAYOUT_ARGS)

XSCHEM_EXE		= $(shell command -v xschem)
XSCHEM_ARGS     = --rcfile $(PDK_ROOT)/$(PDK)/libs.tech/xschem/xschemrc
XSCHEM          = $(XSCHEM_EXE) $(XSCHEM_ARGS)


klayout:
	$(KLAYOUT) $(TOP)


xschem:
	$(XSCHEM) $(TOP)