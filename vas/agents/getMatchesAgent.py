from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message
import json
from datetime import datetime


class GetMatchesAgent(Agent):
    def set_date_range(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    class FilterAndSendMatchesBehaviour(OneShotBehaviour):
        async def run(self):
            print(f"[GetMatchesAgent] : Filtering matches between {self.agent.start_date} and {self.agent.end_date}...")

            try:
                with open("data/matches.json", "r") as file:
                    matches = json.load(file).get("matches", [])
            except FileNotFoundError:
                print("[GetMatchesAgent] : Error: matches.json not found.")
                await self.agent.stop()
                return

            start_date = datetime.strptime(self.agent.start_date, "%Y-%m-%d")
            end_date = datetime.strptime(self.agent.end_date, "%Y-%m-%d")

            self.agent.filtered_matches = [
                {
                    "date": match["utcDate"][:10],
                    "home_team": match["homeTeam"]["shortName"],
                    "away_team": match["awayTeam"]["shortName"]
                }
                for match in matches
                if start_date <= datetime.strptime(match["utcDate"][:10], "%Y-%m-%d") <= end_date
            ]

            print(f"[GetMatchesAgent] : Found {len(self.agent.filtered_matches)} matches.")

            with open("agentsData/matches/filtered_matches.json", "w") as output_file:
                json.dump(self.agent.filtered_matches, output_file, indent=4)

            if self.agent.filtered_matches:
                first_match = self.agent.filtered_matches.pop(0)
                await self.send_match_to_data_agent(first_match)

        async def send_match_to_data_agent(self, match):
            """
            Metoda za slanje utakmice GetMatchesDataAgentu.
            """
            msg = Message(to="getmatchesdata@localhost")
            msg.body = json.dumps(match)
            msg.set_metadata("performative", "inform")
            msg.set_metadata("ontology", "match_data")
            await self.send(msg)
            print(f"[GetMatchesAgent] : Sent match {match['home_team']} vs {match['away_team']} to GetMatchesDataAgent.")

    class AwaitPredictionBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=30)
            if msg and msg.get_metadata("ontology") == "prediction_complete":
                print("[GetMatchesAgent] : Received prediction completion notification.")

                if self.agent.filtered_matches:
                    next_match = self.agent.filtered_matches.pop(0)
                    await self.send_match_to_data_agent(next_match)
                else:
                    print("[GetMatchesAgent] : All matches processed.")
                    await self.agent.stop()

        async def send_match_to_data_agent(self, match):
            """
            Metoda za slanje utakmice GetMatchesDataAgentu.
            """
            msg = Message(to="getmatchesdata@localhost")
            msg.body = json.dumps(match)
            msg.set_metadata("performative", "inform")
            msg.set_metadata("ontology", "match_data")
            await self.send(msg)
            print(f"[GetMatchesAgent] : Sent match {match['home_team']} vs {match['away_team']} to GetMatchesDataAgent.")

    async def setup(self):
        print("[GetMatchesAgent] : Agent started!")
        self.add_behaviour(self.FilterAndSendMatchesBehaviour())
        self.add_behaviour(self.AwaitPredictionBehaviour())
