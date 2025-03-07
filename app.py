import folium
import pandas as pd
import geopandas as gpd
from folium.plugins import MarkerCluster

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

# Calcolare la percentuale di voti rispetto agli iscritti
df_merged["PERC_VOTI"] = (df_merged["TOT_VOTI_VALIDI_LISTA"] / df_merged["ISCRITTI_TOT"]) * 100

# Creare la mappa centrata su Genova
mappa = folium.Map(location=[44.4056, 8.9463], zoom_start=12)

# Aggiungere le sezioni alla mappa
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

# Aggiungere popup con info per ogni sezione
for _, row in df_merged.iterrows():
    folium.GeoJson(
        row["geometry"],
        tooltip=folium.Tooltip(
            f"Sezione: {row['SEZIONE']}<br>Percentuale voti: {row['PERC_VOTI']:.2f}%"
        ),
    ).add_to(mappa)

# Salvare la mappa in un file HTML
mappa.save("mappa_sezioni_voti_accorpati.html")

print("Mappa generata e salvata come 'mappa_sezioni_voti_accorpati.html'")
