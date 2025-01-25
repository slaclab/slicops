"""Raw device data

**DO NOT EDIT; automatically generated**

* generator: slicops.pkcli.device_yaml
* input: /home/vagrant/src/slaclab/lcls-tools/lcls_tools/common/devices/yaml/*.yaml

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict


DB = PKDict(
    {
        "AREA_TO_BEAM_PATH": PKDict(
            {
                "BC1": (
                    "CU_ALINE",
                    "CU_HTXI",
                    "CU_HXR",
                    "CU_HXTES",
                    "CU_SFTH",
                    "CU_SXR",
                ),
                "BC1B": (
                    "SC_BSYD",
                    "SC_DASEL",
                    "SC_HXR",
                    "SC_S2_X",
                    "SC_SFTS",
                    "SC_STMO",
                    "SC_STXI",
                    "SC_SXR",
                ),
                "BC2": (
                    "CU_ALINE",
                    "CU_HTXI",
                    "CU_HXR",
                    "CU_HXTES",
                    "CU_SFTH",
                    "CU_SXR",
                ),
                "BC2B": (
                    "SC_BSYD",
                    "SC_DASEL",
                    "SC_HXR",
                    "SC_S2_X",
                    "SC_SFTS",
                    "SC_STMO",
                    "SC_STXI",
                    "SC_SXR",
                ),
                "COL0": (
                    "SC_BSYD",
                    "SC_DASEL",
                    "SC_HXR",
                    "SC_S2_X",
                    "SC_SFTS",
                    "SC_STMO",
                    "SC_STXI",
                    "SC_SXR",
                ),
                "DASEL": ("SC_DASEL",),
                "DEV_AREA": ("DEV_BEAM_PATH",),
                "DIAG0": ("SC_DIAG0",),
                "DL1": (
                    "CU_ALINE",
                    "CU_HTXI",
                    "CU_HXR",
                    "CU_HXTES",
                    "CU_SFTH",
                    "CU_SPEC",
                    "CU_SXR",
                ),
                "DMPH": ("CU_HXR", "SC_HXR"),
                "DMPS": ("CU_SXR", "SC_SXR"),
                "DOG": (
                    "SC_BSYD",
                    "SC_DASEL",
                    "SC_HXR",
                    "SC_S2_X",
                    "SC_SFTS",
                    "SC_STMO",
                    "SC_STXI",
                    "SC_SXR",
                ),
                "GSPEC": ("CU_GSPEC",),
                "GUN": (
                    "CU_ALINE",
                    "CU_GSPEC",
                    "CU_HTXI",
                    "CU_HXR",
                    "CU_HXTES",
                    "CU_SFTH",
                    "CU_SPEC",
                    "CU_SXR",
                ),
                "GUNB": ("SC_DIAG0", "SC_HXR", "SC_SXR"),
                "HTR": (
                    "SC_BSYD",
                    "SC_DASEL",
                    "SC_DIAG0",
                    "SC_HXR",
                    "SC_S2_X",
                    "SC_SFTS",
                    "SC_STMO",
                    "SC_STXI",
                    "SC_SXR",
                ),
                "L0": (
                    "CU_ALINE",
                    "CU_HTXI",
                    "CU_HXR",
                    "CU_HXTES",
                    "CU_SFTH",
                    "CU_SPEC",
                    "CU_SXR",
                ),
                "LTUH": ("CU_HTXI", "CU_HXR", "CU_HXTES", "CU_SFTH", "SC_HXR"),
                "SPEC": ("CU_SPEC",),
                "UNDS": (
                    "CU_SXR",
                    "SC_S2_X",
                    "SC_SFTS",
                    "SC_STMO",
                    "SC_STXI",
                    "SC_SXR",
                ),
            }
        ),
        "AREA_TO_DEVICE": PKDict(
            {
                "BC1": ("OTR11", "OTR12"),
                "BC1B": ("OTR11B",),
                "BC2": ("OTR21",),
                "BC2B": ("OTR21B",),
                "COL0": ("OTRC006",),
                "DASEL": ("PRDAS12", "PRDAS14", "PRDAS17"),
                "DEV_AREA": ("DEV_CAMERA",),
                "DIAG0": ("OTRDG02", "OTRDG04"),
                "DL1": ("OTR2", "OTR3", "OTR4", "OTRH1", "OTRH2"),
                "DMPH": ("OTRDMP",),
                "DMPS": ("OTRDMPB",),
                "DOG": ("OTRDOG",),
                "GSPEC": ("YAGG1",),
                "GUN": ("VCC", "YAG01"),
                "GUNB": ("VCCB",),
                "HTR": ("OTR0H04", "YAGH1", "YAGH2"),
                "L0": ("YAG02", "YAG03"),
                "LTUH": ("YAGPSI",),
                "SPEC": ("YAGS1", "YAGS2"),
                "UNDS": ("BOD10", "BOD12"),
            }
        ),
        "BEAM_PATH_TO_AREA": PKDict(
            {
                "CU_ALINE": ("BC1", "BC2", "DL1", "GUN", "L0"),
                "CU_GSPEC": ("GSPEC", "GUN"),
                "CU_HTXI": ("BC1", "BC2", "DL1", "GUN", "L0", "LTUH"),
                "CU_HXR": ("BC1", "BC2", "DL1", "DMPH", "GUN", "L0", "LTUH"),
                "CU_HXTES": ("BC1", "BC2", "DL1", "GUN", "L0", "LTUH"),
                "CU_SFTH": ("BC1", "BC2", "DL1", "GUN", "L0", "LTUH"),
                "CU_SPEC": ("DL1", "GUN", "L0", "SPEC"),
                "CU_SXR": ("BC1", "BC2", "DL1", "DMPS", "GUN", "L0", "UNDS"),
                "DEV_BEAM_PATH": ("DEV_AREA",),
                "SC_BSYD": ("BC1B", "BC2B", "COL0", "DOG", "HTR"),
                "SC_DASEL": ("BC1B", "BC2B", "COL0", "DASEL", "DOG", "HTR"),
                "SC_DIAG0": ("DIAG0", "GUNB", "HTR"),
                "SC_HXR": (
                    "BC1B",
                    "BC2B",
                    "COL0",
                    "DMPH",
                    "DOG",
                    "GUNB",
                    "HTR",
                    "LTUH",
                ),
                "SC_S2_X": ("BC1B", "BC2B", "COL0", "DOG", "HTR", "UNDS"),
                "SC_SFTS": ("BC1B", "BC2B", "COL0", "DOG", "HTR", "UNDS"),
                "SC_STMO": ("BC1B", "BC2B", "COL0", "DOG", "HTR", "UNDS"),
                "SC_STXI": ("BC1B", "BC2B", "COL0", "DOG", "HTR", "UNDS"),
                "SC_SXR": (
                    "BC1B",
                    "BC2B",
                    "COL0",
                    "DMPS",
                    "DOG",
                    "GUNB",
                    "HTR",
                    "UNDS",
                ),
            }
        ),
        "BEAM_PATH_TO_DEVICE": PKDict(
            {
                "CU_ALINE": (
                    "OTR11",
                    "OTR12",
                    "OTR2",
                    "OTR21",
                    "OTR3",
                    "OTR4",
                    "OTRH1",
                    "OTRH2",
                    "YAG01",
                    "YAG02",
                    "YAG03",
                ),
                "CU_GSPEC": ("YAG01", "YAGG1"),
                "CU_HTXI": (
                    "OTR11",
                    "OTR12",
                    "OTR2",
                    "OTR21",
                    "OTR3",
                    "OTR4",
                    "OTRH1",
                    "OTRH2",
                    "YAG01",
                    "YAG02",
                    "YAG03",
                    "YAGPSI",
                ),
                "CU_HXR": (
                    "OTR11",
                    "OTR12",
                    "OTR2",
                    "OTR21",
                    "OTR3",
                    "OTR4",
                    "OTRDMP",
                    "OTRH1",
                    "OTRH2",
                    "VCC",
                    "YAG01",
                    "YAG02",
                    "YAG03",
                    "YAGPSI",
                ),
                "CU_HXTES": (
                    "OTR11",
                    "OTR12",
                    "OTR2",
                    "OTR21",
                    "OTR3",
                    "OTR4",
                    "OTRH1",
                    "OTRH2",
                    "YAG01",
                    "YAG02",
                    "YAG03",
                    "YAGPSI",
                ),
                "CU_SFTH": (
                    "OTR11",
                    "OTR12",
                    "OTR2",
                    "OTR21",
                    "OTR3",
                    "OTR4",
                    "OTRH1",
                    "OTRH2",
                    "YAG01",
                    "YAG02",
                    "YAG03",
                    "YAGPSI",
                ),
                "CU_SPEC": (
                    "OTR2",
                    "OTR3",
                    "OTRH1",
                    "OTRH2",
                    "YAG01",
                    "YAG02",
                    "YAG03",
                    "YAGS1",
                    "YAGS2",
                ),
                "CU_SXR": (
                    "BOD10",
                    "BOD12",
                    "OTR11",
                    "OTR12",
                    "OTR2",
                    "OTR21",
                    "OTR3",
                    "OTR4",
                    "OTRDMPB",
                    "OTRH1",
                    "OTRH2",
                    "VCC",
                    "YAG01",
                    "YAG02",
                    "YAG03",
                ),
                "DEV_BEAM_PATH": ("DEV_CAMERA",),
                "SC_BSYD": (
                    "OTR0H04",
                    "OTR11B",
                    "OTR21B",
                    "OTRC006",
                    "OTRDOG",
                    "YAGH1",
                    "YAGH2",
                ),
                "SC_DASEL": (
                    "OTR0H04",
                    "OTR11B",
                    "OTR21B",
                    "OTRC006",
                    "OTRDOG",
                    "PRDAS12",
                    "PRDAS14",
                    "PRDAS17",
                    "YAGH1",
                    "YAGH2",
                ),
                "SC_DIAG0": ("OTR0H04", "OTRDG02", "OTRDG04", "VCCB", "YAGH1", "YAGH2"),
                "SC_HXR": (
                    "OTR0H04",
                    "OTR11B",
                    "OTR21B",
                    "OTRC006",
                    "OTRDMP",
                    "OTRDOG",
                    "VCCB",
                    "YAGH1",
                    "YAGH2",
                    "YAGPSI",
                ),
                "SC_S2_X": (
                    "BOD10",
                    "BOD12",
                    "OTR0H04",
                    "OTR11B",
                    "OTR21B",
                    "OTRC006",
                    "OTRDOG",
                    "YAGH1",
                    "YAGH2",
                ),
                "SC_SFTS": (
                    "BOD10",
                    "BOD12",
                    "OTR0H04",
                    "OTR11B",
                    "OTR21B",
                    "OTRC006",
                    "OTRDOG",
                    "YAGH1",
                    "YAGH2",
                ),
                "SC_STMO": (
                    "BOD10",
                    "BOD12",
                    "OTR0H04",
                    "OTR11B",
                    "OTR21B",
                    "OTRC006",
                    "OTRDOG",
                    "YAGH1",
                    "YAGH2",
                ),
                "SC_STXI": (
                    "BOD10",
                    "BOD12",
                    "OTR0H04",
                    "OTR11B",
                    "OTR21B",
                    "OTRC006",
                    "OTRDOG",
                    "YAGH1",
                    "YAGH2",
                ),
                "SC_SXR": (
                    "BOD10",
                    "BOD12",
                    "OTR0H04",
                    "OTR11B",
                    "OTR21B",
                    "OTRC006",
                    "OTRDMPB",
                    "OTRDOG",
                    "VCCB",
                    "YAGH1",
                    "YAGH2",
                ),
            }
        ),
        "DEVICE_KIND_TO_DEVICE": PKDict(
            {
                "screen": (
                    "BOD10",
                    "BOD12",
                    "DEV_CAMERA",
                    "OTR0H04",
                    "OTR11",
                    "OTR11B",
                    "OTR12",
                    "OTR2",
                    "OTR21",
                    "OTR21B",
                    "OTR3",
                    "OTR4",
                    "OTRC006",
                    "OTRDG02",
                    "OTRDG04",
                    "OTRDMP",
                    "OTRDMPB",
                    "OTRDOG",
                    "OTRH1",
                    "OTRH2",
                    "PRDAS12",
                    "PRDAS14",
                    "PRDAS17",
                    "VCC",
                    "VCCB",
                    "YAG01",
                    "YAG02",
                    "YAG03",
                    "YAGG1",
                    "YAGH1",
                    "YAGH2",
                    "YAGPSI",
                    "YAGS1",
                    "YAGS2",
                )
            }
        ),
        "DEVICE_TO_AREA": PKDict(
            {
                "BOD10": ("UNDS",),
                "BOD12": ("UNDS",),
                "DEV_CAMERA": ("DEV_AREA",),
                "OTR0H04": ("HTR",),
                "OTR11": ("BC1",),
                "OTR11B": ("BC1B",),
                "OTR12": ("BC1",),
                "OTR2": ("DL1",),
                "OTR21": ("BC2",),
                "OTR21B": ("BC2B",),
                "OTR3": ("DL1",),
                "OTR4": ("DL1",),
                "OTRC006": ("COL0",),
                "OTRDG02": ("DIAG0",),
                "OTRDG04": ("DIAG0",),
                "OTRDMP": ("DMPH",),
                "OTRDMPB": ("DMPS",),
                "OTRDOG": ("DOG",),
                "OTRH1": ("DL1",),
                "OTRH2": ("DL1",),
                "PRDAS12": ("DASEL",),
                "PRDAS14": ("DASEL",),
                "PRDAS17": ("DASEL",),
                "VCC": ("GUN",),
                "VCCB": ("GUNB",),
                "YAG01": ("GUN",),
                "YAG02": ("L0",),
                "YAG03": ("L0",),
                "YAGG1": ("GSPEC",),
                "YAGH1": ("HTR",),
                "YAGH2": ("HTR",),
                "YAGPSI": ("LTUH",),
                "YAGS1": ("SPEC",),
                "YAGS2": ("SPEC",),
            }
        ),
        "DEVICE_TO_META": PKDict(
            {
                "BOD10": PKDict(
                    {
                        "accessor": PKDict(
                            {
                                "acquire": PKDict(
                                    {
                                        "name": "acquire",
                                        "pv_base": "Acquire",
                                        "pv_name": "YAGS:UNDS:3575:Acquire",
                                        "pv_writable": True,
                                        "py_type": "bool",
                                    }
                                ),
                                "bit_depth": PKDict(
                                    {
                                        "name": "bit_depth",
                                        "pv_base": "N_OF_BITS",
                                        "pv_name": "YAGS:UNDS:3575:N_OF_BITS",
                                        "py_type": "int",
                                    }
                                ),
                                "image": PKDict(
                                    {
                                        "name": "image",
                                        "pv_base": "IMAGE",
                                        "pv_name": "YAGS:UNDS:3575:IMAGE",
                                        "py_type": "ndarray",
                                    }
                                ),
                                "num_cols": PKDict(
                                    {
                                        "name": "num_cols",
                                        "pv_base": "N_OF_COL",
                                        "pv_name": "YAGS:UNDS:3575:N_OF_COL",
                                        "py_type": "int",
                                    }
                                ),
                                "num_rols": PKDict(
                                    {
                                        "name": "num_rols",
                                        "pv_base": "N_OF_ROW",
                                        "pv_name": "YAGS:UNDS:3575:N_OF_ROW",
                                        "py_type": "int",
                                    }
                                ),
                            }
                        ),
                        "area": "UNDS",
                        "beam_path": (
                            "CU_SXR",
                            "SC_S2_X",
                            "SC_SFTS",
                            "SC_STMO",
                            "SC_STXI",
                            "SC_SXR",
                        ),
                        "device_kind": "screen",
                        "device_length": 3661.222,
                        "device_name": "BOD10",
                        "pv_prefix": "YAGS:UNDS:3575",
                    }
                ),
                "BOD12": PKDict(
                    {
                        "accessor": PKDict(
                            {
                                "acquire": PKDict(
                                    {
                                        "name": "acquire",
                                        "pv_base": "Acquire",
                                        "pv_name": "YAGS:UNDS:3795:Acquire",
                                        "pv_writable": True,
                                        "py_type": "bool",
                                    }
                                ),
                                "bit_depth": PKDict(
                                    {
                                        "name": "bit_depth",
                                        "pv_base": "N_OF_BITS",
                                        "pv_name": "YAGS:UNDS:3795:N_OF_BITS",
                                        "py_type": "int",
                                    }
                                ),
                                "image": PKDict(
                                    {
                                        "name": "image",
                                        "pv_base": "IMAGE",
                                        "pv_name": "YAGS:UNDS:3795:IMAGE",
                                        "py_type": "ndarray",
                                    }
                                ),
                                "num_cols": PKDict(
                                    {
                                        "name": "num_cols",
                                        "pv_base": "N_OF_COL",
                                        "pv_name": "YAGS:UNDS:3795:N_OF_COL",
                                        "py_type": "int",
                                    }
                                ),
                                "num_rols": PKDict(
                                    {
                                        "name": "num_rols",
                                        "pv_base": "N_OF_ROW",
                                        "pv_name": "YAGS:UNDS:3795:N_OF_ROW",
                                        "py_type": "int",
                                    }
                                ),
                            }
                        ),
                        "area": "UNDS",
                        "beam_path": (
                            "CU_SXR",
                            "SC_S2_X",
                            "SC_SFTS",
                            "SC_STMO",
                            "SC_STXI",
                            "SC_SXR",
                        ),
                        "device_kind": "screen",
                        "device_length": 3670.392,
                        "device_name": "BOD12",
                        "pv_prefix": "YAGS:UNDS:3795",
                    }
                ),
                "DEV_CAMERA": PKDict(
                    {
                        "accessor": PKDict(
                            {
                                "acquire": PKDict(
                                    {
                                        "name": "acquire",
                                        "pv_base": "cam1:Acquire",
                                        "pv_name": "13SIM1:cam1:Acquire",
                                        "pv_writable": True,
                                        "py_type": "bool",
                                    }
                                ),
                                "bit_depth": PKDict(
                                    {
                                        "name": "bit_depth",
                                        "pv_base": "cam1:N_OF_BITS",
                                        "pv_name": "13SIM1:cam1:N_OF_BITS",
                                        "py_type": "int",
                                    }
                                ),
                                "gain": PKDict(
                                    {
                                        "name": "gain",
                                        "pv_base": "cam1:Gain",
                                        "pv_name": "13SIM1:cam1:Gain",
                                        "pv_writable": True,
                                        "py_type": "int",
                                    }
                                ),
                                "image": PKDict(
                                    {
                                        "name": "image",
                                        "pv_base": "image1:ArrayData",
                                        "pv_name": "13SIM1:image1:ArrayData",
                                        "py_type": "ndarray",
                                    }
                                ),
                                "num_cols": PKDict(
                                    {
                                        "name": "num_cols",
                                        "pv_base": "cam1:ArraySizeY_RBV",
                                        "pv_name": "13SIM1:cam1:ArraySizeY_RBV",
                                        "py_type": "int",
                                    }
                                ),
                                "num_rows": PKDict(
                                    {
                                        "name": "num_rows",
                                        "pv_base": "cam1:ArraySizeX_RBV",
                                        "pv_name": "13SIM1:cam1:ArraySizeX_RBV",
                                        "py_type": "int",
                                    }
                                ),
                            }
                        ),
                        "area": "DEV_AREA",
                        "beam_path": ("DEV_BEAM_PATH",),
                        "device_kind": "screen",
                        "device_length": 0.614,
                        "device_name": "DEV_CAMERA",
                        "pv_prefix": "13SIM1",
                    }
                ),
                "OTR0H04": PKDict(
                    {
                        "accessor": PKDict(
                            {
                                "acquire": PKDict(
                                    {
                                        "name": "acquire",
                                        "pv_base": "Acquire",
                                        "pv_name": "OTRS:HTR:330:Acquire",
                                        "pv_writable": True,
                                        "py_type": "bool",
                                    }
                                ),
                                "bit_depth": PKDict(
                                    {
                                        "name": "bit_depth",
                                        "pv_base": "N_OF_BITS",
                                        "pv_name": "OTRS:HTR:330:N_OF_BITS",
                                        "py_type": "int",
                                    }
                                ),
                                "image": PKDict(
                                    {
                                        "name": "image",
                                        "pv_base": "Image:ArrayData",
                                        "pv_name": "OTRS:HTR:330:Image:ArrayData",
                                        "py_type": "ndarray",
                                    }
                                ),
                                "num_cols": PKDict(
                                    {
                                        "name": "num_cols",
                                        "pv_base": "Image:ArraySize1_RBV",
                                        "pv_name": "OTRS:HTR:330:Image:ArraySize1_RBV",
                                        "py_type": "int",
                                    }
                                ),
                                "num_rows": PKDict(
                                    {
                                        "name": "num_rows",
                                        "pv_base": "Image:ArraySize0_RBV",
                                        "pv_name": "OTRS:HTR:330:Image:ArraySize0_RBV",
                                        "py_type": "int",
                                    }
                                ),
                            }
                        ),
                        "area": "HTR",
                        "beam_path": (
                            "SC_BSYD",
                            "SC_DASEL",
                            "SC_DIAG0",
                            "SC_HXR",
                            "SC_S2_X",
                            "SC_SFTS",
                            "SC_STMO",
                            "SC_STXI",
                            "SC_SXR",
                        ),
                        "device_kind": "screen",
                        "device_length": 24.345,
                        "device_name": "OTR0H04",
                        "pv_prefix": "OTRS:HTR:330",
                    }
                ),
                "OTR11": PKDict(
                    {
                        "accessor": PKDict(
                            {
                                "acquire": PKDict(
                                    {
                                        "name": "acquire",
                                        "pv_base": "Acquire",
                                        "pv_name": "OTRS:LI21:237:Acquire",
                                        "pv_writable": True,
                                        "py_type": "bool",
                                    }
                                ),
                                "bit_depth": PKDict(
                                    {
                                        "name": "bit_depth",
                                        "pv_base": "N_OF_BITS",
                                        "pv_name": "OTRS:LI21:237:N_OF_BITS",
                                        "py_type": "int",
                                    }
                                ),
                                "image": PKDict(
                                    {
                                        "name": "image",
                                        "pv_base": "IMAGE",
                                        "pv_name": "OTRS:LI21:237:IMAGE",
                                        "py_type": "ndarray",
                                    }
                                ),
                                "num_cols": PKDict(
                                    {
                                        "name": "num_cols",
                                        "pv_base": "N_OF_COL",
                                        "pv_name": "OTRS:LI21:237:N_OF_COL",
                                        "py_type": "int",
                                    }
                                ),
                                "num_rols": PKDict(
                                    {
                                        "name": "num_rols",
                                        "pv_base": "N_OF_ROW",
                                        "pv_name": "OTRS:LI21:237:N_OF_ROW",
                                        "py_type": "int",
                                    }
                                ),
                            }
                        ),
                        "area": "BC1",
                        "beam_path": (
                            "CU_ALINE",
                            "CU_HTXI",
                            "CU_HXR",
                            "CU_HXTES",
                            "CU_SFTH",
                            "CU_SXR",
                        ),
                        "device_kind": "screen",
                        "device_length": 34.834,
                        "device_name": "OTR11",
                        "pv_prefix": "OTRS:LI21:237",
                    }
                ),
                "OTR11B": PKDict(
                    {
                        "accessor": PKDict(
                            {
                                "acquire": PKDict(
                                    {
                                        "name": "acquire",
                                        "pv_base": "Acquire",
                                        "pv_name": "PROF:BC1B:470:Acquire",
                                        "pv_writable": True,
                                        "py_type": "bool",
                                    }
                                ),
                                "bit_depth": PKDict(
                                    {
                                        "name": "bit_depth",
                                        "pv_base": "N_OF_BITS",
                                        "pv_name": "PROF:BC1B:470:N_OF_BITS",
                                        "py_type": "int",
                                    }
                                ),
                                "image": PKDict(
                                    {
                                        "name": "image",
                                        "pv_base": "Image:ArrayData",
                                        "pv_name": "PROF:BC1B:470:Image:ArrayData",
                                        "py_type": "ndarray",
                                    }
                                ),
                                "num_cols": PKDict(
                                    {
                                        "name": "num_cols",
                                        "pv_base": "Image:ArraySize1_RBV",
                                        "pv_name": "PROF:BC1B:470:Image:ArraySize1_RBV",
                                        "py_type": "int",
                                    }
                                ),
                                "num_rows": PKDict(
                                    {
                                        "name": "num_rows",
                                        "pv_base": "Image:ArraySize0_RBV",
                                        "pv_name": "PROF:BC1B:470:Image:ArraySize0_RBV",
                                        "py_type": "int",
                                    }
                                ),
                            }
                        ),
                        "area": "BC1B",
                        "beam_path": (
                            "SC_BSYD",
                            "SC_DASEL",
                            "SC_HXR",
                            "SC_S2_X",
                            "SC_SFTS",
                            "SC_STMO",
                            "SC_STXI",
                            "SC_SXR",
                        ),
                        "device_kind": "screen",
                        "device_length": 135.571,
                        "device_name": "OTR11B",
                        "pv_prefix": "PROF:BC1B:470",
                    }
                ),
                "OTR12": PKDict(
                    {
                        "accessor": PKDict(
                            {
                                "acquire": PKDict(
                                    {
                                        "name": "acquire",
                                        "pv_base": "Acquire",
                                        "pv_name": "OTRS:LI21:291:Acquire",
                                        "pv_writable": True,
                                        "py_type": "bool",
                                    }
                                ),
                                "bit_depth": PKDict(
                                    {
                                        "name": "bit_depth",
                                        "pv_base": "N_OF_BITS",
                                        "pv_name": "OTRS:LI21:291:N_OF_BITS",
                                        "py_type": "int",
                                    }
                                ),
                                "image": PKDict(
                                    {
                                        "name": "image",
                                        "pv_base": "IMAGE",
                                        "pv_name": "OTRS:LI21:291:IMAGE",
                                        "py_type": "ndarray",
                                    }
                                ),
                                "num_cols": PKDict(
                                    {
                                        "name": "num_cols",
                                        "pv_base": "N_OF_COL",
                                        "pv_name": "OTRS:LI21:291:N_OF_COL",
                                        "py_type": "int",
                                    }
                                ),
                                "num_rols": PKDict(
                                    {
                                        "name": "num_rols",
                                        "pv_base": "N_OF_ROW",
                                        "pv_name": "OTRS:LI21:291:N_OF_ROW",
                                        "py_type": "int",
                                    }
                                ),
                            }
                        ),
                        "area": "BC1",
                        "beam_path": (
                            "CU_ALINE",
                            "CU_HTXI",
                            "CU_HXR",
                            "CU_HXTES",
                            "CU_SFTH",
                            "CU_SXR",
                        ),
                        "device_kind": "screen",
                        "device_length": 41.512,
                        "device_name": "OTR12",
                        "pv_prefix": "OTRS:LI21:291",
                    }
                ),
                "OTR2": PKDict(
                    {
                        "accessor": PKDict(
                            {
                                "acquire": PKDict(
                                    {
                                        "name": "acquire",
                                        "pv_base": "Acquire",
                                        "pv_name": "OTRS:IN20:571:Acquire",
                                        "pv_writable": True,
                                        "py_type": "bool",
                                    }
                                ),
                                "bit_depth": PKDict(
                                    {
                                        "name": "bit_depth",
                                        "pv_base": "N_OF_BITS",
                                        "pv_name": "OTRS:IN20:571:N_OF_BITS",
                                        "py_type": "int",
                                    }
                                ),
                                "image": PKDict(
                                    {
                                        "name": "image",
                                        "pv_base": "Image:ArrayData",
                                        "pv_name": "OTRS:IN20:571:Image:ArrayData",
                                        "py_type": "ndarray",
                                    }
                                ),
                                "num_cols": PKDict(
                                    {
                                        "name": "num_cols",
                                        "pv_base": "Image:ArraySize1_RBV",
                                        "pv_name": "OTRS:IN20:571:Image:ArraySize1_RBV",
                                        "py_type": "int",
                                    }
                                ),
                                "num_rows": PKDict(
                                    {
                                        "name": "num_rows",
                                        "pv_base": "Image:ArraySize0_RBV",
                                        "pv_name": "OTRS:IN20:571:Image:ArraySize0_RBV",
                                        "py_type": "int",
                                    }
                                ),
                            }
                        ),
                        "area": "DL1",
                        "beam_path": (
                            "CU_ALINE",
                            "CU_HTXI",
                            "CU_HXR",
                            "CU_HXTES",
                            "CU_SFTH",
                            "CU_SPEC",
                            "CU_SXR",
                        ),
                        "device_kind": "screen",
                        "device_length": 14.241,
                        "device_name": "OTR2",
                        "pv_prefix": "OTRS:IN20:571",
                    }
                ),
                "OTR21": PKDict(
                    {
                        "accessor": PKDict(
                            {
                                "acquire": PKDict(
                                    {
                                        "name": "acquire",
                                        "pv_base": "Acquire",
                                        "pv_name": "OTRS:LI24:807:Acquire",
                                        "pv_writable": True,
                                        "py_type": "bool",
                                    }
                                ),
                                "bit_depth": PKDict(
                                    {
                                        "name": "bit_depth",
                                        "pv_base": "N_OF_BITS",
                                        "pv_name": "OTRS:LI24:807:N_OF_BITS",
                                        "py_type": "int",
                                    }
                                ),
                                "image": PKDict(
                                    {
                                        "name": "image",
                                        "pv_base": "IMAGE",
                                        "pv_name": "OTRS:LI24:807:IMAGE",
                                        "py_type": "ndarray",
                                    }
                                ),
                                "num_cols": PKDict(
                                    {
                                        "name": "num_cols",
                                        "pv_base": "N_OF_COL",
                                        "pv_name": "OTRS:LI24:807:N_OF_COL",
                                        "py_type": "int",
                                    }
                                ),
                                "num_rols": PKDict(
                                    {
                                        "name": "num_rols",
                                        "pv_base": "N_OF_ROW",
                                        "pv_name": "OTRS:LI24:807:N_OF_ROW",
                                        "py_type": "int",
                                    }
                                ),
                            }
                        ),
                        "area": "BC2",
                        "beam_path": (
                            "CU_ALINE",
                            "CU_HTXI",
                            "CU_HXR",
                            "CU_HXTES",
                            "CU_SFTH",
                            "CU_SXR",
                        ),
                        "device_kind": "screen",
                        "device_length": 410.405,
                        "device_name": "OTR21",
                        "pv_prefix": "OTRS:LI24:807",
                    }
                ),
                "OTR21B": PKDict(
                    {
                        "accessor": PKDict(
                            {
                                "acquire": PKDict(
                                    {
                                        "name": "acquire",
                                        "pv_base": "Acquire",
                                        "pv_name": "PROF:BC2B:545:Acquire",
                                        "pv_writable": True,
                                        "py_type": "bool",
                                    }
                                ),
                                "bit_depth": PKDict(
                                    {
                                        "name": "bit_depth",
                                        "pv_base": "N_OF_BITS",
                                        "pv_name": "PROF:BC2B:545:N_OF_BITS",
                                        "py_type": "int",
                                    }
                                ),
                                "image": PKDict(
                                    {
                                        "name": "image",
                                        "pv_base": "Image:ArrayData",
                                        "pv_name": "PROF:BC2B:545:Image:ArrayData",
                                        "py_type": "ndarray",
                                    }
                                ),
                                "num_cols": PKDict(
                                    {
                                        "name": "num_cols",
                                        "pv_base": "Image:ArraySize1_RBV",
                                        "pv_name": "PROF:BC2B:545:Image:ArraySize1_RBV",
                                        "py_type": "int",
                                    }
                                ),
                                "num_rows": PKDict(
                                    {
                                        "name": "num_rows",
                                        "pv_base": "Image:ArraySize0_RBV",
                                        "pv_name": "PROF:BC2B:545:Image:ArraySize0_RBV",
                                        "py_type": "int",
                                    }
                                ),
                            }
                        ),
                        "area": "BC2B",
                        "beam_path": (
                            "SC_BSYD",
                            "SC_DASEL",
                            "SC_HXR",
                            "SC_S2_X",
                            "SC_SFTS",
                            "SC_STMO",
                            "SC_STXI",
                            "SC_SXR",
                        ),
                        "device_kind": "screen",
                        "device_length": 355.091,
                        "device_name": "OTR21B",
                        "pv_prefix": "PROF:BC2B:545",
                    }
                ),
                "OTR3": PKDict(
                    {
                        "accessor": PKDict(
                            {
                                "acquire": PKDict(
                                    {
                                        "name": "acquire",
                                        "pv_base": "Acquire",
                                        "pv_name": "OTRS:IN20:621:Acquire",
                                        "pv_writable": True,
                                        "py_type": "bool",
                                    }
                                ),
                                "bit_depth": PKDict(
                                    {
                                        "name": "bit_depth",
                                        "pv_base": "N_OF_BITS",
                                        "pv_name": "OTRS:IN20:621:N_OF_BITS",
                                        "py_type": "int",
                                    }
                                ),
                                "image": PKDict(
                                    {
                                        "name": "image",
                                        "pv_base": "IMAGE",
                                        "pv_name": "OTRS:IN20:621:IMAGE",
                                        "py_type": "ndarray",
                                    }
                                ),
                                "num_cols": PKDict(
                                    {
                                        "name": "num_cols",
                                        "pv_base": "N_OF_COL",
                                        "pv_name": "OTRS:IN20:621:N_OF_COL",
                                        "py_type": "int",
                                    }
                                ),
                                "num_rols": PKDict(
                                    {
                                        "name": "num_rols",
                                        "pv_base": "N_OF_ROW",
                                        "pv_name": "OTRS:IN20:621:N_OF_ROW",
                                        "py_type": "int",
                                    }
                                ),
                            }
                        ),
                        "area": "DL1",
                        "beam_path": (
                            "CU_ALINE",
                            "CU_HTXI",
                            "CU_HXR",
                            "CU_HXTES",
                            "CU_SFTH",
                            "CU_SPEC",
                            "CU_SXR",
                        ),
                        "device_kind": "screen",
                        "device_length": 16.155,
                        "device_name": "OTR3",
                        "pv_prefix": "OTRS:IN20:621",
                    }
                ),
                "OTR4": PKDict(
                    {
                        "accessor": PKDict(
                            {
                                "acquire": PKDict(
                                    {
                                        "name": "acquire",
                                        "pv_base": "Acquire",
                                        "pv_name": "OTRS:IN20:711:Acquire",
                                        "pv_writable": True,
                                        "py_type": "bool",
                                    }
                                ),
                                "bit_depth": PKDict(
                                    {
                                        "name": "bit_depth",
                                        "pv_base": "N_OF_BITS",
                                        "pv_name": "OTRS:IN20:711:N_OF_BITS",
                                        "py_type": "int",
                                    }
                                ),
                                "image": PKDict(
                                    {
                                        "name": "image",
                                        "pv_base": "IMAGE",
                                        "pv_name": "OTRS:IN20:711:IMAGE",
                                        "py_type": "ndarray",
                                    }
                                ),
                                "num_cols": PKDict(
                                    {
                                        "name": "num_cols",
                                        "pv_base": "N_OF_COL",
                                        "pv_name": "OTRS:IN20:711:N_OF_COL",
                                        "py_type": "int",
                                    }
                                ),
                                "num_rols": PKDict(
                                    {
                                        "name": "num_rols",
                                        "pv_base": "N_OF_ROW",
                                        "pv_name": "OTRS:IN20:711:N_OF_ROW",
                                        "py_type": "int",
                                    }
                                ),
                            }
                        ),
                        "area": "DL1",
                        "beam_path": (
                            "CU_ALINE",
                            "CU_HTXI",
                            "CU_HXR",
                            "CU_HXTES",
                            "CU_SFTH",
                            "CU_SXR",
                        ),
                        "device_kind": "screen",
                        "device_length": 17.797,
                        "device_name": "OTR4",
                        "pv_prefix": "OTRS:IN20:711",
                    }
                ),
                "OTRC006": PKDict(
                    {
                        "accessor": PKDict(
                            {
                                "acquire": PKDict(
                                    {
                                        "name": "acquire",
                                        "pv_base": "Acquire",
                                        "pv_name": "PROF:COL0:535:Acquire",
                                        "pv_writable": True,
                                        "py_type": "bool",
                                    }
                                ),
                                "bit_depth": PKDict(
                                    {
                                        "name": "bit_depth",
                                        "pv_base": "N_OF_BITS",
                                        "pv_name": "PROF:COL0:535:N_OF_BITS",
                                        "py_type": "int",
                                    }
                                ),
                                "image": PKDict(
                                    {
                                        "name": "image",
                                        "pv_base": "Image:ArrayData",
                                        "pv_name": "PROF:COL0:535:Image:ArrayData",
                                        "py_type": "ndarray",
                                    }
                                ),
                                "num_cols": PKDict(
                                    {
                                        "name": "num_cols",
                                        "pv_base": "Image:ArraySize1_RBV",
                                        "pv_name": "PROF:COL0:535:Image:ArraySize1_RBV",
                                        "py_type": "int",
                                    }
                                ),
                                "num_rows": PKDict(
                                    {
                                        "name": "num_rows",
                                        "pv_base": "Image:ArraySize0_RBV",
                                        "pv_name": "PROF:COL0:535:Image:ArraySize0_RBV",
                                        "py_type": "int",
                                    }
                                ),
                            }
                        ),
                        "area": "COL0",
                        "beam_path": (
                            "SC_BSYD",
                            "SC_DASEL",
                            "SC_HXR",
                            "SC_S2_X",
                            "SC_SFTS",
                            "SC_STMO",
                            "SC_STXI",
                            "SC_SXR",
                        ),
                        "device_kind": "screen",
                        "device_length": 63.199,
                        "device_name": "OTRC006",
                        "pv_prefix": "PROF:COL0:535",
                    }
                ),
                "OTRDG02": PKDict(
                    {
                        "accessor": PKDict(
                            {
                                "acquire": PKDict(
                                    {
                                        "name": "acquire",
                                        "pv_base": "Acquire",
                                        "pv_name": "OTRS:DIAG0:420:Acquire",
                                        "pv_writable": True,
                                        "py_type": "bool",
                                    }
                                ),
                                "bit_depth": PKDict(
                                    {
                                        "name": "bit_depth",
                                        "pv_base": "N_OF_BITS",
                                        "pv_name": "OTRS:DIAG0:420:N_OF_BITS",
                                        "py_type": "int",
                                    }
                                ),
                                "image": PKDict(
                                    {
                                        "name": "image",
                                        "pv_base": "Image:ArrayData",
                                        "pv_name": "OTRS:DIAG0:420:Image:ArrayData",
                                        "py_type": "ndarray",
                                    }
                                ),
                                "num_cols": PKDict(
                                    {
                                        "name": "num_cols",
                                        "pv_base": "Image:ArraySize1_RBV",
                                        "pv_name": "OTRS:DIAG0:420:Image:ArraySize1_RBV",
                                        "py_type": "int",
                                    }
                                ),
                                "num_rows": PKDict(
                                    {
                                        "name": "num_rows",
                                        "pv_base": "Image:ArraySize0_RBV",
                                        "pv_name": "OTRS:DIAG0:420:Image:ArraySize0_RBV",
                                        "py_type": "int",
                                    }
                                ),
                            }
                        ),
                        "area": "DIAG0",
                        "beam_path": ("SC_DIAG0",),
                        "device_kind": "screen",
                        "device_length": 56.813,
                        "device_name": "OTRDG02",
                        "pv_prefix": "OTRS:DIAG0:420",
                    }
                ),
                "OTRDG04": PKDict(
                    {
                        "accessor": PKDict(
                            {
                                "acquire": PKDict(
                                    {
                                        "name": "acquire",
                                        "pv_base": "Acquire",
                                        "pv_name": "OTRS:DIAG0:525:Acquire",
                                        "pv_writable": True,
                                        "py_type": "bool",
                                    }
                                ),
                                "bit_depth": PKDict(
                                    {
                                        "name": "bit_depth",
                                        "pv_base": "N_OF_BITS",
                                        "pv_name": "OTRS:DIAG0:525:N_OF_BITS",
                                        "py_type": "int",
                                    }
                                ),
                                "image": PKDict(
                                    {
                                        "name": "image",
                                        "pv_base": "Image:ArrayData",
                                        "pv_name": "OTRS:DIAG0:525:Image:ArrayData",
                                        "py_type": "ndarray",
                                    }
                                ),
                                "num_cols": PKDict(
                                    {
                                        "name": "num_cols",
                                        "pv_base": "Image:ArraySize1_RBV",
                                        "pv_name": "OTRS:DIAG0:525:Image:ArraySize1_RBV",
                                        "py_type": "int",
                                    }
                                ),
                                "num_rows": PKDict(
                                    {
                                        "name": "num_rows",
                                        "pv_base": "Image:ArraySize0_RBV",
                                        "pv_name": "OTRS:DIAG0:525:Image:ArraySize0_RBV",
                                        "py_type": "int",
                                    }
                                ),
                            }
                        ),
                        "area": "DIAG0",
                        "beam_path": ("SC_DIAG0",),
                        "device_kind": "screen",
                        "device_length": 61.871,
                        "device_name": "OTRDG04",
                        "pv_prefix": "OTRS:DIAG0:525",
                    }
                ),
                "OTRDMP": PKDict(
                    {
                        "accessor": PKDict(
                            {
                                "acquire": PKDict(
                                    {
                                        "name": "acquire",
                                        "pv_base": "Acquire",
                                        "pv_name": "OTRS:DMPH:695:Acquire",
                                        "pv_writable": True,
                                        "py_type": "bool",
                                    }
                                ),
                                "bit_depth": PKDict(
                                    {
                                        "name": "bit_depth",
                                        "pv_base": "N_OF_BITS",
                                        "pv_name": "OTRS:DMPH:695:N_OF_BITS",
                                        "py_type": "int",
                                    }
                                ),
                                "image": PKDict(
                                    {
                                        "name": "image",
                                        "pv_base": "Image:ArrayData",
                                        "pv_name": "OTRS:DMPH:695:Image:ArrayData",
                                        "py_type": "ndarray",
                                    }
                                ),
                                "num_cols": PKDict(
                                    {
                                        "name": "num_cols",
                                        "pv_base": "Image:ArraySize1_RBV",
                                        "pv_name": "OTRS:DMPH:695:Image:ArraySize1_RBV",
                                        "py_type": "int",
                                    }
                                ),
                                "num_rows": PKDict(
                                    {
                                        "name": "num_rows",
                                        "pv_base": "Image:ArraySize0_RBV",
                                        "pv_name": "OTRS:DMPH:695:Image:ArraySize0_RBV",
                                        "py_type": "int",
                                    }
                                ),
                            }
                        ),
                        "area": "DMPH",
                        "beam_path": ("CU_HXR", "SC_HXR"),
                        "device_kind": "screen",
                        "device_length": 1746.602,
                        "device_name": "OTRDMP",
                        "pv_prefix": "OTRS:DMPH:695",
                    }
                ),
                "OTRDMPB": PKDict(
                    {
                        "accessor": PKDict(
                            {
                                "acquire": PKDict(
                                    {
                                        "name": "acquire",
                                        "pv_base": "Acquire",
                                        "pv_name": "OTRS:DMPS:695:Acquire",
                                        "pv_writable": True,
                                        "py_type": "bool",
                                    }
                                ),
                                "bit_depth": PKDict(
                                    {
                                        "name": "bit_depth",
                                        "pv_base": "N_OF_BITS",
                                        "pv_name": "OTRS:DMPS:695:N_OF_BITS",
                                        "py_type": "int",
                                    }
                                ),
                                "image": PKDict(
                                    {
                                        "name": "image",
                                        "pv_base": "Image:ArrayData",
                                        "pv_name": "OTRS:DMPS:695:Image:ArrayData",
                                        "py_type": "ndarray",
                                    }
                                ),
                                "num_cols": PKDict(
                                    {
                                        "name": "num_cols",
                                        "pv_base": "Image:ArraySize1_RBV",
                                        "pv_name": "OTRS:DMPS:695:Image:ArraySize1_RBV",
                                        "py_type": "int",
                                    }
                                ),
                                "num_rows": PKDict(
                                    {
                                        "name": "num_rows",
                                        "pv_base": "Image:ArraySize0_RBV",
                                        "pv_name": "OTRS:DMPS:695:Image:ArraySize0_RBV",
                                        "py_type": "int",
                                    }
                                ),
                            }
                        ),
                        "area": "DMPS",
                        "beam_path": ("CU_SXR", "SC_SXR"),
                        "device_kind": "screen",
                        "device_length": 3771.399,
                        "device_name": "OTRDMPB",
                        "pv_prefix": "OTRS:DMPS:695",
                    }
                ),
                "OTRDOG": PKDict(
                    {
                        "accessor": PKDict(
                            {
                                "acquire": PKDict(
                                    {
                                        "name": "acquire",
                                        "pv_base": "Acquire",
                                        "pv_name": "PROF:DOG:195:Acquire",
                                        "pv_writable": True,
                                        "py_type": "bool",
                                    }
                                ),
                                "bit_depth": PKDict(
                                    {
                                        "name": "bit_depth",
                                        "pv_base": "N_OF_BITS",
                                        "pv_name": "PROF:DOG:195:N_OF_BITS",
                                        "py_type": "int",
                                    }
                                ),
                                "image": PKDict(
                                    {
                                        "name": "image",
                                        "pv_base": "Image:ArrayData",
                                        "pv_name": "PROF:DOG:195:Image:ArrayData",
                                        "py_type": "ndarray",
                                    }
                                ),
                                "num_cols": PKDict(
                                    {
                                        "name": "num_cols",
                                        "pv_base": "Image:ArraySize1_RBV",
                                        "pv_name": "PROF:DOG:195:Image:ArraySize1_RBV",
                                        "py_type": "int",
                                    }
                                ),
                                "num_rows": PKDict(
                                    {
                                        "name": "num_rows",
                                        "pv_base": "Image:ArraySize0_RBV",
                                        "pv_name": "PROF:DOG:195:Image:ArraySize0_RBV",
                                        "py_type": "int",
                                    }
                                ),
                            }
                        ),
                        "area": "DOG",
                        "beam_path": (
                            "SC_BSYD",
                            "SC_DASEL",
                            "SC_HXR",
                            "SC_S2_X",
                            "SC_SFTS",
                            "SC_STMO",
                            "SC_STXI",
                            "SC_SXR",
                        ),
                        "device_kind": "screen",
                        "device_length": 729.924,
                        "device_name": "OTRDOG",
                        "pv_prefix": "PROF:DOG:195",
                    }
                ),
                "OTRH1": PKDict(
                    {
                        "accessor": PKDict(
                            {
                                "acquire": PKDict(
                                    {
                                        "name": "acquire",
                                        "pv_base": "Acquire",
                                        "pv_name": "OTRS:IN20:465:Acquire",
                                        "pv_writable": True,
                                        "py_type": "bool",
                                    }
                                ),
                                "bit_depth": PKDict(
                                    {
                                        "name": "bit_depth",
                                        "pv_base": "N_OF_BITS",
                                        "pv_name": "OTRS:IN20:465:N_OF_BITS",
                                        "py_type": "int",
                                    }
                                ),
                                "image": PKDict(
                                    {
                                        "name": "image",
                                        "pv_base": "Image:ArrayData",
                                        "pv_name": "OTRS:IN20:465:Image:ArrayData",
                                        "py_type": "ndarray",
                                    }
                                ),
                                "num_cols": PKDict(
                                    {
                                        "name": "num_cols",
                                        "pv_base": "Image:ArraySize1_RBV",
                                        "pv_name": "OTRS:IN20:465:Image:ArraySize1_RBV",
                                        "py_type": "int",
                                    }
                                ),
                                "num_rows": PKDict(
                                    {
                                        "name": "num_rows",
                                        "pv_base": "Image:ArraySize0_RBV",
                                        "pv_name": "OTRS:IN20:465:Image:ArraySize0_RBV",
                                        "py_type": "int",
                                    }
                                ),
                            }
                        ),
                        "area": "DL1",
                        "beam_path": (
                            "CU_ALINE",
                            "CU_HTXI",
                            "CU_HXR",
                            "CU_HXTES",
                            "CU_SFTH",
                            "CU_SPEC",
                            "CU_SXR",
                        ),
                        "device_kind": "screen",
                        "device_length": 9.528,
                        "device_name": "OTRH1",
                        "pv_prefix": "OTRS:IN20:465",
                    }
                ),
                "OTRH2": PKDict(
                    {
                        "accessor": PKDict(
                            {
                                "acquire": PKDict(
                                    {
                                        "name": "acquire",
                                        "pv_base": "Acquire",
                                        "pv_name": "OTRS:IN20:471:Acquire",
                                        "pv_writable": True,
                                        "py_type": "bool",
                                    }
                                ),
                                "bit_depth": PKDict(
                                    {
                                        "name": "bit_depth",
                                        "pv_base": "N_OF_BITS",
                                        "pv_name": "OTRS:IN20:471:N_OF_BITS",
                                        "py_type": "int",
                                    }
                                ),
                                "image": PKDict(
                                    {
                                        "name": "image",
                                        "pv_base": "Image:ArrayData",
                                        "pv_name": "OTRS:IN20:471:Image:ArrayData",
                                        "py_type": "ndarray",
                                    }
                                ),
                                "num_cols": PKDict(
                                    {
                                        "name": "num_cols",
                                        "pv_base": "Image:ArraySize1_RBV",
                                        "pv_name": "OTRS:IN20:471:Image:ArraySize1_RBV",
                                        "py_type": "int",
                                    }
                                ),
                                "num_rows": PKDict(
                                    {
                                        "name": "num_rows",
                                        "pv_base": "Image:ArraySize0_RBV",
                                        "pv_name": "OTRS:IN20:471:Image:ArraySize0_RBV",
                                        "py_type": "int",
                                    }
                                ),
                            }
                        ),
                        "area": "DL1",
                        "beam_path": (
                            "CU_ALINE",
                            "CU_HTXI",
                            "CU_HXR",
                            "CU_HXTES",
                            "CU_SFTH",
                            "CU_SPEC",
                            "CU_SXR",
                        ),
                        "device_kind": "screen",
                        "device_length": 10.211,
                        "device_name": "OTRH2",
                        "pv_prefix": "OTRS:IN20:471",
                    }
                ),
                "PRDAS12": PKDict(
                    {
                        "accessor": PKDict(
                            {
                                "acquire": PKDict(
                                    {
                                        "name": "acquire",
                                        "pv_base": "Acquire",
                                        "pv_name": "PROF:DASEL:440:Acquire",
                                        "pv_writable": True,
                                        "py_type": "bool",
                                    }
                                ),
                                "bit_depth": PKDict(
                                    {
                                        "name": "bit_depth",
                                        "pv_base": "N_OF_BITS",
                                        "pv_name": "PROF:DASEL:440:N_OF_BITS",
                                        "py_type": "int",
                                    }
                                ),
                                "image": PKDict(
                                    {
                                        "name": "image",
                                        "pv_base": "Image:ArrayData",
                                        "pv_name": "PROF:DASEL:440:Image:ArrayData",
                                        "py_type": "ndarray",
                                    }
                                ),
                                "num_cols": PKDict(
                                    {
                                        "name": "num_cols",
                                        "pv_base": "Image:ArraySize1_RBV",
                                        "pv_name": "PROF:DASEL:440:Image:ArraySize1_RBV",
                                        "py_type": "int",
                                    }
                                ),
                                "num_rows": PKDict(
                                    {
                                        "name": "num_rows",
                                        "pv_base": "Image:ArraySize0_RBV",
                                        "pv_name": "PROF:DASEL:440:Image:ArraySize0_RBV",
                                        "py_type": "int",
                                    }
                                ),
                            }
                        ),
                        "area": "DASEL",
                        "beam_path": ("SC_DASEL",),
                        "device_kind": "screen",
                        "device_length": 3014.49,
                        "device_name": "PRDAS12",
                        "pv_prefix": "PROF:DASEL:440",
                    }
                ),
                "PRDAS14": PKDict(
                    {
                        "accessor": PKDict(
                            {
                                "acquire": PKDict(
                                    {
                                        "name": "acquire",
                                        "pv_base": "Acquire",
                                        "pv_name": "PROF:DASEL:655:Acquire",
                                        "pv_writable": True,
                                        "py_type": "bool",
                                    }
                                ),
                                "bit_depth": PKDict(
                                    {
                                        "name": "bit_depth",
                                        "pv_base": "N_OF_BITS",
                                        "pv_name": "PROF:DASEL:655:N_OF_BITS",
                                        "py_type": "int",
                                    }
                                ),
                                "image": PKDict(
                                    {
                                        "name": "image",
                                        "pv_base": "Image:ArrayData",
                                        "pv_name": "PROF:DASEL:655:Image:ArrayData",
                                        "py_type": "ndarray",
                                    }
                                ),
                                "num_cols": PKDict(
                                    {
                                        "name": "num_cols",
                                        "pv_base": "Image:ArraySize1_RBV",
                                        "pv_name": "PROF:DASEL:655:Image:ArraySize1_RBV",
                                        "py_type": "int",
                                    }
                                ),
                                "num_rows": PKDict(
                                    {
                                        "name": "num_rows",
                                        "pv_base": "Image:ArraySize0_RBV",
                                        "pv_name": "PROF:DASEL:655:Image:ArraySize0_RBV",
                                        "py_type": "int",
                                    }
                                ),
                            }
                        ),
                        "area": "DASEL",
                        "beam_path": ("SC_DASEL",),
                        "device_kind": "screen",
                        "device_length": 3073.484,
                        "device_name": "PRDAS14",
                        "pv_prefix": "PROF:DASEL:655",
                    }
                ),
                "PRDAS17": PKDict(
                    {
                        "accessor": PKDict(
                            {
                                "acquire": PKDict(
                                    {
                                        "name": "acquire",
                                        "pv_base": "Acquire",
                                        "pv_name": "PROF:DASEL:818:Acquire",
                                        "pv_writable": True,
                                        "py_type": "bool",
                                    }
                                ),
                                "bit_depth": PKDict(
                                    {
                                        "name": "bit_depth",
                                        "pv_base": "N_OF_BITS",
                                        "pv_name": "PROF:DASEL:818:N_OF_BITS",
                                        "py_type": "int",
                                    }
                                ),
                                "image": PKDict(
                                    {
                                        "name": "image",
                                        "pv_base": "Image:ArrayData",
                                        "pv_name": "PROF:DASEL:818:Image:ArrayData",
                                        "py_type": "ndarray",
                                    }
                                ),
                                "num_cols": PKDict(
                                    {
                                        "name": "num_cols",
                                        "pv_base": "Image:ArraySize1_RBV",
                                        "pv_name": "PROF:DASEL:818:Image:ArraySize1_RBV",
                                        "py_type": "int",
                                    }
                                ),
                                "num_rows": PKDict(
                                    {
                                        "name": "num_rows",
                                        "pv_base": "Image:ArraySize0_RBV",
                                        "pv_name": "PROF:DASEL:818:Image:ArraySize0_RBV",
                                        "py_type": "int",
                                    }
                                ),
                            }
                        ),
                        "area": "DASEL",
                        "beam_path": ("SC_DASEL",),
                        "device_kind": "screen",
                        "device_length": 3118.053,
                        "device_name": "PRDAS17",
                        "pv_prefix": "PROF:DASEL:818",
                    }
                ),
                "VCC": PKDict(
                    {
                        "accessor": PKDict(
                            {
                                "acquire": PKDict(
                                    {
                                        "name": "acquire",
                                        "pv_base": "Acquire",
                                        "pv_name": "CAMR:IN20:186:Acquire",
                                        "pv_writable": True,
                                        "py_type": "bool",
                                    }
                                ),
                                "bit_depth": PKDict(
                                    {
                                        "name": "bit_depth",
                                        "pv_base": "N_OF_BITS",
                                        "pv_name": "CAMR:IN20:186:N_OF_BITS",
                                        "py_type": "int",
                                    }
                                ),
                                "image": PKDict(
                                    {
                                        "name": "image",
                                        "pv_base": "IMAGE",
                                        "pv_name": "CAMR:IN20:186:IMAGE",
                                        "py_type": "ndarray",
                                    }
                                ),
                                "num_cols": PKDict(
                                    {
                                        "name": "num_cols",
                                        "pv_base": "N_OF_COL",
                                        "pv_name": "CAMR:IN20:186:N_OF_COL",
                                        "py_type": "int",
                                    }
                                ),
                                "num_rols": PKDict(
                                    {
                                        "name": "num_rols",
                                        "pv_base": "N_OF_ROW",
                                        "pv_name": "CAMR:IN20:186:N_OF_ROW",
                                        "py_type": "int",
                                    }
                                ),
                            }
                        ),
                        "area": "GUN",
                        "beam_path": ("CU_HXR", "CU_SXR"),
                        "device_kind": "screen",
                        "device_length": 0.0,
                        "device_name": "VCC",
                        "pv_prefix": "CAMR:IN20:186",
                    }
                ),
                "VCCB": PKDict(
                    {
                        "accessor": PKDict(
                            {
                                "acquire": PKDict(
                                    {
                                        "name": "acquire",
                                        "pv_base": "Acquire",
                                        "pv_name": "CAMR:LGUN:950:Acquire",
                                        "pv_writable": True,
                                        "py_type": "bool",
                                    }
                                ),
                                "bit_depth": PKDict(
                                    {
                                        "name": "bit_depth",
                                        "pv_base": "N_OF_BITS",
                                        "pv_name": "CAMR:LGUN:950:N_OF_BITS",
                                        "py_type": "int",
                                    }
                                ),
                                "image": PKDict(
                                    {
                                        "name": "image",
                                        "pv_base": "Image:ArrayData",
                                        "pv_name": "CAMR:LGUN:950:Image:ArrayData",
                                        "py_type": "ndarray",
                                    }
                                ),
                                "num_cols": PKDict(
                                    {
                                        "name": "num_cols",
                                        "pv_base": "Image:ArraySizeY_RBV",
                                        "pv_name": "CAMR:LGUN:950:Image:ArraySizeY_RBV",
                                        "py_type": "int",
                                    }
                                ),
                                "num_rows": PKDict(
                                    {
                                        "name": "num_rows",
                                        "pv_base": "Image:ArraySizeX_RBV",
                                        "pv_name": "CAMR:LGUN:950:Image:ArraySizeX_RBV",
                                        "py_type": "int",
                                    }
                                ),
                            }
                        ),
                        "area": "GUNB",
                        "beam_path": ("SC_DIAG0", "SC_HXR", "SC_SXR"),
                        "device_kind": "screen",
                        "device_length": 0.0,
                        "device_name": "VCCB",
                        "pv_prefix": "CAMR:LGUN:950",
                    }
                ),
                "YAG01": PKDict(
                    {
                        "accessor": PKDict(
                            {
                                "acquire": PKDict(
                                    {
                                        "name": "acquire",
                                        "pv_base": "Acquire",
                                        "pv_name": "YAGS:IN20:211:Acquire",
                                        "pv_writable": True,
                                        "py_type": "bool",
                                    }
                                ),
                                "bit_depth": PKDict(
                                    {
                                        "name": "bit_depth",
                                        "pv_base": "N_OF_BITS",
                                        "pv_name": "YAGS:IN20:211:N_OF_BITS",
                                        "py_type": "int",
                                    }
                                ),
                                "image": PKDict(
                                    {
                                        "name": "image",
                                        "pv_base": "IMAGE",
                                        "pv_name": "YAGS:IN20:211:IMAGE",
                                        "py_type": "ndarray",
                                    }
                                ),
                                "num_cols": PKDict(
                                    {
                                        "name": "num_cols",
                                        "pv_base": "N_OF_COL",
                                        "pv_name": "YAGS:IN20:211:N_OF_COL",
                                        "py_type": "int",
                                    }
                                ),
                                "num_rols": PKDict(
                                    {
                                        "name": "num_rols",
                                        "pv_base": "N_OF_ROW",
                                        "pv_name": "YAGS:IN20:211:N_OF_ROW",
                                        "py_type": "int",
                                    }
                                ),
                            }
                        ),
                        "area": "GUN",
                        "beam_path": (
                            "CU_ALINE",
                            "CU_GSPEC",
                            "CU_HTXI",
                            "CU_HXR",
                            "CU_HXTES",
                            "CU_SFTH",
                            "CU_SPEC",
                            "CU_SXR",
                        ),
                        "device_kind": "screen",
                        "device_length": 0.614,
                        "device_name": "YAG01",
                        "pv_prefix": "YAGS:IN20:211",
                    }
                ),
                "YAG02": PKDict(
                    {
                        "accessor": PKDict(
                            {
                                "acquire": PKDict(
                                    {
                                        "name": "acquire",
                                        "pv_base": "Acquire",
                                        "pv_name": "YAGS:IN20:241:Acquire",
                                        "pv_writable": True,
                                        "py_type": "bool",
                                    }
                                ),
                                "bit_depth": PKDict(
                                    {
                                        "name": "bit_depth",
                                        "pv_base": "N_OF_BITS",
                                        "pv_name": "YAGS:IN20:241:N_OF_BITS",
                                        "py_type": "int",
                                    }
                                ),
                                "image": PKDict(
                                    {
                                        "name": "image",
                                        "pv_base": "Image:ArrayData",
                                        "pv_name": "YAGS:IN20:241:Image:ArrayData",
                                        "py_type": "ndarray",
                                    }
                                ),
                                "num_cols": PKDict(
                                    {
                                        "name": "num_cols",
                                        "pv_base": "Image:ArraySize1_RBV",
                                        "pv_name": "YAGS:IN20:241:Image:ArraySize1_RBV",
                                        "py_type": "int",
                                    }
                                ),
                                "num_rows": PKDict(
                                    {
                                        "name": "num_rows",
                                        "pv_base": "Image:ArraySize0_RBV",
                                        "pv_name": "YAGS:IN20:241:Image:ArraySize0_RBV",
                                        "py_type": "int",
                                    }
                                ),
                            }
                        ),
                        "area": "L0",
                        "beam_path": (
                            "CU_ALINE",
                            "CU_HTXI",
                            "CU_HXR",
                            "CU_HXTES",
                            "CU_SFTH",
                            "CU_SPEC",
                            "CU_SXR",
                        ),
                        "device_kind": "screen",
                        "device_length": 1.388,
                        "device_name": "YAG02",
                        "pv_prefix": "YAGS:IN20:241",
                    }
                ),
                "YAG03": PKDict(
                    {
                        "accessor": PKDict(
                            {
                                "acquire": PKDict(
                                    {
                                        "name": "acquire",
                                        "pv_base": "Acquire",
                                        "pv_name": "YAGS:IN20:351:Acquire",
                                        "pv_writable": True,
                                        "py_type": "bool",
                                    }
                                ),
                                "bit_depth": PKDict(
                                    {
                                        "name": "bit_depth",
                                        "pv_base": "N_OF_BITS",
                                        "pv_name": "YAGS:IN20:351:N_OF_BITS",
                                        "py_type": "int",
                                    }
                                ),
                                "image": PKDict(
                                    {
                                        "name": "image",
                                        "pv_base": "IMAGE",
                                        "pv_name": "YAGS:IN20:351:IMAGE",
                                        "py_type": "ndarray",
                                    }
                                ),
                                "num_cols": PKDict(
                                    {
                                        "name": "num_cols",
                                        "pv_base": "N_OF_COL",
                                        "pv_name": "YAGS:IN20:351:N_OF_COL",
                                        "py_type": "int",
                                    }
                                ),
                                "num_rols": PKDict(
                                    {
                                        "name": "num_rols",
                                        "pv_base": "N_OF_ROW",
                                        "pv_name": "YAGS:IN20:351:N_OF_ROW",
                                        "py_type": "int",
                                    }
                                ),
                            }
                        ),
                        "area": "L0",
                        "beam_path": (
                            "CU_ALINE",
                            "CU_HTXI",
                            "CU_HXR",
                            "CU_HXTES",
                            "CU_SFTH",
                            "CU_SPEC",
                            "CU_SXR",
                        ),
                        "device_kind": "screen",
                        "device_length": 4.615,
                        "device_name": "YAG03",
                        "pv_prefix": "YAGS:IN20:351",
                    }
                ),
                "YAGG1": PKDict(
                    {
                        "accessor": PKDict(
                            {
                                "acquire": PKDict(
                                    {
                                        "name": "acquire",
                                        "pv_base": "Acquire",
                                        "pv_name": "YAGS:IN20:841:Acquire",
                                        "pv_writable": True,
                                        "py_type": "bool",
                                    }
                                ),
                                "bit_depth": PKDict(
                                    {
                                        "name": "bit_depth",
                                        "pv_base": "N_OF_BITS",
                                        "pv_name": "YAGS:IN20:841:N_OF_BITS",
                                        "py_type": "int",
                                    }
                                ),
                                "image": PKDict(
                                    {
                                        "name": "image",
                                        "pv_base": "IMAGE",
                                        "pv_name": "YAGS:IN20:841:IMAGE",
                                        "py_type": "ndarray",
                                    }
                                ),
                                "num_cols": PKDict(
                                    {
                                        "name": "num_cols",
                                        "pv_base": "N_OF_COL",
                                        "pv_name": "YAGS:IN20:841:N_OF_COL",
                                        "py_type": "int",
                                    }
                                ),
                                "num_rols": PKDict(
                                    {
                                        "name": "num_rols",
                                        "pv_base": "N_OF_ROW",
                                        "pv_name": "YAGS:IN20:841:N_OF_ROW",
                                        "py_type": "int",
                                    }
                                ),
                            }
                        ),
                        "area": "GSPEC",
                        "beam_path": ("CU_GSPEC",),
                        "device_kind": "screen",
                        "device_length": 1.839,
                        "device_name": "YAGG1",
                        "pv_prefix": "YAGS:IN20:841",
                    }
                ),
                "YAGH1": PKDict(
                    {
                        "accessor": PKDict(
                            {
                                "acquire": PKDict(
                                    {
                                        "name": "acquire",
                                        "pv_base": "Acquire",
                                        "pv_name": "YAGS:HTR:625:Acquire",
                                        "pv_writable": True,
                                        "py_type": "bool",
                                    }
                                ),
                                "bit_depth": PKDict(
                                    {
                                        "name": "bit_depth",
                                        "pv_base": "N_OF_BITS",
                                        "pv_name": "YAGS:HTR:625:N_OF_BITS",
                                        "py_type": "int",
                                    }
                                ),
                                "image": PKDict(
                                    {
                                        "name": "image",
                                        "pv_base": "Image:ArrayData",
                                        "pv_name": "YAGS:HTR:625:Image:ArrayData",
                                        "py_type": "ndarray",
                                    }
                                ),
                                "num_cols": PKDict(
                                    {
                                        "name": "num_cols",
                                        "pv_base": "Image:ArraySize1_RBV",
                                        "pv_name": "YAGS:HTR:625:Image:ArraySize1_RBV",
                                        "py_type": "int",
                                    }
                                ),
                                "num_rows": PKDict(
                                    {
                                        "name": "num_rows",
                                        "pv_base": "Image:ArraySize0_RBV",
                                        "pv_name": "YAGS:HTR:625:Image:ArraySize0_RBV",
                                        "py_type": "int",
                                    }
                                ),
                            }
                        ),
                        "area": "HTR",
                        "beam_path": (
                            "SC_BSYD",
                            "SC_DASEL",
                            "SC_DIAG0",
                            "SC_HXR",
                            "SC_S2_X",
                            "SC_SFTS",
                            "SC_STMO",
                            "SC_STXI",
                            "SC_SXR",
                        ),
                        "device_kind": "screen",
                        "device_length": 32.253,
                        "device_name": "YAGH1",
                        "pv_prefix": "YAGS:HTR:625",
                    }
                ),
                "YAGH2": PKDict(
                    {
                        "accessor": PKDict(
                            {
                                "acquire": PKDict(
                                    {
                                        "name": "acquire",
                                        "pv_base": "Acquire",
                                        "pv_name": "YAGS:HTR:675:Acquire",
                                        "pv_writable": True,
                                        "py_type": "bool",
                                    }
                                ),
                                "bit_depth": PKDict(
                                    {
                                        "name": "bit_depth",
                                        "pv_base": "N_OF_BITS",
                                        "pv_name": "YAGS:HTR:675:N_OF_BITS",
                                        "py_type": "int",
                                    }
                                ),
                                "image": PKDict(
                                    {
                                        "name": "image",
                                        "pv_base": "Image:ArrayData",
                                        "pv_name": "YAGS:HTR:675:Image:ArrayData",
                                        "py_type": "ndarray",
                                    }
                                ),
                                "num_cols": PKDict(
                                    {
                                        "name": "num_cols",
                                        "pv_base": "Image:ArraySize1_RBV",
                                        "pv_name": "YAGS:HTR:675:Image:ArraySize1_RBV",
                                        "py_type": "int",
                                    }
                                ),
                                "num_rows": PKDict(
                                    {
                                        "name": "num_rows",
                                        "pv_base": "Image:ArraySize0_RBV",
                                        "pv_name": "YAGS:HTR:675:Image:ArraySize0_RBV",
                                        "py_type": "int",
                                    }
                                ),
                            }
                        ),
                        "area": "HTR",
                        "beam_path": (
                            "SC_BSYD",
                            "SC_DASEL",
                            "SC_DIAG0",
                            "SC_HXR",
                            "SC_S2_X",
                            "SC_SFTS",
                            "SC_STMO",
                            "SC_STXI",
                            "SC_SXR",
                        ),
                        "device_kind": "screen",
                        "device_length": 33.311,
                        "device_name": "YAGH2",
                        "pv_prefix": "YAGS:HTR:675",
                    }
                ),
                "YAGPSI": PKDict(
                    {
                        "accessor": PKDict(
                            {
                                "acquire": PKDict(
                                    {
                                        "name": "acquire",
                                        "pv_base": "Acquire",
                                        "pv_name": "YAGS:LTUH:743:Acquire",
                                        "pv_writable": True,
                                        "py_type": "bool",
                                    }
                                ),
                                "bit_depth": PKDict(
                                    {
                                        "name": "bit_depth",
                                        "pv_base": "N_OF_BITS",
                                        "pv_name": "YAGS:LTUH:743:N_OF_BITS",
                                        "py_type": "int",
                                    }
                                ),
                                "image": PKDict(
                                    {
                                        "name": "image",
                                        "pv_base": "Image:ArrayData",
                                        "pv_name": "YAGS:LTUH:743:Image:ArrayData",
                                        "py_type": "ndarray",
                                    }
                                ),
                                "num_cols": PKDict(
                                    {
                                        "name": "num_cols",
                                        "pv_base": "Image:ArraySize1_RBV",
                                        "pv_name": "YAGS:LTUH:743:Image:ArraySize1_RBV",
                                        "py_type": "int",
                                    }
                                ),
                                "num_rows": PKDict(
                                    {
                                        "name": "num_rows",
                                        "pv_base": "Image:ArraySize0_RBV",
                                        "pv_name": "YAGS:LTUH:743:Image:ArraySize0_RBV",
                                        "py_type": "int",
                                    }
                                ),
                            }
                        ),
                        "area": "LTUH",
                        "beam_path": (
                            "CU_HTXI",
                            "CU_HXR",
                            "CU_HXTES",
                            "CU_SFTH",
                            "SC_HXR",
                        ),
                        "device_kind": "screen",
                        "device_length": 1461.796,
                        "device_name": "YAGPSI",
                        "pv_prefix": "YAGS:LTUH:743",
                    }
                ),
                "YAGS1": PKDict(
                    {
                        "accessor": PKDict(
                            {
                                "acquire": PKDict(
                                    {
                                        "name": "acquire",
                                        "pv_base": "Acquire",
                                        "pv_name": "YAGS:IN20:921:Acquire",
                                        "pv_writable": True,
                                        "py_type": "bool",
                                    }
                                ),
                                "bit_depth": PKDict(
                                    {
                                        "name": "bit_depth",
                                        "pv_base": "N_OF_BITS",
                                        "pv_name": "YAGS:IN20:921:N_OF_BITS",
                                        "py_type": "int",
                                    }
                                ),
                                "image": PKDict(
                                    {
                                        "name": "image",
                                        "pv_base": "IMAGE",
                                        "pv_name": "YAGS:IN20:921:IMAGE",
                                        "py_type": "ndarray",
                                    }
                                ),
                                "num_cols": PKDict(
                                    {
                                        "name": "num_cols",
                                        "pv_base": "N_OF_COL",
                                        "pv_name": "YAGS:IN20:921:N_OF_COL",
                                        "py_type": "int",
                                    }
                                ),
                                "num_rols": PKDict(
                                    {
                                        "name": "num_rols",
                                        "pv_base": "N_OF_ROW",
                                        "pv_name": "YAGS:IN20:921:N_OF_ROW",
                                        "py_type": "int",
                                    }
                                ),
                            }
                        ),
                        "area": "SPEC",
                        "beam_path": ("CU_SPEC",),
                        "device_kind": "screen",
                        "device_length": 18.588,
                        "device_name": "YAGS1",
                        "pv_prefix": "YAGS:IN20:921",
                    }
                ),
                "YAGS2": PKDict(
                    {
                        "accessor": PKDict(
                            {
                                "acquire": PKDict(
                                    {
                                        "name": "acquire",
                                        "pv_base": "Acquire",
                                        "pv_name": "YAGS:IN20:995:Acquire",
                                        "pv_writable": True,
                                        "py_type": "bool",
                                    }
                                ),
                                "bit_depth": PKDict(
                                    {
                                        "name": "bit_depth",
                                        "pv_base": "N_OF_BITS",
                                        "pv_name": "YAGS:IN20:995:N_OF_BITS",
                                        "py_type": "int",
                                    }
                                ),
                                "image": PKDict(
                                    {
                                        "name": "image",
                                        "pv_base": "IMAGE",
                                        "pv_name": "YAGS:IN20:995:IMAGE",
                                        "py_type": "ndarray",
                                    }
                                ),
                                "num_cols": PKDict(
                                    {
                                        "name": "num_cols",
                                        "pv_base": "N_OF_COL",
                                        "pv_name": "YAGS:IN20:995:N_OF_COL",
                                        "py_type": "int",
                                    }
                                ),
                                "num_rols": PKDict(
                                    {
                                        "name": "num_rols",
                                        "pv_base": "N_OF_ROW",
                                        "pv_name": "YAGS:IN20:995:N_OF_ROW",
                                        "py_type": "int",
                                    }
                                ),
                            }
                        ),
                        "area": "SPEC",
                        "beam_path": ("CU_SPEC",),
                        "device_kind": "screen",
                        "device_length": 21.414,
                        "device_name": "YAGS2",
                        "pv_prefix": "YAGS:IN20:995",
                    }
                ),
            }
        ),
    }
)
