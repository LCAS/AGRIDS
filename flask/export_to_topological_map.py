import yaml
import math
import datetime
import pyproj

def haversine(lat1, lon1, lat2, lon2):
    # Radius of the Earth in meters
    R = 6371000

    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c

    return distance

def convert_to_meters(coordinates, center_coordinates):
    center_lon, center_lat = center_coordinates
    lon, lat = coordinates

    # Approximate conversion factor for latitude and longitude to meters
    lat_to_m = 111111  # 1 degree of latitude is approximately 111,111 meters
    lon_to_m = 111111 * math.cos(math.radians(center_lat))  # 1 degree of longitude is approximately 111,111 meters * cos(latitude)

    # Calculate the distance from the center in meters
    x_dist = (lon - center_lon) * lon_to_m
    y_dist = (lat - center_lat) * lat_to_m

    return x_dist, y_dist

def find_centre(topo_map_point_list, topo_map_line_list):
    print("def find_centre")
    # Extract coordinates from point list
    point_coords = [point['coordinates'] for point in topo_map_point_list]
    #print("point_coords: " + str(point_coords))

    # Extract coordinates from line list
    line_coords = [coord for line in topo_map_line_list for coord in line['coordinates']]
    #print("line_coords: " + str(line_coords))

    # Combine all coordinates
    all_coords = point_coords + line_coords
    #print("all_coords: " + str(all_coords))

    # Separate latitudes and longitudes
    latitudes = [coord[1] for coord in all_coords]
    longitudes = [coord[0] for coord in all_coords]

    # Calculate mean latitude and longitude
    mean_latitude = sum(latitudes) / len(latitudes)
    mean_longitude = sum(longitudes) / len(longitudes)

    center_coordinates = (mean_latitude, mean_longitude)
    #print("center_coordinates: " + str(center_coordinates))
    return center_coordinates

def generate_datum_yaml(center_coordinates):
    data = {
        'datum_latitude': center_coordinates[0],
        'datum_longitude': center_coordinates[1]
    }

    return yaml.dump(data, default_flow_style=False)

def generate_topological_map(topo_map_point_list, last_updated, metric_map, name, center_coordinates):
    topo_map_data = {
        "meta": {
            "last_updated": last_updated,
            "metric_map": metric_map,
            "name": name
        },
        "nodes": []
    }

    # Create node entries
    node_dict = {}
    for point in topo_map_point_list:
        lon_meters, lat_meters = convert_to_meters(point['coordinates'], center_coordinates)
        node_entry = {
            "meta": {
                "map": metric_map,
                "node": point['topo_map_node_id'],
                "pointset": name
            },
            "node": {
                "edges": [],
                "localise_by_topic": "",
                "name": point['topo_map_node_id'],
                "parent_frame": "map",
                "pose": {
                    "orientation": {"w": 0, "x": 0, "y": 0, "z": 0},
                    "position": {"x": lon_meters, "y": lat_meters, "z": 0}
                },
                "properties": {
                    "xy_goal_tolerance": 0.3,
                    "yaw_goal_tolerance": 0.1
                },
                "restrictions_planning": "True",
                "restrictions_runtime": "obstacleFree_1",
                "verts": [{"x": lon_meters, "y": lat_meters}]
            }
        }
        topo_map_data["nodes"].append(node_entry)
        node_dict[point['topo_map_node_id']] = point

    # Create edge entries
    for node_id_1, node_1 in node_dict.items():
        for node_id_2, node_2 in node_dict.items():
            if node_id_1 != node_id_2 and node_id_1 in node_id_2 or node_id_2 in node_id_1:
                edge_entry = {
                    "action": "move_base",
                    "action_type": "move_base_msgs/MoveBaseGoal",
                    "config": [],
                    "edge_id": f"{node_id_1}_to_{node_id_2}",
                    "fail_policy": "fail",
                    "fluid_navigation": True,
                    "goal": {
                        "target_pose": {
                            "header": {"frame_id": "$node.parent_frame"},
                            "pose": {"x": 0, "y": 0, "z": 0, "orientation": {"w": 0, "x": 0, "y": 0, "z": 0}}
                        }
                    },
                    "node": node_id_2,
                    "recovery_behaviours_config": "",
                    "restrictions_planning": "True",
                    "restrictions_runtime": "obstacleFree_1"
                }
                # Find corresponding node and add edge
                for node_entry in topo_map_data["nodes"]:
                    if node_entry["node"]["name"] == node_id_1:
                        node_entry["node"]["edges"].append(edge_entry)
                        break

    return yaml.dump(topo_map_data)

def export_to_topological_map(topo_map_point_list, topo_map_line_list, vineyard_id):
    print("def export_to_topological_map")

    center_coordinates = find_centre(topo_map_point_list, topo_map_line_list)

    last_updated = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    metric_map = str(vineyard_id)
    name = str(vineyard_id)

    yaml_topological_map = generate_topological_map(topo_map_point_list, last_updated, metric_map, name, [center_coordinates[1], center_coordinates[0]])
    #print(yaml_topological_map)

    return yaml_topological_map

def export_to_topological_map_datum(topo_map_point_list, topo_map_line_list):
    print("def export_to_topological_map")

    center_coordinates = find_centre(topo_map_point_list, topo_map_line_list)

    # Generate YAML content
    yaml_datum = generate_datum_yaml(center_coordinates)

    return yaml_datum