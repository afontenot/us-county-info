import csv
from collections import defaultdict


planning_regions = {
    "Northwest Hills Planning Region": {
        "fips": "09160",
        "municipalities": (
            "Barkhamsted",
            "Burlington",
            "Canaan",
            "Colebrook",
            "Cornwall",
            "Goshen",
            "Hartland",
            "Harwinton",
            "Kent",
            "Litchfield",
            "Morris",
            "New Hartford",
            "Norfolk",
            "N. Canaan",
            "Roxbury",
            "Salisbury",
            "Sharon",
            "Torrington",
            "Warren",
            "Washington",
            "Winchester",
        ),
    },
    "Capitol Planning Region": {
        "fips": "09110",
        "municipalities": (
            "Hartford",
            "New Britain",
            "Andover",
            "Avon",
            "Berlin",
            "Bloomfield",
            "Bolton",
            "Canton",
            "Columbia",
            "Coventry",
            "E. Granby",
            "E. Hartford",
            "E. Windsor",
            "Ellington",
            "Enfield",
            "Farmington",
            "Glastonbury",
            "Granby",
            "Hebron",
            "Manchester",
            "Mansfield",
            "Marlborough",
            "Newington",
            "Plainville",
            "Rocky Hill",
            "Simsbury",
            "Somers",
            "S. Windsor",
            "Southington",
            "Stafford",
            "Suffield",
            "Tolland",
            "Vernon",
            "W. Hartford",
            "Wethersfield",
            "Willington",
            "Windsor",
            "Windsor Locks",
        ),
    },
    "Northeastern Connecticut Planning Region": {
        "fips": "09150",
        "municipalities": (
            "Ashford",
            "Brooklyn",
            "Canterbury",
            "Chaplin",
            "Eastford",
            "Hampton",
            "Killingly",
            "Plainfield",
            "Pomfret",
            "Putnam",
            "Scotland",
            "Sterling",
            "Thompson",
            "Union",
            "Voluntown",
            "Woodstock",
        ),
    },
    "Western Connecticut Planning Region": {
        "fips": "09190",
        "municipalities": (
            "Danbury",
            "Norwalk",
            "Stamford",
            "Bethel",
            "Bridgewater",
            "Brookfield",
            "Darien",
            "Greenwich",
            "New Canaan",
            "New Fairfield",
            "New Milford",
            "Newtown",
            "Redding",
            "Ridgefield",
            "Sherman",
            "Weston",
            "Westport",
            "Wilton",
        ),
    },
    "Greater Bridgeport Planning Region": {
        "fips": "09120",
        "municipalities": (
            "Bridgeport",
            "Easton",
            "Fairfield",
            "Monroe",
            "Stratford",
            "Trumbull",
        ),
    },
    "Naugatuck Valley Planning Region": {
        "fips": "09140",
        "municipalities": (
            "Ansonia",
            "Bristol",
            "Derby",
            "Shelton",
            "Waterbury",
            "Beacon Falls",
            "Bethlehem",
            "Cheshire",
            "Middlebury",
            "Naugatuck",
            "Oxford",
            "Plymouth",
            "Prospect",
            "Seymour",
            "Southbury",
            "Thomaston",
            "Watertown",
            "Wolcott",
            "Woodbury",
        ),
    },
    "South Central Connecticut Planning Region": {
        "fips": "09170",
        "municipalities": (
            "Meriden",
            "Milford",
            "New Haven",
            "W. Haven",
            "Bethany",
            "Branford",
            "E. Haven",
            "Guilford",
            "Hamden",
            "Madison",
            "N. Branford",
            "N. Haven",
            "Orange",
            "Wallingford",
            "Woodbridge",
        ),
    },
    "Lower Connecticut River Valley Planning Region": {
        "fips": "09130",
        "municipalities": (
            "Chester",
            "Clinton",
            "Cromwell",
            "Deep River",
            "Durham",
            "E. Haddam",
            "E. Hampton",
            "Essex",
            "Haddam",
            "Killingworth",
            "Lyme",
            "Middlefield",
            "Middletown",
            "Old Lyme",
            "Old Saybrook",
            "Portland",
            "Westbrook",
        ),
    },
    "Southeastern Connecticut Planning Region": {
        "fips": "09180",
        "municipalities": (
            "New London",
            "Norwich",
            "Bozrah",
            "Colchester",
            "E. Lyme",
            "Franklin",
            "Griswold",
            "Groton",
            # "Jewett City",  # a borough of Griswold, not reported separately
            "Lebanon",
            "Ledyard",
            "Lisbon",
            "Montville",
            "N. Stonington",
            "Preston",
            "Salem",
            "Sprague",
            "Stonington",
            "Waterford",
            "Windham",
        ),
    },
}

municipalities = {}
for region_name, region in planning_regions.items():
    for municipality in region["municipalities"]:
        municipalities[municipality] = region_name

visited_municipalities = set()
vote_data = {}

with open(
    "data/State_of_Connecticut_Elections_Database__2020_Nov_3_General_Election_President_State_of_Connecticut.csv"
) as f:
    while True:
        line = next(f)
        if line.startswith("Totals"):
            break
    csvf = csv.reader(f)
    for line in csvf:
        if line[0] == "Totals":
            break
        location = line[0]
        visited_municipalities.add(location)
        planning_region = municipalities[location]
        if planning_region not in vote_data:
            vote_data[planning_region] = defaultdict(int)
        vote_data[planning_region]["dem"] += int(line[1].replace(",", ""))
        vote_data[planning_region]["rep"] += int(line[2].replace(",", ""))
        vote_data[planning_region]["total"] += int(line[-1].replace(",", ""))


assert set(municipalities) == visited_municipalities

fips_data = {}

for planning_region, votes in vote_data.items():
    fips = planning_regions[planning_region]["fips"]
    fips_data[fips] = {
        "LOCATION": f"{planning_region}, Connecticut",
        "REP": votes["rep"] / votes["total"],
        "DEM": votes["dem"] / votes["total"],
    }
