# AGRIDS

## Setup
Setup Fiware Orion and the Flask web app follow the instruction on the README files, [Orion README](orion) and [Flask App README](flask)

## Flask Web App
The web app is the interface to import, store, visualise and export data to and from AGRIDS.

### Import Data
Currently, data can be created and imported to AGRIDS in three ways.

#### 1. Creating a vineyard map from scratch.
Points, lines and polygons can be drawn on the map to represent, blocks, vine rows and also other infrastructure such as buildings and storage tanks, using the buttons on the top right of the map.

Once the features have been drawn click on the edit properties button.
Click on a shape, e.g. block polygon to enter the details of the block, such as name, variety etc.

To switch back to editing the shapes and to add more polygons, lines and points click on the edit geometries button.

To save enter a unique vineyard ID and click save to store in AGRIDS.

![image](https://github.com/jondave/VISTA/assets/6209386/9fce845b-a42d-4e6e-a86e-ade7949637a4)

#### 2. Import vine rows with labelled end posts as a CSV file.
To import a CSV file, the columns must be in the format; Latitude, Longitude, Row, where Row is a number corresponding the row numbering system used by the vineyard, there must only be two latitude and longitude points with the same row number.

| Latitude | Longitude | Row |
| -------- | --------- | --- |
| 53.555   | -0.555    | 1   |
| 53.566   | -0.566    | 1   |
| 53.577   | -0.577    | 2   |
| 53.588   | -0.588    | 2   |

Once the CSV file has been uploaded the rows are shown on the map.

Other features such as blocks and infrastructure can be added to the map as described above.

To save enter a unique vineyard ID and click save to store in AGRIDS.

![image](https://github.com/jondave/VISTA/assets/6209386/8731e3cc-8829-4f52-848f-31cadfee8b0f)

#### 3. Import vine rows with unlabelled end posts as a CSV file.
To import a CSV file without the row end posts having labels, the file collums must be in the format; Latitude, Longitude.

| Latitude | Longitude |
| -------- | --------- |
| 53.555   | -0.555    |
| 53.566   | -0.566    |
| 53.577   | -0.577    |
| 53.588   | -0.588    |

Once the CSV file has been uploaded the end posts are shown on the map as yellow points.

If the orientation of all the rows is the same simply, click on edit properties then click on two points that represent a row's end posts.

If the  orientation of all the rows is not the same draw polygons around blocks of vine rows. When this is complete click on edit properties then click on two points that represent a row's end posts in each polygon.

Click on generate lines, the rows will be created connecting the rows' end posts.

If the points turn red the post has not been connected to another post, click on edit geometries and move the lines to connected misaligned rows.

Other features such as blocks and infrastructure can be added to the map as described above.

To save enter a unique vineyard ID and click save to store in AGRIDS.

![image](https://github.com/jondave/VISTA/assets/6209386/63dc7bdf-7751-49d5-acc9-b6929b7d0d71)

### Visualise Data
Data stored in AGRIDS can be visualised on the map, and data layers can be shown and hidden by clicking the checkboxes.

Properties of the features can be shown by clicking on the feature in the map.

Data computed for the whole vineyard and for each block are tabulated below the map.

![image](https://github.com/jondave/VISTA/assets/6209386/d3f5942e-069f-4320-94e6-86dd0e92466c)

### Export Data
Data stored in AGRIDS can be exported in different formats.

A GeoJSON file is created depending on the data layers selected by the checkboxes, the selected features and their properties are then explored.

The computed vineyard and block data can be exported as a PDF report.

Navigation and topological maps can be exported as specific robotic formats and as a KML file.

![image](https://github.com/jondave/VISTA/assets/6209386/2a74c98a-12cd-4524-9dfb-fa823dab1f03)

## Fiware Orion Entities
| Vineyard               | Block                       | Vine Row                    | Vine                     | Polygon                 | Line                      | Point                    | Photo                   |
| ---------------------- | --------------------------- | --------------------------- | ------------------------ | ----------------------- | ------------------------- | ------------------------ | ----------------------- |
| vineyard_id: String    | block_id: String            | vine_row_id: String         | vine_id: String          | polygon_id: String      | line_id: String           | point_id: String         | photo_id: String        |
| name: String           | user_defined_id: String     | user_defined_id: String     | user_defined_id: String  | user_defined_id: String | user_defined_id: String   | user_defined_id: String  | user_defined_id: String |
| owner: String          | vineyard_id: String         | vineyard_id: String         | vineyard_id: String      | vineyard_id: String     | vineyard_id: String       | vineyard_id: String      | vineyard_id: String     |
| street_address: String | name: string                | block_id: String            | vine_row_id: String      | name: String            | name: String              | name: String             | vine_id: String         |
| geom: geo:json Polygon | date_start: DateTime        | under_vine_width: Float     | grapes_number: Float     | category: String        | category: String          | category: String         | storage_url: String     |
|                        | date_end: DateTime          | vine_spacing: Float         | grapes_yield: Float      | class: String           | class: String             | class: String            |                         |
|                        | row_spacing_m: Float        | anchor_post_distance: Float | rootstock: String        | geom: geo:json Polygon  | geom: geo:json LineString | location: geo:json Point |                         |
|                        | under_vine_width: Float     | geom: geo:json LineString   | variety: String          |                         |                           |                          |                         |
|                        | anchor_post_distance: Float |                             | location: geo:json Point |                         |                           |                          |                         |
|                        | vine_spacing: Float         |                             |                          |                         |                           |                          |                         |
|                        | variety: String             |                             |                          |                         |                           |                          |                         |
|                        | geom: geo:json Polygon      |                             |                          |                         |                           |                          |                         |

Polygon, line and point are for other farm infrastructure such as buildings, drainage ditches and storage takes.
