import xml.etree.ElementTree as ET
from xml.dom import minidom

def prettify(elem):
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="    ")

def coordinates_to_xml(coordinate_data, row_width):
    # Create the root element
    antonav = ET.Element('antonav', version="0.1", generator="antoCartographer")
    
    nodes = []
    ways = []
    node_id = 1
    way_id = 1
    
    # First pass: Create nodes and store their references
    for item in coordinate_data:
        node_ids = []
        for coord in item['coordinates']:
            node = ET.Element('node', id=str(node_id), lat=str(coord[1]), lon=str(coord[0]))
            nodes.append(node)
            node_ids.append(str(node_id))
            node_id += 1
        
        ways.append((way_id, node_ids, item['mid_row_line_id']))
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

# Example usage
# coordinate_data = [
#     {'mid_row_line_id': 'pn-v1_to_pn-v2_mid_row_line', 'coordinates': [[-0.978411881, 51.5972804675], [-0.978642649, 51.5971723295]], 'type': 'LineString'},
#     {'mid_row_line_id': 'pn-v2_to_pn-v3_mid_row_line', 'coordinates': [[-0.97836146, 51.597277095500004], [-0.9786423635, 51.5971454645]], 'type': 'LineString'}
# ]

# xml_content = coordinates_to_xml(coordinate_data)
# print(xml_content)  # Print the XML content
