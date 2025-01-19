import asyncio
from agents.getMatchesAgent import GetMatchesAgent
from agents.getMatchesDataAgent import GetMatchesDataAgent
from agents.randomForestAgent import RandomForestAgent
import os
import shutil

async def main():
    directories_to_clear = ["agentsData/matches", "agentsData/matchesAnalytics", "agentsData/predictions"]
    for directory in directories_to_clear:
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.makedirs(directory)

    print("[Main] : Directories cleared.")

    start_date = "2025-01-20"
    end_date = "2025-01-27"

    data_agent = GetMatchesDataAgent("getmatchesdata@localhost", "tajna")
    forest_agent = RandomForestAgent("randomforest@localhost", "tajna")
    matches_agent = GetMatchesAgent("getmatches@localhost", "tajna")
    matches_agent.set_date_range(start_date, end_date)

    await forest_agent.start()
    print("[Main] : RandomForestAgent started and running...")

    await data_agent.start()
    print("[Main] : GetMatchesDataAgent started and running...")

    await asyncio.sleep(5)
    await matches_agent.start()
    print("[Main] : GetMatchesAgent started and running...")

    while forest_agent.is_alive() or data_agent.is_alive() or matches_agent.is_alive():
        await asyncio.sleep(1)

    print("[Main] : All agents stopped.")

if __name__ == "__main__":
    asyncio.run(main())
