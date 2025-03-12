import streamlit as st
import pandas as pd
import json
import folium
from streamlit_folium import folium_static

# Impostazioni della pagina
st.set_page_config(page_title="Dashboard Elettorale Genova", layout="wide")
st.markdown("""
    <style>
    body { background-color: black; color: white; }
    .stApp { background-color: black; color: white; }
    </style>
""", unsafe_allow_html=True)

# Caricare i dati dai file
file_excel = "/mnt/data/regionali2024_voti_lista_v2 accorpati.xlsx"
xls = pd.ExcelFile(file_excel)
df_voti = pd.read_excel(xls, sheet_name="Totali per sezione")
df_municipi = pd.read_excel(xls, sheet_name="Somma voti semplificata")
df_percentuali = pd.read_excel(xls, sheet_name="Percentuali")

# Caricare i file GeoJSON
file_municipi_geojson = "/mnt/data/Modified_Municipi_Genova.geojson"
file_sezioni_geojson = "/mnt/data/precincts_genova_original.geojson"
with open(file_municipi_geojson, "r", encoding="utf-8") as f:
    municipi_geojson = json.load(f)
with open(file_sezioni_geojson, "r", encoding="utf-8") as f:
    sezioni_geojson = json.load(f)

# Sidebar per la selezione della vista
st.sidebar.title("Seleziona la visualizzazione")
option = st.sidebar.radio("Scegli una mappa:", ["Mappa voti per Municipio", "Mappa voti per Sezione", "Grafici per Municipio"])

# Mappa voti per municipio
if option == "Mappa voti per Municipio":
    st.title("Mappa dei voti per Municipio")
    m = folium.Map(location=[44.4, 8.9], zoom_start=11, tiles='cartodb dark_matter')
    
    for feature in municipi_geojson["features"]:
        municipio = feature["properties"]["name"]
        voti_totali = df_municipi[df_municipi["Municipio"] == municipio]["Totale votanti"].sum()
        tooltip = f"Municipio: {municipio}<br>Voti Totali: {voti_totali}"
        folium.GeoJson(feature, tooltip=tooltip, style_function=lambda x: {"fillColor": "blue", "color": "white", "weight": 1, "fillOpacity": 0.5}).add_to(m)
    
    folium_static(m)

# Mappa voti per sezione
elif option == "Mappa voti per Sezione":
    st.title("Mappa dei voti per Sezione")
    m = folium.Map(location=[44.4, 8.9], zoom_start=11, tiles='cartodb dark_matter')
    
    for feature in sezioni_geojson["features"]:
        sezione = feature["properties"]["sezione"]
        voti_totali = df_voti[df_voti["SEZIONE"] == sezione]["Totale votanti"].sum()
        tooltip = f"Sezione: {sezione}<br>Voti Totali: {voti_totali}"
        folium.GeoJson(feature, tooltip=tooltip, style_function=lambda x: {"fillColor": "green", "color": "white", "weight": 1, "fillOpacity": 0.5}).add_to(m)
    
    folium_static(m)

# Grafico per Municipio
elif option == "Grafici per Municipio":
    st.title("Totale votanti per Municipio")
    st.bar_chart(df_municipi.set_index("Municipio")["Totale votanti"])

