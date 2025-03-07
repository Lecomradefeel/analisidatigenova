import streamlit as st
import geopandas as gpd
import folium
from shapely.ops import unary_union
from streamlit_folium import st_folium
import pandas as pd
import matplotlib.pyplot as plt

# Caricare i dati
@st.cache_data
def load_data():
    file_geojson = "precincts_genova_original.geojson"  # GeoJSON delle sezioni
    file_voti = "regionali2024_voti_lista_v2 accorpati.xlsx"  # Dati sui voti
    file_statistiche = "statistiche_municipi.xlsx"  # Dati demografici
    
    # Caricare i poligoni delle sezioni
    gdf_sezioni = gpd.read_file(file_geojson)
    
    # Caricare i dati dei voti
    df_voti = pd.read_excel(file_voti)
    
    # Caricare i dati demografici
    df_statistiche = pd.read_excel(file_statistiche)
    
    return gdf_sezioni, df_voti, df_statistiche

gdf_sezioni, df_voti, df_statistiche = load_data()

# Accorpare le sezioni per MUNICIPIO
st.write("### Aggregazione per MUNICIPIO")
gdf_municipi = gdf_sezioni.dissolve(by="municipio")

gdf_municipi["geometry"] = gdf_sezioni.groupby("municipio")["geometry"].apply(lambda x: unary_union(x))

# Unire i dati di voto e le statistiche
st.write("### Unione con i dati di voto e statistiche")
df_voti["municipio"] = df_voti["MUNICIPIO"].str.lower()
df_statistiche["municipio"] = df_statistiche["MUNICIPIO"].str.lower()
gdf_municipi = gdf_municipi.merge(df_voti, left_on="municipio", right_on="municipio", how="left")
gdf_municipi = gdf_municipi.merge(df_statistiche, left_on="municipio", right_on="municipio", how="left")

# Creare una mappa interattiva con filtri
def create_map(selected_municipio):
    m = folium.Map(location=[44.4073, 8.9339], zoom_start=12)
    
    filtered_data = gdf_municipi if selected_municipio == "Tutti" else gdf_municipi[gdf_municipi["municipio"] == selected_municipio]
    
    for _, row in filtered_data.iterrows():
        folium.GeoJson(
            row["geometry"],
            name=row["municipio"],
            tooltip=f"{row['municipio'].capitalize()}\nVoti AVS: {row['AVS - Lista Sansa - Possibile']}\nPercentuale: {row['AVS_ratio']:.2%}\nEtà Media: {row['Età Media']}\nNati: {row['Nati']}"
        ).add_to(m)
    
    return m

# Aggiungere filtri per municipio e statistiche
st.write("### Filtri")
municipi_options = ["Tutti"] + list(gdf_municipi["municipio"].unique())
selected_municipio = st.selectbox("Seleziona un Municipio", municipi_options)

statistiche_options = ["Tutti", "Età Media", "Nati"]
selected_statistica = st.selectbox("Seleziona un dato statistico", statistiche_options)

st.write("### Mappa dei Municipi di Genova con Voti AVS e Dati Demografici")
mappa = create_map(selected_municipio)
st_folium(mappa, width=700, height=500)

# Analisi Statistica
st.write("### Analisi dei Voti e Dati Demografici")
fig, ax = plt.subplots()
filtered_data = gdf_municipi if selected_municipio == "Tutti" else gdf_municipi[gdf_municipi["municipio"] == selected_municipio]

if selected_statistica == "Età Media":
    filtered_data.plot(column="Età Media", cmap="Blues", legend=True, ax=ax)
    plt.title(f"Distribuzione dell'Età Media per {selected_municipio}")
elif selected_statistica == "Nati":
    filtered_data.plot(column="Nati", cmap="Greens", legend=True, ax=ax)
    plt.title(f"Distribuzione dei Nati per {selected_municipio}")
else:
    filtered_data.plot(column="AVS_ratio", cmap="Reds", legend=True, ax=ax)
    plt.title(f"Distribuzione percentuale voti AVS per {selected_municipio}")

st.pyplot(fig)

# Tabelle e approfondimenti
st.write("### Dati per Municipio")
st.dataframe(filtered_data[["municipio", "AVS - Lista Sansa - Possibile", "TOT_VOTI_VALIDI_LISTA", "AVS_ratio", "Età Media", "Nati"]])
