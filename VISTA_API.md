# VISTA API, Entities and Attributes

## Fiware Orion API
VISTA uses Fireware Orion for data storage.

[VISTA Fiware API](https://app.swaggerhub.com/apis-docs/VISTA_LCAS/fiware-ngsi_v_2_specification/1.0#/)

[VISTA Fiware API JSON](documents/vista-fiwire-ngsiv2-openapi.json)

Note that by default the max number of entities returned by Orion is 20 to increase this use the query `limit=<number>` e.g. `limit=1000`, the max number is 1000.

## VISTA API
- To directly access data stored in Orion use an API key, admins can generate API keys from the `generate_key.html` page.
- To access data stored in Orion use `https://vista.zrok.lcas.group/v2_secure/entities?api_key=<API_KEY>`
- To filter use the [Orion filtering options](https://fiware-orion.readthedocs.io/en/1.3.0/user/filtering/index.html), e.g. to return all vine rows where the vineyard ID is the Riseholme vineyard `http://vista.zrok.lcas.group/v2_secure/entities?type=VineRow&q=vineyard_id==riseholme&limit=1000&api_key=<API_KEY>`

### View Entities in Orion
TO view entities in Orion use a browser and URL `https://vista.zrok.lcas.group/v2_secure/entities?api_key=<API_KEY>`

Or the curl or request command.
```
curl -X GET "https://vista.zrok.lcas.group/v2_secure/entities?api_key=<API_KEY>" \
     -u "<user>:<password>"
```

To filter use the [Orion filtering options](https://fiware-orion.readthedocs.io/en/1.3.0/user/filtering/index.html), e.g. to return vine rows where the vineyard ID is the Riseholme vineyard use browser with URL `http://vista.zrok.lcas.group/v2_secure/entities?type=VineRow&q=vineyard_id==riseholmeapi_key=<API_KEY>`

Or the curl or request command.
```
curl -X GET "https://vista.zrok.lcas.group/v2_secure/entities?type=VineRow&q=vineyard_id==riseholme&api_key=<API_KEY>" \
     -u "<user>:<password>"
```

### Create Entities in Orion
Once you have an API key entities are created using the standard Orion POST method.

For example to create an entity with "entity_id" (a UUID), of type "Test" with an attribute "text" with value "hello", run this curl command.

```
curl -X POST "https://vista.zrok.lcas.group/v2_secure/entities?api_key=<API_KEY>" \
     -H "Content-Type: application/json" \
     -u "<user>:<password>" \
     -d '{
            "id": "<entity_id>",
            "type": "Test",
            "text": {
                "type": "Text",
                "value": "hello"
            }
        }'
```

### Update Entities in Orion
Entities are updated using the standard Orion PATCH method.

For example the entity with "entity_id" (a UUID) to update its attribute "text" with value "updated_hello", run this curl command.

```
curl -X PATCH "https://vista.zrok.lcas.group/v2_secure/entities/<entity_id>?api_key=<API_KEY>" \
     -H "Content-Type: application/json" \
     -u "<user>:<password>" \
     -d '{
            "text": {
                "value": "updated_hello"
            }
        }'
```


### Delete Entities in Orion
Entities are deleted using the standard Orion DELETE method.

For example to delete the entity with "entity_id" (a UUID) run this curl command.

```
curl -X DELETE "https://vista.zrok.lcas.group/v2_secure/entities/<entity_id>?api_key=<API_KEY>" \
     -u "<user>:<password>"
```

## Fiware Orion Entities

### Vineyard

```
"id": str(uuid.uuid4()),
"type": "Vineyard",
"vineyard_id": {
    "value": vineyard_id,
    "type": "String"
},
"name": {
    "value": vineyard_name,
    "type": "String"
},
"street_address": {
    "value": street_address,
    "type": "String"
},
"owner": {
    "value": owner,
    "type": "String"
},
"geom": {
    "type": "geo:json",
    "value": {
        "type": "MultiPoint",
        "coordinates": coordinates
    }
}
```

### Block

```
"id": str(uuid.uuid4()),
"type": "Block",
"vineyard_id": {
    "value": vineyard_id,
    "type": "String"
},
"user_defined_id": {
    "value": user_defined_id,
    "type": "String"
},
"name": {
    "value": name,
    "type": "String"
},
"row_spacing_m": {
    "value": row_spacing_m,
    "type": "Float"
},
"variety": {
    "value": variety,
    "type": "String"
},
"clone": {
    "value": clone,
    "type": "String"
},
"rootstock": {
    "value": rootstock,
    "type": "String"
},
"trelis_type": {
    "value": trelis_type,
    "type": "String"
},
"anchor_post_distance": {
    "value": anchor_post_distance,
    "type": "Float"
},
"under_vine_width": {
    "value": under_vine_width,
    "type": "Float"
},
"vine_spacing_m": {
    "value": vine_spacing_m,
    "type": "Float"
},
"date_start": {
    "value": date_start,
    "type": "DateTime"
},
"date_end": {
    "value": date_end,
    "type": "DateTime"
},
"geom": {
    "type": "geo:json",
    "value": {
        "type": "MultiPoint",
        "coordinates": coordinates
    }
}
```

### Vine Row

```
"id": str(uuid.uuid4()),
"type": "VineRow",
"vineyard_id": {
    "value": vineyard_id,
    "type": "String"
},
"block_id": {
    "value": block_id,
    "type": "String"
},
"user_defined_id": {
    "value": user_defined_id,
    "type": "String"
},
"orientation": {
   "value": orientation,
   "type": "Float"
},
"category": {
    "value": category,
    "type": "String"
},
"class": {
    "value": class_string,
    "type": "String"
},
"vine_spacing": {
    "value": vine_spacing,
    "type": "Float"
},
"under_vine_width": {
    "value": under_vine_width,
    "type": "Float"
},
"anchor_post_distance": {
    "value": anchor_post_distance,
    "type": "Float"
},
"post_spacing": {
    "value": post_spacing,
    "type": "Float"
},
"variety_row": {
    "value": variety,
    "type": "String"
},
"clone": {
    "value": clone,
    "type": "String"
},
"rootstock": {
    "value": rootstock,
    "type": "String"
},
"trelis_type": {
    "value": trelis_type,
    "type": "String"
},
"pruning_style": {
    "value": pruning_style,
    "type": "String"
},
"fruiting_wire_height": {
    "value": fruiting_wire_height,
    "type": "String"
},
"pruning_wire_height": {
    "value": pruning_wire_height,
    "type": "String"
},
"geom": {
    "type": "geo:json",
    "value": {
        "type": "LineString",
        "coordinates": coordinates
    }
}
```

### Vine

```
"id": str(uuid.uuid4()),
"type": "Vine",
"vineyard_id": {
    "value": vineyard_id,
    "type": "String"
},
"vine_row_id": {
    "value": vine_row_id,
    "type": "String"
},
"user_defined_id": {
    "value": user_defined_id,
    "type": "String"
},
"variety": {
    "value": variety,
    "type": "String"
},
"clone": {
    "value": clone,
    "type": "String"
},
"rootstock": {
    "value": rootstock,
    "type": "String"
},
"grapes_number": {
    "value": grapes_number,
    "type": "Integer"
},
"grapes_yield": {
    "value": grapes_yield,
    "type": "Float"
},
"location": {
    "type": "geo:json",
    "value": {
        "type": "Point",
        "coordinates": coordinates
    }
}
```

### Polygon

```
"id": str(uuid.uuid4()),
"type": "polygon",
"name": {
    "value": name,
    "type": "String"
},
"category": {
    "value": category,
    "type": "String"
},
"class": {
    "value": class_string,
    "type": "String"
},
"vineyard_id": {
    "value": vineyard_id,
    "type": "String"
},
"geom": {
    "type": "geo:json",
    "value": {
        "type": "MultiPoint",
        "coordinates": geom_coordinates
    }
}
```

### Line

```
"id": str(uuid.uuid4()),
"type": "line",
"name": {
    "value": name,
    "type": "String"
},
"category": {
    "value": category,
    "type": "String"
},
"class": {
    "value": class_string,
    "type": "String"
},
"vineyard_id": {
    "value": vineyard_id,
    "type": "String"
},
"geom": {
    "type": "geo:json",
    "value": {
        "type": "LineString",
        "coordinates": coordinates
    }
}
```

### Point

```
"id": str(uuid.uuid4()),
"type": "point",
"name": {
    "value": name,
    "type": "String"
},
"category": {
    "value": category,
    "type": "String"
},
"class": {
    "value": class_string,
    "type": "String"
},
"vineyard_id": {
    "value": vineyard_id,
    "type": "String"
},
"location": {
    "type": "geo:json",
    "value": {
        "type": "Point",
        "coordinates": coordinates
    }
}
```

Polygon, line and point are for other farm infrastructure such as buildings, drainage ditches and storage tanks.

### Photo

```
"id": str(uuid.uuid4()),
"type": "Photo",
"vine_id": {
    "type": "String",
    "value": vine_id
},
"photo_url": {
    "type": "URL",
    "value": photo_url
},
"vineyard_id": {
    "type": "String",
    "value": vineyard_name
},
"timestamp": {
    "type": "DateTime",
    "value": timestamp
}
```

## Entity Attribute Classes and Categories

Format
```
"Category": [
    "Class_1",
    "Class_2",
    "Class_3"
]
```

### Polygon

```
"Building": [
    "Building - Tasting room",
    "Neighbouring Utilities – Schools, sports fields, residential etc",
    "Winery building"
],
"Field feature": [
    "Composting Area",
    "Conservation area",
    "Degraded area",
    "Environmentally Sensitive Area",
    "Eroded area",
    "Evaporation Ponds",
    "Native Vegetation",
    "Pond",
    "Seepage Pads",
    "Threatened Species",
    "Wetlands",
    "Wildlife area",
    "Runway"
],
"Hazardous items": [
    "Mixing Area",
    "No fly zones"
],
"Site": [
    "Equipment Clean Down",
    "Picnic area",
    "Staff parking",
    "Washdown area"
]
```

### Line

```
"Field feature": [
    "Footpath",
    "Natural waterways",
    "Underground drainage line",
    "Trackways"
],
"Hazardous items": [
    "Disposal Trenches"
],
"Site": [
    "Hard Track",
    "On farm roads"
],
"Utilities": [
    "Electricity cable - overhead",
    "Electricity cable - underground",
    "Gas line"
],
"Water": [
    "Irrigation line",
    "Irrigation line (depth)",
    "Irrigation submain",
    "Mains water",
    "River"
]
```

### Point

```
"Building": [
    "Building - Ageing",
    "Building - Tasting room",
    "Farm House",
    "House",
    "Site Office",
    "Tasting room",
    "Toilets",
    "Winery building",
    "Worker Accommodation",
    "Workshop"
],
"Field feature": [
    "Composting Area",
    "Conservation area",
    "Evaporation Ponds",
    "Pond",
    "Seepage Pads",
    "Trees",
    "Dam",
    "Foot path stile",
    "Rock pile",
    "Underground drainage outlet"
],
"Hazardous items": [
    "Chemical mixing area",
    "Chemical storage",
    "Controlled Waste",
    "Discharge point",
    "Fertiliser Storage",
    "Fuel Storage",
    "Mixing Area",
    "Waste Collection point",
    "Waste storage point"
],
"Site": [
    "Fire evacuation point",
    "Fire hydrant",
    "First Aid kit location",
    "Delivery points",
    "Dip Sites",
    "Equipment Clean Down",
    "Exit point",
    "Extraction point",
    "Flushing Point",
    "General parking",
    "Ground Control Point",
    "Loading area",
    "Manhole",
    "Picnic area",
    "Pit",
    "Septic Tank",
    "Washdown area",
    "Entrance",
    "Temperature sensor point"
],
"Tech point location": [
    "Temperature sensor point"
],
"Utilities": [
    "Electric point - outside",
    "Electricity pylon",
    "Telegraph pole"
],
"Water": [
    "Irrigation Controller",
    "Irrigation Filter",
    "Irrigation Pump",
    "Irrigation Valve",
    "Mains water meter",
    "Pressure Main",
    "Water storage",
    "Water Tank",
    "Water Tap"
]
```





























