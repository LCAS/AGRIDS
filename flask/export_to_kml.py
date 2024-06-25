import simplekml

def create_kml(topo_map_point_list, topo_map_line_list):
    kml = simplekml.Kml()
    
    # Adding points
    for point in topo_map_point_list:
        kml.newpoint(name=point['topo_map_node_id'], coords=[(point['coordinates'][0], point['coordinates'][1])])
    
    # Adding polylines
    for line in topo_map_line_list:
        # Convert coordinates to comma-separated string
        coords_str = ' '.join([f"{coord[0]},{coord[1]},0.0" for coord in line['coordinates']])
        linestring = kml.newlinestring(name=line['topo_map_edge_id'])
        linestring.coords = [(coord[0], coord[1], 0.0) for coord in line['coordinates']]
        linestring.altitudemode = simplekml.AltitudeMode.clamptoground  # Set altitude mode to clamp to ground
    
    return kml.kml()

def export_to_kml(features_list):
    kml = simplekml.Kml()
    
    for feature in features_list:
        feature_type = feature['type']
        
        if feature_type == 'point':
            kml.newpoint(name=feature['name'], coords=[(feature['coordinates'][0][0], feature['coordinates'][0][1])])
        
        elif feature_type == 'linestring':
            linestring = kml.newlinestring(name=feature['name'])
            linestring.coords = [(coord[0], coord[1], 0.0) for coord in feature['coordinates']]
            linestring.altitudemode = simplekml.AltitudeMode.clamptoground  # Set altitude mode to clamp to ground
        
        elif feature_type == 'polygon':
            pol = kml.newpolygon(name=feature['name'])
            pol.outerboundaryis = [(coord[0], coord[1], 0.0) for coord in feature['coordinates'][0]]
            pol.altitudemode = simplekml.AltitudeMode.clamptoground  # Set altitude mode to clamp to ground
            pol.extrude = 1
            pol.tessellate = 1

    return kml.kml()