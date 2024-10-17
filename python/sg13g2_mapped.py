"""
usage: from sg13g2_mapped import sg13g2_mapped_pdk
"""

from grules import grulesobj
from glayout.flow.pdk.mappedpdk import MappedPDK, SetupPDKFiles
from pathlib import Path


LAYER = {
    # BEOL
    "Metal1.drawing": (8, 0),
    "Metal2.drawing": (10, 0),
    "Metal3.drawing": (30, 0),
    "Metal4.drawing": (50, 0),
    "Metal5.drawing": (67, 0),
    "TopMetal1.drawing": (126, 0),
    "TopMetal2.drawing": (134, 0),
    "Via1.drawing": (19, 0),
    "Via2.drawing": (29, 0),
    "Via3.drawing": (49, 0),
    "Via4.drawing": (66, 0),
    "TopVia1.drawing": (125, 0),
    "TopVia2.drawing": (133, 0),
    "Cont.drawing": (6, 0),
    # FEOL
    "Substrate.drawing": (40, 0),
    "Activ.drawing": (1, 0),
    "GatPoly.drawing": (5, 0),
    "PolyRes.drawing": (128, 0),
    "nSD.drawing": (7, 0),
    "pSD.drawing": (14, 0),
    "NWell.drawing": (31, 0),
    "PWell.drawing": (46, 0),
    # Others
    "nBuLay.drawing": (32, 0),
    "SalBlock.drawing": (28, 0),
    "ThickGateOx.drawing": (44, 0),
    "MIM.drawing": (36, 0),
    "Vmim.drawing": (129, 0),
    "Passiv.drawing": (9, 0),
    "NoMetFiller.drawing": (160, 0),
    "ThinFilmRes.drawing": (146, 0),
    "IND.drawing": (27, 0),
    "EdgeSeal.drawing": (39, 0),
    "dfpad.drawing": (41, 0),
    "TEXT.drawing": (63, 0),
    "Recog.drawing": (99, 0),
    "DigiBnd.drawing": (16, 0),
    "DigiBnd.drawing0": (16, 10),
    "RES.drawing": (24, 0),
    "SRAM.drawing": (25, 0),
    "TRANS.drawing": (26, 0),
    "DigiSub.drawing": (60, 0),
    "HeatTrans.drawing": (51, 0),
    "HeatRes.drawing": (52, 0),
    "NoRCX.drawing": (148, 0),
    "BiWind.drawing": (3, 0),
    "BasPoly.drawing": (13, 0),
    "EmWind.drawing": (33, 0),
    "DeepCo.drawing": (35, 0),
    "EmPoly.drawing": (55, 0),
    "Varicap.drawing": (70, 0),
    "EmWind3.drawing": (90, 0),
    "EmWiHV3.drawing": (91, 0),
    "ColOpen.drawing": (101, 0),
    "ColWind.drawing": (139, 0),
    "EmWiHV.drawing": (156, 0),
    "DeepVia.drawing": (152, 0),
    "LBE.drawing": (157, 0),
    "BackMetal1.drawing": (20, 0),
    "BackPassiv.drawing": (23, 0),
    "IntBondVia.drawing": (72, 0),
    "IntBondMet.drawing": (73, 0),
    "DevBondVia.drawing": (74, 0),
    "DevBondMet.drawing": (75, 0),
    "DevTrench.drawing": (76, 0),
    "Redist.drawing": (77, 0),
    "FBE.drawing": (54, 0),
    "AntVia1.drawing": (83, 0),
    "AntMetal2.drawing": (84, 0),
    "AntMetal1.drawing": (132, 0),
    "FLM.drawing": (142, 0),
    "SNSRing.drawing": (135, 0),
    "Sensor.drawing": (136, 0),
    "SNSArms.drawing": (137, 0),
    "SNSCMOSVia.drawing": (138, 0),
    "SNSBotVia.drawing": (149, 0),
    "SNSTopVia.drawing": (151, 0),
    "NLDB.drawing": (15, 0),
    "PLDB.drawing": (45, 0),
    "RedBuLay.drawing": (92, 0),
    "NLDD.drawing": (112, 0),
    "PLDD.drawing": (113, 0),
    "NExt.drawing": (114, 0),
    "PExt.drawing": (115, 0),
    "INLDPWL.drawing": (127, 0),
    "nBuLayCut.drawing": (131, 0),
    "GraphBot.drawing": (78, 0),
    "GraphTop.drawing": (79, 0),
    "GraphCont.drawing": (85, 0),
    "SiWG.drawing": (86, 0),
    "SiGrating.drawing": (87, 0),
    "SiNGrating.drawing": (88, 0),
    "GraphPas.drawing": (89, 0),
    "GraphPad.drawing": (97, 0),
    "GraphMetal1.drawing": (109, 0),
    "GraphMet1L.drawing": (110, 0),
    "GraphGate.drawing": (118, 0),
    "SiNWG.drawing": (119, 0),
    "IC.drawing": (48, 0),
    "NoDRC.drawing": (62, 0),
    "RadHard.drawing": (68, 0),
    "MemCap.drawing": (69, 0),
    "SMOS.drawing": (93, 0),
    "Polimide.drawing": (98, 0),
    "EXTBlock.drawing": (111, 0),
    "NExtHV.drawing": (116, 0),
    "PExtHV.drawing": (117, 0),
    "MEMPAD.drawing": (124, 0),
    "HafniumOx.drawing": (143, 0),
    "MEMVia.drawing": (145, 0),
    "RFMEM.drawing": (147, 0),
    "FGEtch.drawing": (153, 0),
    "CtrGat.drawing": (154, 0),
    "FGImp.drawing": (155, 0),
    "AlCuStop.drawing": (159, 0),
    "prBoundary.drawing": (189, 0),
    "Exchange0.drawing": (190, 0),
    "Exchange1.drawing": (191, 0),
    "Exchange2.drawing": (192, 0),
    "Exchange3.drawing": (193, 0),
    "Exchange4.drawing": (194, 0),
    "isoNWell.drawing": (257, 0),
}

sg13g2_glayer_mapping = {
    # BEOL
    "met5": "Metal5.drawing",
    "via4": "Via4.drawing",
    "met4": "Metal4.drawing",
    "via3": "Via3.drawing",
    "met3": "Metal3.drawing",
    "via2": "Via2.drawing",
    "met2": "Metal2.drawing",
    "via1": "Via1.drawing",
    "met1": "Metal1.drawing",
    "mcon": "Cont.drawing",
    # FEOL
    "poly": "GatPoly.drawing",
    "active_diff": "Activ.drawing",
    "active_tap": "Activ.drawing",
    "n+s/d": "nSD.drawing",
    "p+s/d": "pSD.drawing",
    "nwell": "NWell.drawing",
    "pwell": "PWell.drawing",
    "dnwell": "TEXT.drawing",
    "capmet": "TEXT.drawing",
}

# note for DRC, there is mim_option 'A'. This is the one configured for use


openfasoc_dir = (
    Path(__file__).resolve().parent.parent.parent.parent.parent.parent.parent
)

sg13g2_drc_file = Path(__file__).resolve().parent / "sg13g2mcu_drc.lydrc"
pdk_root = Path("/usr/bin/miniconda3/share/pdk/")
lvs_schematic_ref_file = (
    openfasoc_dir
    / "common"
    / "platforms"
    / "sg13g2osu9t"
    / "cdl"
    / "sg13g2mcu_osu_sc_9T.spice"
)
magic_drc_file = (
    pdk_root / "sg13g2mcuC" / "libs.tech" / "magic" / "sg13g2mcuC.magicrc"
)
lvs_setup_tcl_file = (
    pdk_root / "sg13g2mcuC" / "libs.tech" / "netgen" / "sg13g2mcuC_setup.tcl"
)
temp_dir = None


pdk_files = SetupPDKFiles(
    pdk_root=pdk_root,
    klayout_drc_file=sg13g2_drc_file,
    lvs_schematic_ref_file=lvs_schematic_ref_file,
    lvs_setup_tcl_file=lvs_setup_tcl_file,
    magic_drc_file=magic_drc_file,
    temp_dir=temp_dir,
    pdk="sg13g2",
).return_dict_of_files()

sg13g2_mapped_pdk = MappedPDK(
    name="sg13g2",
    glayers=sg13g2_glayer_mapping,
    models={"nfet": "nfet_03v3", "pfet": "pfet_03v3", "mimcap": "mimcap_1p0fF"},
    layers=LAYER,
    pdk_files=pdk_files,
    grules=grulesobj,
)

# configure the grid size and other settings
sg13g2_mapped_pdk.gds_write_settings.precision = 5 * 10**-9
sg13g2_mapped_pdk.cell_decorator_settings.cache = False
