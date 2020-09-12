#!/bin/env python3

import urllib.parse
import urllib.request
import sys
import json
from RegionMapData import regions, regionmap

x0 = -49985
y0 = -40985
z0 = -24105

def findRegion(x, y, z):
    px = int((x - x0) * 83 / 4096)
    pz = int((z - z0) * 83 / 4096)
    
    if px < 0 or pz < 0 or pz >= len(regionmap):
        return None
    else:
        row = regionmap[pz]
        rx = 0
        
        for rl, pv in row:
            if px < rx + rl:
                break
            else:
                rx += rl
        else:
            pv = 0

        if pv == 0:
            return None
        else:
            return (pv, regions[pv])

def main():
    sysname = sys.argv[1]
    url = 'https://www.edsm.net/api-v1/systems?systemName=' + urllib.parse.quote(sysname) + '&coords=1&showId=1'
    with urllib.request.urlopen(url) as f:
        systems = json.load(f)
    for system in systems:
        region = findRegion(system['coords']['x'], system['coords']['y'], system['coords']['z'])
        if region is not None:
            print('System {0} at ({1},{2},{3}) is in region {4} ({5})'.format(
                system['name'],
                system['coords']['x'],
                system['coords']['y'],
                system['coords']['z'],
                region[0],
                region[1]
            ))
        else:
            print('System {0} at ({1},{2},{3}) is outside the region map'.format(
                system['name'],
                system['coords']['x'],
                system['coords']['y'],
                system['coords']['z']
            ))

        id64 = system['id64']
        masscode = id64 & 7
        z = (((id64 >> 3) & (0x3FFF >> masscode)) << masscode) * 10 + z0
        y = (((id64 >> (17 - masscode)) & (0x1FFF >> masscode)) << masscode) * 10 + y0
        x = (((id64 >> (30 - masscode * 2)) & (0x3FFF >> masscode)) << masscode) * 10 + x0
        region2 = findRegion(x, y, z)
        if region2 != region:
            print('Boxel of system {0} is at ({1},{2},{3})'.format(
                system['name'],
                x,
                y,
                z
            ))
            if region2 is not None:
                print('({0},{1},{2}) is in region {3} ({4})'.format(
                    x,
                    y,
                    z,
                    region2[0],
                    region2[1]
                ))
            else:
                print('({0},{1},{2}) is outside the region map'.format(
                    x,
                    y,
                    z
                ))

if __name__ == '__main__':
    main()
