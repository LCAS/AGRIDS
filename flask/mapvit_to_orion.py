import requests
import json

import uuid

import orion_add_vineyard # create_vineyard_entity
import orion_add_block # create_block_entity
import orion_add_vinerow # create_vine_row_entity
import orion_add_point_feature # create_point_feature_entity
import orion_add_line_feature # create_line_feature_entity
import orion_add_polygon_feature # create_polygon_feature_entity

def read_geojson(file_path):
    with open(file_path, 'r') as f:
        geojson_data = json.load(f)
    return geojson_data

def print_geojson(geojson_data):
    print(json.dumps(geojson_data, indent=4))

def mapvit_to_orion(geojson_data, vineyard_id, vine_spacing, under_vine_width, anchor_post_distance):

    feature_counts = {}
    for feature in geojson_data["features"]:
        feature_type = feature["properties"]["type"]
        feature_counts[feature_type] = feature_counts.get(feature_type, 0) + 1

        # Points (not vines)
        if feature["properties"]["type"] == "point":
            name = feature["properties"].get("name", "Unknown")
            category = feature["properties"].get("category", "Unknown")
            class_string = feature["properties"].get("class", "Unknown")
            coordinates = feature["geometry"]["coordinates"]
            #print(name)
            orion_add_point_feature.create_point_feature_entity(name, category, class_string, vineyard_id, coordinates)

        # Lines (not vine rows)
        if feature["properties"]["type"] == "line":
            name = feature["properties"].get("name", "Unknown")
            category = feature["properties"].get("category", "Unknown")
            class_string = feature["properties"].get("class", "Unknown")
            coordinates = feature["geometry"]["coordinates"]
            #print(name)
            orion_add_line_feature.create_line_feature_entity(name, category, class_string, vineyard_id, coordinates)

        # Polygons (not blocks)
        if feature["properties"]["type"] == "polygon":
            name = feature["properties"].get("name", "Unknown")
            category = feature["properties"].get("category", "Unknown")
            class_string = feature["properties"].get("class", "Unknown")
            coordinates = feature["geometry"]["coordinates"]

            # Format coordinates
            coordinates_formatted = []                
            for sublist in coordinates:
                for item in sublist:
                    coordinates_formatted.append(item)
            
            #print(name)
            #orion_add_polygon_feature.create_polygon_feature_entity(name, category, class_string, vineyard_id, coordinates_formatted)

        # Vine Rows
        if feature["properties"]["type"] == "row":
            name = feature["properties"].get("name", "Unknown")
            category = feature["properties"].get("category", "Unknown")
            class_string = feature["properties"].get("class", "Unknown")
            block = feature["properties"].get("block", "Unknown")
            short_code = feature["properties"].get("shortCode", "Unknown")
            coordinates = feature["geometry"]["coordinates"]
            #print(short_code)
            orion_add_vinerow.create_vine_row_entity(str(uuid.uuid4()), block, str(vineyard_id), short_code, 0, category, class_string, vine_spacing, under_vine_width, anchor_post_distance, coordinates)

        # Blocks
        if feature["properties"]["type"] == "block":
            name = feature["properties"].get("name", "Unknown")
            category = feature["properties"].get("category", "Unknown")
            class_string = feature["properties"].get("class", "Unknown")
            short_code = feature["properties"].get("shortCode", "Unknown")
            coordinates = feature["geometry"]["coordinates"]
            
            #print(name)
            orion_add_block.create_block_entity(str(uuid.uuid4()), vineyard_id, short_code, name, 0, 0, "2024-01-01T00:00:00Z", "2024-12-31T00:00:00Z", coordinates[0][0])

    return feature_counts

# if __name__ == "__main__":
#     file_path = "static/jojos_vineyard.geojson"
#     geojson_data = read_geojson(file_path)
#     #print_geojson(geojson_data)
    
#     vineyard_id = "jojo"
#     vine_spacing = 1
#     under_vine_width = 0.5
#     anchor_post_distance = 2

#     feature_counts = mapvit_to_orion(geojson_data, vineyard_id, vine_spacing, under_vine_width, anchor_post_distance)
#     for feature_type, count in feature_counts.items():
#         print(f"{feature_type} count: {count}")