from flask import Flask, request, jsonify
from pydantic import BaseModel
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from geopy.distance import geodesic
import json
import requests
import os

import google.generativeai as genai

from sat import ImgSat
from pc import retrieve_from_pinecone
from embed import get_model_and_tokenizer
from gemini import get_gemini_response

from pinecone import Pinecone

from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Load and preprocess the data when the app starts
cols = ['Id', 'Name', 'Date', 'Time', 'RecordID', 'Status', 'Lat', 'Lon',
        'MaxWind', 'MinPressure', '34kt_NE', '34kt_SE', '34kt_SW', '34kt_NW',
        '50kt_NE', '50kt_SE', '50kt_SW', '50kt_NW', '64kt_NE', '64kt_SE',
        '64kt_SW', '64kt_NW', 't']

dtypes = {
    'Id': 'string',
    'Name': 'string',
    'Date': 'datetime64[ns]',
    'Time': 'string',
    'RecordID': 'string',
    'Status': 'string',
    'Lat': 'float64',
    'Lon': 'float64',
    'MaxWind': 'float64',
    'MinPressure': 'float64',
    '34kt_NE': 'float64',
    '34kt_SE': 'float64',
    '34kt_SW': 'float64',
    '34kt_NW': 'float64',
    '50kt_NE': 'float64',
    '50kt_SE': 'float64',
    '50kt_SW': 'float64',
    '50kt_NW': 'float64',
    '64kt_NE': 'float64',
    '64kt_SE': 'float64',
    '64kt_SW': 'float64',
    '64kt_NW': 'float64'
}

genai.configure(api_key="")
gemini = genai.GenerativeModel("gemini-1.5.flash")
isat = ImgSat()

pc = Pinecone(api_key="")
index = pc.Index("news-hurricanes")
embed_model, embed_tokenizer = get_model_and_tokenizer()

# Read and preprocess the data
def load_data():
    data = []

    def convert_lat_lon(lat_str, lon_str):
        lat = float(lat_str[:-1])
        lon = float(lon_str[:-1])
        if lat_str.endswith('S'):
            lat = -lat
        if lon_str.endswith('W'):
            lon = -lon
        return lat, lon

    with open('hurdat2.txt', 'r') as file:
        name = ""
        id = ""
        skip = False
        for line in file:
            values = [value.strip() for value in line.strip().split(",")]
            if len(values) < 5:
                name = values[1]
                id = values[0]
                skip = int(values[2]) < 4
                continue
            if skip: continue
            lat, lon = convert_lat_lon(values[4], values[5])
            row = [id, name] + values[:4] + [lat, lon] + values[6:]
            data.append(row)

    df = pd.DataFrame.from_records(data, columns=cols).astype(dtypes)
    df['Date'] = pd.to_datetime(df['Date'])
    cutoff_date = datetime.now() - timedelta(days=15 * 365)
    df = df[df['Date'] >= cutoff_date]

    df['MaxRadius_km'] = df.apply(calculate_max_radius, axis=1)
    return df

# Calculate the maximum radius in kilometers
def calculate_max_radius(row):
    wind_radii = [
        row['34kt_NE'], row['34kt_SE'], row['34kt_SW'], row['34kt_NW'],
        row['50kt_NE'], row['50kt_SE'], row['50kt_SW'], row['50kt_NW'],
        row['64kt_NE'], row['64kt_SE'], row['64kt_SW'], row['64kt_NW']
    ]
    mx = max(wind_radii)
    if mx < 10:
        mx = 260.
    return mx * 1.852

# Haversine function to calculate distance
def haversine(lat1, lon1, lat2, lon2):
    lat1_rad = np.radians(lat1)
    lon1_rad = np.radians(lon1)
    lat2_rad = np.radians(lat2)
    lon2_rad = np.radians(lon2)
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = np.sin(dlat / 2.0)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2.0)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    r = 6371.0
    return r * c

# Find hurricanes that intersect with a given location
def find_intersecting_hurricanes(df, target_lat, target_lon):
    intersecting_hurricanes = []

    for _, row in df.iterrows():
        distance = haversine(row['Lat'], row['Lon'], target_lat, target_lon)
        if distance <= row['MaxRadius_km']:
            row['Distance_km'] = distance
            intersecting_hurricanes.append(row)

    return pd.DataFrame(intersecting_hurricanes)

# Input model for the API
class LocationInput(BaseModel):
    lat: float
    lng: float

# Load data at startup
df = load_data()

# API endpoint to find hurricanes
@app.route("/find_hurricanes", methods=['POST'])
def find_hurricanes():
    location = LocationInput(**request.json)
    target_lat = location.lat
    target_lon = location.lng

    intersecting_df = find_intersecting_hurricanes(df, target_lat, target_lon)
    top_5_ids = (
        intersecting_df.groupby('Id')
        .agg(Name=('Name', 'max'), Min_Distance_km=('Distance_km', 'min'), Max_Wind=('MaxWind', 'max'))
        .sort_values(by='Min_Distance_km')
        .head(5)
        .index.tolist()
    )

    matching_rows_df = df[df['Id'].isin(top_5_ids)]
    
    colors = ['#343131','#A04747','#D8A25E','#EEDF7A','#E2F1E7']
    hurricanes_json = {}
    idx = 0

    for hurricane_id, group in matching_rows_df.groupby('Id'):
        hurricanes_json[hurricane_id] = {
            'name': group['Name'].iloc[0],
            'maxSpeed': group['MaxWind'].max(),
            'color': colors[idx],
            'points': [{'lat': row['Lat'], 'lng': row['Lon'], 'r': row['MaxRadius_km'], 'speed': row['MaxWind']} for _, row in group.iterrows()]
        }
        idx += 1
    print(hurricanes_json)
    return jsonify(hurricanes_json)

def get_location_details(latitude, longitude):
    api_key = ""  # Replace with your API key
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&key={api_key}"
    response = requests.get(url)
    data = response.json()
    data = data['results'][0]

    # Extracting the ZIP code, state, and county
    zip_code = next(
        (component['long_name'] for component in data['address_components']
         if 'postal_code' in component['types']),
        None
    )

    state = next(
        (component['long_name'] for component in data['address_components']
         if 'administrative_area_level_1' in component['types']),
        None
    )

    county = next(
        (component['long_name'] for component in data['address_components']
         if 'administrative_area_level_2' in component['types']),
        None
    )

    return state, county, zip_code

def load_zip_data():
    try:
        df = pd.read_csv('insurance_data.csv', dtype={
            'ZIP code': str,
            'State': str,
            'City': str,
            'Average annual cost': float,
            'Percent difference from national average': float
        })
        return df
    except FileNotFoundError:
        print("CSV file not found. Make sure the file is placed in the correct location.")
        return pd.DataFrame()

df_zip = load_zip_data()

# Input model for ZIP code
class ZipInput(BaseModel):
    zipcode: str

@app.route("/get_zip_data", methods=['POST'])
def get_zip_data():
    zip_input = ZipInput(**request.json)
    zipcode = zip_input.zipcode
    matching_rows = df_zip[df_zip['ZIP code'] == zipcode]

    if matching_rows.empty:
        return jsonify({"detail": "ZIP code not found"}), 404

    # Convert the matching rows to a dictionary
    zip_data = matching_rows.to_dict(orient='records')
    return jsonify(zip_data[0])

def getZ(zipcode):
    # Filter the DataFrame for the requested ZIP code
    matching_rows = df_zip[df_zip['ZIP code'] == zipcode]

    if matching_rows.empty:
        matching_rows = df_zip[df_zip['ZIP code'] == "33592"]

    # Convert the matching rows to a dictionary
    zip_data = matching_rows.to_dict(orient='records')
    return zip_data[0]

@app.route("/analysis", methods=['POST'])
def get_info():
    inp = LocationInput(**request.json)
    state, county, zip = get_location_details(inp.lat, inp.lng)
    print(state, county, zip)
    dt = getZ(zip)
    rag, sources = retrieve_from_pinecone(index, embed_model, embed_tokenizer, state, county, zip)
    sat_vid, gemini_response = get_gemini_response(gemini, isat, inp.lat, inp.lng, rag, state, county, zip, dt["Average annual cost"], dt["Percent difference from national average"])
    ret = jsonify({
        "satelliteVideo": sat_vid,
        "geminiResponse": gemini_response,
        "sources": sources,
        "insurance cost": dt["Average annual cost"],
        "insurance percent diff": dt["Percent difference from national average"]
    })
    print("RET", ret)
    return ret

if __name__ == "__main__":
    app.run(debug=True)
