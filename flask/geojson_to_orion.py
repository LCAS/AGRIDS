import requests
import json

import uuid

import orion_add_vineyard # create_vineyard_entity
import orion_add_block # create_block_entity
import orion_add_vinerow # create_vine_row_entity
import orion_add_point_feature # create_point_feature_entity
import orion_add_line_feature # create_line_feature_entity
import orion_add_polygon_feature # create_polygon_feature_entity

def geojson_to_orion(geojson_data, vineyard_id):
    print("def geojson_to_orion")

    for feature in geojson_data["features"]:

        # Points (not vines)
        if feature["properties"]["feature_type"] == "point":
            name = feature["properties"].get("name", "Unknown")
            category = feature["properties"].get("category", "Unknown")
            class_string = feature["properties"].get("class", "Unknown")
            coordinates = feature["geometry"]["coordinates"]

            print("Point: " + str(name))
            orion_add_point_feature.create_point_feature_entity(name, category, class_string, vineyard_id, coordinates)

        # Lines (not vine rows)
        if feature["properties"]["feature_type"] == "line":
            name = feature["properties"].get("name", "Unknown")
            category = feature["properties"].get("category", "Unknown")
            class_string = feature["properties"].get("class", "Unknown")
            coordinates = feature["geometry"]["coordinates"]

            print("Line: " + str(name))
            orion_add_line_feature.create_line_feature_entity(name, category, class_string, vineyard_id, coordinates)

        # Polygons (not blocks)
        if feature["properties"]["feature_type"] == "polygon":
            name = feature["properties"].get("name", "Unknown")
            category = feature["properties"].get("category", "Unknown")
            class_string = feature["properties"].get("class", "Unknown")
            coordinates = feature["geometry"]["coordinates"]

            # Format coordinates
            coordinates_formatted = []                
            for sublist in coordinates:
                for item in sublist:
                    coordinates_formatted.append(item)            
            
            print("Polygon: " + str(name))
            orion_add_polygon_feature.create_polygon_feature_entity(name, category, class_string, vineyard_id, coordinates_formatted)

        # Vine Rows
        if feature["properties"]["feature_type"] == "row":
            user_defined_id = feature["properties"].get("user_defined_id", "Unknown")
            block_id = feature["properties"].get("block_id", "Unknown")
            anchor_post_distance = feature["properties"].get("anchor_post_distance", "Unknown")
            under_vine_width = feature["properties"].get("under_vine_width", "Unknown")
            vine_spacing = feature["properties"].get("vine_spacing", "Unknown")
            coordinates = feature["geometry"]["coordinates"]
            category = "row"
            class_string = "vineyard"
            
            print("Row: " + str(user_defined_id))
            orion_add_vinerow.create_vine_row_entity(str(uuid.uuid4()), block_id, str(vineyard_id), user_defined_id, 0, category, class_string, vine_spacing, under_vine_width, anchor_post_distance, coordinates)

        # Blocks
        if feature["properties"]["feature_type"] == "block":
            user_defined_id = feature["properties"].get("user_defined_id", "Unknown")
            name = feature["properties"].get("name", "Unknown")
            variety = feature["properties"].get("variety", "Unknown")
            #row_spacing_m = feature["properties"].get("row_spacing_m", "Unknown")
            variety = feature["properties"].get("variety", "Unknown")
            anchor_post_distance = feature["properties"].get("anchor_post_distance", "Unknown")
            under_vine_width = feature["properties"].get("under_vine_width", "Unknown")
            vine_spacing = feature["properties"].get("vine_spacing", "Unknown")
            name = feature["properties"].get("name", "Unknown")
            coordinates = feature["geometry"]["coordinates"]
            
            print("Block: " + str(user_defined_id))
            print("coordinates:" + str(coordinates))
            print("coordinates[0]:" + str(coordinates[0]))
            orion_add_block.create_block_entity(str(uuid.uuid4()), vineyard_id, user_defined_id, name, 0, variety, anchor_post_distance, under_vine_width, vine_spacing, "2024-01-01T00:00:00Z", "2024-12-31T00:00:00Z", coordinates[0])