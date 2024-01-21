import json
import os

import fastf1
import numpy as np
import utils
from fastf1.ergast import Ergast
import pandas as pd
fastf1.Cache.enable_cache("cache")
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

def lap_chart(
    year: int,
    event: str | int,
    session: str,
) -> any:
    ergast = Ergast()

    race_names_df = ergast.get_race_schedule(season=year, result_type="pandas")
    event_number = race_names_df[race_names_df["raceName"] == event]["round"].values[0]
    drivers_df = ergast.get_driver_info(
        season=year, round=event_number, result_type="pandas"
    )
    laptimes_df = ergast.get_lap_times(
        season=year, round=event_number, result_type="pandas", limit=2000
    ).content[0]
    laptimes_df = pd.merge(laptimes_df, drivers_df, how="left", on="driverId")

    results_df = ergast.get_race_results(
        season=year, round=event_number, result_type="pandas"
    ).content[0]
    results_df = results_df[["driverCode", "constructorName"]]

    # merge results_df on laptime_df
    laptimes_df = pd.merge(laptimes_df, results_df, how="left", on="driverCode")

    team_colors = utils.team_colors(year)
    # add team_colors to laptimes_df
    laptimes_df["fill"] = laptimes_df["constructorName"].map(team_colors)

    #  rename number as x and position as y
    laptimes_df.rename(
        columns={"number": "x", "position": "y", "driverCode": "id"}, inplace=True
    )

    lap_chart_data = []

    for driver in laptimes_df["id"].unique():
        data = laptimes_df[laptimes_df["id"] == driver]
        fill = data["fill"].values[0]
        data = data[["x", "y"]]
        data_dict = data.to_dict(orient="records")
        driver_dict = {"id": driver, "fill": fill, "data": data_dict}
        # add this to all_data
        lap_chart_data.append(driver_dict)

    lap_chart_dict = {"lapChartData": lap_chart_data}

    return lap_chart_dict


# Your list of events
events_list = events

# Loop through each event
for event in events_list:
    session = "Race"

    lap_position_dict = lap_chart(YEAR, event, session)

    # Specify the file path where you want to save the JSON data
    file_path = f"{event}/{session}/lap_position.json"

    # Save the dictionary to a JSON file
    with open(file_path, "w") as json_file:
        json.dump(lap_position_dict, json_file)

    print(f"Dictionary saved to {file_path}")
