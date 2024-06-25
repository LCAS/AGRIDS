from geographiclib.geodesic import Geodesic

def extend_line(line, extension_distance):
    # Extract latitude and longitude coordinates
    start_lat, start_lon = line[0][1], line[0][0]
    end_lat, end_lon = line[-1][1], line[-1][0]

    # Calculate bearing from start to end point
    bearing = Geodesic.WGS84.Inverse(start_lat, start_lon, end_lat, end_lon)['azi1']

    # Calculate new start and end points
    new_start_point = Geodesic.WGS84.Direct(start_lat, start_lon, bearing + 180, float(extension_distance))
    new_end_point = Geodesic.WGS84.Direct(end_lat, end_lon, bearing, float(extension_distance))

    # Convert new start and end points back to latitude and longitude coordinates
    new_start_coord = [new_start_point['lon2'], new_start_point['lat2']]
    new_end_coord = [new_end_point['lon2'], new_end_point['lat2']]
    
    # Create two new lines as list of two coordinates
    line_start = [new_start_coord, [line[0][0], line[0][1]]]
    line_end = [[line[-1][0], line[-1][1]], new_end_coord]

    return [line_start, line_end]

# Example usage
#lines = [
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

#extended_lines = extend_line(lines)
#print(extended_lines)
