import json
from shapely.geometry import shape, mapping, MultiLineString
from shapely.ops import unary_union
from collections import defaultdict

def create_enclosing_polygons(geojson_data):
    if isinstance(geojson_data, str):
        geojson_data = json.loads(geojson_data)

    # Separate polygons and lines
    blocks = []
    lines = []

    for feature in geojson_data['features']:
        geom_type = feature['geometry']['type']
        if geom_type == 'Polygon' and 'block_area_id' in feature['properties']:
            blocks.append(feature)
        elif geom_type == 'LineString' and 'vine_row_id' in feature['properties']:
            lines.append(feature)

    # Group lines by the block they fall within
    block_groups = defaultdict(list)
    for line in lines:
        line_shape = shape(line['geometry'])
        for block in blocks:
            block_shape = shape(block['geometry'])
            if block_shape.contains(line_shape):
                block_area_id = block['properties']['block_area_id']
                block_groups[block_area_id].append(line_shape)
                break

    # Create a convex hull for each group of lines within each block
    polygons = []
    for block in blocks:
        block_area_id = block['properties']['block_area_id']
        if block_area_id in block_groups:
            lines_in_block = block_groups[block_area_id]
            
            # Combine the lines into a single MultiLineString
            combined_lines = MultiLineString(lines_in_block)
            
            # Create a convex hull around the combined lines
            polygon = combined_lines.convex_hull
            
            # Create a geojson feature for the polygon
            polygon_feature = {
                "type": "Feature",
                "properties": {
                    "vine_row_boundary_id": str(block_area_id) + "_row_boundary"
                },
                "geometry": mapping(polygon)
            }
            
            polygons.append(polygon_feature)

    # Create a new FeatureCollection for the polygons
    polygon_feature_collection = {
        "type": "FeatureCollection",
        "features": polygons
    }

    # return polygon_feature_collection
    return json.dumps(polygon_feature_collection, indent=2)

# Example usage:
# geojson_data = json.loads(your_geojson_string)
# result = create_enclosing_polygons(geojson_data)
# print(json.dumps(result, indent=2))
