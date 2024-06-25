from geopy.distance import geodesic

def interpolate_points(coords, point_spacing, initial_offset, last_offset):
    interpolated_points = []
    
    # Calculate the distance between the first and last coordinates
    total_distance = geodesic(coords[0], coords[-1]).meters
    
    # Adjust the total distance for initial and last offsets
    total_distance -= (initial_offset + last_offset)
    
    # Calculate the number of points to interpolate
    num_points = max(2, int(total_distance / point_spacing)) + 1  # Ensure at least 2 points, plus one for the first point
    
    # Calculate the distance between each interpolated point
    segment_distance = total_distance / (num_points - 1)  # -1 to include the last point
    
    # Interpolate points along the line
    for i in range(num_points):
        if i == 0:
            fraction = initial_offset / total_distance
        elif i == num_points - 1:
            fraction = 1  # Ensure the last point is at the end of the line
        else:
            fraction = (initial_offset + (i - 1) * segment_distance) / total_distance
        
        new_lat = coords[0][0] + fraction * (coords[-1][0] - coords[0][0])
        new_lon = coords[0][1] + fraction * (coords[-1][1] - coords[0][1])
        
        # Ensure no points are created within last_offset from the end
        if i == num_points - 1 and last_offset > 0:
            if geodesic((new_lat, new_lon), coords[-1]).meters <= last_offset:
                continue
        
        interpolated_points.append([new_lat, new_lon])
    
    return interpolated_points

# Example usage
# coordinates = [[-0.978437024, 51.597282185], [-0.978448555, 51.597276781], [-0.978473015, 51.597265319], 
#                [-0.978542205, 51.597232897], [-0.978611395, 51.597200475], [-0.978629638, 51.597191926], 
#                [-0.97864117, 51.597186522]]  # Example line coordinates
# point_spacing = 5  # Spacing in meters
# initial_offset = 1  # Initial offset in meters
# last_offset = 1  # Last offset in meters

# # Interpolate points for the entire line
# interpolated_points = interpolate_points(coordinates, point_spacing, initial_offset, last_offset)

# print(interpolated_points)
