import streamlit as st
import folium
import pandas as pd
import geopandas as gpd
from streamlit_folium import folium_static

# Percorsi dei file
data_voti = "regionali2024_voti_lista_v2 accorpati.xlsx"
data_municipi = "Municipi Genova.geojson"

# Liste di interesse
liste_partiti = ["Lega", "FdI", "FI", "AVS", "PD", "M5S", "PCI, PaP, RC", "Altro Bucci", "Altro Orlando", "Altro"]

# Caricamento dati
@st.cache_data
def load_data():
    df_voti = pd.read_excel(data_voti, sheet_name="Somma voti semplificata")
    df_percentuali = pd.read_excel(data_voti, sheet_name="Percentuali")
    gdf_municipi = gpd.read_file(data_municipi)
    return df_voti, df_percentuali, gdf_municipi

df_voti, df_percentuali, gdf_municipi = load_data()

# Stampiamo i nomi delle colonne per verificare il problema
st.write("Colonne in df_voti:", df_voti.columns.tolist())
st.write("Colonne in df_percentuali:", df_percentuali.columns.tolist())
st.write("Colonne in gdf_municipi:", gdf_municipi.columns.tolist())

# Rinominare la colonna nei municipi per uniformarla con df_voti
if "NOME_MUNIC" in gdf_municipi.columns:
    gdf_municipi.rename(columns={"NOME_MUNIC": "MUNICIPIO"}, inplace=True)

if "NOME_MUNIC" in df_voti.columns:
    df_voti.rename(columns={"NOME_MUNIC": "MUNICIPIO"}, inplace=True)

if "NOME_MUNIC" in df_percentuali.columns:
    df_percentuali.rename(columns={"NOME_MUNIC": "MUNICIPIO"}, inplace=True)

# Controllare se "MUNICIPIO" esiste ora
if "MUNICIPIO" not in df_voti.columns:
    st.error("⚠️ Errore: 'MUNICIPIO' non trovato in df_voti!")
if "MUNICIPIO" not in df_percentuali.columns:
    st.error("⚠️ Errore: 'MUNICIPIO' non trovato in df_percentuali!")
if "MUNICIPIO" not in gdf_municipi.columns:
    st.error("⚠️ Errore: 'MUNICIPIO' non trovato in gdf_municipi!")

# Se le colonne sono presenti, procediamo con il merge
if "MUNICIPIO" in df_voti.columns and "MUNICIPIO" in gdf_municipi.columns:
    gdf_municipi = gdf_municipi.merge(df_voti, on="MUNICIPIO", how="left")
if "MUNICIPIO" in df_percentuali.columns and "MUNICIPIO" in gdf_municipi.columns:
    gdf_municipi = gdf_municipi.merge(df_percentuali, on="MUNICIPIO", how="left", suffixes=("_VOTI", "_PERC"))

# Creazione della sidebar per navigazione
st.sidebar.title("Seleziona una vista")
sezione = st.sidebar.radio("", ["🏠 Home", "🗺 Mappa Municipi"])

# Pagina Home
if sezione == "🏠 Home":
    st.title("Dashboard Elettorale Genova")
    st.write("""
    👋 Benvenuto nella Dashboard Elettorale di Genova!  
    Seleziona una delle seguenti sezioni dal menu a sinistra per accedere ai dati.
    """)

# Pagina Mappa Municipi
elif sezione == "🗺 Mappa Municipi":
    st.header("Mappa dei voti per Municipio")
    m = folium.Map(location=[44.4056, 8.9463], zoom_start=12)

    # Aggiungere i tooltip con i voti e le percentuali
    for _, row in gdf_municipi.iterrows():
        tooltip_text = f"<b>Municipio: {row['MUNICIPIO']}</b><br>"
        for lista in liste_partiti:
            voti_col = f"{lista}_VOTI"
            perc_col = f"{lista}_PERC"
            if voti_col in gdf_municipi.columns and perc_col in gdf_municipi.columns:
                tooltip_text += f"{lista}: {row[voti_col]} voti ({row[perc_col]:.2f}%)<br>"
        folium.GeoJson(
            row["geometry"],
            tooltip=folium.Tooltip(tooltip_text)
        ).add_to(m)

    folium_static(m)
