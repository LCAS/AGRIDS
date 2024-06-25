from geopy.distance import geodesic
import math
import interpolate_points

def extend_line_points(coordinates_list, distance_to_extend, node_spacing_along_row, node_spacing_row_initial_offset, node_spacing_row_last_offset, row_width):
    extended_points = []
    extended_lines = []
    interpolated_nodes = []
    # distance_to_extend = 3
    # node_spacing_along_row = 10
    # node_spacing_row_initial_offset = 10
    # node_spacing_row_last_offset = 10
    # row_width = 5

    for line in coordinates_list:
        line_id = line['mid_row_line_id']
        line_coords = line['coordinates']
        start_point = line_coords[0]
        end_point = line_coords[-1]
        mid_row_line_length = line['length']

        node_spacing_along_row = round(mid_row_line_length / 5)
        node_spacing_row_initial_offset = round(mid_row_line_length / 5)
        node_spacing_row_last_offset = round(mid_row_line_length / 5)

        # Calculate the bearing between start and end points
        bearing_start_end = bearing(start_point, end_point)

        # Calculate the new points at a certain distance along the line
        new_start_point = geodesic(meters=distance_to_extend).destination(start_point, bearing_start_end + 180)
        new_end_point = geodesic(meters=distance_to_extend).destination(end_point, bearing_start_end)

        # Append the new points with line id
        extended_points.append({'topo_map_node_id': str(line_id) + '_node_start', 'coordinates': [new_start_point.latitude, new_start_point.longitude], 'type': 'Point'})
        extended_points.append({'topo_map_node_id': str(line_id) + '_node_end', 'coordinates': [new_end_point.latitude, new_end_point.longitude], 'type': 'Point'})

        # Interpolate points between the new start and end points
        interpolated_points = interpolate_points.interpolate_points([[new_start_point.latitude, new_start_point.longitude], [new_end_point.latitude, new_end_point.longitude]], node_spacing_along_row, node_spacing_row_initial_offset, node_spacing_row_last_offset)

        point_number = 0
        for point_coordinates in interpolated_points:
            interpolated_nodes.append({'topo_map_node_id': str(line_id) + '_node_' + str(point_number), 'coordinates': point_coordinates, 'type': 'Point'})
            point_number += 1

        # Connect the interpolated points
        for i in range(len(interpolated_points) - 1):
            extended_lines.append({
                'topo_map_edge_id': str(line_id) + '_edge_' + str(i),
                'coordinates': [interpolated_points[i], interpolated_points[i + 1]],
                'type': 'LineString'
            })

        # Connect new_start_point to the first interpolated point
        extended_lines.append({
            'topo_map_edge_id': str(line_id) + '_start_edge',
            'coordinates': [[new_start_point.latitude, new_start_point.longitude], interpolated_points[0]],
            'type': 'LineString'
        })

        # Connect new_end_point to the last interpolated point
        extended_lines.append({
            'topo_map_edge_id': str(line_id) + '_end_edge',
            'coordinates': [interpolated_points[-1], [new_end_point.latitude, new_end_point.longitude]],
            'type': 'LineString'
        })

        # Connect new_start_point to nearby points
        for point in extended_points:
            if point['type'] == 'Point':
                point_coords = point['coordinates']
                if geodesic((new_start_point.latitude, new_start_point.longitude), point_coords).meters <= row_width:
                    extended_lines.append({
                        'topo_map_edge_id': 'start_to_' + point['topo_map_node_id'],
                        'coordinates': [[new_start_point.latitude, new_start_point.longitude], point_coords],
                        'type': 'LineString'
                    })

        # Connect new_end_point to nearby points
        for point in extended_points:
            if point['type'] == 'Point':
                point_coords = point['coordinates']
                if geodesic((new_end_point.latitude, new_end_point.longitude), point_coords).meters <= row_width:
                    extended_lines.append({
                        'topo_map_edge_id': 'end_to_' + point['topo_map_node_id'],
                        'coordinates': [[new_end_point.latitude, new_end_point.longitude], point_coords],
                        'type': 'LineString'
                    })

    return extended_points, extended_lines, interpolated_nodes

# Function to calculate bearing between two points
def bearing(point1, point2):
    lat1, lon1 = point1
    lat2, lon2 = point2

    d_lon = lon2 - lon1

    y = math.sin(math.radians(d_lon)) * math.cos(math.radians(lat2))
    x = math.cos(math.radians(lat1)) * math.sin(math.radians(lat2)) - \
        math.sin(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.cos(math.radians(d_lon))

    initial_bearing = math.atan2(y, x)

    return math.degrees(initial_bearing)

# Example usage
# mid_row_line_coordinates_list = [
#     {'mid_row_line_id': 'row1_to_row2_mid_row_line', 'coordinates': [[-0.978411881, 51.5972804675], [-0.978642649, 51.5971723295]], 'type': 'LineString'}
# ]
# distance = 100  # Change this to the distance you want to extend the line by (in meters)

# extended_points = extend_line_points(mid_row_line_coordinates_list, distance)
# print(extended_points)
