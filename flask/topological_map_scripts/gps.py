# https://github.com/LCAS/environment_common/blob/main/environment_common/convertors/tools/gps.py

#chatGPT-3.5's attempt
from math import radians, sin, cos, sqrt, atan2, degrees

def calculate_displacement(lat1in, lon1in, lat2in, lon2in):
    # Convert coordinates to radians
    lat1, lon1 = radians(lat1in), radians(lon1in)
    lat2, lon2 = radians(lat2in), radians(lon2in)

    # Earth radius in meters
    earth_radius = 6371000

    # Haversine formula
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = sin(delta_lat/2)**2 + cos(lat1) * cos(lat2) * sin(delta_lon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))

    # Calculate displacement in meters
    displacement_y = earth_radius * c
    displacement_x = earth_radius * c * cos(lat1)

    #displacement_y = displacement_y if lat1in < lat2in else -displacement_y
    #displacement_x = displacement_x if lon1in < lon2in else -displacement_x

    print(f'Lat: {round(lat1in,5)},{round(lat2in,5)},{round(displacement_y,1)} \t| Lon: {round(lon1in,5)},{round(lon2in,5)},{round(displacement_x,1)}')
    return displacement_y, displacement_x



def calculate_distance_changes(lat1, lon1, lat2, lon2):
    # Convert coordinates to radians
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    # Earth radius in meters
    earth_radius = 111111 #meters

    # Haversine formula
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    # Calculate distance changes in latitude and longitude
    distance_change_lat = degrees(delta_lat) * earth_radius
    distance_change_lon = degrees(delta_lon) * earth_radius * cos(lat1)

    return round(distance_change_lat,2), round(distance_change_lon,2)



def calculate_coordinates(lat, lon, dx, dy):
    # Earth radius in meters
    earth_radius = 6371000

    # Convert latitude and longitude to radians
    lat = radians(lat)
    lon = radians(lon)

    # Calculate displacement in radians
    displacement_lat = dx / earth_radius
    displacement_lon = dy / (earth_radius * cos(lat))

    # Calculate new latitude and longitude
    new_lat = lat + displacement_lat
    new_lon = lon + displacement_lon

    # Convert back to degrees
    new_lat = degrees(new_lat)
    new_lon = degrees(new_lon)

    # Return gps corrected by metric input
    return new_lat, new_lon



#def add_to_gps(latitude, longitude, node_pose_list, node):
#    x_offset = (node_pose_list[node]['x']) / (cos(latitude) * 111111)
#    y_offset = (node_pose_list[node]['y']) / (111111)
#    return latitude + (y_offset*0.95), longitude + (-x_offset*1.65)















def metric(datum_latitude, datum_longitude, datum_elevation, latitude, longitude, elevation):
    x = (datum_latitude - latitude) / (111111)
    y = (datum_longitude - longitude) / (cos(latitude) * 111111)
    z = datum_elevation - elevation
    return x, y, z

def gps(datum_latitude, datum_longitude, datum_elevation, x, y, z):
    latitude = datum_latitude + (x * 111111)
    longitude = datum_longitude + (y * cos(latitude) * 111111)
    elevation = datum_elevation + z
    return latitude, longitude, elevation

def add_metric_to_gps(datum_latitude, datum_longitude, datum_elevation, lat, lon, ele, x, y, z):
     xLat, yLon, zEle = metric(datum_latitude, datum_longitude, datum_elevation, lat, lon, ele)
     return gps(datum_latitude, datum_longitude, datum_elevation, xLat+x, yLon+y, zEle+z)




#datum: lat lon
#node: lat, lon
#tmap = metric(node) - metric(datum)
#tmap = metric(node-datum)
def get_relative_metric(datum, node):
    return metric(node)-metric(datum)




#datum: lat lon
#tmap: xd, yd
#node = gps(metric(datum)+tmap)
#node = datum+gps(tmap)
def get_relative_metric(datum, tmap):
    return datum+metric(node)






##################################################################### This one works
import geopy.distance
def get_datumrelative_metric_from_gps(datum, gnss):
    lat1, lon1 = datum['latitude'], datum['longitude']
    lat2, lon2 = gnss['latitude'], gnss['longitude']

    # Get average width difference from left and right longitudes
    x1 = geopy.distance.geodesic((lat1, lon1), (lat1,lon2)).m
    x2 = geopy.distance.geodesic((lat2, lon1), (lat2,lon2)).m
    x = (x1+x2)/2
    if lat1 > lat2: x = -x
    # ^ this is the longitude displacement in m

    # Get average height difference from top and bottom latitudes
    y1 = geopy.distance.geodesic((lat1, lon1), (lat2,lon1)).m
    y2 = geopy.distance.geodesic((lat1, lon2), (lat2,lon2)).m
    y = (y1+y2)/2
    if lon1 > lon2: y = -y
    # ^ this is the latitude displacement in m

    # Get displacement of gnss from a datum point
    z = gnss['elevation'] - datum['elevation']
    return {'x':x, 'y':y, 'z':z}

def get_gps_from_datumrelative_metric(datum, xyz):
    # Get gnss of a datum point shifted by xyz metres
    lat = degrees( radians(datum['latitude']) + ( xyz['y'] / 6371000 ))
    lon = degrees( radians(datum['longitude']) + ( xyz['x'] / (6371000 * cos(radians(datum['latitude']))) ))
    return {'latitude': lat, 'longitude': lon, 'elevation': datum['elevation']}

def displace_gps_by_metric_relative_to_datum(datum, gnss, xyz):
    metric = get_datumrelative_metric_from_gps(datum, gnss)
    new_xyz = {'x':metric['x']+xyz['x'], 'y':metric['y']+xyz['y'], 'z':metric['z']+xyz['z']}
    new_gnss = get_gps_from_datumrelative_metric(datum, new_xyz)
    return new_gnss

def get_bounds(gps_list):
    lats = [l[0] for l in gps_list]
    lons = [l[1] for l in gps_list]
    north, south = max(lats), min(lats)
    east, west = max(lons), min(lons)
    return {'north':north, 'east':east, 'south':south, 'west':west}

def get_range(bounds):
    ne = {'latitude':bounds['north'], 'longitude':bounds['east'], 'elevation':0}
    sw = {'latitude':bounds['south'], 'longitude':bounds['west'], 'elevation':0}
    xyz = get_datumrelative_metric_from_gps(sw, ne)
    return xyz['x'], xyz['y']
################################################################################# This one works

if __name__=='__main__':
    datum = {'latitude': 53.2648, 'longitude': -0.5310, 'elevation': 0}
    print(' datum', datum)

    sw = {'latitude': 53.2648, 'longitude': -0.5318, 'elevation': 0}
    print('ori sw', sw)

    ne = {'latitude': 53.2675, 'longitude': -0.5248, 'elevation': 0}
    print('ori ne', ne)

    print('\n\nFind distance from datum to sw corner:')
    print(' datum', datum)
    print('ori sw', sw)
    map_frame_pose = get_datumrelative_metric_from_gps(datum, sw)
    print('\nmap pos: ', map_frame_pose)

    #dims = get_datumrelative_metric_from_gps(sw, ne)
    #print('   sw to ne: ', dims)

    #gps = get_gps_from_datumrelative_metric(sw, map_frame_pose)
    #print('ori sw', sw)
    #print('new sw', gps)

    # need to use the map_frame_pose and the datum to get the sw gps
    print('\n\nUse map_pose and datum to find sw:')
    print('map pos', map_frame_pose)
    print('  datum', datum)
    sw_copy = displace_gps_by_metric_relative_to_datum(datum, datum, map_frame_pose)
    print('\nori sw', sw)
    print('new sw', sw_copy)
    print('\n')