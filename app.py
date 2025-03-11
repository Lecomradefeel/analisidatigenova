# Controllo delle colonne dopo il merge
st.write("Colonne dopo il merge:", gdf_municipi.columns.tolist())

# Controllo dei dati per un municipio a caso
st.write("Anteprima dati per un municipio:", gdf_municipi.sample(1))

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
            voti = row[voti_col] if voti_col in gdf_municipi.columns and not pd.isna(row[voti_col]) else 0
            perc = row[perc_col] if perc_col in gdf_municipi.columns and not pd.isna(row[perc_col]) else 0
            tooltip_text += f"{lista}: {int(voti)} voti ({perc:.2f}%)<br>"

        folium.GeoJson(
            row["geometry"],
            tooltip=folium.Tooltip(tooltip_text)
        ).add_to(m)

    folium_static(m)
