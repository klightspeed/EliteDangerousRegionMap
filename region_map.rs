mod region_map_data;

use crate::region_map_data::{REGIONS, REGION_MAP};
use reqwest::Url;
use serde_json::Value;
use std::env::args;
use std::error::Error;

//
// Crates 'reqwest' (with feature 'blocking') and 'serde_json' are required in order to translate
// system names into coordinates via EDSM API
// You can use the code below without installing them if you already have an id64 or coordinates
//

const X0: f64 = -49985.0;
const Y0: f64 = -40985.0;
const Z0: f64 = -24105.0;

#[derive(Copy, Clone, Debug, PartialEq)]
pub struct Region {
    id: u32,
    name: &'static str,
}

#[derive(Clone, Debug, PartialEq)]
pub struct System {
    id64: u64,
    name: String,
    x: f64,
    y: f64,
    z: f64,
    region: Option<Region>,
    boxel_x: f64,
    boxel_y: f64,
    boxel_z: f64,
    boxel_region: Option<Region>,
}

fn find_region(x: f64, _y: f64, z: f64) -> Option<Region> {
    let px = ((x - X0) * 83.0 / 4096.0).floor();
    let pz = ((z - Z0) * 83.0 / 4096.0).floor();

    if px >= 0.0 && pz >= 0.0 {
        if let Some(row) = REGION_MAP.get(pz as usize) {
            let mut acc = 0;
            let mut pv = 0;

            for &(a, b) in row.iter() {
                acc += a;
                if acc > px as i32 {
                    pv = b;
                    break;
                }
            }

            return match pv {
                0 => None,
                _ => Some(Region {
                    id: pv as u32,
                    name: REGIONS[pv as usize],
                }),
            };
        }
    }
    None
}

fn find_region_for_boxel(id64: u64) -> (f64, f64, f64) {
    let mass_code = id64 & 7;
    (
        (((id64 >> (30 - mass_code * 2)) & (0x3FFF >> mass_code)) << mass_code) as f64 * 10.0 + X0,
        (((id64 >> (17 - mass_code)) & (0x1FFF >> mass_code)) << mass_code) as f64 * 10.0 + Y0,
        (((id64 >> 3) & (0x3FFF >> mass_code)) << mass_code) as f64 * 10.0 + Z0,
    )
}

fn find_regions_for_system(system: &str) -> Result<Vec<System>, Box<dyn Error>> {
    let url = Url::parse_with_params(
        "https://www.edsm.net/api-v1/systems",
        &[("systemName", system), ("coords", "1"), ("showId", "1")],
    );
    let mut res = Vec::new();
    for region_raw in serde_json::from_str::<Value>(reqwest::blocking::get(url?)?.text()?.as_str())?
        .as_array()
        .ok_or("fe")?
    {
        let id64 = region_raw["id64"].as_u64().ok_or("System id64 not found")?;
        let coords = region_raw["coords"]
            .as_object()
            .ok_or("System coords not found")?;
        let x = coords
            .get("x")
            .ok_or("System x coord not found")?
            .as_f64()
            .ok_or("System x coord is invalid")?;
        let y = coords
            .get("y")
            .ok_or("System y coord not found")?
            .as_f64()
            .ok_or("System y coord is invalid")?;
        let z = coords
            .get("z")
            .ok_or("System z coord not found")?
            .as_f64()
            .ok_or("System z coord is invalid")?;
        let region = find_region(x, y, z);
        let (boxel_x, boxel_y, boxel_z) = find_region_for_boxel(id64);
        let boxel_region = find_region(boxel_x, boxel_y, boxel_z);

        res.push(System {
            id64,
            name: String::from(region_raw["name"].as_str().ok_or("System name not found")?),
            x,
            y,
            z,
            region,
            boxel_x,
            boxel_y,
            boxel_z,
            boxel_region,
        })
    }
    Ok(res)
}

fn main() -> Result<(), Box<dyn Error>> {
    if args().len() <= 1 {
        eprintln!("Usage: {0} 'System Name' [...]", args().next().unwrap());
        return Ok(());
    }

    for system in args()
        .collect::<Vec<String>>()
        .split_first()
        .ok_or("Args len should have been checked before")?
        .1
    {
        for found in find_regions_for_system(system)? {
            if let Some(region) = found.region {
                println!(
                    "System {0} at ({1},{2},{3}) is in region {4} ({5})",
                    found.name, found.x, found.y, found.z, region.id, region.name
                )
            } else {
                println!(
                    "System {0} at ({1},{2},{3}) is outside the region map",
                    found.name, found.x, found.y, found.z
                )
            }

            if let Some(box_region) = found.boxel_region {
                if found.region.filter(|r| r.id != box_region.id).is_some() {
                    println!(
                        "Boxel of system {0} at ({1},{2},{3}) is in region {4} ({5})",
                        found.name, found.x, found.y, found.z, box_region.id, box_region.name
                    )
                }
            } else {
                println!(
                    "Boxel of system {0} at ({1},{2},{3}) is outside the region map",
                    found.name, found.x, found.y, found.z
                )
            }
        }
    }
    Ok(())
}
