import requests
import json

import uuid

from shapely.geometry import LineString, Polygon

import orion_add_vineyard # create_vineyard_entity (assuming this exists)
import orion_add_block # create_block_entity (assuming this exists)
import orion_add_vinerow # create_vine_row_entity (assuming this exists)
import orion_add_point_feature # create_point_feature_entity (not used here)
import orion_add_line_feature # create_line_feature_entity (not used here)
import orion_add_polygon_feature # create_polygon_feature_entity (not used here)

def mapbox_to_orion_csv(vineyard_id, geojson_data):
    print("def mapbox_to_orion_csv")

    json_data = json.loads(geojson_data)["features"]

    # Collect linestring features
    linestring_features = []

    for feature in json_data:
        if feature["geometry"]["type"] == "LineString":
            #print("feature[geometry][type] == LineString")
            linestring_features.append(feature)

    #print("linestring_features" + str(linestring_features))

    for feature in json_data:
        # Blocks
        if feature["properties"]["type"] == "block":
            block_user_defined_id = feature["properties"].get("blockName", "Unknown")
            short_code = feature["properties"].get("shortCode", "Unknown")
            variety = feature["properties"].get("variety", "Unknown")
            vine_spacing = float(feature["properties"].get("vineSpacing", "Unknown"))
            under_vine_width = float(feature["properties"].get("underVineWidth", "Unknown"))
            anchor_post_distance = float(feature["properties"].get("anchorPostDistance", "Unknown"))
            coordinates = feature["geometry"]["coordinates"]

            print("Saved block " + str(block_user_defined_id) + " in vineyard " + str(vineyard_id))
            orion_add_block.create_block_entity(str(uuid.uuid4()), str(vineyard_id), str(short_code), str(block_user_defined_id), 0, variety, anchor_post_distance, under_vine_width, vine_spacing, "2024-01-01T00:00:00Z", "2024-12-31T00:00:00Z", coordinates[0])

            block_polygon = Polygon(coordinates[0]) 
            #print("block_polygon " + str(block_polygon))

            # Process linestrings against the block polygon
            linestring_features_to_remove = []
            for linestring_feature in linestring_features:
                #print("for linestring_feature in linestring_features")
                row_user_defined_id = linestring_feature["properties"].get("Row", 0)
                row_coordinates = linestring_feature["geometry"]["coordinates"]
                #print("row_coordinates " + str(row_coordinates))
                row_linestring = LineString(row_coordinates)
                #print("row_linestring " + str(list(row_linestring.coords)))

                if block_polygon.intersection(row_linestring):
                    #print("if block_polygon.within(row_linestring)")
                    print("Saved vine row " + str(row_user_defined_id) + " in block " + str(short_code) + " in vineyard " + str(vineyard_id))
                    # print(
                    #     "vine_row_id: " + str(uuid.uuid4()) + 
                    #     " block_id: " + str(short_code) + 
                    #     " vineyard_id: " + str(vineyard_id) + 
                    #     " user_defined_id: row_" + str(row_user_defined_id) + 
                    #     " orientation: " + str(0) + 
                    #     " category: vineyard" + 
                    #     " class_string: row" + 
                    #     " vine_spacing: " + vine_spacing +
                    #     " under_vine_width: " + under_vine_width +
                    #     " anchor_post_distance: " + anchor_post_distance +
                    #     " row_coordinates: " + str(row_coordinates)
                    # )
                    orion_add_vinerow.create_vine_row_entity(str(uuid.uuid4()), str(short_code), str(vineyard_id), "row_" + str(row_user_defined_id), 0, "vineyard", "row", vine_spacing, under_vine_width, anchor_post_distance, row_coordinates)
                    linestring_features_to_remove.append(linestring_feature)

            # Remove processed linestrings from the list
            for item in linestring_features_to_remove:
                linestring_features.remove(item)