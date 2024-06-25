import json
import numpy as np
from shapely.geometry import shape
from pyproj import Geod

def get_padded_bounding_box(geojson_string, padding_meters):
    """
    Calculate the bounding box coordinates that enclose all features in the GeoJSON
    and add a padding of specified meters to the final shape.

    Parameters:
    - geojson_string: str, a valid GeoJSON string.
    - padding_meters: float, padding in meters to add to the bounding box.

    Returns:
    - list of tuples representing the coordinates of the padded bounding box.
    """
    geojson_data = json.loads(geojson_string)

    # Extract all coordinates from the GeoJSON
    def extract_coordinates(geojson):
        coords = []
        if geojson['type'] == 'FeatureCollection':
            for feature in geojson['features']:
                geom = shape(feature['geometry'])
                coords.extend(list(geom.exterior.coords) if geom.geom_type == 'Polygon' else list(geom.coords))
        elif geojson['type'] == 'Feature':
            geom = shape(geojson['geometry'])
            coords.extend(list(geom.exterior.coords) if geom.geom_type == 'Polygon' else list(geom.coords))
        elif geojson['type'] in ['Polygon', 'MultiPolygon', 'LineString', 'MultiLineString', 'Point', 'MultiPoint']:
            geom = shape(geojson)
            coords.extend(list(geom.exterior.coords) if geom.geom_type == 'Polygon' else list(geom.coords))
        return coords

    all_coords = extract_coordinates(geojson_data)
    all_coords = np.array(all_coords)

    if all_coords.size == 0:
        raise ValueError("No valid coordinates found in the GeoJSON data.")

    # Convert to [longitude, latitude] format for pyproj
    all_coords_reversed = [[lon, lat] for lon, lat in all_coords]

    # Calculate the bounding box
    min_lon, min_lat = np.min(all_coords_reversed, axis=0)
    max_lon, max_lat = np.max(all_coords_reversed, axis=0)

    # Calculate the center latitude for the bounding box
    center_latitude = (min_lat + max_lat) / 2

    # Define a function to calculate the padding in degrees
    def meter_to_degree(meters, latitude):
        geod = Geod(ellps='WGS84')
        lon1, lat1, _ = geod.fwd(0, latitude, 90, meters)
        lon2, lat2, _ = geod.fwd(0, latitude, 270, meters)
        lon_padding = lon2 - lon1
        lat_padding = lat2 - lat1
        return lon_padding, lat_padding

    # Calculate padding in degrees
    lon_padding, lat_padding = meter_to_degree(padding_meters, center_latitude)

    # Create the padded bounding box
    padded_min_lon = min_lon - lon_padding
    padded_max_lon = max_lon + lon_padding
    padded_min_lat = min_lat - lat_padding
    padded_max_lat = max_lat + lat_padding

    # Create the bounding box coordinates in [longitude, latitude] format
    bounding_box_coords = [
        [padded_min_lon, padded_min_lat],
        [padded_max_lon, padded_min_lat],
        [padded_max_lon, padded_max_lat],
        [padded_min_lon, padded_max_lat],
        [padded_min_lon, padded_min_lat]
    ]

    return bounding_box_coords

# Example usage
# geojson_string = '{"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": {"type": "LineString", "coordinates": [[-0.976308, 51.595821], [-0.977365, 51.595324]]}, "properties": {"type": "row", "Row": "1"}}, {"type": "Feature", "geometry": {"type": "LineString", "coordinates": [[-0.976329, 51.595838], [-0.977386, 51.595342]]}, "properties": {"type": "row", "Row": "2"}}]}'
# padded_bbox = get_padded_bounding_box(geojson_string, 50)
# print(padded_bbox)
