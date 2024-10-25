from ihp_pcells import create_bulk, contains_polygons, drc_check
from glayout.flow.pdk.sg13g2_mapped import sg13g2_mapped_pdk


def test_nmos_bulk_5x5():
    c = create_bulk(sg13g2_mapped_pdk, "nmos", 5, 5)

    assert not contains_polygons(c, "NWell.drawing")
    assert contains_polygons(c, "pSD.drawing")
    assert not contains_polygons(c, "nSD.drawing")
    assert not contains_polygons(c, "ThickGateOx.drawing")

    drc = drc_check(c)
    assert drc == 0, f"Got {drc} errors"


def test_pmos_bulk_5x5():
    c = create_bulk(sg13g2_mapped_pdk, "pmos", 5, 5)

    assert contains_polygons(c, "NWell.drawing")
    assert not contains_polygons(c, "pSD.drawing")
    assert not contains_polygons(c, "nSD.drawing")
    assert not contains_polygons(c, "ThickGateOx.drawing")

    drc = drc_check(c)
    assert drc == 0, f"Got {drc} errors"


def test_nmos_hv_bulk_5x5():
    c = create_bulk(sg13g2_mapped_pdk, "nmos_hv", 5, 5)

    assert not contains_polygons(c, "NWell.drawing")
    assert contains_polygons(c, "pSD.drawing")
    assert not contains_polygons(c, "nSD.drawing")
    assert contains_polygons(c, "ThickGateOx.drawing")

    drc = drc_check(c)
    assert drc == 0, f"Got {drc} errors"


def test_pmos_hv_bulk_5x5():
    c = create_bulk(sg13g2_mapped_pdk, "pmos_hv", 5, 5)

    assert contains_polygons(c, "NWell.drawing")
    assert not contains_polygons(c, "pSD.drawing")
    assert not contains_polygons(c, "nSD.drawing")
    assert contains_polygons(c, "ThickGateOx.drawing")

    drc = drc_check(c)
    assert drc == 0, f"Got {drc} errors"
