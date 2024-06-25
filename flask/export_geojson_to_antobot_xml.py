import xml.etree.ElementTree as ET
from xml.dom import minidom

def prettify(elem):
    if not isinstance(elem, ET.Element):
        raise ValueError("Expected an Element object, got {}".format(type(elem)))
    
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="    ")

def coordinates_to_xml(geojson_data, row_width):
    # Create the root element
    antonav = ET.Element('antonav', version="0.1", generator="antoCartographer")
    
    nodes = []
    ways = []
    node_id = 1
    way_id = 1
    
    # Filter features with mid_row_line_id and extract coordinates
    for feature in geojson_data['features']:
        if 'mid_row_line_id' in feature['properties']:
            coordinates = feature['geometry']['coordinates']
            mid_row_line_id = feature['properties']['mid_row_line_id']
            
            node_ids = []
            for coord in coordinates:
                node = ET.Element('node', id=str(node_id), lat=str(coord[1]), lon=str(coord[0]))
                nodes.append(node)
                node_ids.append(str(node_id))
                node_id += 1
            
            ways.append((way_id, node_ids, mid_row_line_id))
            way_id += 1
    
    # Add nodes to the root element
    for node in nodes:
        antonav.append(node)
    
    # Second pass: Create way elements using stored node references
    for way_id, node_ids, mid_row_line_id in ways:
        way = ET.SubElement(antonav, 'way', id=str(way_id))
        ET.SubElement(way, 'tag', k="navMethod", v="corridorFruit")
        ET.SubElement(way, 'tag', k="rowType", v="middle")
        ET.SubElement(way, 'tag', k="rowNumber", v=str(mid_row_line_id))
        ET.SubElement(way, 'tag', k="rowWidth", v=str(row_width))
        for nid in node_ids:
            ET.SubElement(way, 'nd', ref=nid)

    # Generate the prettified XML string
    xml_str = prettify(antonav)

    # Remove the default extra newlines
    xml_lines = [line for line in xml_str.split('\n') if line.strip() != '']

    # Join the lines with newline characters
    final_xml_str = "\n".join(xml_lines)

    # Return the final XML string
    return final_xml_str