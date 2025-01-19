import json

replacement_rules = {
    "Nottingham Forest": "Nottingham",
    "Newcastle United": "Newcastle",
    "Newcastle Utd": "Newcastle",
    "Manchester United": "Man United",
    "Manchester Utd": "Man United",
    "Manchester City": "Man City",
    "Wolverhampton Wanderers": "Wolverhampton",
    "Ipswich" : "Ipswich Town",
    "Brighton" : "Brighton Hove"
}

input_file_path = "shouts.json"
output_file_path = "shouts_names.json"

with open(input_file_path, "r") as file:
    shouts = json.load(file)

for team_data in shouts:
    original_name = team_data["Squad"]
    if original_name in replacement_rules:
        team_data["Squad"] = replacement_rules[original_name]

with open(output_file_path, "w") as file:
    json.dump(shouts, file, indent=4)

print(f"Team names in {input_file_path} have been updated and saved to {output_file_path}.")