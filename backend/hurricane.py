from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from geopy.distance import geodesic
from numba import jit


# Define the columns
cols = ['Id', 'Name', 'Date', 'Time', 'RecordID',
        'Status', 'Lat', 'Lon',
        'MaxWind', 'MinPressure',
        '34kt_NE', '34kt_SE', '34kt_SW', '34kt_NW',
        '50kt_NE', '50kt_SE', '50kt_SW', '50kt_NW',
        '64kt_NE', '64kt_SE', '64kt_SW', '64kt_NW', 't']

# Prepare a list to collect data
data = []

# Function to convert latitude/longitude strings to float
def convert_lat_lon(lat_str, lon_str):
    lat = float(lat_str[:-1])  # Remove the last character (N/S)
    lon = float(lon_str[:-1])  # Remove the last character (E/W)
    if lat_str.endswith('S'):
        lat = -lat  # Southern hemisphere
    if lon_str.endswith('W'):
        lon = -lon  # Western hemisphere
    return lat, lon

# Read the file and process the lines
with open('hurdat2.txt', 'r') as file:
    name = ""
    id = ""
    skip = False
    for line in file:
        values = [value.strip() for value in line.strip().split(",")]
        if len(values) < 5:
            name = values[1]
            id = values[0]
            if (cnt := int(values[2])) < 4:
                skip = True
            else:
                skip = False
            continue
        if skip: continue
        # Convert lat/lon
        lat, lon = convert_lat_lon(values[4], values[5])  # 'Lat' and 'Lon' columns
        # Append the row as a dictionary
        row = [id, name] + values[:4] + [lat, lon] + values[6:]
        data.append(row)

# Create the DataFrame using from_records with specified dtypes
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


df = pd.DataFrame.from_records(data, columns=cols).astype(dtypes)
pd.set_option('display.max_columns', None)

# Calculate the cutoff date for the last 10 years
cutoff_date = datetime.now() - timedelta(days=15 * 365)  # Approximation for 10 years

# Convert the 'Date' column to datetime for filtering
df['Date'] = pd.to_datetime(df['Date'])
df = df[df['Date'] >= cutoff_date]


# Print the tail of the DataFrame
print(df.tail())
# Print the median latitude and longitude
print("Median Latitude:", df['Lat'].median())
print("Median Longitude:", df['Lon'].median())

# Function to calculate the maximum radius in kilometers
def calculate_max_radius(row):
    """Calculate the maximum wind radius in kilometers from the wind speed columns."""
    wind_radii = [
        row['34kt_NE'], row['34kt_SE'], row['34kt_SW'], row['34kt_NW'],
        row['50kt_NE'], row['50kt_SE'], row['50kt_SW'], row['50kt_NW'],
        row['64kt_NE'], row['64kt_SE'], row['64kt_SW'], row['64kt_NW']
    ]
    mx = max(wind_radii)
    if mx < 10:
        mx = 260.
    return mx * 1.852  # Convert knots to kilometers

# Calculate maximum radius for each hurricane
df['MaxRadius_km'] = df.apply(calculate_max_radius, axis=1)
# Function to create bounding box and filter
# Haversine function to calculate the distance between two points
@jit(nopython=True)
def haversine(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance between two points on the Earth."""
    # Convert degrees to radians
    lat1_rad = np.radians(lat1)
    lon1_rad = np.radians(lon1)
    lat2_rad = np.radians(lat2)
    lon2_rad = np.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = np.sin(dlat / 2.0)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2.0)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    
    # Radius of Earth in kilometers
    r = 6371.0
    return r * c
def find_intersecting_hurricanes_fast(df, target_lat, target_lon):
    """Find hurricanes that intersect with a given latitude and longitude based on their MaxRadius_km."""
    intersecting_hurricanes = []

    for _, row in df.iterrows():
        hurricane_location = (row['Lat'], row['Lon'])
        distance = haversine(hurricane_location[0], hurricane_location[1], target_lat, target_lon)
        
        # Use MaxRadius_km for comparison
        if distance <= row['MaxRadius_km']:
            row['Distance_km'] = distance  # Add distance to the row
            intersecting_hurricanes.append(row)

    return pd.DataFrame(intersecting_hurricanes)# Example usage: Check for hurricanes intersecting with a position
# Example usage: Check for hurricanes intersecting with a position
target_lat = 27.9517  # example latitude
target_lon = -82.45    # example longitude

intersecting_hurricanes_df = find_intersecting_hurricanes_fast(df, target_lat, target_lon)

# Display the results
print(intersecting_hurricanes_df[['Id', 'Name', 'Lat', 'Lon', 'MaxRadius_km', 'Distance_km', 'MaxWind']])

# Get unique names with corresponding minimum distances and maximum wind speed
unique_names_distances = (
    intersecting_hurricanes_df.groupby('Id')
    .agg(
        Name=('Name', 'max'),
        Min_Distance_km=('Distance_km', 'min'),  # Get the minimum distance for each unique name
        Max_Wind=('MaxWind', 'max'),             # Get the maximum wind speed for each unique name
        Latest_Date=('Date', 'max'),

    )
    .reset_index()
)

# Sort by minimum distance
unique_names_distances_sorted = unique_names_distances.sort_values(by='Max_Wind')

# Print the unique names with their corresponding minimum distances and maximum wind speed, sorted by distance
print("Unique Hurricane Names with Minimum Distances and Maximum Winds (Sorted by Distance):")
print(unique_names_distances_sorted)

# Get the list of Ids from the top 5 entries in unique_names_distances_sorted
top_5_ids = unique_names_distances_sorted[:5]['Id'].tolist()
print(top_5_ids)

# Filter the original DataFrame to include only rows with Ids that match the top 5
matching_rows_df = df[df['Id'].isin(top_5_ids)]

# Display the rows that match the top 5 Ids
print("All matching rows for the top 5 Ids:")
print(matching_rows_df.tail())
print(len(matching_rows_df))


import json

# Create the JSON structure for the matching rows
hurricanes_json = {}
for hurricane_id, group in matching_rows_df.groupby('Id'):
    name = group['Name'].iloc[0]
    max_speed = group['MaxWind'].max()  # Max speed for that hurricane
    points = [
        {
            'lat': row['Lat'],
            'lng': row['Lon'],
            'r': row['MaxRadius_km']
        }
        for _, row in group.iterrows()
    ]
    
    # Determine color based on max_speed, for example:
    if max_speed >= 130:
        color = 'red'
    elif max_speed >= 90:
        color = 'orange'
    else:
        color = 'yellow'
    
    # Add to the hurricanes_json dictionary
    hurricanes_json[hurricane_id] = {
        'name': name,
        'maxSpeed': max_speed,
        'color': color,
        'points': points
    }

# Convert to JSON string
hurricanes_json_str = json.dumps(hurricanes_json, indent=4)

# Print the formatted JSON
print(hurricanes_json_str)

