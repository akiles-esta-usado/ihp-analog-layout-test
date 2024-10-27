from pydantic import validate_arguments

import shapely as sp
from shapely import Polygon, affinity

import gdstk

from gdsfactory.grid import grid
from gdsfactory.cell import cell
from gdsfactory.component import Component, copy
from gdsfactory.components.rectangle import rectangle
from gdsfactory import ComponentReference
from gdsfactory.components.bbox import bbox
import gdsfactory


from glayout.flow.primitives.via_gen import via_array, via_stack
from glayout.flow.primitives.guardring import tapring
from glayout.flow.primitives.fet import pmos, nmos

from glayout.flow.routing.c_route import c_route
from glayout.flow.routing.L_route import L_route
from glayout.flow.routing.straight_route import straight_route

from glayout.flow.spice import Netlist

from glayout.flow.pdk.mappedpdk import MappedPDK
from glayout.flow.pdk.util.snap_to_grid import component_snap_to_grid
from glayout.flow.pdk.sg13g2_mapped import sg13g2_mapped_pdk
from glayout.flow.pdk.sg13g2_mapped.layers import LAYER
from glayout.flow.pdk.util.comp_utils import (
    evaluate_bbox,
    to_float,
    to_decimal,
    prec_array,
    prec_center,
    prec_ref_center,
    movey,
    align_comp_to_port,
)
from glayout.flow.pdk.util.port_utils import (
    rename_ports_by_orientation,
    rename_ports_by_list,
    add_ports_perimeter,
    print_ports,
)


from IPython.display import display, clear_output
import IPython.display

import svgutils.transform as sg

import ipywidgets as widgets

import numpy as np
from pathlib import Path
from typing import Optional, Union
from pprint import pprint
from decimal import Decimal

from subprocess import run

# Redirect all outputs here
hide = widgets.Output()


sg13g2_mapped_pdk.activate()


## Helpers
##########


def display_gds(gds_file, scale=3):
    # Generate an SVG image
    top_level_cell = gdstk.read_gds(gds_file).top_level()[0]
    top_level_cell.write_svg("out.svg")
    # Scale the image for displaying
    fig = sg.fromfile("out.svg")
    fig.set_size((str(float(fig.width) * scale), str(float(fig.height) * scale)))
    fig.save("out.svg")

    # Display the image
    IPython.display.display(IPython.display.SVG("out.svg"))


def display_component(component, scale=3):
    # Save to a GDS file
    with hide:
        component.write_gds("out.gds")
    display_gds("out.gds", scale)


def get_sorted_port_list(
    c: Component | ComponentReference,
    layer: tuple = None,
    prefix=None,
    suffix=None,
    orientation=None,
    width=None,
    layers_excluded=None,
    port_type=None,
    names=None,
    clockwise=None,
):
    ports = c.get_ports_dict(
        layer=layer,
        prefix=prefix,
        suffix=suffix,
        orientation=orientation,
        width=width,
        layers_excluded=layers_excluded,
        port_type=port_type,
        names=names,
        clockwise=clockwise,
    ).keys()

    ports = sorted(x.split("_") for x in ports)

    return ["_".join(port) for port in ports]


def contains_polygons(c: Component, layer: str = None):
    if layer:
        return len(c.get_polygons(by_spec=LAYER[layer])) > 0
    else:
        return len(c.get_polygons()) > 0


def count_polygons(c: Component, layer: str):
    multipolygon = c.get_polygons(by_spec=LAYER[layer], as_shapely_merged=True)
    return len(sp.get_parts(multipolygon))


def get_corner(c: ComponentReference, corner: str):
    (xmin, ymin), (xmax, ymax) = c.get_bounding_box()
    x = xmin if "l" in corner else xmax
    y = ymin if "b" in corner else ymax
    return x, y


def drc_check(c: Component) -> int:
    if len(c.get_polygons()) == 0:
        raise ValueError("Component has no polygons in it")

    drc_dir = Path("./tmp_drc")
    drc_dir.mkdir(parents=True, exist_ok=True)
    c.write_gds(gdspath=drc_dir / "tmp_drc.gds")
    output = run(
        ["make", "TOP=tmp_drc", "klayout-drc"],
        capture_output=True,
        text=True,
        universal_newlines=True,
    )
    drc_error_line = output.stdout.splitlines()[-1]

    return int(drc_error_line.replace("Number of DRC errors: ", ""))


def lvs_check(c: Component, netlist: str):
    if len(c.get_polygons()) == 0:
        raise ValueError("Component has no polygons in it")

    lvs_dir = Path("./tmp_lvs")
    lvs_dir.mkdir(parents=True, exist_ok=True)

    (lvs_dir / "tmp_lvs.gds").unlink(missing_ok=True)
    c.write_gds(
        gdspath=lvs_dir / "tmp_lvs.gds",
        on_duplicate_cell="overwrite",
        with_metadata=False,
    )

    cell_name = gdsfactory.import_gds(lvs_dir / "tmp_lvs.gds").name

    c.name = cell_name
    (lvs_dir / "tmp_lvs.spice").write_text(
        "\n".join(
            [
                "* TMP DRC FILE",
                f".SUBCKT {cell_name}",
                netlist,
                f".ENDS {cell_name}",
            ]
        ),
    )

    output = run(
        ["make", "TOP=tmp_lvs", f"TOP_GDS_CELL={cell_name}", "klayout-lvs"],
        capture_output=True,
        text=True,
    )

    for line in output.stdout.splitlines():
        if "ERROR : Netlists" in line:
            return False

        if "INFO : Congratulations!" in line:
            return True


## Primitives
#############


def create_bulk(pdk, fet_type: str, length, height, metal_top="met1"):
    fet_type = fet_type.lower()
    c = Component()

    active_size = (length - 1.24, height - 0.7)
    active_ref = c << rectangle(
        size=active_size, layer=LAYER["Activ.drawing"], centered=True
    )

    c << via_array(
        glayer1="active_tap",
        glayer2=metal_top,
        pdk=pdk,
        size=active_size,
        lay_bottom=True,  # Bottom layer connects all vias
        lay_every_layer=True,  # All layers connect all vias
        fullbottom=True,  # Bottom layer takes complete size
    )

    if "nmos" in fet_type:
        c << rectangle(
            size=evaluate_bbox(active_ref, padding=0.03),
            layer=LAYER["pSD.drawing"],
            centered=True,
        )

    if "pmos" in fet_type:
        c << rectangle(size=(length, height), layer=LAYER["NWell.drawing"], centered=True)

    if "hv" in fet_type:
        c << rectangle(size=(length, height), layer="ThickGateOx.drawing", centered=True)

    return c.flatten()


def generate_thick_gate_oxide(source: Component):
    c = Component()
    merged = sp.intersection_all(
        [
            source.get_polygons(by_spec=LAYER["Activ.drawing"], as_shapely_merged=True),
            source.get_polygons(by_spec=LAYER["GatPoly.drawing"], as_shapely_merged=True),
        ]
    )

    # Draw scaled bounds
    bounds = Polygon.from_bounds(*merged.bounds)

    # With buffer
    c.add_polygon(
        bounds.buffer(
            distance=0.35,
            cap_style="flat",
            join_style="mitre",  # Always use mitre
        ),
        layer=LAYER["ThickGateOx.drawing"],
    )

    return c


def insert_tapring(pdk: MappedPDK, c: Component, fet_type: str):
    fet_type = fet_type.lower()

    size = evaluate_bbox(c, padding=pdk.util_max_metal_seperation() + 1)
    c_center = prec_center(c)

    if "nmos" in fet_type:
        sdlayer = "p+s/d"
    else:
        sdlayer = "n+s/d"

    guard_ring = tapring(
        pdk,
        sdlayer=sdlayer,
        enclosed_rectangle=size,
    )

    if "pmos" in fet_type:
        guard_ring << rectangle(
            size=evaluate_bbox(guard_ring), layer=LAYER["NWell.drawing"], centered=True
        )

    guard_ring = guard_ring.flatten()

    ref = c << guard_ring

    ref.move(
        origin=c_center,
        destination=prec_center(ref),
    )


## Fets
#######


def sg_nmos(pdk: MappedPDK, width, length, nf, high_voltage: bool, bulk: bool = True):
    c = Component()

    nmos_inst = nmos(
        pdk,
        width=width,
        length=length,
        fingers=nf,
        with_tie=False,
        with_dnwell=False,
        with_dummy=False,
        with_substrate_tap=False,
    )

    nmos_inst: Component = nmos_inst.remove_layers(layers=[LAYER["PWell.drawing"]])
    nmos_inst: Component = nmos_inst.remove_layers(layers=[LAYER["nSD.drawing"]])

    for corners in nmos_inst.get_polygons(by_spec=LAYER["GatPoly.drawing"]):
        shape = (corners[0], corners[2])  # bottom left, top right
        if abs(shape[0][1] - shape[1][1]) < length:
            continue

        nmos_inst << bbox(bbox=shape, layer=LAYER["HeatTrans.drawing"])

    nmos_ref = c << nmos_inst

    if bulk:
        bulk_ref: ComponentReference = c << create_bulk(
            pdk, "nmos", length=evaluate_bbox(nmos_inst)[0], height=1.3
        )

        # bulk_ref.movex(
        #     origin=bulk_ref.get_bounding_box()[0], destination=nmos_ref.get_bounding_box()[0]
        # )

        nmos_height = evaluate_bbox(nmos_ref)[1]
        bulk_height = evaluate_bbox(bulk_ref)[1]

        # Inmediate connection of source and bulk
        bulk_ref.movey((nmos_height + bulk_height) / 2 - 0.16)

    if high_voltage:
        nmos_inst << generate_thick_gate_oxide(nmos_inst)

    c.add_ports(nmos_ref.get_ports_dict())

    return c


def sg_nmos_array(pdk: MappedPDK, rows, cols, nmos_params):
    c = Component()

    block = sg_nmos(pdk, **nmos_params)

    # Measured to make it the same difference on pmos_hv and nmos_hv
    spacing = (pdk.util_max_metal_seperation(), pdk.util_max_metal_seperation())

    c << prec_array(
        custom_comp=block,
        rows=rows,
        columns=cols,
        spacing=spacing,
    )

    insert_tapring(pdk, c, fet_type="nmos_hv")

    return c


def sg_pmos(
    pdk: MappedPDK, width, length, nf, high_voltage: bool, bulk: bool = True, **kwargs
):
    c = Component()

    pmos_inst = pmos(
        pdk,
        width=width,
        length=length,
        fingers=nf,
        with_tie=False,
        dnwell=False,
        with_dummy=False,
        with_substrate_tap=False,
        **kwargs,
    )

    for corners in pmos_inst.get_polygons(by_spec=LAYER["GatPoly.drawing"]):
        shape = (corners[0], corners[2])  # bottom left, top right
        if abs(shape[0][1] - shape[1][1]) < length:
            continue

        pmos_inst << bbox(bbox=shape, layer=LAYER["HeatTrans.drawing"])

    pmos_ref = c << pmos_inst

    if bulk:
        bulk_ref: ComponentReference = c << create_bulk(
            pdk, "pmos", length=evaluate_bbox(pmos_inst)[0], height=1.3
        )

        pmos_height = evaluate_bbox(pmos_ref)[1]
        bulk_height = evaluate_bbox(bulk_ref)[1]

        # Ipmediate connection of fet and bulk
        bulk_ref.movey((pmos_height + bulk_height) / 2 - 1.1)

    c.add_ports(pmos_ref.get_ports_dict())

    if high_voltage:
        pmos_inst << generate_thick_gate_oxide(pmos_inst)

    return c.flatten()


def sg_pmos_array(pdk: MappedPDK, rows, cols, pmos_hv_params):
    c = Component()

    block = sg_pmos(pdk, **pmos_hv_params)

    padding = 0

    # Measured to make it the same difference on pmos_hv and nmos_hv
    # current_separation = 0.97
    # desired_separation = pdk.util_max_metal_seperation()
    # padding = -(current_separation - desired_separation) / 2
    # c.add_ref(
    #     component=block,
    #     rows=rows,
    #     columns=cols,
    #     spacing=evaluate_bbox(block, padding=padding),
    # )

    # Measured to make it the same difference on pmos_hv and nmos_hv
    # 0.03 is adjustment to make this equal to pmos block
    spacing = (
        -1.24,
        -(0.97 - pdk.util_max_metal_seperation()),
    )

    c << prec_array(
        custom_comp=block,
        rows=rows,
        columns=cols,
        spacing=spacing,
    )

    return c


def sg_power_pmos(
    pdk: MappedPDK, width: float, length: float, nf: int, high_voltage: bool
):
    c = sg_pmos(
        pdk,
        width=width,
        length=length,
        nf=nf,
        high_voltage=high_voltage,
        bulk=False,
        # Next are specific to glayout's pmos
        sd_route_topmet="met4",
        gate_route_topmet="met3",
        interfinger_rmult=2,
        gate_rmult=2,
        sd_rmult=2,
    )

    vias: Component = None
    for corners in c.get_polygons(by_spec=LAYER["Metal2.drawing"]):
        left, bottom = np.min(corners, axis=0).tolist()
        right, top = np.max(corners, axis=0).tolist()

        if abs(top - bottom) < length:
            continue

        if vias is None:
            vias = via_array(
                pdk,
                glayer1="met2",
                glayer2="met4",
                size=(right - left, top - bottom),
                lay_bottom=True,  # Bottom layer connects all vias
                lay_every_layer=True,  # All layers connect all vias
                fullbottom=True,  # Bottom layer takes complete size
            )

        vias_ref = c << vias
        vias_ref.move(
            origin=vias_ref.get_bounding_box()[0],  # bottom left corner
            destination=(left, bottom),
        )

    return c
