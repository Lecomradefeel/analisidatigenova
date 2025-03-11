import streamlit as st

# Titolo della dashboard
st.title("Dashboard Elettorale Genova")

st.write("""
👋 Benvenuto nella Dashboard Elettorale di Genova!  
Seleziona una delle seguenti sezioni per accedere alle analisi dettagliate. 🚀
""")

# Sidebar con i link ai branch
st.sidebar.title("Seleziona una vista")

st.sidebar.page_link("mappa-municipi/app.py", label="🗺 Mappa per Municipio")
st.sidebar.page_link("mappa-sezioni/app.py", label="🗺 Mappa per Sezione")
st.sidebar.page_link("mappa-traffico/app.py", label="🚶 Mappa Traffico Pedonale")
st.sidebar.page_link("tabelle-voti/app.py", label="📋 Tabella Voti per Sezione")
st.sidebar.page_link("grafici-municipi/app.py", label="📊 Grafici Voti per Municipio")

st.write("⚠️ Seleziona una sezione dal menu a sinistra per iniziare.")
