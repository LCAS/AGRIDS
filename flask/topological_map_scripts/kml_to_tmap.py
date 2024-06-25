# adapted from https://github.com/LCAS/environment_common/blob/main/environment_common/convertors/kml_to_tmap.py

import sys, os
import yaml
import xml.etree.ElementTree as ET
from pprint import pprint

from topological_map_scripts.tmap import TMapTemplates
from topological_map_scripts.gps import calculate_displacement, calculate_distance_changes

class KmlRead:

    @classmethod
    def polyline_to_dictlist(cls, polyline_str, name, tagtype, circuit=False):
        pls = polyline_str.replace('\n','').replace('\t','').split(' ')
        coords = [g.split(',') for g in pls]
        print("polyline_str: " + str(polyline_str))
        print("pls: " + str(pls))

        dictlist = [{'longitude':round(float(gnss[0]),6),
                     'latitude': round(float(gnss[1]),6),
                     'elevation':round(float(gnss[2]),6),
                     'raw_name': f"{name} {i}",
                     'raw_connections': []} for i,gnss in enumerate(coords)]

        if tagtype in ['LineString','Polygon']:
            for i in range(0,len(dictlist)-1):
                dictlist[i]['raw_connections'] += [dictlist[i+1]['raw_name']]
            for i in range(1,len(dictlist)):
                dictlist[i]['raw_connections'] += [dictlist[i-1]['raw_name']]

        if tagtype == 'Polygon':
            dictlist[0]['raw_connections'] += [dictlist[-1]['raw_name']]
            dictlist[-1]['raw_connections'] += [dictlist[0]['raw_name']]

        return dictlist


    # @classmethod
    # def get_coords(cls, root):
    #     details = dict()
    #     for i, base in enumerate(root[0]):
    #         if 'Placemark' in base.tag:
    #             name, coords = '', ''
    #             tags = {field.tag.split('}')[-1]:field for field in base}
    #             name = tags['name'].text
    #             if 'LineString' in tags:
    #                 coords = tags['LineString'][0].text
    #                 tagtype = 'LineString'
    #             elif 'Polygon' in tags:
    #                 coords = tags['Polygon'][0][0][0].text
    #                 tagtype = 'Polygon'
    #             elif 'Point' in tags:
    #                 coords = tags['Point'][0].text
    #                 tagtype = 'Point'
    #             details[name] = cls.polyline_to_dictlist(coords, name, tagtype)
    #     return details

    @classmethod
    def get_coords(cls, root):
        details = dict()
        
        # Iterate through all Placemark elements in the KML file
        for placemark in root.findall('.//{http://www.opengis.net/kml/2.2}Placemark'):
            # Extract the name of the Placemark, if available
            name = placemark.find('.//{http://www.opengis.net/kml/2.2}name')
            name_text = name.text if name is not None else "Unnamed"
            
            # Extract the coordinates based on the geometry type
            point = placemark.find('.//{http://www.opengis.net/kml/2.2}Point')
            line_string = placemark.find('.//{http://www.opengis.net/kml/2.2}LineString')
            polygon = placemark.find('.//{http://www.opengis.net/kml/2.2}Polygon')
            
            if point is not None:
                coordinates_str = point.find('.//{http://www.opengis.net/kml/2.2}coordinates').text
                tagtype = 'Point'
            elif line_string is not None:
                coordinates_str = line_string.find('.//{http://www.opengis.net/kml/2.2}coordinates').text
                tagtype = 'LineString'
            elif polygon is not None:
                coordinates_str = polygon.find('.//{http://www.opengis.net/kml/2.2}coordinates').text
                tagtype = 'Polygon'
            else:
                # Skip if there's no valid geometry
                continue
            
            # Split the coordinates string and convert them to a list of dictionaries
            coords = cls.polyline_to_dictlist(coordinates_str, name_text, tagtype)
            
            # Store the coordinates in the details dictionary
            details[name_text] = coords
        
        return details



def group_similar_coords(coord_dict_list):

    # Add initial labels for use in filtering later
    for i in range(len(coord_dict_list)):
        coord_dict_list[i]['name'] = str(i)
        coord_dict_list[i]['keep'] = False
        coord_dict_list[i]['clear'] = False

    # Mark each node as to be cleared or kept
    for node in coord_dict_list:

        # Skip if node is already to be cleared
        if node['clear']: continue

        # Mark node to keep (first time seeing node)
        node['keep'] = True
        node['cleared_by'] = node['raw_name']
        la, lo = node['latitude'], node['longitude']

        for node2 in coord_dict_list:

            # Skip if node has been viewed already
            if node2['keep'] or node2['clear']: continue

            # If node 1 and node 2 are within close proximity, clear node 2
            la2, lo2 = node2['latitude'], node2['longitude']
            if abs(la-la2) < 0.00001 and abs(lo-lo2) < 0.00001:

                # Mark node for clearance so it is not viewed anymore
                node2['clear'] = True
                node2['cleared_by'] = node['raw_name']

                # Copy the cleared nodes connections into the kept node's details
                node['raw_connections'] += node2['raw_connections']

    #pprint(coord_dict_list)

    keeps = ['latitude', 'longitude', 'elevation', 'raw_name', 'raw_connections']
    kept = [{f:n[f] for f in keeps} for n in coord_dict_list if not n['clear']]
    for i in range(len(kept)):
        kept[i]['name'] = f"WayPoint{i+1}"

    final_convertor = {cdl['raw_name']: cdl['name'] for cdl in kept}
    convertor = {cdl['raw_name']: final_convertor[cdl['cleared_by']] for cdl in coord_dict_list}
    for k in kept:
        print('keeping? '+str(k))
        k['connections'] = set(convertor[c] if c in convertor else c for c in k['raw_connections'])
        del k['raw_connections'], k['raw_name']

    #[print(c) for c in kept]
    return kept


def run(args=None):

    # datum_path = '../data/datum.yaml'
    # with open(datum_path) as f:
    #     data = f.read()
    #     datum = yaml.safe_load(data)

    print("run")

    datum = args['datum']

    place_id = args['location_name']
    lat = datum['datum_latitude']
    lon = datum['datum_longitude']

    kml_path = args['src']
    locations = dict()
    tree = ET.parse(kml_path)
    root = tree.getroot()
    coords = KmlRead.get_coords(root)
    #print("coords = KmlRead.get_coords(root)")
    #print(coords)

    allpoints = sum(coords.values(),[])
    #[print(f"{l['longitude']} : {l['latitude']}) \t-- {l['raw_name']} {l['raw_connections']}") for l in allpoints]

    lesspoints = group_similar_coords(allpoints)
    print(lesspoints)
    for l in lesspoints:
        l['y'], l['x'] = calculate_distance_changes(lat, lon, l['latitude'], l['longitude'])
    [print(f"{l['name']} ({l['longitude']}:{l['latitude']})  -  {l['connections']}") for l in lesspoints]
    print(f"Reduced {len(allpoints)} raw points down to {len(lesspoints)}")

    #[print(f"{l['name']} ({round(l['x'],1)}:{round(l['y'],1)})  -  {l['connections']}") for l in lesspoints]

    tmap = TMapTemplates.vert_sample
    #tmap += TMapTemplates.vert_opening
    #tmap += TMapTemplates.vert_ring.format(**{'id':'vert2', 'sz':1})
    print('|\n|\n|\n|\n|', place_id)
    tmap += TMapTemplates.opening.format(**{'gen_time':0, 'location':place_id})

    node = {'location':place_id, 'vert': 'vert1', 'restrictions':'robot', 'connections':None}
    edge = {'action':'move_base', 'action_type':'move_base_msgs/MoveBaseGoal', 'restrictions':'robot'}
    for l in lesspoints:
        node.update({'name':l['name'], 'x':l['x'], 'y':l['y']})
        tmap += TMapTemplates.node.format(**node)
        if not l['connections']:
            tmap += TMapTemplates.edges_empty
        else:
            tmap += TMapTemplates.edges_start
            for c in l['connections']:
                edge.update({'name':l['name'], 'name2':c})
                tmap += TMapTemplates.edges.format(**edge)

    return tmap

    # tmap_path = 'autogen.tmap2.yaml'
    # print(tmap_path)
    # with open(tmap_path, 'w') as f:
    #     f.write(tmap)

def main(args=None):

    src = '../data/jojo_topo_map.kml'
    location_name = "jojo"
    if not location_name:
        print('missing ENVVAR FIELD_NAME, not continuing')
        return
    print('Generating map for field: '+location_name)
    args = {'src': src, 'location_name':location_name, 'line_col':'ff2f2fd3', 'line_width':'4', 'fill_col':'c02f2fd3', 'shape_size':0.000005}
    run(args)

if __name__ == '__main__':
    main()