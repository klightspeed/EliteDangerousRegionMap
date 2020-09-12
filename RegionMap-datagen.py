#!/bin/env python3

from PIL import Image
from numpy import asarray
regionmap = asarray(Image.open('RegionMap.png'))
region1 = 42 * 4

regions = [
    None,
    "Galactic Centre",
    "Empyrean Straits",
    "Ryker's Hope",
    "Odin's Hold",
    "Norma Arm",
    "Arcadian Stream",
    "Izanami",
    "Inner Orion-Perseus Conflux",
    "Inner Scutum-Centaurus Arm",
    "Norma Expanse",
    "Trojan Belt",
    "The Veils",
    "Newton's Vault",
    "The Conduit",
    "Outer Orion-Perseus Conflux",
    "Orion-Cygnus Arm",
    "Temple",
    "Inner Orion Spur",
    "Hawking's Gap",
    "Dryman's Point",
    "Sagittarius-Carina Arm",
    "Mare Somnia",
    "Acheron",
    "Formorian Frontier",
    "Hieronymus Delta",
    "Outer Scutum-Centaurus Arm",
    "Outer Arm",
    "Aquila's Halo",
    "Errant Marches",
    "Perseus Arm",
    "Formidine Rift",
    "Vulcan Gate",
    "Elysian Shore",
    "Sanguineous Rim",
    "Outer Orion Spur",
    "Achilles's Altar",
    "Xibalba",
    "Lyra's Song",
    "Tenebrae",
    "The Abyss",
    "Kepler's Crest",
    "The Void"
]

lines = []
for l in regionmap[::-1]:
    rle = []
    p = 0
    n = 0
    for px in l:
        px = 0 if px == 0 else (region1 - px) // 4 + 1
        if px != p:
            rle.append((n, p))
            p = px
            n = 1
        else:
            n += 1
    rle.append((n, p))
    lines.append(rle)
with open('RegionMapData.py', 'wt') as f:
    f.write('#!/bin/env python3\n')
    f.write('\n')
    f.write('regions = [\n')
    for r in regions:
        f.write('    {0},\n'.format(repr(r)))
    f.write(']\n')
    f.write('\n')
    f.write('regionmap = [\n')
    for l in lines:
        f.write('    {0},\n'.format(repr(l)))
    f.write(']\n')
    f.write('\n')

