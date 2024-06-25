import json

def create_geojson(features_lists):
    features_list = []
    
    # Function to add features
    def add_feature(feature_data):
        try:
            feature_type = feature_data['type']
            geometry = {
                "type": feature_type,
                "coordinates": feature_data['coordinates']
            }
            # Check if 'properties' tag exists, if not, add an empty dictionary
            properties = feature_data.get('properties', {})
            # Extract additional properties if they exist
            additional_properties = {k: v for k, v in feature_data.items() if k != 'type' and k != 'coordinates' and k != 'properties'}
            properties.update(additional_properties)
            feature = {
                "type": "Feature",
                "geometry": geometry,
                "properties": properties
            }
            features_list.append(feature)
        except KeyError as e:
            print(f"Missing key in feature data: {e}")
        except TypeError as e:
            print(f"Type error in feature data: {e}")
    
    # Add features from each list
    for feature_list in features_lists:
        for feature_data in feature_list:
            # Ensure feature_data is a dictionary and has the expected structure
            if isinstance(feature_data, dict) and 'type' in feature_data and 'coordinates' in feature_data:
                # Check if the feature is a polygon and if its coordinate array needs to be nested more deeply
                if feature_data['type'] == 'Polygon' and isinstance(feature_data['coordinates'], list) and not isinstance(feature_data['coordinates'][0][0], list):
                    feature_data['coordinates'] = [feature_data['coordinates']]
                add_feature(feature_data)
            else:
                print(f"Invalid feature data structure: {feature_data}")
    
    # Create GeoJSON file
    feature_collection = {
        "type": "FeatureCollection",
        "features": features_list
    }
    
    # Just return the json file
    return json.dumps(feature_collection, indent=2)

# # Example usage
# block_data_list = [
#     {
#         'type': 'Polygon',
#         'block_id': 1,
#         'user_defined_id': 'A1',
#         'name': 'Block A1',
#         'coordinates': [[-122.419416, 37.775732], [-122.428378, 37.775732], [-122.428378, 37.771853], [-122.419416, 37.771853], [-122.419416, 37.775732]],
#         'area': 0.01,
#         'perimeter': 0.1,
#         'total_rows': 5,
#         'total_row_length': 10.5,
#         'under_vine_area': 0.005
#     },
#     # Add more block data as needed
# ]

# vine_row_data_list = [
#     {
#         'type': 'LineString',
#         'vine_row_id': 1,
#         'user_defined_id': 'VR1',
#         'block_id': 1,
#         'coordinates': [[-122.419416, 37.775732], [-122.428378, 37.775732]],
#         'length': 0.01
#     },
#     # Add more vine row data as needed
# ]

# point_data_list = [
#     {
#         'type': 'Point',
#         'point_id': 1,
#         'user_defined_id': 'P1',
#         'coordinates': [-122.419416, 37.775732]
#     },
#     # Add more point data as needed
# ]

# Call the function with all lists of features
# create_geojson([block_data_list, vine_row_data_list, point_data_list], "data/output.geojson")
