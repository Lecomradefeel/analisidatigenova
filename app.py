import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit.components.v1 import html

# Percorsi dei file
data_voti = "regionali2024_voti_lista_v2 accorpati.xlsx"
data_municipi = "Modified_Municipi_Genova.geojson"
mappa_html = "mappa_municipi.html"

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
    st.write("Questa mappa mostra la distribuzione dei voti per municipio.")
    
    # Leggere il file HTML della mappa e visualizzarlo in Streamlit
    with open(mappa_html, "r", encoding="utf-8") as f:
        map_html = f.read()
    
    html(map_html, height=600, scrolling=True)
