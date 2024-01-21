import json
import os

import fastf1
import numpy as np
import pandas as pd
import requests

YEAR = 2019

events = [
    'Australian Grand Prix', 
           'Bahrain Grand Prix', 'Chinese Grand Prix', 
    'Azerbaijan Grand Prix', 'Spanish Grand Prix', 'Monaco Grand Prix',
    'Canadian Grand Prix', 'French Grand Prix', 'Austrian Grand Prix', 
    'British Grand Prix', 'German Grand Prix', 'Hungarian Grand Prix', 
    'Belgian Grand Prix', 'Italian Grand Prix', 'Singapore Grand Prix', 
           'Russian Grand Prix', 'Japanese Grand Prix', 'Mexican Grand Prix', 
    'United States Grand Prix', 'Brazilian Grand Prix', 'Abu Dhabi Grand Prix'
          ]

def get_strategy(year: int, event: str | int) -> any:
    f1session = fastf1.get_session(year, event, "R")
    f1session.load(telemetry=False, weather=False, messages=False)
    laps = f1session.laps

    drivers_list = pd.unique(laps["Driver"])

    drivers = pd.DataFrame(drivers_list, columns=["Driver"])
    drivers["FinishOrder"] = drivers.index + 1

    # Get the LapNumber of the first lap of each stint
    first_lap = (
        laps[["Driver", "Stint", "Compound", "LapNumber"]]
        .groupby(["Driver", "Stint", "Compound"])
        .first()
        .reset_index()
    )
    #  Add FinishOrder to first_lap
    first_lap = pd.merge(first_lap, drivers, on="Driver")
    # change LapNumber to LapStart
    first_lap = first_lap.rename(columns={"LapNumber": "LapStart"})
    # reduce the lapstart by 1
    first_lap["LapStart"] = first_lap["LapStart"] - 1

    # find the last lap of each stint
    last_lap = (
        laps[["Driver", "Stint", "Compound", "LapNumber"]]
        .groupby(["Driver", "Stint", "Compound"])
        .last()
        .reset_index()
    )
    #  change LapNumber to LapEnd
    last_lap = last_lap.rename(columns={"LapNumber": "LapEnd"})

    # combine first_lap and last_lap
    stint_laps = pd.merge(first_lap, last_lap, on=["Driver", "Stint", "Compound"])
    #  to cover for outliers
    stint_laps["fill"] = "white"

    compound_colors_2018 = {
        "HYPERSOFT": "pink",
        "ULTRASOFT": "purple",
        "SUPERSOFT": "red",
        "SOFT": "yellow",
        "MEDIUM": "white",
        "HARD": "blue",
        "SUPERHARD": "orange",
        "INTERMEDIATE": "darkblue",
        "WET": "green",
    }

    compound_colors_normal = {
        "SOFT": "red",
        "MEDIUM": "yellow",
        "HARD": "white",
        "INTERMEDIATE": "blue",
        "WET": "green",
    }
    if year == 2018:
        compound_colors = compound_colors_2018
    else:
        compound_colors = compound_colors_normal

    stint_laps["fill"] = stint_laps["Compound"].map(compound_colors)

    # sort by FinishOrder
    stint_laps = stint_laps.sort_values(by=["FinishOrder"], ascending=[True])

    stint_laps_dict = stint_laps.to_dict("records")

    return {"strategy": stint_laps_dict}


# Your list of events
events_list = events

# Loop through each event
for event in events_list:
    session = "Race"

    strategy_dict = get_strategy(YEAR, event)

    # Specify the file path where you want to save the JSON data
    file_path = f"{event}/{session}/strategy.json"

    # Save the dictionary to a JSON file
    with open(file_path, "w") as json_file:
        json.dump(strategy_dict, json_file)

    print(f"Dictionary saved to {file_path}")
