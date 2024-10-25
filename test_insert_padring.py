from gdsfactory import Component
from gdsfactory.components import rectangle

from ihp_pcells import contains_polygons, drc_check
from glayout.flow.pdk.sg13g2_mapped import sg13g2_mapped_pdk
from glayout.flow.pdk.sg13g2_mapped.layers import LAYER


from ihp_pcells import insert_tapring


def test_padring_over_nmos():
    c = Component()

    rect = (
        c
        << rectangle(size=(10, 10), layer=LAYER["TEXT.drawing"], centered=True).flatten()
    )
    rect.movey(-10)
    rect.movex(5)

    insert_tapring(sg13g2_mapped_pdk, c, "nmos")

    assert not contains_polygons(c, "NWell.drawing")
    assert not contains_polygons(c, "nSD.drawing")
    assert contains_polygons(c, "pSD.drawing")
    drc = drc_check(c)
    assert drc == 0, f"Got {drc} errors"


def test_padring_over_pmos():
    c = Component()

    rect = (
        c
        << rectangle(size=(10, 10), layer=LAYER["TEXT.drawing"], centered=True).flatten()
    )
    rect.movey(-10)
    rect.movex(5)

    insert_tapring(sg13g2_mapped_pdk, c, "pmos")

    assert contains_polygons(c, "NWell.drawing")
    assert contains_polygons(c, "nSD.drawing")
    assert not contains_polygons(c, "pSD.drawing")
    drc = drc_check(c)
    assert drc == 0, f"Got {drc} errors"
