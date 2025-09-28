import streamlit as st
import pandas as pd
import altair as alt
import requests
from io import StringIO

def load_original_data():
    url = 'https://raw.githubusercontent.com/kaisupaukkeri/bi_project/main/data/processed/ilmanlaatu_tampere_helsinki.csv'
    response = requests.get(url)
    if response.status_code == 200:
        return pd.read_csv(StringIO(response.text))
    else:
        st.error("Failed to load data from GitHub.")
        return None

st.title("Ilmanlaadun vertailu: Helsinki vs Tampere")
st.write("Raportti perustuu avoimeen ilmanlaatudataan, joka on saatavilla ilmatieteenlaitoksen sivuilta. Tarkoituksena on vertailla kaupunkien keskustojen ilmanlaatua viikon ajalta, joten mittausasemiksi on valittu Tampereelta Linja-autoaseman sekä Helsingistä Mannerheimintien mittausasema.")

st.markdown("###### PM2.5")
st.write("Halkaisijaltaan alle 2,5 µm hiukkasia kutsutaan pienhiukkasiksi. Ne ovat niin pieniä, että ne voivat tunkeutua syvälle keuhkoihin. Korkeat PM2.5 pitoisuudet heikentävät ilmanlaatua merkittävästi ja voivat aiheuttaa hengitys- ja sydänsairauksia, erityisesti lapsille, vanhuksille ja astmaatikoille.")

st.markdown("###### AQI")
st.write("Ilmanlaatuindeksi (Air Quality Index) kuvaa ilmanlaadun yleistä tasoa, joka perustuu epäpuhtauksien mittauksiin. Mitä suurempi luku on, sitä huonompi on ilmanlaatu.")

st.markdown("###### NO2")
st.write("Typpidioksidi on kaasumainen epäpuhtaus, jota on pääsiasiassa liikenteen päästöissä. Typpidioksidi ärsyttää hengitysteitä ja voi pahentaa keuhkosairauksia.")


# CSV:n lukeminen
df = load_original_data()

# Muutetaan datetime aikamuotoon
df["datetime"] = pd.to_datetime(df["datetime"])

# Korjataan sarakenimet (helpompi käsitellä)
df = df.rename(columns={
    "Particulate matter < 2.5 µm": "PM25",
    "Air Quality Index": "AQI",
    "Nitrogen dioxide": "NO2"
})

# Taulukko keskiarvoista yleiskuvan saamiseksi
st.subheader("Yleiskuva kaupunkien ilmanlaadusta")
st.write("Tässä taulukossa on koottuna keskiarvot mittaustuloksista 7 vuorokauden ajalta.")
# Ryhmitellään keskiarvot kaikista mittareista (PM25, NO2, AQI) per location
keskiarvot = df.groupby("location")[["PM25", "NO2", "AQI"]].mean().reset_index()

# Näytetään siistissä muodossa
st.dataframe(keskiarvot, use_container_width=True)


st.subheader("Valitse kaupunki ja mittari ilmanlaadun tarkastelua varten.")

# Valitaan kaupungit
kaupungit = st.multiselect(
    "Valitse kaupungit:",
    options=df["location"].unique(),
    default=list(df["location"].unique())
)

# Suodatetaan data kaupungin perusteella
df_filtered = df[df["location"].isin(kaupungit)]

# Valitaan mittari
valinta = st.selectbox(
    "Valitse mittari:",
    ["PM25", "AQI", "NO2"]
)

# 1. Keskiarvot (pylväskaavio)
st.markdown("#####")
st.subheader(f"Pylväskaavio keskiarvoista: {valinta}")
st.write("")

keskiarvot = df_filtered.groupby("location")[[valinta]].mean().reset_index()

# Pylväsdiagrammeihin siistimmät nimet
keskiarvot["location"] = keskiarvot["location"].replace({
    "Helsinki Mannerheimintie": "Helsinki",
    "Tampere Linja-autoasema": "Tampere"
})



bar = alt.Chart(keskiarvot).mark_bar().encode(
    x=alt.X("location:N", title="Kaupunki"),
    y=alt.Y(f"{valinta}:Q", title=f"{valinta} (keskiarvo)"),
    color="location:N"
)
st.altair_chart(bar, use_container_width=True)


# 2. Viivakaavio
st.subheader(f"Viivakaavio: {valinta}")
line = alt.Chart(df_filtered).mark_line(point=True).encode(
    x=alt.X("datetime:T", title="Aika"),
    y=alt.Y(f"{valinta}:Q", title=valinta),
    color=alt.Color("location:N", title="Kaupunki"),
    tooltip=["datetime", "location", f"{valinta}"]
).properties(width=800, height=400)

st.altair_chart(line, use_container_width=False)

# 3. Pistekaavio
#st.subheader("Pistekaavio")
#scatter = alt.Chart(df_filtered).mark_point(size=60).encode(
#    x=alt.X("datetime:T", title="Aika"),
#    y=alt.Y(f"{valinta}:Q", title=valinta),
#    color=alt.Color("location:N", title="Kaupunki"),
#    tooltip=["datetime", "location", f"{valinta}"]
#).properties(width=800, height=400)

#st.altair_chart(scatter, use_container_width=False)


# Näytetään raakadata
st.subheader("Raakadata")
st.write(df.tail(10)) # Tulostetaan raakadatasta uusimmat arvot