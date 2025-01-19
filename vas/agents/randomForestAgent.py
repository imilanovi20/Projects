from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import json
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import os

class RandomForestAgent(Agent):
    class PredictionBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=30)
            if msg and msg.get_metadata("ontology") == "prediction_data":
                print("[RandomForestAgent] : Received match data for prediction.")
                match_data = json.loads(msg.body)

                try:
                    features = self.agent.prepare_features(match_data)

                    columns = [
                        'team_a_ppg_dif_l4', 'team_b_ppg_dif_l4', 'team_a_shots_average',
                        'team_b_shots_average', 'predict_xg_overall_team_a', 'predict_xg_overall_team_b',
                        'predict_xg_home_team_a', 'predict_xg_away_team_b', 'position_a_prematch',
                        'position_b_prematch', 'ppg_dif_difference', 'xg_difference', 'shots_difference',
                        'position_difference', 'xg_difference_home_away'
                    ]
                    features_df = pd.DataFrame([features], columns=columns)
                    prediction = self.agent.rf_model.predict(features_df)[0]
                    prediction_label = {0: "Home Win", 1: "Away Win", 2: "Draw"}[prediction]

                except Exception as e:
                    print(f"[RandomForestAgent] : Error in prediction: {e}")
                    prediction_label = "Can not predict"

                output_folder = "agentsData/predictions"
                os.makedirs(output_folder, exist_ok=True)
                output_file = f"{match_data['date']}-{match_data['home_team']}-{match_data['away_team']}-prediction.json"
                with open(f"{output_folder}/{output_file}", "w") as file:
                    json.dump({
                        "date": match_data['date'],
                        "home_team": match_data['home_team'],
                        "away_team": match_data['away_team'],
                        "prediction": prediction_label
                    }, file, indent=4)

                print(f"[RandomForestAgent] : Prediction saved to {output_folder}/{output_file}")

                reply = Message(to=str(msg.sender))
                reply.set_metadata("performative", "inform")
                reply.set_metadata("ontology", "prediction_result")
                reply.body = json.dumps({"prediction": prediction_label})
                await self.send(reply)
                print(f"[RandomForestAgent] : Prediction sent: {prediction_label}")

    def prepare_features(self, match_data):
        points = {"W": 3, "D": 1, "L": 0}
        calculate_ppg = lambda last_4: sum(points[r] for r in last_4) / len(last_4)

        team_a_ppg_dif_l4 = calculate_ppg(match_data["home_last_4"])
        team_b_ppg_dif_l4 = calculate_ppg(match_data["away_last_4"])
        team_a_shots_average = match_data["home_avg_shots"]
        team_b_shots_average = match_data["away_avg_shots"]
        predict_xg_overall_team_a = float(match_data["home_team_overall_xg"] or 0)
        predict_xg_overall_team_b = float(match_data["away_team_overall_xg"] or 0)
        predict_xg_home_team_a = float(match_data["home_team_home_xg"] or 0)
        predict_xg_away_team_b = float(match_data["away_team_away_xg"] or 0)
        position_a_prematch = match_data["home_team_overall_position"] or 0
        position_b_prematch = match_data["away_team_overall_position"] or 0

        ppg_dif_difference = team_a_ppg_dif_l4 - team_b_ppg_dif_l4
        xg_difference = predict_xg_overall_team_a - predict_xg_overall_team_b
        shots_difference = team_a_shots_average - team_b_shots_average
        position_difference = position_a_prematch - position_b_prematch
        xg_difference_home_away = predict_xg_home_team_a - predict_xg_away_team_b

        return [
            team_a_ppg_dif_l4,
            team_b_ppg_dif_l4,
            team_a_shots_average,
            team_b_shots_average,
            predict_xg_overall_team_a,
            predict_xg_overall_team_b,
            predict_xg_home_team_a,
            predict_xg_away_team_b,
            position_a_prematch,
            position_b_prematch,
            ppg_dif_difference,
            xg_difference,
            shots_difference,
            position_difference,
            xg_difference_home_away
        ]

    async def setup(self):
        print("[RandomForestAgent] : Agent started!")
        self.rf_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)

        train_data = pd.read_csv("data/train_model/processed_train_dataset.csv", sep=",")
        train_data["ppg_dif_difference"] = train_data["team_a_ppg_dif_l4"] - train_data["team_b_ppg_dif_l4"]
        train_data["xg_difference"] = train_data["predict_xg_overall_team_a"] - train_data["predict_xg_overall_team_b"]
        train_data["xg_difference_home_away"] = train_data["predict_xg_home_team_a"] - train_data["predict_xg_away_team_b"]
        train_data["shots_difference"] = train_data["team_a_shots_average"] - train_data["team_b_shots_average"]
        train_data["position_difference"] = train_data["position_a_prematch"] - train_data["position_b_prematch"]

        selected_features = [
            'team_a_ppg_dif_l4', 'team_b_ppg_dif_l4', 'team_a_shots_average',
            'team_b_shots_average', 'predict_xg_overall_team_a', 'predict_xg_overall_team_b',
            'predict_xg_home_team_a', 'predict_xg_away_team_b', 'position_a_prematch',
            'position_b_prematch', 'ppg_dif_difference', 'xg_difference', 'shots_difference',
            'position_difference', 'xg_difference_home_away'
        ]

        X = train_data[selected_features]
        y = train_data["Result"]
        self.rf_model.fit(X, y)
        print("[RandomForestAgent] : Model training complete.")
        self.add_behaviour(self.PredictionBehaviour())
