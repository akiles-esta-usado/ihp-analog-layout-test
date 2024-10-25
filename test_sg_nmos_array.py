from gdsfactory import Component
from gdsfactory.components import rectangle

from ihp_pcells import contains_polygons, drc_check, lvs_check
from glayout.flow.pdk.sg13g2_mapped import sg13g2_mapped_pdk
from glayout.flow.pdk.sg13g2_mapped.layers import LAYER


from ihp_pcells import sg_nmos_array


def test_basic():
    nmos_params = {"width": 10, "length": 0.45, "nf": 2, "high_voltage": False}
    c = sg_nmos_array(sg13g2_mapped_pdk, 1, 1, nmos_params)

    assert not contains_polygons(c, "ThickGateOx.drawing")

    drc = drc_check(c)
    assert drc == 0, f"Got {drc} errors"

    netlist = "M1 D G S S sg13_lv_nmos L=0.45u W=10u M=2"
    assert lvs_check(c, netlist=netlist)


def test_bigger_hv():
    nmos_params = {"width": 10, "length": 1, "nf": 30, "high_voltage": True}
    c = sg_nmos_array(sg13g2_mapped_pdk, 3, 2, nmos_params)

    assert contains_polygons(c, "ThickGateOx.drawing")

    drc = drc_check(c)
    assert drc == 0, f"Got {drc} errors"

    netlist = """
    M1 D1 G1 S S sg13_hv_nmos L=1u W=10u M=30
    M2 D2 G2 S S sg13_hv_nmos L=1u W=10u M=30
    M3 D3 G3 S S sg13_hv_nmos L=1u W=10u M=30
    M4 D4 G4 S S sg13_hv_nmos L=1u W=10u M=30
    M5 D5 G5 S S sg13_hv_nmos L=1u W=10u M=30
    M6 D6 G6 S S sg13_hv_nmos L=1u W=10u M=30
    """
    assert lvs_check(c, netlist=netlist)
