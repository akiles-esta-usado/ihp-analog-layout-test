KLAYOUT_EXE		= $(shell command -v klayout)
KLAYOUT_ARGS	= -c misc/klayoutrc -t -e
KLAYOUT			= $(KLAYOUT_EXE) $(KLAYOUT_ARGS)
KLAYOUT_CLI     = $(KLAYOUT) -b -zz

XSCHEM_EXE		= $(shell command -v xschem)
XSCHEM_ARGS     = --rcfile $(realpath misc/xschemrc)
XSCHEM          = $(XSCHEM_EXE) $(XSCHEM_ARGS)

TOP_GDS         ?= $(realpath $(TOP)/$(TOP).gds)
TOP_GDS_CELL    ?= $(TOP)
TOP_SCH         ?= $(realpath $(TOP)/$(TOP).sch)
TOP_SPICE       ?= $(abspath $(TOP)/$(TOP).spice)
TOP_SCRIPT      ?= $(abspath $(TOP)/$(TOP).py)

export SPICE_USERINIT_DIR ?= $(PDK_ROOT)/$(PDK)/libs.tech/ngspice


#-------------------------------------------------------------------------------
# xschem                     Open Top schematic
# xschem-tb                  Open a testbench specified with TOP variable
# xschem-netlist             
# xschem-lvs-prefix          Generates LVS spice with X prefix
# xschem-lvs-noprefix        Generates LVS spice without X prefix
# xschem-lvs                 Generates LVS spice used by IHP

.PHONY: xschem
xschem:
	$(XSCHEM) $(TOP_SCH)


.PHONY: xschem-tb
xschem-tb:
	$(XSCHEM) $(TOP)


.PHONY: xschem-netlist
xschem-netlist:
	$(XSCHEM) \
		--netlist \
		--no_x \
		--quit \
		--netlist_path $(TOP) \
		$(TOP_SCH)

	readlink -f $(TOP_SPICE)


.PHONY: xschem-lvs-prefix
xschem-lvs-prefix:
	$(XSCHEM) \
		--netlist \
		--no_x \
		--quit \
	 	--netlist_path $(TOP) \
		--netlist_filename $(TOP_SPICE) \
		--preinit 'set lvs_netlist 1; set spiceprefix 1' \
		$(TOP_SCH)

	readlink -f $(TOP_SPICE)


.PHONY: xschem-lvs-noprefix
xschem-lvs-noprefix:
	$(XSCHEM) \
		--netlist \
		--no_x \
		--quit \
		--netlist_path $(TOP) \
		--netlist_filename $(TOP_SPICE) \
		--preinit 'set lvs_netlist 1; set spiceprefix 0' \
		$(TOP_SCH)

	readlink -f $(TOP_SPICE)


.PHONY: xschem-lvs
xschem-lvs: xschem-lvs-noprefix



.PHONY: xschem-create
xschem-create:
ifeq (,$(realpath $(TOP_SCH)))
	$(XSCHEM_EXE) \
	--no_x \
	--quit \
	--command "xschem clear; xschem saveas $(TOP_SCH)"
endif


.PHONY: xschem-tb-create
xschem-tb-create:
ifeq (,$(realpath $(TOP)))
	$(XSCHEM_EXE) \
	--no_x \
	--quit \
	--command "xschem clear; xschem saveas $(TOP)"
endif


#-------------------------------------------------------------------------------
# klayout           Open module gds with klayout
# klayout-script    Run python script
# klayout-lvs       Performs LVS
# klayout-lvs-gui   Performs LVS and open GUI
# klayout-drc       Performs DRC
# klayout-drc-gui   Performs DRC and open gui
# klayout-drc-full  Like klayout-drc-gui but cellname should match

.PHONY: klayout
klayout:
	$(KLAYOUT) $(TOP_GDS)


.PHONY: klayout-script
klayout-script:
	$(KLAYOUT_CLI) -r $(TOP)


# --help -h                 Displays this help message.
# --layout=<layout_path>    Specifies the file path of the input GDS file.
# --netlist=<netlist_path>  Specifies the file path of the input netlist file.
# --run_dir=<run_dir_path>  Run directory to save all the generated results [default: pwd]
# --topcell=<topcell_name>  Specifies the name of the top cell to be used.
# --run_mode=<run_mode>     Selects the allowed KLayout mode. (flat, deep). [default: flat]
# --no_net_names            Omits net names in the extracted netlist.
# --spice_comments          Includes netlist comments in the extracted netlist.
# --net_only                Generates netlist objects only in the extracted netlist.
# --no_simplify             Disables simplification for both layout and schematic netlists.
# --no_series_res           Prevents simplification of series resistors for both layout and schematic.
# --no_parallel_res         Prevents simplification of parallel resistors for both layout and schematic.
# --combine_devices         Enables device combination for both layout and schematic netlists.
# --top_lvl_pins            Creates pins for top-level circuits in both layout and schematic netlists.
# --purge                   Removes unused nets from both layout and schematic netlists.
# --purge_nets              Purges floating nets from both layout and schematic netlists.
# --verbose                 Enables detailed rule execution logs for debugging purposes.

.PHONY: klayout-lvs
klayout-lvs:
	touch $(TOP_SPICE)
	python $(PDK_ROOT)/$(PDK)/libs.tech/klayout/tech/lvs/run_lvs.py \
		--layout=$(TOP_GDS) \
		--netlist=$(TOP_SPICE) \
		--topcell=$(TOP_GDS_CELL) \
		--run_mode=flat \
		--run_dir=$(TMP_DIR)/$(TOP) \
		--verbose


.PHONY: klayout-lvs-gui
klayout-lvs-gui:
	touch $(TOP_SPICE)
	python $(PDK_ROOT)/$(PDK)/libs.tech/klayout/tech/lvs/run_lvs.py \
		--layout=$(TOP_GDS) \
		--netlist=$(TOP_SPICE) \
		--topcell=$(TOP_GDS_CELL) \
		--run_mode=flat \
		--run_dir=$(TMP_DIR)/$(TOP) \
		--verbose

	$(KLAYOUT) $(TOP)/$(TOP).gds -mn $(TMP_DIR)/$(TOP)/$(TOP).lvsdb

# in_gds                 path to the GDS layout to check (required in batch mode)
# cell                   name of the cell to check
# log_file               path to the log file [default: no log file]
# report_file            path to the report database [default: sg13g2_maximal.lyrdb in the script directory]
# offGrid                
# density                
# filler                 
# noRecommendedRules     
# sanityRules            
# checkDensityRules      

.PHONY: klayout-drc
klayout-drc:
	$(KLAYOUT_CLI) -r $(PDK_ROOT)/$(PDK)/libs.tech/klayout/tech/drc/sg13g2_maximal.lydrc \
		-rd in_gds=$(TOP_GDS) \
		-rd log_file=$(TMP_DIR)/$(TOP)/$(TOP)_drc.log \
		-rd report_file=$(TMP_DIR)/$(TOP)/$(TOP).lyrdb \
		-rd offGrid=true \
		-rd density=false \
		-rd filler=true \
		-rd noRecommendedRules=true \
		-rd sanityRules=true \
		-rd checkDensityRules=true


.PHONY: klayout-drc-gui
klayout-drc-gui:
	$(KLAYOUT_CLI) -r $(PDK_ROOT)/$(PDK)/libs.tech/klayout/tech/drc/sg13g2_maximal.lydrc \
		-rd in_gds=$(TOP_GDS) \
		-rd log_file=$(TMP_DIR)/$(TOP)/$(TOP)_drc.log \
		-rd report_file=$(TMP_DIR)/$(TOP)/$(TOP).lyrdb \
		-rd offGrid=true \
		-rd density=false \
		-rd filler=true \
		-rd noRecommendedRules=true \
		-rd sanityRules=true \
		-rd checkDensityRules=true

	$(KLAYOUT) $(TOP)/$(TOP).gds -m $(TMP_DIR)/$(TOP)/$(TOP).lyrdb


.PHONY: klayout-drc-full
klayout-drc-full:
	$(KLAYOUT_CLI) -r $(PDK_ROOT)/$(PDK)/libs.tech/klayout/tech/drc/sg13g2_maximal.lydrc \
		-rd in_gds=$(TOP_GDS) \
		-rd cell=$(TOP) \
		-rd log_file=$(TMP_DIR)/$(TOP)/$(TOP)_drc.log \
		-rd report_file=$(TMP_DIR)/$(TOP)/$(TOP).lyrdb \
		-rd offGrid=true \
		-rd density=false \
		-rd filler=true \
		-rd noRecommendedRules=true \
		-rd sanityRules=true \
		-rd checkDensityRules=true

	$(KLAYOUT) $(TOP)/$(TOP).gds -m $(TMP_DIR)/$(TOP)/$(TOP).lyrdb
