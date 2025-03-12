import streamlit as st
import pandas as pd
import json
import folium
from streamlit_folium import folium_static
import plotly.express as px

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
option = st.sidebar.radio("Scegli una mappa:", ["Mappa voti per Municipio", "Mappa voti per Sezione", "Mappa degli Astenuti", "Grafici per Municipio", "Grafici per Sezione"])

# Mappa voti per municipio
if option == "Mappa voti per Municipio":
    st.title("Mappa dei voti per Municipio")
    m = folium.Map(location=[44.4, 8.9], zoom_start=11, tiles='cartodb dark_matter')
    
    for feature in municipi_geojson["features"]:
        municipio = feature["properties"]["name"]
        municipio_data = df_municipi[df_municipi["Municipio"] == municipio]
        voti_totali = municipio_data["Totale votanti"].sum()
        tooltip = f"Municipio: {municipio}<br>Voti Totali: {voti_totali}"<br>
        for col in municipio_data.columns[2:]:
            tooltip += f"{col}: {municipio_data[col].values[0]} voti ({df_percentuali[df_percentuali['Municipio'] == municipio][col].values[0]}%)<br>"
        folium.GeoJson(feature, tooltip=tooltip, style_function=lambda x: {"fillColor": "blue", "color": "white", "weight": 1, "fillOpacity": 0.5}).add_to(m)
    
    folium_static(m)

# Mappa voti per sezione
elif option == "Mappa voti per Sezione":
    st.title("Mappa dei voti per Sezione")
    m = folium.Map(location=[44.4, 8.9], zoom_start=11, tiles='cartodb dark_matter')
    
    for feature in sezioni_geojson["features"]:
        sezione = feature["properties"]["sezione"]
        voti_totali = df_voti[df_voti["SEZIONE"] == sezione]["Totale votanti"].sum()
        tooltip = f"Sezione: {sezione}<br>Voti Totali: {voti_totali}"<br>
        for col in df_voti.columns[3:]:
            tooltip += f"{col}: {df_voti[df_voti['SEZIONE'] == sezione][col].sum()} voti<br>"
        folium.GeoJson(feature, tooltip=tooltip, style_function=lambda x: {"fillColor": "green", "color": "white", "weight": 1, "fillOpacity": 0.5}).add_to(m)
    
    folium_static(m)

# Mappa degli Astenuti
elif option == "Mappa degli Astenuti":
    st.title("Mappa degli Astenuti")
    m = folium.Map(location=[44.4, 8.9], zoom_start=11, tiles='cartodb dark_matter')
    
    for feature in municipi_geojson["features"]:
        municipio = feature["properties"]["name"]
        municipio_data = df_municipi[df_municipi["Municipio"] == municipio]
        astenuti = municipio_data["Totale iscritti"].sum() - municipio_data["Totale votanti"].sum()
        perc_astenuti = (astenuti / municipio_data["Totale iscritti"].sum()) * 100
        tooltip = f"Municipio: {municipio}<br>Astenuti: {astenuti} ({perc_astenuti:.2f}%)"
        folium.GeoJson(feature, tooltip=tooltip, style_function=lambda x: {"fillColor": "red", "color": "white", "weight": 1, "fillOpacity": 0.5}).add_to(m)
    
    folium_static(m)

# Grafici per Municipio
elif option == "Grafici per Municipio":
    st.title("Totale voti per lista nei Municipi")
    df_melted = df_municipi.melt(id_vars=["Municipio"], var_name="Lista", value_name="Voti")
    fig = px.bar(df_melted, x="Municipio", y="Voti", color="Lista", title="Distribuzione voti per Municipio")
    st.plotly_chart(fig)

# Grafici per Sezione
elif option == "Grafici per Sezione":
    st.title("Totale voti per lista nelle Sezioni")
    df_melted = df_voti.melt(id_vars=["SEZIONE"], var_name="Lista", value_name="Voti")
    fig = px.bar(df_melted, x="SEZIONE", y="Voti", color="Lista", title="Distribuzione voti per Sezione")
    st.plotly_chart(fig)

