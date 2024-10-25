from gdsfactory import Component
from gdsfactory.components import rectangle

from ihp_pcells import contains_polygons, drc_check, lvs_check
from glayout.flow.pdk.sg13g2_mapped import sg13g2_mapped_pdk
from glayout.flow.pdk.sg13g2_mapped.layers import LAYER


from ihp_pcells import sg_pmos


def test_basic():
    c = sg_pmos(sg13g2_mapped_pdk, 5, 0.45, 2, high_voltage=False)
    netlist = "M1 D G S S sg13_lv_pmos L=0.45u W=5u M=2"

    assert not contains_polygons(c, "ThickGateOx.drawing")
    drc = drc_check(c)
    assert drc == 0, f"Got {drc} errors"

    assert lvs_check(c, netlist=netlist)


def test_multifinger():
    c = sg_pmos(sg13g2_mapped_pdk, 10, 0.45, 5, high_voltage=False)
    netlist = "M1 D G S S sg13_lv_pmos L=0.45u W=10u M=5"

    assert not contains_polygons(c, "ThickGateOx.drawing")
    drc = drc_check(c)
    assert drc == 0, f"Got {drc} errors"

    assert lvs_check(c, netlist=netlist)


def test_basic_hv():
    c = sg_pmos(sg13g2_mapped_pdk, 5, 0.45, 2, high_voltage=True)
    netlist = "M1 D G S S sg13_hv_pmos L=0.45u W=5u M=2"

    assert contains_polygons(c, "ThickGateOx.drawing")
    drc = drc_check(c)
    assert drc == 0, f"Got {drc} errors"

    assert lvs_check(c, netlist=netlist)


def test_multifinger_hv():
    c = sg_pmos(sg13g2_mapped_pdk, 10, 0.45, 5, high_voltage=True)
    netlist = "M1 D G S S sg13_hv_pmos L=0.45u W=10u M=5"

    assert contains_polygons(c, "ThickGateOx.drawing")
    drc = drc_check(c)
    assert drc == 0, f"Got {drc} errors"

    assert lvs_check(c, netlist=netlist)
