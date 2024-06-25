import requests

from pyproj import Geod

def calculate_line_length(coordinates):
    geod = Geod('+a=6378137 +f=0.0033528106647475126')
    
    # Check if coordinates are in the nested format
    if isinstance(coordinates[0][0], list):
        # Coordinates are in the nested format
        flat_coordinates = [point for segment in coordinates for point in segment]
    else:
        # Coordinates are already flat
        flat_coordinates = coordinates

    # Extract latitudes and longitudes from the flattened coordinates list
    lats = [coord[1] for coord in flat_coordinates]
    lons = [coord[0] for coord in flat_coordinates]

    total_length = geod.line_length(lons, lats)
    return total_length

FIWARE_ORION_BASE_URL = "http://cabbage-xps-8900:1026/v2/entities/"
fiware_orion_url_vine_row = f"{FIWARE_ORION_BASE_URL}?type=VineRow&limit=200"
vine_row_response = requests.get(fiware_orion_url_vine_row)

vine_row_data_list = []

if vine_row_response.status_code == 200:
    vine_row_data = vine_row_response.json()
    for vine_row_entity in vine_row_data:
        vine_row_id = vine_row_entity['id']
        user_defined_id = vine_row_entity['user_defined_id']['value']
        block_id = vine_row_entity['block_id']['value']
        coordinates = vine_row_entity['geom']['value']['coordinates']
        length = calculate_line_length(coordinates)
        vine_row_data_list.append({'vine_row_id': vine_row_id, 'user_defined_id': user_defined_id, 'coordinates': coordinates, 'length': length})

else:
    print(f"Failed to retrieve vine_row data. Status code: {vine_row_response.status_code}")

#print(vine_row_data_list[8]['coordinates'])

# Define the Geod object
#geod = Geod('+a=6378137 +f=0.0033528106647475126')

# Your list of coordinates
#coordinates = [
#    [[53.227176517, -0.549053745], [53.22716327, -0.548876719]],
#    [[53.227150826, -0.548941092], [53.227128346, -0.548984008]],
#    [[53.227127543, -0.549103366], [53.22705609, -0.548782842]]
#]

#coordinates = coordinates # vine_row_data_list[8]['coordinates']
#print(coordinates)

# Extract latitudes and longitudes from the coordinates list
#lats = [coord[1] for coord in coordinates]
#lons = [coord[0] for coord in coordinates]

# Calculate the total length of the line
#total_length = geod.line_length(lons, lats)

# Format the total_length to display three decimal places
#formatted_length = f"{total_length:.3f}"

# Print the result
#print(formatted_length)
