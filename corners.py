import fastf1
import os
import json
import utils

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
         
# sessions = [
#     "Practice 1",
#       "Practice 2",
#       "Practice 3",
#       # "Qualifying",
#       # "Race",
# ]

def sessions_available(year: int, event: str | int) -> any:
    # get sessions available for a given year and event
    event = str(event)
    data = utils.LatestData(year)
    sessions = data.get_sessions(event)
    return sessions



import fastf1
import os
import json
import pandas as pd



from fastf1.req import Cache

PROTO = "https"
HOST = "api.multiviewer.app"
HEADERS = {'User-Agent': f'FastF1/'}


def _make_url(path: str):
    return f"{PROTO}://{HOST}{path}"


def get_circuit(*, year: int, circuit_key: int) :
    """:meta private:
    Request circuit data from the MultiViewer API and return the JSON
    response."""
    url = _make_url(f"/api/v1/circuits/{circuit_key}/{year}")
    response = Cache.requests_get(url, headers=HEADERS)
    if response.status_code != 200:
        _logger.debug(f"[{response.status_code}] {response.content.decode()}")
        return None

    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return None


def get_circuit_info(*, year: int, circuit_key: int):
    """:meta private:
    Load circuit information from the MultiViewer API and convert it into
    as :class:``SessionInfo`` object.

    Args:
        year: The championship year
        circuit_key: The unique circuit key (defined by the F1 livetiming API)
    """
    data = get_circuit(year=year, circuit_key=circuit_key)

    if not data:
        _logger.warning("Failed to load circuit info")
        return None

    ret = list()
    for cat in ('corners', 'marshalLights', 'marshalSectors'):
        rows = list()
        for entry in data[cat]:
            rows.append((
                float(entry.get('trackPosition', {}).get('x', 0.0)),
                float(entry.get('trackPosition', {}).get('y', 0.0)),
                int(entry.get('number', 0)),
                str(entry.get('letter', "")),
                float(entry.get('angle', 0.0)),
                float(entry.get('length',0.0))
            ))
        ret.append(
            pd.DataFrame(
                rows,
                columns=['X', 'Y', 'Number', 'Letter', 'Angle', 'Distance']
            )
        )

    rotation = float(data.get('rotation', 0.0))

    circuit_info =  ret[0]
        

    return circuit_info

for event in events:
    sessions = utils.get_sessions(YEAR, event)
    for session in sessions:
        f1session = fastf1.get_session(YEAR, event, session)
        f1session.load()
        circuit_key = f1session.session_info['Meeting']['Circuit']['Key']
        circuit_info = get_circuit_info(year=YEAR,
                                        circuit_key=circuit_key)
        corner_info ={
            "CornerNumber": circuit_info['Number'].tolist(),
            "X": circuit_info['X'].tolist(),
            "Y": circuit_info['Y'].tolist(),
            "Angle": circuit_info['Angle'].tolist(),
            "Distance": (circuit_info['Distance']/10).tolist(),
        }

        driver_folder = f"{event}/{session}"
        file_path = f"{event}/{session}/corners.json"
        if not os.path.exists(driver_folder):
            os.makedirs(driver_folder)
        # Save the dictionary to a JSON file
        with open(file_path, "w") as json_file:
            json.dump(corner_info, json_file)

        

