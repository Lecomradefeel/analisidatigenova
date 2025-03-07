import folium
import pandas as pd
import geopandas as gpd
import streamlit as st
import numpy as np
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster

# Titolo della pagina Streamlit
st.title("Mappa delle Sezioni Elettorali")

# Percorso del file Shapefile (se disponibile)
shapefile_path = "precincts_genova_original.shp"

# Caricare il file SHP con gestione avanzata della geometria
gdf = gpd.read_file(shapefile_path)

gdf["geometry"] = gdf["geometry"].apply(lambda geom: geom.buffer(0) if not geom.is_valid else geom)

# Percorso del file Excel
excel_path = "regionali2024_voti_lista_v2 accorpati.xlsx"

# Caricare i dati di voto
df_voti = pd.read_excel(excel_path, sheet_name="Worksheet")

# Convertire SEZIONE in intero per garantire la compatibilità
df_voti["SEZIONE"] = df_voti["SEZIONE"].astype(int)

gdf["SEZIONE"] = gdf["SEZIONE"].astype(int)

# Unire i dati geografici con i dati di voto
df_merged = gdf.merge(df_voti, on="SEZIONE", how="left")

# Convertire tutte le colonne di voto in numerico
df_merged[df_voti.columns[1:]] = df_merged[df_voti.columns[1:]].apply(pd.to_numeric, errors="coerce").fillna(0)

# Calcolare la percentuale di voti rispetto agli iscritti
df_merged["PERC_VOTI"] = (df_merged["TOT_VOTI_VALIDI_LISTA"] / df_merged["ISCRITTI_TOT"]) * 100

# Calcolare la percentuale di voti per lista evitando divisione per zero
df_merged["TOT_VOTI_VALIDI_LISTA"] = df_merged["TOT_VOTI_VALIDI_LISTA"].replace(0, np.nan)

df_merged["TOT_VOTI_VALIDI_LISTA"].fillna(1, inplace=True)  # Per evitare divisioni per zero

liste_partiti = [col for col in df_voti.columns if col not in ["SEZIONE", "ISCRITTI_TOT", "TOT_VOTI_VALIDI_LISTA"]]
for lista in liste_partiti:
    df_merged[f"PERC_{lista}"] = (df_merged[lista] / df_merged["TOT_VOTI_VALIDI_LISTA"]) * 100

# Riempire eventuali valori nulli generati dalla divisione per zero
df_merged = df_merged.fillna(0)

# Opzioni di visualizzazione
view_option = st.radio("Seleziona la vista della mappa:", ["Percentuale votanti", "Distribuzione per lista"])

# Creare la mappa centrata su Genova
mappa = folium.Map(location=[44.4056, 8.9463], zoom_start=12)

if view_option == "Percentuale votanti":
    choropleth = folium.Choropleth(
        geo_data=gdf,
        name="Sezioni elettorali",
        data=df_merged,
        columns=["SEZIONE", "PERC_VOTI"],
        key_on="feature.properties.SEZIONE",
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Percentuale voti espressi"
    ).add_to(mappa)

else:
    selected_lista = st.selectbox("Seleziona la lista/partito da visualizzare:", liste_partiti)
    choropleth = folium.Choropleth(
        geo_data=gdf,
        name="Distribuzione per lista",
        data=df_merged,
        columns=["SEZIONE", f"PERC_{selected_lista}"],
        key_on="feature.properties.SEZIONE",
        fill_color="Blues",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=f"Percentuale voti per {selected_lista}"
    ).add_to(mappa)

# Aggiungere popup con info per ogni sezione
for _, row in df_merged.iterrows():
    folium.GeoJson(
        row["geometry"],
        tooltip=folium.Tooltip(
            f"Sezione: {row['SEZIONE']}<br>"
            f"Percentuale voti espressi: {row['PERC_VOTI']:.2f}%<br>"
            f"{selected_lista if view_option == 'Distribuzione per lista' else ''}: {row[f'PERC_{selected_lista}']:.2f}%"
        ),
    ).add_to(mappa)

# Mostrare la mappa in Streamlit
folium_static(mappa)

st.write("Mappa caricata con successo!")


