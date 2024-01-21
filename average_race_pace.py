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

def average_race_pace(
    year: int,
    event: str | int,
    session: str,
) -> any:
    f1session = fastf1.get_session(
        year,
        event,
        session,
        # backend="fastf1",
        # force_ergast=False,
    )
    f1session.load(telemetry=False, weather=False, messages=False)
    laps = f1session.laps

    laps = laps.loc[laps.LapNumber > 1]
    laps = laps.pick_track_status(
        "1",
    )
    laps["LapTime"] = laps.Sector1Time + laps.Sector2Time + laps.Sector3Time

    # convert LapTime to seconds
    laps["LapTime"] = laps["LapTime"].apply(lambda x: x.total_seconds())

    laps = laps.loc[laps.LapTime < laps.LapTime.min() * 1.07]

    df = laps[["LapTime", "Driver"]].groupby("Driver").mean().reset_index(drop=False)
    df = df.sort_values(by="LapTime").reset_index(drop=True)
    df["LapTime"] = df["LapTime"].round(3)
    df["Diff"] = (df["LapTime"] - df["LapTime"].min()).round(3)
    teams = laps[["Driver", "Team"]].drop_duplicates().reset_index(drop=True)
    # join teams and df
    df = df.merge(teams, on="Driver", how="left")

    # car_colors = utils.team_colors(year)

    # df["fill"] = df["Team"].map(car_colors)

    df_json = df.to_dict("records")

    return {"racePace": df_json}


# Your list of events
events_list = events

# Loop through each event
for event in events_list:
    session = "Race"

    race_pace_dict = average_race_pace(YEAR, event, session)

    # Specify the file path where you want to save the JSON data
    file_path = f"{event}/{session}/average_race_pace.json"

    # Save the dictionary to a JSON file
    with open(file_path, "w") as json_file:
        json.dump(race_pace_dict, json_file)

    print(f"Dictionary saved to {file_path}")
