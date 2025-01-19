import requests
import json

# Vaš API ključ za football-data.org
api_key = "5fbee9675c9943d399c7cf46d3ad99b3"
headers = {"X-Auth-Token": api_key}

# Funkcija za dohvaćanje svih timova u Premier ligi
def get_teams():
    url = "https://api.football-data.org/v4/competitions/PL/teams"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Greška u dohvaćanju timova: {response.status_code}")
        print(response.text)
        return None
    return response.json()

# Funkcija za dohvaćanje rasporeda svih utakmica
def get_matches():
    url = "https://api.football-data.org/v4/competitions/PL/matches"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Greška u dohvaćanju utakmica: {response.status_code}")
        print(response.text)
        return None
    return response.json()

# Dohvati sve timove
teams_data = get_teams()
if teams_data is None:
    exit()

# Spremi sirove podatke o timovima u JSON
with open("teams.json", "w") as f:
    json.dump(teams_data, f, indent=4)
print("Podaci o timovima spremljeni u teams.json")

# Dohvati sve utakmice
matches_data = get_matches()
if matches_data is None:
    exit()

# Spremi sirove podatke o utakmicama u JSON
with open("matches.json", "w") as f:
    json.dump(matches_data, f, indent=4)
print("Podaci o utakmicama spremljeni u matches.json")

# Izračun atributa
# Učitaj podatke iz lokalnih datoteka
with open("teams.json", "r") as f:
    teams_data = json.load(f)

with open("matches.json", "r") as f:
    matches_data = json.load(f)

# Dohvati pozicije timova iz podataka o timovima
def get_team_position(team_id):
    for team in teams_data["teams"]:
        if team["id"] == team_id:
            return team.get("position", None)
    return None

# Izračunaj bodove po utakmici (PPG) i razliku za posljednje 4 utakmice
def calculate_ppg_diff(team_id, matches_data):
    team_matches = [
        match for match in matches_data["matches"]
        if match["homeTeam"]["id"] == team_id or match["awayTeam"]["id"] == team_id
    ]
    
    # Sortiraj utakmice prema datumu (najnovije prve)
    team_matches.sort(key=lambda x: x["utcDate"], reverse=True)
    
    # Izračunaj bodove za posljednje 4 utakmice
    last_4_matches = team_matches[:4]
    points_last_4 = 0
    for match in last_4_matches:
        if match["homeTeam"]["id"] == team_id and match["score"]["winner"] == "HOME_TEAM":
            points_last_4 += 3
        elif match["awayTeam"]["id"] == team_id and match["score"]["winner"] == "AWAY_TEAM":
            points_last_4 += 3
        elif match["score"]["winner"] == "DRAW":
            points_last_4 += 1
    
    # Ukupni bodovi i broj utakmica
    total_points = 0
    for match in team_matches:
        if match["homeTeam"]["id"] == team_id and match["score"]["winner"] == "HOME_TEAM":
            total_points += 3
        elif match["awayTeam"]["id"] == team_id and match["score"]["winner"] == "AWAY_TEAM":
            total_points += 3
        elif match["score"]["winner"] == "DRAW":
            total_points += 1
    
    total_matches = len(team_matches)
    overall_ppg = total_points / total_matches if total_matches > 0 else 0
    ppg_last_4 = points_last_4 / 4 if len(last_4_matches) > 0 else 0
    
    return ppg_last_4 - overall_ppg

# Izračunaj prosječan broj udaraca po utakmici (ako je dostupan u tim podacima)
def calculate_shots_average(team_id, matches_data):
    team_matches = [
        match for match in matches_data["matches"]
        if match["homeTeam"]["id"] == team_id or match["awayTeam"]["id"] == team_id
    ]
    total_shots = 0
    total_matches = 0
    
    for match in team_matches:
        # Provjeri podatke o šutevima (ako postoje)
        if match["homeTeam"]["id"] == team_id:
            total_shots += match.get("homeTeamShots", 0)
        elif match["awayTeam"]["id"] == team_id:
            total_shots += match.get("awayTeamShots", 0)
        total_matches += 1
    
    return total_shots / total_matches if total_matches > 0 else 0

# Pripremi podatke za sve utakmice
data = []
for match in matches_data["matches"]:
    home_team_id = match["homeTeam"]["id"]
    away_team_id = match["awayTeam"]["id"]
    
    home_team_ppg_diff = calculate_ppg_diff(home_team_id, matches_data)
    away_team_ppg_diff = calculate_ppg_diff(away_team_id, matches_data)
    
    home_position = get_team_position(home_team_id)
    away_position = get_team_position(away_team_id)
    
    home_shots_average = calculate_shots_average(home_team_id, matches_data)
    away_shots_average = calculate_shots_average(away_team_id, matches_data)
    
    data.append({
        "match_id": match["id"],
        "match_date": match["utcDate"],
        "home_team": match["homeTeam"]["name"],
        "away_team": match["awayTeam"]["name"],
        "home_team_ppg_diff": home_team_ppg_diff,
        "away_team_ppg_diff": away_team_ppg_diff,
        "home_position": home_position,
        "away_position": away_position,
        "home_shots_average": home_shots_average,
        "away_shots_average": away_shots_average,
    })

# Spremi obrađene podatke u JSON
with open("processed_match_data.json", "w") as f:
    json.dump(data, f, indent=4)

print("Obrađeni podaci spremljeni u processed_match_data.json")
