from gdsfactory import Component

# from glayout.flow.primitives.via_gen import via_stack
from pcell_via_utils import via_stack


from sg13g2_mapped import sg13g2_mapped_pdk
from pathlib import Path

module = "test_via_stack"
module_path = Path(module)
module_gds = module_path / f"{module}.gds"


# comp = via_stack(sg13g2_mapped_pdk, glayer1="poly", glayer2="met5") # DRC Errors: 0
# comp = via_stack(sg13g2_mapped_pdk, glayer1="active_diff", glayer2="met5")  # DRC Errors: 0
comp = via_stack(sg13g2_mapped_pdk, glayer1="active_tap", glayer2="met5")  # DRC Errors: 0
comp.name = module
comp.show()

module_path.mkdir(parents=True, exist_ok=True)
module_gds.unlink(missing_ok=True)
comp.write_gds(module_gds)
