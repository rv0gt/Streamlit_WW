import streamlit as st
from arcgis.gis import GIS
from arcgis.features import FeatureLayer
import pandas as pd

# Login-Funktion
def login(username_v, passwort_v):
    try:
        # Initialisiere GIS
        gis = GIS(username=username_v, password=passwort_v)
        return gis
    except Exception as e:
        st.error(f"Login fehlgeschlagen: {e}")
        return None

# Funktion zur Konvertierung des DataFrames in Features
def df_to_features(df):
    features = []
    for _, row in df.iterrows():
        feature = {
            "attributes": row.to_dict()
        }
        features.append(feature)
    return features

# Funktion zum Hochladen der Features in den Feature Layer
def update_features(layer, features):
    result = layer.edit_features(updates=features)
    return result


# Parkplatz-Berechnungsfunktion
def berechne_parkplaetze(features_df):
    try:
        # Anwenden der Parkplatzfunktion auf jede Zeile
        features_df['Parkplatz'] = features_df.apply(lambda row: parking(row['category'], row['Area_srf']), axis=1)
        return features_df
    except Exception as e:
        st.error(f"Fehler bei der Parkplatzberechnung: {e}")
        return None
    

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

# Streamlit-App-Layout
st.title("Parkplatzberechnung")

#Initialisierung Session states: 
if 'df' not in st.session_state:
    st.session_state.df = None
if 'gis' not in st.session_state:
    st.session_state.gis = None
if 'flayer' not in st.session_state:
    st.session_state.flayer = None
if 'edited_df' not in st.session_state:
    st.session_state.edited_df = None

# Eingabefelder für Benutzername und Passwort
username_v = st.text_input("Benutzername")
passwort_v = st.text_input("Passwort", type="password")

# Knopf zum Einloggen
if st.button('Einloggen'):
    gis = login(username_v, passwort_v)
    if gis:
        st.session_state.gis = gis
        st.success("Erfolgreich eingeloggt.")
    else:
        st.session_state.gis = None

# Knopf zum Daten abrufen
if st.session_state.gis is not None and st.button('Daten herunterladen'):
    # Feature Layer abrufen
    item_id = "99c41e925ec4402886932319b5b80c3f"
    table_item = st.session_state.gis.content.get(item_id)
    st.session_state.flayer = table_item.layers[0]

    # Features als DataFrame herunterladen
    st.session_state.df = pd.DataFrame.spatial.from_layer(st.session_state.flayer)
    st.success("Daten erfolgreich heruntergeladen.")


if st.session_state.df is not None: 

    # Create the grouped DataFrame
    columns_to_display = ['OBJECTID', 'haus', 'Area_srf', 'category', 'Parkplatz']
    df_update = st.session_state.df[columns_to_display]
    df_update = st.data_editor(df_update)

    if st.button("Parkplätze aktualisieren:"):
        st.session_state.edited_df = berechne_parkplaetze(df_update)
        #st.session_state.data = st.session_state.edited_df  # Aktualisiere die originalen Daten mit den bearbeiteten
        st.success("Parkplätze erfolgreich berechnet und Daten aktualisiert.")
        st.write("Neuberechnete Tabelle:")
        columns_to_display2 = ['OBJECTID', 'haus', 'Area_srf', 'category', 'Parkplatz']
        st.write(st.session_state.edited_df[columns_to_display2])

    # Button zum Hochladen der Daten
    if st.button("Daten hochladen"):
        edited_features = df_to_features(st.session_state.edited_df)
        update_result = update_features(st.session_state.flayer, edited_features)
        if update_result['updateResults'][0]['success']:
            st.success("Daten erfolgreich hochgeladen!")
        else:
            st.error("Fehler beim Hochladen der Daten!")

