import csv


boroughs = {
    "Matanuska-Susitna Borough": {"fips": "02170", "common": "Matanuska-Susitna"},
    "Yukon-Koyukuk Census Area": {"fips": "02290", "common": "Yukon-Koyukuk"},
    "Copper River Census Area": {"fips": "02066", "common": "Copper River"},
    "Haines Borough": {"fips": "02100", "common": "Haines"},
    "Fairbanks North Star Borough": {"fips": "02090", "common": "Fairbanks North Star"},
    "Bethel Census Area": {"fips": "02050", "common": "Bethel"},
    "Southeast Fairbanks Census Area": {
        "fips": "02240",
        "common": "Southeast Fairbanks",
    },
    "Northwest Arctic Borough": {"fips": "02188", "common": "Northwest Arctic"},
    "Kenai Peninsula Borough": {"fips": "02122", "common": "Kenai Peninsula"},
    "Kusilvak Census Area": {"fips": "02158", "common": "Kusilvak"},
    "Juneau City and Borough": {"fips": "02110", "common": "Juneau"},
    "Nome Census Area": {"fips": "02180", "common": "Nome"},
    "Dillingham Census Area": {"fips": "02070", "common": "Dillingham"},
    "Yakutat City and Borough": {"fips": "02282", "common": "Yakutat"},
    "Petersburg Borough": {"fips": "02195", "common": "Petersburg"},
    "Aleutians East Borough": {"fips": "02013", "common": "Aleutians East"},
    "Lake and Peninsula Borough": {"fips": "02164", "common": "Lake and Peninsula"},
    "Denali Borough": {"fips": "02068", "common": "Denali"},
    "Wrangell City and Borough": {"fips": "02275", "common": "Wrangell"},
    "Skagway Municipality": {"fips": "02230", "common": "Skagway"},
    "Kodiak Island Borough": {"fips": "02150", "common": "Kodiak Island"},
    "Bristol Bay Borough": {"fips": "02060", "common": "Bristol Bay"},
    "Prince of Wales-Hyder Census Area": {
        "fips": "02198",
        "common": "Prince of Wales-Hyder",
    },
    "Ketchikan Gateway Borough": {"fips": "02130", "common": "Ketchikan Gateway"},
    "Hoonah-Angoon Census Area": {"fips": "02105", "common": "Hoonah-Angoon"},
    "Anchorage Municipality": {"fips": "02020", "common": "Anchorage"},
    "North Slope Borough": {"fips": "02185", "common": "North Slope"},
    "Sitka City and Borough": {"fips": "02220", "common": "Sitka"},
    "Aleutians West Census Area": {"fips": "02016", "common": "Aleutians West"},
    "Chugach Census Area": {"fips": "02063", "common": "Chugach"},
}

fips_data = {}
common = {}

for key, val in boroughs.items():
    fips = val["fips"]
    common_name = val["common"]
    common[common_name] = key
    fips_data[fips] = {"LOCATION": f"{key}, Alaska"}

with open(
    "data/Alaska 1960-2020 County Equivalent For Import_iterative_estimate.csv"
) as f:
    csvf = csv.reader(f)
    header = next(csvf)
    for line in csvf:
        if line[0] == "Total":
            break
        # skip overseas ballots, unaggregated
        if line[0] == "HD 99":
            continue
        location = common[line[0]]
        fips = boroughs[location]["fips"]
        fips_data[fips]["DEM"] = float(line[4]) / float(line[12])
        fips_data[fips]["REP"] = float(line[10]) / float(line[12])
