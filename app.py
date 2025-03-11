import streamlit as st
import folium
import pandas as pd
import geopandas as gpd
from streamlit_folium import folium_static

# Percorsi dei file
data_voti = "regionali2024_voti_lista_v2 accorpati.xlsx"
data_municipi = "Modified_Municipi_Genova.geojson"

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

# Rinominare le colonne nei dataset per uniformarle
gdf_municipi.rename(columns={"NOME_MUNIC": "MUNICIPIO"}, inplace=True)
df_voti.rename(columns={"Municipio": "MUNICIPIO"}, inplace=True)
df_percentuali.rename(columns={"Municipio": "MUNICIPIO"}, inplace=True)

# Unire i dati dei voti e delle percentuali ai municipi
gdf_municipi = gdf_municipi.merge(df_voti, on="MUNICIPIO", how="left")
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
            if voti_col in gdf_municipi.columns and perc_col in gdf_municipi.columns and not pd.isna(row[voti_col]) and not pd.isna(row[perc_col]):
                tooltip_text += f"{lista}: {row[voti_col]} voti ({row[perc_col]:.2f}%)<br>"
        folium.GeoJson(
            row["geometry"],
            tooltip=folium.Tooltip(tooltip_text)
        ).add_to(m)

    folium_static(m)
