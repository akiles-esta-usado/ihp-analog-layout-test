from gdsfactory import Component
from gdsfactory.components import rectangle

from ihp_pcells import contains_polygons, drc_check, lvs_check
from glayout.flow.pdk.sg13g2_mapped import sg13g2_mapped_pdk
from glayout.flow.pdk.sg13g2_mapped.layers import LAYER


from ihp_pcells import sg_nmos


def test_basic():
    netlist = "M1 D G S S sg13_lv_nmos L=0.45u W=5u M=2"
    c = sg_nmos(sg13g2_mapped_pdk, 5, 0.45, 2, high_voltage=False)

    assert not contains_polygons(c, "ThickGateOx.drawing")
    drc = drc_check(c)
    assert drc == 0, f"Got {drc} errors"

    assert lvs_check(c, netlist=netlist)


def test_multifinger():
    netlist = "M1 D G S S sg13_lv_nmos L=0.45u W=10u M=5"
    c = sg_nmos(sg13g2_mapped_pdk, 10, 0.45, 5, high_voltage=False)

    assert not contains_polygons(c, "ThickGateOx.drawing")
    drc = drc_check(c)
    assert drc == 0, f"Got {drc} errors"

    assert lvs_check(c, netlist=netlist)


def test_basic_hv():
    netlist = "M1 D G S S sg13_hv_nmos L=0.45u W=5u M=2"
    c = sg_nmos(sg13g2_mapped_pdk, 5, 0.45, 2, high_voltage=True)

    assert contains_polygons(c, "ThickGateOx.drawing")
    drc = drc_check(c)
    assert drc == 0, f"Got {drc} errors"

    assert lvs_check(c, netlist=netlist)


def test_multifinger_hv():
    netlist = "M1 D G S S sg13_hv_nmos L=0.45u W=10u M=5"
    c = sg_nmos(sg13g2_mapped_pdk, 10, 0.45, 5, high_voltage=True)

    assert contains_polygons(c, "ThickGateOx.drawing")
    drc = drc_check(c)
    assert drc == 0, f"Got {drc} errors"

    assert lvs_check(c, netlist=netlist)
