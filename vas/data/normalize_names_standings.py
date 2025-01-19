import json

replacement_rules = {
    "Nottingham Forest": "Nottingham",
    "Newcastle United": "Newcastle",
    "Newcastle Utd": "Newcstle",
    "Manchester United" : "Man United",
    "Manchester Utd" : "Man United",
    "Manchester City": "Man City",
    "Wolverhampton Wanderers": "Wolverhampton",
    "Ipswich" : "Ipswich Town",
    "Brighton" : "Brighton Hove"
}

input_file_path = "EPL_standings.json"
output_file_path = "EPL_standings_names.json"

with open(input_file_path, "r") as file:
    standings = json.load(file)

def replace_team_names(standings, rules):
    for category in standings:
        for team in standings[category]:
            original_name = team["Team"]
            if original_name in rules:
                team["Team"] = rules[original_name]
    return standings

updated_standings = replace_team_names(standings, replacement_rules)

with open(output_file_path, "w") as file:
    json.dump(updated_standings, file, indent=4)

print(f"Team names have been updated and saved to {output_file_path}.")
