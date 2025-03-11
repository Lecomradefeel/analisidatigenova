import streamlit as st
import folium
import pandas as pd
import geopandas as gpd
from streamlit_folium import folium_static
import plotly.express as px

# Percorsi dei file
data_voti = "regionali2024_voti_lista_v2 accorpati.xlsx"
data_sezioni = "precincts_genova_original.geojson"
data_municipi = "Municipi Genova.geojson"

# Caricamento dati
@st.cache_data
def load_data():
    df_voti = pd.read_excel(data_voti)
    gdf_sezioni = gpd.read_file(data_sezioni)
    gdf_municipi = gpd.read_file(data_municipi)
    return df_voti, gdf_sezioni, gdf_municipi

df_voti, gdf_sezioni, gdf_municipi = load_data()

# Verificare i nomi delle colonne
st.write("Colonne in gdf_municipi:", gdf_municipi.columns.tolist())
st.write("Colonne in df_voti:", df_voti.columns.tolist())

# Assicurarsi che il nome della colonna sia coerente
if "municipio" in df_voti.columns:
    df_voti.rename(columns={"municipio": "MUNICIPIO"}, inplace=True)
if "municipio" in gdf_municipi.columns:
    gdf_municipi.rename(columns={"municipio": "MUNICIPIO"}, inplace=True)

# Unire i dati delle sezioni ai voti
gdf_sezioni = gdf_sezioni.merge(df_voti, on="SEZIONE", how="left")

# Unire i dati dei municipi ai voti aggregati
df_voti_municipi = df_voti.groupby("MUNICIPIO").sum().reset_index()
gdf_municipi = gdf_municipi.merge(df_voti_municipi, on="MUNICIPIO", how="left")

# Creazione delle tabs
st.sidebar.title("Dashboard Elettorale Genova")
tabs = ["Mappa per Municipio", "Mappa per Sezione", "Mappa Traffico Pedonale", "Tabella Voti", "Grafici Municipi"]
selected_tab = st.sidebar.radio("Seleziona una vista", tabs)

# Tab 1: Mappa con i voti per municipio
if selected_tab == "Mappa per Municipio":
    st.header("Mappa dei voti per Municipio")
    m = folium.Map(location=[44.4056, 8.9463], zoom_start=12)
    folium.Choropleth(
        geo_data=gdf_municipi,
        name="Municipi",
        data=gdf_municipi,
        columns=["MUNICIPIO", "TOT_VOTI_VALIDI_LISTA"],
        key_on="feature.properties.MUNICIPIO",
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Voti per Municipio"
    ).add_to(m)
    folium_static(m)

# Tab 2: Mappa con i voti per sezione
elif selected_tab == "Mappa per Sezione":
    st.header("Mappa dei voti per Sezione")
    m = folium.Map(location=[44.4056, 8.9463], zoom_start=12)
    folium.Choropleth(
        geo_data=gdf_sezioni,
        name="Sezioni",
        data=gdf_sezioni,
        columns=["SEZIONE", "TOT_VOTI_VALIDI_LISTA"],
        key_on="feature.properties.SEZIONE",
        fill_color="BuPu",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Voti per Sezione"
    ).add_to(m)
    folium_static(m)

# Tab 3: Mappa punti di traffico pedonale (placeholder)
elif selected_tab == "Mappa Traffico Pedonale":
    st.header("Mappa dei punti di traffico pedonale")
    st.write("Dati da definire. Possiamo usare OpenStreetMap o fonti regionali.")

# Tab 4: Tabella con i voti per sezione
elif selected_tab == "Tabella Voti":
    st.header("Tabella Voti per Sezione")
    st.dataframe(df_voti)

# Tab 5: Grafici per municipi
elif selected_tab == "Grafici Municipi":
    st.header("Grafico dei voti per Municipio")
    fig = px.bar(df_voti_municipi, x="MUNICIPIO", y="TOT_VOTI_VALIDI_LISTA", title="Voti per Municipio")
    st.plotly_chart(fig)

st.write("Dashboard creata con successo!")
