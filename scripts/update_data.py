import datetime as dt
import pandas as pd
from datetime import datetime

from fmiopendata.wfs import download_stored_query

# Retrieve the latest hour of data from a bounding box
end_time = dt.datetime.now() - dt.timedelta(hours=3)
start_time = end_time - dt.timedelta(days=7)
# Convert times to properly formatted strings
start_time = start_time.isoformat(timespec="seconds") + "Z"
# -> 2025-09-28T12:00:00Z
end_time = end_time.isoformat(timespec="seconds") + "Z"
# -> 2025-09-28T13:00:00Z

obs = download_stored_query("urban::observations::airquality::hourly::multipointcoverage", # ILMANLAATUPARAMETRI = Air Quality Parameter
                            args=["bbox=23,60,26,63",
                                  "starttime=" + start_time,
                                  "endtime=" + end_time])

# Exctact the desired information from the data and save it filtered_df
records = []

for datet, locations in obs.data.items():
    for location, pollutants in locations.items():
        record = {'datetime': datet, 'location': location}
        for pollutant, values in pollutants.items():
            record[pollutant] = values['value']
        records.append(record)

df = pd.DataFrame(records)
filtered_df = df[df['location'].isin(['Tampere Linja-autoasema','Helsinki Mannerheimintie', 'Vantaa Tikkurila Neilikkatie', 'Espoo Leppävaara Läkkisepänkuja'])][['datetime','location', 'Particulate matter < 2.5 µm','Air Quality Index', 'Nitrogen dioxide']]

# Save data in csv format
filtered_df.to_csv("data/processed/ilmanlaatu_tampere_helsinki.csv", index=False)