import pandas as pd

data = pd.read_csv("train_dataset.csv", sep=";")

print("Nazivi stupaca u datasetu:", data.columns)

if 'HomeWin' not in data.columns or 'AwayWin' not in data.columns:
    raise KeyError("Stupci 'HomeWin' i 'AwayWin' ne postoje u datasetu.")

data['Result'] = data.apply(
    lambda row: 0 if row['HomeWin'] == 1 else (1 if row['AwayWin'] == 1 else 2), axis=1
)

selected_features = [
    'team_a_ppg_dif_l4',
    'team_b_ppg_dif_l4',
    'team_a_shots_average',
    'team_b_shots_average',
    'predict_xg_overall_team_a',
    'predict_xg_overall_team_b',
    'position_a_prematch',
    'position_b_prematch',
    'predict_xg_home_team_a',
    'predict_xg_away_team_b',
    'Result'
]

processed_data = data[selected_features]

processed_data.to_csv("processed_train_dataset.csv", index=False)
print("Dataset uspješno obrađen i spremljen kao 'processed_train_dataset.csv'.")
