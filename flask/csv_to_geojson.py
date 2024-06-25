import pandas as pd
import geojson

def csv_to_geojson(input_csv, output_geojson):
    '''
    CSV in the format 
    Ref	Latitude	Longitude	height	Code	Row
    1	51.59582063	-0.976308092	238.395	EP	91
    2	51.5958375	-0.976328625	238.51	EP	90
    3	51.59585509	-0.976350153	238.584	EP	89
    '''
    
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(input_csv)

    # Initialize an empty list to store features
    features = []

    # Check if 'Row' column exists in the file
    if 'Row' in df.columns:
        # Iterate through each unique row number in the DataFrame
        for row_number in df['Row'].unique():
            # Filter rows with the current row number
            rows = df[df['Row'] == row_number]

            # Check if there are exactly two rows with the same row number
            if len(rows) == 2:
                # Extract coordinates for the two rows
                coords = [
                    [rows.iloc[0]['Longitude'], rows.iloc[0]['Latitude']],
                    [rows.iloc[1]['Longitude'], rows.iloc[1]['Latitude']]
                ]
                # Create a LineString feature with the coordinates and row number as properties
                feature = geojson.Feature(geometry=geojson.LineString(coords), properties={"Row": str(row_number)})
                # Add the feature to the list of features
                features.append(feature)

    # If no 'Row' column exists in the file create a geojson of just points
    else:
        # Iterate through each row to create Point features
        for index, row in df.iterrows():
            # Extract coordinates from Latitude and Longitude columns
            coords = [row['Longitude'], row['Latitude']]
            # Create a Point feature with the coordinates and additional properties if needed
            feature = geojson.Feature(geometry=geojson.Point(coords))
            # Add the feature to the list of features
            features.append(feature)

    # Create a FeatureCollection from the list of features
    feature_collection = geojson.FeatureCollection(features)

    # Write the FeatureCollection to a GeoJSON file
    with open(output_geojson, 'w') as f:
        geojson.dump(feature_collection, f)

# Call the function with input and output file paths
csv_to_geojson('data/jojos_end_posts_rows_labelled.csv', 'data/output.geojson')