import streamlit as st
from arcgis.gis import GIS
from arcgis.features import FeatureLayer
import pandas as pd

# Definiere die Parkplatzfunktion
def parking(use, sqm):
    rate_map = {
        'Wohnen': ((sqm * 0.8) / 90) * (0.7 + 0.15),
        'Gewerbe': 0.6 * 0.86 * 0.84 * (sqm / 100),
        'Büro': 0.6 * 0.86 * 2 * (sqm / 100),
        'Gastro': 0.6 * 0.86 * 15 * (sqm / 100),
        'Verkauf': 0.6 * 0.86 * 6.4 * (sqm / 100),
        'Bildung': 0.6 * 0.86 * 1.5 * (sqm / 100),
        'Kunst': 0.6 * 0.86 * 0.84 * (sqm / 100),
        'Lager': 0.6 * 0.86 * 0.11 * (sqm / 100),
    }
    return round(rate_map.get(use, 0), 0)

# Funktion, um die ArcGIS-Code auszuführen
def run_arcgis_code(username_v, passwort_v):
    try:
        # Initialisiere GIS
        gis = GIS(username=username_v, password=passwort_v)
        # Zugriff auf die Tabelle mit der Item ID
        item_id = "97780b8cac26484fbe561f3c59732435"
        table_item = gis.content.get(item_id)

        # Holen der Tabelle aus dem Item
        table_layer = table_item.tables[0]
        # Abfragen aller Features aus der Tabelle
        features = table_layer.query()

        # Konvertieren der Features in ein Spatially Enabled DataFrame (SDF)
        sdf = features.sdf
        # Konvertieren des Spatially Enabled DataFrame (SDF) in ein pandas DataFrame
        df = pd.DataFrame(sdf)

        # Anwenden der Parkplatzfunktion auf jede Zeile
        df['Parkplatz'] = df.apply(lambda row: parking(row['category'], row['Area_srf']), axis=1)
        # Aktualisieren der Features in der Tabelle mit den neuen 'Parkplatz' Werten
        updated_features = []
        for idx, row in df.iterrows():
            feature = features.features[idx]
            feature.attributes['Parkplatz'] = row['Parkplatz']
            updated_features.append(feature)

        # Anwenden der Updates auf die Tabelle
        table_layer.edit_features(updates=updated_features)


        # Anzeigen des aktualisierten DataFrames
        #st.write(df)
        return True

    except Exception as e:
        st.error(f"Login fehlgeschlagen: {e}")
        return False

# Streamlit-App-Layout
st.title("ArcGIS Parkplatzberechnung")

# Eingabefelder für Benutzername und Passwort
username_v = st.text_input("Benutzername")
passwort_v = st.text_input("Passwort", type="password")

if st.button('Parkplätze berechnen'):
    if run_arcgis_code(username_v, passwort_v):
        st.success("Parkplätze erfolgreich berechnet.")
    else:
        st.error("Ungültiger Benutzername oder Passwort. Bitte versuche es erneut.")
