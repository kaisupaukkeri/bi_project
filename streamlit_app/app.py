import streamlit as st
import pandas as pd
import altair as alt
import requests
from io import StringIO
from datetime import datetime

def load_original_data():
    url = 'https://raw.githubusercontent.com/kaisupaukkeri/bi_project/main/data/processed/ilmanlaatu_tampere_helsinki.csv'
    response = requests.get(url)
    if response.status_code == 200:
        return pd.read_csv(StringIO(response.text))
    else:
        st.error("Failed to load data from GitHub.")
        return None

# Write text to the raport
st.title("Ilmanlaadun vertailu: Tampere vs Uudenmaan suurimmat kaupungit")
st.write("Raportti perustuu avoimeen ilmanlaatudataan, joka on saatavilla ilmatieteenlaitoksen sivuilta. Tarkoituksena on vertailla kaupunkien keskustojen ilmanlaatua viikon ajalta, joten mittausasemiksi on valittu Tampereelta Linja-autoaseman, Helsingistä Mannerheimintien mittausasema, Espoosta Leppävaaran Läkkisepänkuja sekä Vantaalta Tikkurilan Neilikkatie.")

st.markdown("###### PM2.5")
st.write("Halkaisijaltaan alle 2,5 µm hiukkasia kutsutaan pienhiukkasiksi. Ne ovat niin pieniä, että ne voivat tunkeutua syvälle keuhkoihin. Korkeat PM2.5 pitoisuudet heikentävät ilmanlaatua merkittävästi ja voivat aiheuttaa hengitys- ja sydänsairauksia, erityisesti lapsille, vanhuksille ja astmaatikoille.")

st.markdown("###### AQI")
st.write("Ilmanlaatuindeksi (Air Quality Index) kuvaa ilmanlaadun yleistä tasoa, joka perustuu epäpuhtauksien mittauksiin. Mitä suurempi luku on, sitä huonompi on ilmanlaatu.")

st.markdown("###### NO2")
st.write("Typpidioksidi on kaasumainen epäpuhtaus, jota on pääsiasiassa liikenteen päästöissä. Typpidioksidi ärsyttää hengitysteitä ja voi pahentaa keuhkosairauksia.")


# Read CSV file
df = load_original_data()

# Change datetime variable to datetime
df["datetime"] = pd.to_datetime(df["datetime"])

# Change column names (easier to handle)
df = df.rename(columns={
    "Particulate matter < 2.5 µm": "PM25",
    "Air Quality Index": "AQI",
    "Nitrogen dioxide": "NO2"
})

# Table of averages to get an overview
st.subheader("Yleiskuva kaupunkien ilmanlaadusta")
st.write("Tässä taulukossa on koottuna keskiarvot mittaustuloksista 7 vuorokauden ajalta.")

# Add timestamp to report
csv_path = 'https://raw.githubusercontent.com/kaisupaukkeri/bi_project/main/data/processed/ilmanlaatu_tampere_helsinki.csv'
response = requests.head(csv_url)
last_modified = response.headers.get('Last-Modified')
last_updated = datetime.strptime(last_modified, '%a, %d %b %Y %H:%M:%S %Z')

st.caption(f"📅 Viimeisin päivitys: {last_updated.strftime('%Y-%m-%d %H:%M:%S')}")

# Group the averages from all meters (PM25, NO2, AQI) per location
keskiarvot = df.groupby("location")[["PM25", "NO2", "AQI"]].mean().reset_index()

# Näytetään siistissä muodossa
st.dataframe(keskiarvot, use_container_width=True)

# The latest update
#with open("../data/processed/last_updated.txt") as f:
#    last_updated = f.read()

#st.caption(f"📅 Viimeisin päivitys: {last_updated}")

st.subheader("Valitse kaupunki ja mittari ilmanlaadun tarkastelua varten.")
st.write("Oletukseksi on asetettu Tampereen ja Helsingin ilmanlaadun tarkastelu, mutta halutessasi voit vertailla kaikkien neljän mittausaseman ilmanlaatuja.")

# Choose cities
kaupungit = st.multiselect(
    "Valitse kaupungit:",
    options=df["location"].unique(),
    #default=list(df["location"].unique())
    default=["Helsinki Mannerheimintie", "Tampere Linja-autoasema"]
)

# Filter data by city
df_filtered = df[df["location"].isin(kaupungit)]

# Choose a metric
valinta = st.selectbox(
    "Valitse mittari:",
    ["PM25", "AQI", "NO2"]
)

# 1. The averages (bar chart)
st.markdown("#####")
st.subheader(f"Pylväskaavio keskiarvoista: {valinta}")
st.write("")

keskiarvot = df_filtered.groupby("location")[[valinta]].mean().reset_index()

# Cleanest names to bar chart
keskiarvot["location"] = keskiarvot["location"].replace({
    "Helsinki Mannerheimintie": "Helsinki",
    "Tampere Linja-autoasema": "Tampere",
    "Espoo Leppävaara Läkkisepänkuja": "Espoo",
    "Vantaa Tikkurila Neilikkatie": "Vantaa"
})

bar = alt.Chart(keskiarvot).mark_bar().encode(
    x=alt.X("location:N", title="Kaupunki"),
    y=alt.Y(f"{valinta}:Q", title=f"{valinta} (keskiarvo)"),
    color="location:N"
)
st.altair_chart(bar, use_container_width=True)


# 2. Line chart
st.subheader(f"Viivakaavio: {valinta}")
line = alt.Chart(df_filtered).mark_line(point=True).encode(
    x=alt.X("datetime:T", title="Aika"),
    y=alt.Y(f"{valinta}:Q", title=valinta),
    color=alt.Color("location:N", title="Kaupunki"),
    tooltip=["datetime", "location", f"{valinta}"]
).properties(width=800, height=400)

st.altair_chart(line, use_container_width=False)

# 3. Dot chart
#st.subheader("Pistekaavio")
#scatter = alt.Chart(df_filtered).mark_point(size=60).encode(
#    x=alt.X("datetime:T", title="Aika"),
#    y=alt.Y(f"{valinta}:Q", title=valinta),
#    color=alt.Color("location:N", title="Kaupunki"),
#    tooltip=["datetime", "location", f"{valinta}"]
#).properties(width=800, height=400)

#st.altair_chart(scatter, use_container_width=False)

# Show raw data
st.subheader("Raakadata")
st.write(df.tail(10)) # Print latest values from raw data