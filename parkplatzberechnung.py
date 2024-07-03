import streamlit as st
from arcgis.gis import GIS
from arcgis.features import FeatureLayer
import pandas as pd

# ArcGIS credentials
username_v = 'katarzyna.stefanska_ww'
passwort_v = 'Schule-1'

# Define the parking function
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

# Function to execute the ArcGIS code
def run_arcgis_code():
    # Initialize GIS
    gis = GIS(username=username_v, password=passwort_v)

    # Access the table layer using the Item ID
    item_id = "97780b8cac26484fbe561f3c59732435"
    table_item = gis.content.get(item_id)

    # Get the table layer from the item
    table_layer = table_item.tables[0]

    # Query all features from the table layer
    features = table_layer.query()

    # Convert the features to a Spatially Enabled DataFrame (SDF)
    sdf = features.sdf

    # Convert the Spatially Enabled DataFrame (SDF) to a pandas DataFrame
    df = pd.DataFrame(sdf)

    # Apply the parking function to each row
    df['Parkplatz'] = df.apply(lambda row: parking(row['category'], row['Area_srf']), axis=1)

    # Update the features in the table layer with the new 'Parkplatz' values
    updated_features = []
    for idx, row in df.iterrows():
        feature = features.features[idx]
        feature.attributes['Parkplatz'] = row['Parkplatz']
        updated_features.append(feature)

    # Apply the updates to the table layer
    table_layer.edit_features(updates=updated_features)

    # Display the updated DataFrame
    st.write(df)

# Streamlit app layout
st.title("ArcGIS Parking Calculation")

if st.button('Run ArcGIS Code'):
    run_arcgis_code()
    st.success("ArcGIS code executed successfully.")

