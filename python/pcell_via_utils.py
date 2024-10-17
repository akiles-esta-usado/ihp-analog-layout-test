from gdsfactory.cell import cell
from gdsfactory.component import Component
from gdsfactory.components.rectangle import rectangle
from glayout.flow.pdk.mappedpdk import MappedPDK
from glayout.flow.pdk.util.comp_utils import (
    evaluate_bbox,
    move,
)
from glayout.flow.pdk.util.port_utils import (
    rename_ports_by_orientation,
)
from typing import Literal
from math import sqrt


def get_metalization_via_width(
    pdk: MappedPDK, glayer: str, bottom_via: str = None, top_via: str = None
):
    """
    Estimates the minimum width of a metal or poly used on vias
    """
    width = 0

    if bottom_via:
        bottom_width = pdk.get_grule(bottom_via)["width"]
        bottom_enclosure = pdk.get_grule(glayer, bottom_via)["min_enclosure"]
        width_contender = bottom_width + 2 * bottom_enclosure

        width = width_contender if width_contender > width else width

    if top_via:
        top_width = pdk.get_grule(top_via)["width"]
        top_enclosure = pdk.get_grule(glayer, top_via)["min_enclosure"]
        width_contender = top_width + 2 * top_enclosure

        width = width_contender if width_contender > width else width

    if (
        "min_area" in pdk.get_grule(glayer)
        and pdk.get_grule(glayer)["min_area"] > width**2
    ):
        width = sqrt(pdk.get_grule(glayer)["min_area"])

    return width


def get_via_width(pdk: MappedPDK):
    """
    Returns a dictionary with the widths used by vias and metalization based on
    enclosure and min_area
    """
    width = {
        "mcon": pdk.get_grule("mcon")["width"],
        "via1": pdk.get_grule("via1")["width"],
        "via2": pdk.get_grule("via2")["width"],
        "via3": pdk.get_grule("via3")["width"],
        "via4": pdk.get_grule("via4")["width"],
    }

    width["poly"] = get_metalization_via_width(
        pdk,
        "poly",
        top_via="mcon",
    )
    width["active_diff"] = get_metalization_via_width(
        pdk,
        "active_diff",
        top_via="mcon",
    )
    width["active_tap"] = get_metalization_via_width(
        pdk,
        "active_tap",
        bottom_via="mcon",
    )
    width["met1"] = get_metalization_via_width(
        pdk,
        "met1",
        bottom_via="mcon",
        top_via="via1",
    )
    width["met2"] = get_metalization_via_width(
        pdk,
        "met2",
        bottom_via="via1",
        top_via="via2",
    )
    width["met3"] = get_metalization_via_width(
        pdk,
        "met3",
        bottom_via="via2",
        top_via="via3",
    )
    width["met4"] = get_metalization_via_width(
        pdk,
        "met4",
        bottom_via="via3",
        top_via="via4",
    )
    width["met5"] = get_metalization_via_width(
        pdk,
        "met5",
        bottom_via="via4",
    )

    return width


def __error_check_order_layers(
    pdk: MappedPDK, glayer1: str, glayer2: str
) -> tuple[tuple[int, int], tuple[str, str]]:
    """correctly order layers (level1 should be lower than level2)"""

    # check that the generic layers specfied can be routed between
    if not all([pdk.is_routable_glayer(met) for met in [glayer1, glayer2]]):
        raise ValueError("via_stack: specify between two routable layers")

    name_to_level_mapping = {
        "active_diff": 0,
        "active_tap": 0,
        "poly": 0,
        "met1": 1,
        "met2": 2,
        "met3": 3,
        "met4": 4,
        "met5": 5,
    }

    level1 = name_to_level_mapping[glayer1]
    level2 = name_to_level_mapping[glayer2]

    if level1 > level2:
        return ((level2, level1), (glayer2, glayer1))

    return ((level1, level2), (glayer1, glayer2))


def __get_layer_dim(
    pdk: MappedPDK,
    glayer: str,
    mode: Literal["both", "above", "below"] = "both",
) -> float:
    """Returns the required dimension of a routable layer in a via stack
    glayer is the routable glayer
    mode is one of [both,below,above]
    This specfies the vias to consider. (layer dims may be made smaller if its possible to ignore top/bottom vias)
    ****enclosure rules of the via above and below are considered by default, via1<->met2<->via2
    ****using below specfier only considers the enclosure rules for the via below, via1<->met2
    ****using above specfier only considers the enclosure rules for the via above, met2<->via2
    ****specfying both or below for active/poly layer is valid, function knows to ignore below
    """
    # error checking
    if not pdk.is_routable_glayer(glayer):
        raise ValueError("__get_layer_dim: glayer must be a routable layer")

    # split into above rules and below rules
    consider_above = mode == "both" or mode == "above"
    consider_below = mode == "both" or mode == "below"
    is_lvl0 = any([hint in glayer for hint in ["poly", "active"]])
    layer_dim = 0
    if consider_below and not is_lvl0:
        via_below = (
            "mcon" if glayer == "met1" else "via" + str(int(glayer[-1]) - 1)
        )
        layer_dim = (
            pdk.get_grule(via_below)["width"]
            + 2 * pdk.get_grule(via_below, glayer)["min_enclosure"]
        )
    if consider_above:
        via_above = "mcon" if is_lvl0 else "via" + str(glayer[-1])
        layer_dim = max(
            layer_dim,
            pdk.get_grule(via_above)["width"]
            + 2 * pdk.get_grule(via_above, glayer)["min_enclosure"],
        )
    layer_dim = max(layer_dim, pdk.get_grule(glayer)["min_width"])
    return layer_dim


# @cell
def via_stack(
    pdk: MappedPDK,
    glayer1: str,
    glayer2: str,
    centered: bool = True,
    fullbottom: bool = False,
    fulltop: bool = False,
    assume_bottom_via: bool = False,
    same_layer_behavior: Literal["lay_nothing", "min_square"] = "min_square",
) -> Component:
    """produces a single via stack between two layers that are routable (metal, poly, or active)
    The via_stack produced is always a square (hieght=width)

    args:
    pdk: MappedPDK is the pdk to use
    glayer1: str is the glayer to start on
    glayer2: str is the glayer to end on
    ****NOTE it does not matter what order you pass layers
    fullbottom: if True will lay the bottom layer all over the area of the viastack else makes minimum legal size (ignores min area)
    assume_bottom_via: legalize viastack assuming the via underneath bottom met is present, e.g. if bottom met is met3, assume via2 is present
    fulltop: if True will lay the top layer all over the area of the viastack else makes minimum legal size (ignores min area)
    ****NOTE: generator can figure out which layer is top and which is bottom (i.e. met5 is higher than met1)
    same_layer_behavior: sometimes (especially when used in other generators) it is unknown what two layers are specfied
    this option provides the generator with guidance on how to handle a case where same layer is given
    by default, (lay_nothing option) nothing is laid and an empty component is returned
    if min_square is specfied, a square of min_width * min_width is laid

    ports, some ports are not layed when it does not make sense (e.g. empty component):
    top_met_...all edges
    bottom_via_...all edges
    bottom_met_...all edges
    bottom_layer_...all edges (may be different than bottom met if on diff/poly)
    """
    ordered_layer_info = __error_check_order_layers(pdk, glayer1, glayer2)
    level1, level2 = ordered_layer_info[0]
    glayer1, glayer2 = ordered_layer_info[1]

    widths = get_via_width(pdk)

    viastack = Component()

    # if same level return component with min_width rectangle on that layer
    if level1 == level2:
        if same_layer_behavior == "lay_nothing":
            return viastack

        min_square = viastack << rectangle(
            size=(widths[glayer1], widths[glayer1]),
            layer=pdk.get_glayer(glayer1),
            centered=centered,
        )

        # update ports
        if level1 == 0:  # both poly or active
            viastack.add_ports(
                min_square.get_ports_list(), prefix="bottom_layer_"
            )
        else:  # both mets
            viastack.add_ports(min_square.get_ports_list(), prefix="top_met_")
            viastack.add_ports(
                min_square.get_ports_list(), prefix="bottom_met_"
            )
        viastack.show()

    else:
        ports_to_add = dict()
        for level in range(level1, level2 + 1):
            via_name = "mcon" if level == 0 else "via" + str(level)
            layer_name = glayer1 if level == 0 else "met" + str(level)
            # get layer sizing
            mode = (
                "below"
                if level == level2
                else ("above" if level == level1 else "both")
            )
            mode = "both" if assume_bottom_via and level == level1 else mode
            layer_dim = __get_layer_dim(pdk, layer_name, mode=mode)
            # place met/via, do not place via if on top layer
            if level != level2:
                via_dim = pdk.get_grule(via_name)["width"]
                via_ref = viastack << rectangle(
                    size=[widths[via_name], widths[via_name]],
                    layer=pdk.get_glayer(via_name),
                    centered=True,
                )
            lay_ref = viastack << rectangle(
                size=[widths[layer_name], widths[layer_name]],
                layer=pdk.get_glayer(layer_name),
                centered=True,
            )
            # update ports
            if layer_name == glayer1:
                ports_to_add["bottom_layer_"] = lay_ref.get_ports_list()
                ports_to_add["bottom_via_"] = via_ref.get_ports_list()
            if (level1 == 0 and level == 1) or (
                level1 > 0 and layer_name == glayer1
            ):
                ports_to_add["bottom_met_"] = lay_ref.get_ports_list()
            if layer_name == glayer2:
                ports_to_add["top_met_"] = lay_ref.get_ports_list()
        # implement fulltop and fullbottom options. update ports_to_add accordingly
        if fullbottom:
            bot_ref = viastack << rectangle(
                size=evaluate_bbox(viastack),
                layer=pdk.get_glayer(glayer1),
                centered=True,
            )
            if level1 != 0:
                ports_to_add["bottom_met_"] = bot_ref.get_ports_list()
            ports_to_add["bottom_layer_"] = bot_ref.get_ports_list()
        if fulltop:
            ports_to_add["top_met_"] = (
                viastack
                << rectangle(
                    size=evaluate_bbox(viastack),
                    layer=pdk.get_glayer(glayer2),
                    centered=True,
                )
            ).get_ports_list()
        # add all ports in ports_to_add
        for prefix, ports_list in ports_to_add.items():
            viastack.add_ports(ports_list, prefix=prefix)
        # move SW corner to 0,0 if centered=False
        if not centered:
            viastack = move(viastack, (viastack.xmax, viastack.ymax))
    return rename_ports_by_orientation(viastack.flatten())
