from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import json
import os
from datetime import datetime

class GetMatchesDataAgent(Agent):
    class ProcessMatchBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=30)
            if msg and msg.get_metadata("ontology") == "match_data":
                print("[GetMatchesDataAgent] : Received match data")
                match = json.loads(msg.body)

                try:
                    analytics = self.agent.generate_analytics(match["date"], match["home_team"], match["away_team"])

                    # Save analytics to JSON
                    output_folder = "agentsData/matchesAnalytics"
                    os.makedirs(output_folder, exist_ok=True)
                    output_file = os.path.join(output_folder, f"{match['date']}-{match['home_team']}-{match['away_team']}-analytics.json")
                    with open(output_file, "w") as file:
                        json.dump(analytics, file, indent=4)

                    print(f"[GetMatchesDataAgent] : Saved analytics to {output_file}")

                    # Send analytics to RandomForestAgent
                    prediction_msg = Message(to="randomforest@localhost")
                    prediction_msg.set_metadata("performative", "request")
                    prediction_msg.set_metadata("ontology", "prediction_data")
                    prediction_msg.body = json.dumps(analytics)
                    await self.send(prediction_msg)
                    print(f"[GetMatchesDataAgent] : Sent analytics for prediction: {match['home_team']} vs {match['away_team']}")

                    prediction_response = await self.receive(timeout=30)
                    if prediction_response and prediction_response.get_metadata("ontology") == "prediction_result":
                        prediction_result = json.loads(prediction_response.body)
                        print(f"[GetMatchesDataAgent] : Received prediction: {prediction_result['prediction']}")

                        # Notify GetMatchesAgent
                        msg_to_matches = Message(to="getmatches@localhost")
                        msg_to_matches.set_metadata("performative", "inform")
                        msg_to_matches.set_metadata("ontology", "prediction_complete")
                        await self.send(msg_to_matches)
                        print(f"[GetMatchesDataAgent] : Notified GetMatchesAgent about completed prediction for {match['home_team']} vs {match['away_team']}.")

                except Exception as e:
                    print(f"[GetMatchesDataAgent] : Error processing match data: {e}")

    def generate_analytics(self, date, home_team, away_team):
        with open("data/matches.json", "r") as file:
            matches = json.load(file).get("matches", [])

        home_last_4 = self.get_last_matches(matches, home_team, date)
        away_last_4 = self.get_last_matches(matches, away_team, date)

        with open("data/shouts_names.json", "r") as file:
            shout_data = json.load(file)
        home_shots = self.get_avg_shots(shout_data, home_team)
        away_shots = self.get_avg_shots(shout_data, away_team)

        with open("data/EPL_standings_names.json", "r") as file:
            standings = json.load(file)
        home_data = self.get_xg_and_position(standings, home_team)
        away_data = self.get_xg_and_position(standings, away_team)

        return {
            "date": date,
            "home_team": home_team,
            "away_team": away_team,
            "home_last_4": home_last_4,
            "away_last_4": away_last_4,
            "home_avg_shots": home_shots,
            "away_avg_shots": away_shots,
            "home_team_overall_position": home_data["overall_position"],
            "home_team_overall_xg": home_data["overall_xg"],
            "home_team_home_xg": home_data["home_xg"],
            "away_team_overall_position": away_data["overall_position"],
            "away_team_overall_xg": away_data["overall_xg"],
            "away_team_away_xg": away_data["away_xg"]
        }

    def get_last_matches(self, matches, team, date):
        last_matches = []
        date = datetime.strptime(date, "%Y-%m-%d")
        for match in matches:
            match_date = datetime.strptime(match["utcDate"][:10], "%Y-%m-%d")
            if match_date < date and (match["homeTeam"]["shortName"] == team or match["awayTeam"]["shortName"] == team):
                if match["homeTeam"]["shortName"] == team:
                    result = self.get_match_result(match, "home")
                else:
                    result = self.get_match_result(match, "away")
                last_matches.append(result)
            if len(last_matches) == 4:
                break
        return last_matches

    def get_match_result(self, match, side):
        if match["score"]["winner"] == "DRAW":
            return "D"
        elif match["score"]["winner"] == "HOME_TEAM" and side == "home":
            return "W"
        elif match["score"]["winner"] == "AWAY_TEAM" and side == "away":
            return "W"
        else:
            return "L"

    def get_avg_shots(self, shout_data, team):
        for team_data in shout_data:
            if team_data["Squad"] == team:
                return round(team_data["Sh"] / team_data["# Pl"], 2)
        return 0

    def get_xg_and_position(self, standings, team):
        overall_entry = next((entry for entry in standings["Overall"] if entry["Team"] == team), None)
        overall_xg = overall_entry["xG"] if overall_entry else None
        overall_position = overall_entry["\u2116"] if overall_entry else None

        home_entry = next((entry for entry in standings["Home"] if entry["Team"] == team), None)
        home_xg = home_entry["xG"] if home_entry else None

        away_entry = next((entry for entry in standings["Away"] if entry["Team"] == team), None)
        away_xg = away_entry["xG"] if away_entry else None

        return {
            "overall_position": overall_position,
            "overall_xg": overall_xg,
            "home_xg": home_xg,
            "away_xg": away_xg
        }

    async def setup(self):
        print("[GetMatchesDataAgent] : Agent started!")
        self.add_behaviour(self.ProcessMatchBehaviour())
