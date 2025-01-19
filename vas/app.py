from flask import Flask, render_template, request, redirect, url_for
import asyncio
import os
import shutil
import json
from agents.getMatchesAgent import GetMatchesAgent
from agents.getMatchesDataAgent import GetMatchesDataAgent
from agents.randomForestAgent import RandomForestAgent

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        asyncio.run(run_agents(start_date, end_date))

        return render_template('index.html')

    return render_template('index.html')


@app.route('/results')
def results():
    analytics_folder = "agentsData/matchesAnalytics"
    predictions_folder = "agentsData/predictions"

    matches_data = []

    if os.path.exists(predictions_folder):
        for prediction_file in os.listdir(predictions_folder):
            if prediction_file.endswith(".json"):
                with open(os.path.join(predictions_folder, prediction_file), 'r') as pred_file:
                    prediction = json.load(pred_file)

                    analytics_file = os.path.join(analytics_folder, prediction_file.replace("prediction", "analytics"))
                    if os.path.exists(analytics_file):
                        with open(analytics_file, 'r') as anal_file:
                            analytics = json.load(anal_file)

                            combined_data = {**analytics, **prediction}
                            matches_data.append(combined_data)

    return render_template('results.html', predictions=matches_data)


async def run_agents(start_date, end_date):
    directories_to_clear = ["agentsData/matches", "agentsData/matchesAnalytics", "agentsData/predictions"]
    for directory in directories_to_clear:
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.makedirs(directory)

    data_agent = GetMatchesDataAgent("getmatchesdata@localhost", "tajna")
    forest_agent = RandomForestAgent("randomforest@localhost", "tajna")
    matches_agent = GetMatchesAgent("getmatches@localhost", "tajna")
    matches_agent.set_date_range(start_date, end_date)

    await forest_agent.start()
    await data_agent.start()
    await asyncio.sleep(5)
    await matches_agent.start()

    while forest_agent.is_alive() or data_agent.is_alive() or matches_agent.is_alive():
        await asyncio.sleep(1)


if __name__ == "__main__":
    app.run(debug=True)
