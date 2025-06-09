#!/usr/bin/env python3
"""
Constants for the waste calendar extractor.
"""

# Luxembourgish month names mapping
MONTH_NAMES = [
    "JANUAR",
    "FEBRUAR",
    "MÄERZ",
    "ABRËLL",
    "MEE",
    "JUNI",
    "JULI",
    "AUGUST",
    "SEPTEMBER",
    "OKTOBER",
    "NOVEMBER",
    "DEZEMBER",
]
MONTH_NUMBERS = {month: index + 1 for index, month in enumerate(MONTH_NAMES)}

# Waste collection type keywords for detection
WASTE_TYPE_KEYWORDS = [
    "reschtoffäll",
    "déchets ménagers",
    "residual waste",
    "pabeier",
    "papier",
    "paper",
    "carton",
    "glas",
    "verre",
    "glass",
    "verpackungen",
    "emballages",
    "packaging",
    "valorlux",
    "organesch",
    "organiques",
    "organic",
    "aalt gezei",
    "vieux vêtements",
    "old clothes",
    "beemercher",
    "sapins",
    "christmas trees",
]
