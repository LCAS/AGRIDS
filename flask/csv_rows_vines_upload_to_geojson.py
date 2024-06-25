import pandas as pd
import geojson

def csv_to_geojson(file):
    '''
    CSV in the format 
    Point       Latitude    Longitude   Type        Number  Row     Variety
    ROW01VINE01 53.26818125 -0.52427621 Vine        1       1       Pinot Noir
    ROW01VINE02 53.26817004 -0.52427306 Vine        2       1       Pinot Noir
    ROW01VINE03 53.26815714 -0.52426999 Vine        3       1       Pinot Noir
    ROW01POLE01 53.26818842 -0.52427737 End Post    1       1
    ROW01POLE04 53.26803849 -0.52424047 End Post    1       2
    ROW02POLE01 53.26818522 -0.52431449 End Post    2       1
    '''
    
    df = pd.read_csv(file)
    # Initialize an empty list to store features
    features = []

    # Iterate through rows in the DataFrame
    for index, row in df.iterrows():
        if row['Type'] == 'Vine':
            # Create Point feature for Vine
            name = f"vine_row_{row['Row']}_vine_{row['Number']}"
            coordinates = [row['Longitude'], row['Latitude']]
            properties = {
                'Type': row['Type'],
                'Name': name,
                'Row': row['Row'],
                'Number': row['Number'],
                'Variety': row['Variety'],
                'VineRowID': row['Row']
            }
            feature = {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': coordinates
                },
                'properties': properties
            }
            features.append(feature)

    # Group end posts by row number
    end_posts = {}
    for index, row in df.iterrows():
        if row['Type'] == 'End Post':
            row_number = row['Row']
            if row_number not in end_posts:
                end_posts[row_number] = []
            end_posts[row_number].append({
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [row['Longitude'], row['Latitude']]
                },
                'properties': {
                    'Type': row['Type'],
                    'Number': row['Number'],
                    'Row': row['Row']
                }
            })

    # Create LineString features between consecutive end posts with the same row number
    for row_number, posts in end_posts.items():
        if len(posts) > 1:
            for i in range(len(posts) - 1):
                start_post = posts[i]
                end_post = posts[i + 1]
                line_coords = [
                    start_post['geometry']['coordinates'],
                    end_post['geometry']['coordinates']
                ]
                line_properties = {
                    'Type': 'Row',
                    #'Start': start_post['properties']['Number'],
                    #'End': end_post['properties']['Number'],
                    'Row': row_number
                }
                line_feature = {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'LineString',
                        'coordinates': line_coords
                    },
                    'properties': line_properties
                }
                features.append(line_feature)

    # Create a FeatureCollection from the list of features
    feature_collection = geojson.FeatureCollection(features)

    return feature_collection
