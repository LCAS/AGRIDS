from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

# Create a PDF document
def create_pdf(data_list, vineyard_name, vineyard_area, vineyard_total_rows, vineyard_total_row_length, under_vine_area, mid_row_area, vineyard_total_vines, street_address, owner):
    # Create a BytesIO object to hold the PDF data
    buffer = BytesIO()
    
    document = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    # Get the default stylesheet
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    title_style = styles['Title']
    heading2_style = styles['Heading2']

    # Create a title and add it to elements
    title = Paragraph(str(vineyard_name), title_style)
    elements.append(title)
    
    # Add some space
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Owner: " + str(owner), normal_style))
    elements.append(Paragraph("Address: " + str(street_address), normal_style))
    
    # Add some space
    elements.append(Spacer(1, 12))
    
    elements.append(Paragraph("Vineyard Data", heading2_style))
    elements.append(Paragraph("Total Area: " + str(vineyard_area) + " m<sup>2</sup>", normal_style))
    elements.append(Paragraph("Total Vine Rows: " + str(vineyard_total_rows), normal_style))
    elements.append(Paragraph("Total Vines: " + str(vineyard_total_vines), normal_style))
    elements.append(Paragraph("Total Vine Row Length: " + str(vineyard_total_row_length) + " m", normal_style))
    elements.append(Paragraph("Total Under Vine Area: " + str(under_vine_area) + " m<sup>2</sup>", normal_style))
    elements.append(Paragraph("Total Mid Row Area: " + str(mid_row_area) + " m<sup>2</sup>", normal_style))

    # Add some space
    elements.append(Spacer(1, 12))

    # Create a description paragraph and add it to elements
    elements.append(Paragraph("Block Data", heading2_style))

    # Add some space after the description
    elements.append(Spacer(1, 12))

    # Create a table data list with headers
    table_data = [['Short Code', 'Name', 'Area (m2)', 'Rows', 'Vines', 'Row Length (m)', 'Under Vine (m2)', 'Mid Row (m2)']]

    # Append rows to the table data
    for item in data_list:
        table_data.append([
            item['user_defined_id'],
            item['name'],
            item['area'],
            item['total_rows'],
            item['number_of_vines_in_block'],
            item['total_row_length'],
            item['under_vine_area_block'],
            item['mid_row_area_block']
        ])

    # Create a Table object with specified column widths
    col_widths = [60, 80, 60, 40, 80, 80, 80, 80]
    table = Table(table_data, colWidths=col_widths)

    # Add style to the table
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    table.setStyle(style)

    # Add the table to the elements list
    elements.append(table)

    # Build the PDF
    document.build(elements)
    
    # Move the buffer position to the beginning
    buffer.seek(0)
    
    return buffer.getvalue()

# Example
# Sample block_data_list
# block_data_list = [
#     {'block_id': 1, 'user_defined_id': 'A1', 'name': 'Block A', 'coordinates': 'Coord A', 'area': 100.0, 
#      'perimeter': 50.0, 'total_rows': 10, 'total_row_length': 200.0, 'under_vine_area_block': 50.0, 
#      'mid_row_area_block': 50.0, 'number_of_vines_in_block': 500, 'type': 'Polygon'},
#     {'block_id': 2, 'user_defined_id': 'B1', 'name': 'Block B', 'coordinates': 'Coord B', 'area': 150.0, 
#      'perimeter': 75.0, 'total_rows': 15, 'total_row_length': 250.0, 'under_vine_area_block': 70.0, 
#      'mid_row_area_block': 80.0, 'number_of_vines_in_block': 750, 'type': 'Polygon'}
# ]

# vineyard_name = "Vineyard 1"
# vineyard_area =  500
# vineyard_total_rows = 100
# vineyard_total_row_length = 700                            
# under_vine_area = 150
# mid_row_area = 200
# vineyard_total_vines = 300

# # Generate the PDF and return as byte stream
# pdf_content = create_pdf(block_data_list, vineyard_name, vineyard_area, vineyard_total_rows, vineyard_total_row_length, under_vine_area, mid_row_area, vineyard_total_vines)

# # Save the PDF to a file for demonstration purposes
# with open('data/vineyard_data.pdf', 'wb') as f:
#     f.write(pdf_content)

# print("PDF created successfully!")