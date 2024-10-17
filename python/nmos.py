from glayout.flow.primitives.fet import nmos
from sg13g2_mapped import sg13g2_mapped_pdk

from pathlib import Path


module = "nmos"
module_path = Path(module)
module_gds = module_path / f"{module}.gds"


comp = nmos(
    pdk=sg13g2_mapped_pdk,
    fingers=5,
    with_dnwell=False,
    with_dummy=False,
    with_substrate_tap=False,
)

comp.show()


module_path.mkdir(parents=True, exist_ok=True)
module_gds.unlink(missing_ok=True)

comp.write_gds(module_gds)
