import datetime as dt
import pandas as pd

from fmiopendata.wfs import download_stored_query

pd.set_option('display.max_columns', None)

# Retrieve the latest hour of data from a bounding box
end_time = dt.datetime.now()
start_time = end_time - dt.timedelta(days=2)
# Convert times to properly formatted strings
start_time = start_time.isoformat(timespec="seconds") + "Z"
# -> 2025-09-28T12:00:00Z
end_time = end_time.isoformat(timespec="seconds") + "Z"
# -> 2025-09-28T13:00:00Z



obs = download_stored_query("urban::observations::airquality::hourly::multipointcoverage", # ILMANLAATUPARAMETRI
                            args=["bbox=23,60,26,63",
                                  "starttime=" + start_time,
                                  "endtime=" + end_time])

obs = download_stored_query("fmi::observations::airquality::hourly::multipointcoverage", # ILMANLAATUPARAMETRI
                            args=["place=Tampere",
                                  "starttime=" + start_time,
                                  "endtime=" + end_time])

latest_tstep = max(obs.data.keys())
location = max(obs.data[latest_tstep].keys())
obs.data[latest_tstep][location] # tulostaa arvot

records = []

for datet, locations in obs.data.items():
    for location, pollutants in locations.items():
        record = {'datetime': datet, 'location': location}
        for pollutant, values in pollutants.items():
            record[pollutant] = values['value']
        records.append(record)

df = pd.DataFrame(records)

df[df['location'].isin(['Tampere Linja-autoasema','Tampere Kaleva','Helsinki Teollisuuskatu', 'Helsinki Tapanila 2'])][['datetime','location', 'Particulate matter < 2.5 µm','Air Quality Index', 'Nitrogen dioxide']]