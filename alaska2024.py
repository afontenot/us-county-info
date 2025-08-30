import csv
from collections import defaultdict

import geopandas as gpd
import pyproj
from shapely.ops import transform

# Source: https://www.elections.alaska.gov/research/district-maps/
precinct_data = gpd.read_file("data/2024/alaska/Precincts.shp")
# Source: https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html
county_data = gpd.read_file("data/2024/cb_2024_us_county_500k.shp")

# the primary output for analysis
fips_data = {}

alaska_county_equivalents = []
for county in (row[1] for row in county_data.iterrows()):
    if county["STATE_NAME"].lower() == "alaska":
        alaska_county_equivalents.append(county)
        fips_data[county["GEOID"]] = {"LOCATION": f"{county["NAME"]}, Alaska (ED votes)"}

# convert Alaska's precincts from Web Mercator to NAD83
reproj = pyproj.Transformer.from_proj(3857, 4269, always_xy=True)

precinct_to_borough = {}
results = {}

for precinct in (row[1] for row in precinct_data.iterrows()):
    pre_geom = transform(reproj.transform, precinct["geometry"])
    area = pre_geom.area
    total_overlap = 0
    for borough in alaska_county_equivalents:
        # prepare results dict for later
        results[borough["GEOID"]] = defaultdict(int)
        overlap = borough["geometry"].intersection(pre_geom).area / area
        total_overlap += overlap
        if overlap > 0.0001:
            precinct_code = precinct["Precinct_N"].split(" ")[0]
            precinct_to_borough.setdefault(precinct_code, []).append((borough["GEOID"], overlap))

shared_votes = 0
# Source: https://www.elections.alaska.gov/enr/
with open("data/2024/alaska/Alaska_2024_ENRbyPrecinct.csv") as f:
    csvf = csv.reader(f)
    header = next(csvf)
    pname_i = header.index("Precinct_name")
    contest_i = header.index("Contest_title")
    party_i = header.index("Party_Code")
    votes_i = header.index("total_votes")
    for line in csvf:
        contest = line[contest_i]
        if contest != "U.S. President / Vice President":
            continue
        precinct_code = line[pname_i].split(" ")[0]

        # skip unaggregated overseas ballots
        if precinct_code == "HD99":
            continue

        # FIXME: skip absentee / early votes aggregated at district level
        if precinct_code.startswith("District"):
            continue

        party = line[party_i]
        votes = int(line[votes_i])
        boroughs = precinct_to_borough[precinct_code]
        assert len(boroughs) > 0
        if len(boroughs) > 1:
            shared_votes += votes
        total_overlap = sum(b[1] for b in boroughs)
        for borough in boroughs:
            weighted_votes = votes * borough[1] / total_overlap
            results[borough[0]]["TOTAL"] += weighted_votes
            if party in ("DEM", "REP"):
                results[borough[0]][party] += weighted_votes

total_votes = 0
for fips, party_votes in results.items():
    fips_data[fips]["DEM"] = party_votes["DEM"] / party_votes["TOTAL"]
    fips_data[fips]["REP"] = party_votes["REP"] / party_votes["TOTAL"]
    total_votes += party_votes["TOTAL"]

print(f"Alaska: approx. {total_votes} votes found.")
print(f"Alaska: {shared_votes} shared between multiple boroughs.")
