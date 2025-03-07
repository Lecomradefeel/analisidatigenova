import folium
import pandas as pd
import geopandas as gpd
import streamlit as st
import numpy as np
from streamlit_folium import folium_static

# Titolo della pagina Streamlit
st.title("Mappa della Distribuzione dei Voti per Lista")

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

# Rimuovere colonne non necessarie
colonne_da_escludere = ["UNITA_URBANISTICA", "CIRCOSCRIZIONE", "COD_MUNICIPIO", "MUNICIPIO", "ISCRITTI_TOT", "SCH_BIANCHE", "SCH_NULLE", "VOTI_CONTESTATI"]
df_voti = df_voti.drop(columns=[col for col in colonne_da_escludere if col in df_voti.columns])

# Accorpare le colonne con nomi simili solo se esistono
pattern_mapping = {
    "Altro": [col for col in df_voti.columns if "Altro" in col],
    "Altro Bucci": [col for col in df_voti.columns if "Altro Bucci" in col],
    "Altro Orlando": [col for col in df_voti.columns if "Altro Orlando" in col],
    "FdI": [col for col in df_voti.columns if "FdI" in col],
    "PD": [col for col in df_voti.columns if "PD" in col],
    "M5S": [col for col in df_voti.columns if "M5S" in col],
    "FI": [col for col in df_voti.columns if "FI" in col],
    "AVS": [col for col in df_voti.columns if "AVS" in col]
}

for new_col, patterns in pattern_mapping.items():
    existing_columns = [col for col in patterns if col in df_voti.columns]
    if existing_columns:
        df_voti[new_col] = df_voti[existing_columns].sum(axis=1, min_count=1)
        df_voti.drop(columns=existing_columns, inplace=True)

# Definire liste_partiti prima dell'unione
liste_partiti = [col for col in df_voti.columns if col != "SEZIONE"]

# Unire i dati geografici con i dati di voto
df_merged = gdf.merge(df_voti, on="SEZIONE", how="left")

# Convertire tutte le colonne di voto in numerico
df_merged[liste_partiti] = df_merged[liste_partiti].apply(pd.to_numeric, errors="coerce").fillna(0)

# Creare una colonna con il totale effettivo dei voti validi
df_merged["TOT_VOTI_VALIDI"] = df_merged[liste_partiti].sum(axis=1)

# Calcolare la percentuale di voti per lista rispetto al totale effettivo dei voti validi
for lista in liste_partiti:
    df_merged[f"PERC_{lista}"] = (df_merged[lista] / df_merged["TOT_VOTI_VALIDI"]) * 100

# Pulizia dati per evitare errori nella mappa
df_merged = df_merged.replace([np.inf, -np.inf], 0).fillna(0)

# Creare la mappa centrata su Genova
mappa = folium.Map(location=[44.4056, 8.9463], zoom_start=12)

# Aggiungere popup con info per ogni sezione
for _, row in df_merged.iterrows():
    tooltip_text = f"Sezione: {row['SEZIONE']}<br>"
    for lista in liste_partiti:
        tooltip_text += f"{lista}: {row[lista]} voti ({row[f'PERC_{lista}']:.2f}%)<br>"
    
    folium.GeoJson(
        row["geometry"],
        tooltip=folium.Tooltip(tooltip_text),
    ).add_to(mappa)

# Mostrare la mappa in Streamlit
folium_static(mappa)

st.write("Mappa caricata con successo!")
