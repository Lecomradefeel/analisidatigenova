import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import pandas as pd

# Caricare i dati
@st.cache_data
def load_data():
    file_geojson = "precincts_genova_original.geojson"  # GeoJSON delle sezioni
    file_voti = "regionali2024_voti_lista_v2 accorpati.xlsx"  # Dati sui voti
    
    # Caricare i poligoni delle sezioni
    gdf_sezioni = gpd.read_file(file_geojson)
    
    # Caricare i dati dei voti
    df_voti = pd.read_excel(file_voti)
    
    return gdf_sezioni, df_voti

gdf_sezioni, df_voti = load_data()

# Unire i dati di voto con le sezioni elettorali
gdf_sezioni = gdf_sezioni.merge(df_voti, left_on="SEZIONE", right_on="SEZIONE", how="left")

# Creare una mappa interattiva
def create_map():
    m = folium.Map(location=[44.4073, 8.9339], zoom_start=12)
    
    for _, row in gdf_sezioni.iterrows():
        folium.GeoJson(
            row["geometry"],
            name=row["SEZIONE"],
            tooltip=f"Sezione: {row['SEZIONE']}\nVoti AVS: {row['AVS - Lista Sansa - Possibile']}\nPercentuale: {row['AVS_ratio']:.2%}"
        ).add_to(m)
    
    return m

st.write("### Mappa delle Sezioni Elettorali di Genova con Voti AVS")
mappa = create_map()
st_folium(mappa, width=700, height=500)

# Tabelle e approfondimenti
st.write("### Dati per Sezione Elettorale")
st.dataframe(gdf_sezioni[["SEZIONE", "AVS - Lista Sansa - Possibile", "TOT_VOTI_VALIDI_LISTA", "AVS_ratio"]])
