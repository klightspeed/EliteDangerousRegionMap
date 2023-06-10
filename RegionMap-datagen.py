#!/bin/env python3

from PIL import Image
from numpy import asarray
import json
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

with open('region_map_data.rs', 'wt') as f:
    f.write("pub const REGIONS: &[&str] = &[")
    f.write('\n')
    f.write('    "",\n')
    f.write(',\n'.join('    "{0}"'.format(r) for r in regions[1:]))
    f.write('\n')
    f.write('];\n')
    f.write('\n')
    f.write("pub const REGION_MAP: &[&[(i32, i32)]] = &[")
    f.write('\n')
    f.write(',\n'.join('    &[' + ','.join(repr((u, v)) for u, v in row) + ']' for row in lines))
    f.write('\n')
    f.write('];\n')
    f.write('\n')

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

with open('RegionMapData.json', 'wt') as f:
    f.write('{\n')
    f.write('    "regions": [\n')
    f.write('        {0}\n'.format(',\n        '.join(json.dumps(r) for r in regions)))
    f.write('    ],\n')
    f.write('    "regionmap": [\n');
    f.write('        {0}\n'.format(',\n        '.join(json.dumps([[int(rl), int(rv)] for rl, rv in l]) for l in lines)))
    f.write('    ]\n')
    f.write('}\n')

with open('RegionMapData.cs', 'wt') as f:
    f.write('namespace EliteDangerousRegionMap\n')
    f.write('{\n')
    f.write('    public static partial class RegionMap\n')
    f.write('    {\n')
    f.write('        private static string[] RegionNames = new[]\n')
    f.write('        {\n')
    for r in regions:
        f.write('            {0},\n'.format(json.dumps(r)))
    f.write('        };\n')
    f.write('\n')
    f.write('        private static (int, int)[][] RegionMapLines = new[]\n')
    f.write('        {\n')
    for row in lines:
        f.write('            new[]{' + ','.join(repr((l, v)) for l, v in row) + '},\n')
    f.write('        };\n')
    f.write('    }\n')
    f.write('}\n')

