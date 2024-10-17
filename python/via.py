from glayout.flow.pdk.mappedpdk import MappedPDK
from gdsfactory import Component
from gdsfactory.components import rectangle
from sg13g2_mapped import sg13g2_mapped_pdk

from pathlib import Path

from math import sqrt


def via(PDK: MappedPDK):
    met1_layer = PDK.get_glayer("met1")
    met2_layer = PDK.get_glayer("met2")
    via1_layer = PDK.get_glayer("via1")

    via_size = PDK.get_grule("via1")["width"]
    met1_size = via_size + 2 * PDK.get_grule("via1", "met1")["min_enclosure"]
    met2_size = via_size + 2 * PDK.get_grule("via1", "met2")["min_enclosure"]

    if met1_size**2 < PDK.get_grule("met1")["min_area"]:
        met1_size = sqrt(PDK.get_grule("met1")["min_area"])

    if met2_size**2 < PDK.get_grule("met2")["min_area"]:
        met2_size = sqrt(PDK.get_grule("met2")["min_area"])

    top_level = Component(name="via")

    top_level << rectangle(
        size=(met1_size, met1_size),
        layer=met1_layer,
        centered=True,
    )
    top_level << rectangle(
        size=(via_size, via_size), layer=via1_layer, centered=True
    )
    top_level << rectangle(
        size=(met2_size, met2_size),
        layer=met2_layer,
        centered=True,
    )

    return top_level


module = "via"
module_path = Path(module)
module_gds = module_path / f"{module}.gds"

comp = via(PDK=sg13g2_mapped_pdk)
comp.name = module
comp.show()

module_path.mkdir(parents=True, exist_ok=True)
module_gds.unlink(missing_ok=True)
comp.write_gds(module_gds)
