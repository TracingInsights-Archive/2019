import json
import os

import numpy as np
import pandas as pd
import requests
from io import BytesIO

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

def get_overtakes(year: int, event: str) -> any:
    def get_overtakes_df(year, event):
        if year == 2023:
            url = "https://docs.google.com/spreadsheets/d/1M4aepPJaIfdqE9oU3L-2CQqKIyubLXG4Q4cqWnyqxp4/export?format=csv"
        if year == 2022:
            url = "https://docs.google.com/spreadsheets/d/1cuS3B6hk4iQmMaRQoMTcogIInJpavnV7rKuEsiJnEbU/export?format=csv"
        if year == 2021:
            url = "https://docs.google.com/spreadsheets/d/1ANQnPVkefRmvzrmGvEqXoqQ4dBfgcI_R9FPg-0BcM34/export?format=csv"
        if year == 2020:
            url = "https://docs.google.com/spreadsheets/d/1eG9WTkXKzFT4NMh-WqHOMs5G0UuPGnb6wP4CnFD8uzY/export?format=csv"
        if year == 2019:
            url = "https://docs.google.com/spreadsheets/d/10nHg7BIs5ySh_dE9uuIz2lq-gRWcg02tIMr0EPgPvJs/export?format=csv"
        if year == 2018:
            url = "https://docs.google.com/spreadsheets/d/1MyAwQdczccdca_FAIiZKkqZNauNh3ts99JZ278S2OKc/export?format=csv"

        response = requests.get(url, timeout=10)
        df = pd.read_csv(BytesIO(response.content))
        df = df[["Driver", event]]
        # replace NaNs with 0s
        df = df.fillna(0)
        # convert numbers to ints
        df[event] = df[event].astype(int)
        # replace event with "overtakes"
        df = df.rename(columns={event: "overtakes"})
        return df

    def get_overtaken_df(year, event):
        if year == 2023:
            url = "https://docs.google.com/spreadsheets/d/1wszzx694Ot-mvA5YrFCpy3or37xMgnC0XpE8uNnJLWk/export?format=csv"
        if year == 2022:
            url = "https://docs.google.com/spreadsheets/d/19_XFDD3BZDIQVkNE4bG6dwuKvMaO4g5HNaUARGaJwhE/export?format=csv"
        if year == 2021:
            url = "https://docs.google.com/spreadsheets/d/1dQBHnd3AXEPNH5I75cjbzAAzi9ipqGk3v9eZT9eYKS4/export?format=csv"
        if year == 2020:
            url = "https://docs.google.com/spreadsheets/d/1snyntPMxYH4_KHSRI96AwBoJQrPbX6OanJAcqbYyW-Y/export?format=csv"
        if year == 2019:
            url = "https://docs.google.com/spreadsheets/d/11FfFkXErJg7F22iVwJo9XfLFAWucMBVlzL1qUGWxM3s/export?format=csv"
        if year == 2018:
            url = "https://docs.google.com/spreadsheets/d/1XJXAEyRpRS_UwLHzEtN2PdIaFJYGWSN6ypYN8Ecwp9A/export?format=csv"

        response = requests.get(url, timeout=10)
        df = pd.read_csv(BytesIO(response.content))
        df = df[["Driver", event]]
        # replace NaNs with 0s
        df = df.fillna(0)
        # convert numbers to ints
        df[event] = df[event].astype(int)
        df = df.rename(columns={event: "overtaken"})
        return df

    overtakes = get_overtakes_df(year, event)
    overtaken = get_overtaken_df(year, event)
    df = overtakes.merge(overtaken, on="Driver")

    # remove drivers with 0 overtakes and 0 overtaken
    df = df[(df["overtakes"] != 0) | (df["overtaken"] != 0)]

    # sort in the decreasing order of overtakes
    df = df.sort_values(
        by=["overtakes", "overtaken"], ascending=[False, True]
    ).reset_index(drop=True)
    # convert to dictionary
    df_dict = df.to_dict(orient="records")

    return {"overtakes": df_dict}


# Your list of events
events_list = events

# Loop through each event
for event in events_list:
    session = "Race"

    overtakes_dict = get_overtakes(YEAR, event)

    # Specify the file path where you want to save the JSON data
    file_path = f"{event}/{session}/overtakes.json"

    # Save the dictionary to a JSON file
    with open(file_path, "w") as json_file:
        json.dump(overtakes_dict, json_file)

    print(f"Dictionary saved to {file_path}")
