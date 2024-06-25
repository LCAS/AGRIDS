from geographiclib.geodesic import Geodesic
from shapely.geometry import Point, Polygon
import numpy as np
from pyproj import Geod

def calculate_bearing(lat1, lon1, lat2, lon2):
    # Calculate bearing between two points
    return Geodesic.WGS84.Inverse(lat1, lon1, lat2, lon2)['azi1']

def extend_point(lat, lon, bearing, distance):
    # Extend a point along a given bearing by a specified distance

    result = Geodesic.WGS84.Direct(lat, lon, bearing, distance)
    return [result['lon2'], result['lat2']]

def calculate_polygon_area(coordinates):
    polygon = Polygon(coordinates)
    poly_area, _ = Geod(ellps="WGS84").geometry_area_perimeter(polygon)
    return poly_area

def generate_polygon(line, width):
    polygon = []
    for i in range(len(line) - 1):
        lat1, lon1 = line[i]
        lat2, lon2 = line[i+1]
        bearing = calculate_bearing(lat1, lon1, lat2, lon2)
        
        # Extend points on either side of the line
        point_1 = extend_point(lat1, lon1, (bearing - 90) % 360, width)
        point_2 = extend_point(lat1, lon1, (bearing + 90) % 360, width)
        
        polygon.extend([point_1, point_2])

    # Extend the last point in the line to create the final set of points
    lat_last, lon_last = line[-1]
    point_last_1 = extend_point(lat_last, lon_last, (bearing - 90) % 360, width)
    point_last_2 = extend_point(lat_last, lon_last, (bearing + 90) % 360, width)
    polygon.extend([point_last_1, point_last_2])

    # Sort the polygon points based on their angles relative to the line
    centroid = Point(np.mean([point[1] for point in polygon]), np.mean([point[0] for point in polygon]))
    angles = np.arctan2(np.array([point[0] - centroid.y for point in polygon]),
                        np.array([point[1] - centroid.x for point in polygon]))
    sorted_polygon = [point for _, point in sorted(zip(angles, polygon))]
    
    # Check the orientation of the polygon
    if Polygon(sorted_polygon).area < 0:
        # If the area is negative, the polygon is clockwise, so reverse the order
        sorted_polygon = sorted_polygon[::-1]

    # Close the polygon
    sorted_polygon.append(sorted_polygon[0])
    
    # Convert the polygon points to the desired format [longitude, latitude]
    formatted_polygon = [[point[1], point[0]] for point in sorted_polygon]

    area = calculate_polygon_area(formatted_polygon)

    return formatted_polygon, area


# Input line
#line = [
#    [-0.97823534, 51.597268698],
#    [-0.978246872, 51.597263294],
#    [-0.978320521, 51.597228782],
#    [-0.978389711, 51.59719636],
#    [-0.978458901, 51.597163938],
#    [-0.978528091, 51.597131516],
#    [-0.97859728, 51.597099094],
#    [-0.978622281, 51.597087379],
#    [-0.978633812, 51.597081975]
#]

# Width of the polygon (distance perpendicular to the line)
#width = 0.5  # in meters

# Generate the polygon
#polygon, area = generate_polygon(line, width)
#print(polygon)
#print(area)