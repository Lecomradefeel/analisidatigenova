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

# Rinominare la colonna nei municipi per uniformarla con df_voti
gdf_municipi.rename(columns={"NOME_MUNIC": "MUNICIPIO"}, inplace=True)

# Sommare i voti per AVS + PD + M5S
df_voti["PROGRESSISTI"] = df_voti[["AVS - Lista Sansa - Possibile", "PD", "M5S"]].sum(axis=1)

df_voti_municipi = df_voti.groupby("MUNICIPIO")["PROGRESSISTI"].sum().reset_index()
df_voti_sezioni = df_voti.groupby("SEZIONE")["PROGRESSISTI"].sum().reset_index()

# Unire i dati alle mappe
gdf_municipi = gdf_municipi.merge(df_voti_municipi, on="MUNICIPIO", how="left")
gdf_sezioni = gdf_sezioni.merge(df_voti_sezioni, on="SEZIONE", how="left")

# Creazione delle tabs
st.sidebar.title("Dashboard Elettorale Genova")
tabs = ["Mappa per Municipio", "Mappa per Sezione", "Mappa Traffico Pedonale", "Tabella Voti", "Grafici Municipi"]
selected_tab = st.sidebar.radio("Seleziona una vista", tabs)

# Tab 1: Mappa con i voti progressisti per municipio
if selected_tab == "Mappa per Municipio":
    st.header("Mappa dei voti progressisti per Municipio")
    m = folium.Map(location=[44.4056, 8.9463], zoom_start=12)
    folium.Choropleth(
        geo_data=gdf_municipi,
        name="Municipi",
        data=gdf_municipi,
        columns=["MUNICIPIO", "PROGRESSISTI"],
        key_on="feature.properties.MUNICIPIO",
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Voti AVS + PD + M5S"
    ).add_to(m)

    for _, row in gdf_municipi.iterrows():
        folium.GeoJson(
            row["geometry"],
            tooltip=folium.Tooltip(f"Municipio: {row['MUNICIPIO']}<br>Voti Progressisti: {row['PROGRESSISTI']}")
        ).add_to(m)

    folium_static(m)

# Tab 2: Mappa con i voti progressisti per sezione
elif selected_tab == "Mappa per Sezione":
    st.header("Mappa dei voti progressisti per Sezione")
    m = folium.Map(location=[44.4056, 8.9463], zoom_start=12)
    folium.Choropleth(
        geo_data=gdf_sezioni,
        name="Sezioni",
        data=gdf_sezioni,
        columns=["SEZIONE", "PROGRESSISTI"],
        key_on="feature.properties.SEZIONE",
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Voti AVS + PD + M5S"
    ).add_to(m)

    for _, row in gdf_sezioni.iterrows():
        folium.GeoJson(
            row["geometry"],
            tooltip=folium.Tooltip(f"Sezione: {row['SEZIONE']}<br>Voti Progressisti: {row['PROGRESSISTI']}")
        ).add_to(m)

    folium_static(m)

# Tab 3: Mappa punti di traffico pedonale (placeholder)
elif selected_tab == "Mappa Traffico Pedonale":
    st.header("Mappa dei punti di traffico pedonale")
    st.write("Dati da definire. Possiamo usare OpenStreetMap o fonti regionali.")

# Tab 4: Tabella con i voti per sezione
elif selected_tab == "Tabella Voti":
    st.header("Tabella Voti per Sezione")
    st.dataframe(df_voti.drop(columns=["UNITA_URBANISTICA", "CIRCOSCRIZIONE", "COD_MUNICIPIO", "ISCRITTI_TOT", "TOT_VOTI_VALIDI_LISTA", "SCH_BIANCHE", "SCH_NULLE", "VOTI_CONTESTATI"]))

# Tab 5: Grafici per municipi
elif selected_tab == "Grafici Municipi":
    st.header("Distribuzione dei voti per lista nei Municipi")
    df_voti_long = df_voti.melt(id_vars=["MUNICIPIO"], value_vars=["AVS - Lista Sansa - Possibile", "PD", "M5S"], var_name="Lista", value_name="Voti")
    fig = px.bar(df_voti_long, x="MUNICIPIO", y="Voti", color="Lista", title="Voti per lista nei Municipi", barmode="stack")
    st.plotly_chart(fig)

st.write("Dashboard creata con successo!")


