#-------------------------------------------------------------------------------
# Environment Variables

export PDK=ihp-sg13g2
export TMP_DIR=/tmp/ihp-project

#-------------------------------------------------------------------------------
# Workdir setup

include misc/make-setup.mk

$(shell mkdir -p $(TMP_DIR))
ifneq (,$(TOP))
$(shell mkdir -p $(TMP_DIR)/$(TOP))
endif

#-------------------------------------------------------------------------------
# Inclusion of modules

include misc/tools.mk
include misc/work_environment.mk

#-------------------------------------------------------------------------------
# IHP Specific rules

test:
	pytest test_create_bulk.py
	pytest test_insert_padring.py
	pytest test_sg_nmos_array.py
	pytest test_sg_nmos.py
	pytest test_sg_pmos_array.py
	pytest test_sg_pmos.py