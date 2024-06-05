from functools import reduce
from math import ceil, floor
from multiprocessing.pool import Pool
from os import makedirs

import geopandas as gpd
from shapely import minimum_bounding_circle, minimum_bounding_radius
from shapely.geometry import Polygon, Point

import alaska
import connecticut


print("Reading data...")
# Source: https://www.census.gov/geographies/mapping-files/time-series/geo/carto-boundary-file.html
county_data = gpd.read_file("data/cb_2022_us_county_500k.shp")
vote_data = {}

# Source: https://github.com/tonmcg/US_County_Level_Election_Results_08-20
with open("data/2020_US_County_Level_Presidential_Results.csv") as f:
    headers = next(f).split(",")
    fips_i = headers.index("county_fips")
    state_i = headers.index("state_name")
    county_i = headers.index("county_name")
    rep_i = headers.index("per_gop")
    dem_i = headers.index("per_dem")
    for line in f:
        line = line.split(",")
        fips = line[fips_i]
        state = line[state_i]
        county = line[county_i]
        rep = line[rep_i]
        dem = line[dem_i]
        vote_data[fips] = {
            "LOCATION": f"{county}, {state}",
            "REP": float(rep),
            "DEM": float(dem),
        }

# Connecticut Planning Regions
# Source: https://electionhistory.ct.gov/eng/contests/view/15175
vote_data.update(connecticut.fips_data)

# Alaska Boroughs - Estimated Results, Not Official!
# Source: https://rrhelections.com/index.php/2021/04/13/alaska-presidential-results-by-county-equivalent-1960-2020/9/
vote_data.update(alaska.fips_data)

print("Precomputing county data...")
counties = {}
grid_diag_2 = 2.0 ** (1 / 2) / 2.0
for entry in (row[1] for row in county_data.iterrows()):
    # add 0.1 extra padding to work around any potential geometry issues
    radius = minimum_bounding_radius(entry["geometry"]) + grid_diag_2 + 0.1
    centroid = minimum_bounding_circle(entry["geometry"]).centroid

    # add voting data
    assert entry["GEOID"] == entry["STATEFP"] + entry["COUNTYFP"]
    county_vote_data = vote_data.get(entry["GEOID"])
    if county_vote_data:
        for key, value in county_vote_data.items():
            entry[key] = value
    else:
        print("No data for", entry["STATE_NAME"], entry["NAMELSAD"], entry["GEOID"])

    counties[(centroid, radius)] = entry


def check_grid(args):
    lon, lat = args
    poly = Polygon(
        (
            (lon, lat),
            (lon + 1, lat),
            (lon + 1, lat + 1),
            (lon, lat + 1),
        )
    )
    loc = Point(lon + 0.5, lat + 0.5)
    intersecting_counties = []
    for key, entry in counties.items():
        centroid, radius = key
        if loc.dwithin(centroid, radius):
            if poly.intersects(entry["geometry"]):
                intersecting_counties.append(entry)
    if intersecting_counties:
        gdf = gpd.GeoDataFrame(intersecting_counties)
        makedirs(f"grid/{lon}", exist_ok=True)
        with open(f"grid/{lon}/{lat}.geojson", "w") as of:
            of.write(gdf.to_json())


grid_size = 360 * 180
print(f"Calculating grid ({grid_size} cells):")

args = [(lon, lat) for lon in range(-180, 180) for lat in range(-90, 90)]
with Pool() as pool:
    grid_count = 0
    for _ in pool.imap_unordered(check_grid, args):
        grid_count += 1
        print(f"\r{round(100 * grid_count / grid_size, 1)}% ", end="")
