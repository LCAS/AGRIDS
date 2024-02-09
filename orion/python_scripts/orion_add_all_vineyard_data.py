import orion_add_vineyard
import orion_add_block
import orion_add_vinerow
import orion_add_vine
import orion_add_image

# Function to create vineyard entity
def create_vineyard(vineyard_params):
    orion_add_vineyard.create_vineyard_entity(**vineyard_params)

# Function to create block entity
def create_block(block_params):
    orion_add_block.create_block_entity(**block_params)

# Function to create vine row entity
def create_vine_row(vine_row_params):
    orion_add_vinerow.create_vine_row_entity(**vine_row_params)

# Function to create vine entity
def create_vine(vine_params):
    orion_add_vine.create_vine_entity(**vine_params)

# Function to create image entity
def create_image(image_params):
    orion_add_image.create_photo_entity(**image_params)

# Define parameters for entities
vineyard_params = {
    "vineyard_name": "Lincoln Vineyard",
    "street_address": "University of Lincoln, Brayford Pool, Lincoln, LN6 7TS",
    "owner": "University of Lincoln",
    "geom_coordinates": [
        [53.22705288052429, -0.5491956099145128],
        [53.22721987218854, -0.5493028982765445],
        [53.227284099578306, -0.5489220245913319],
        [53.226951721795565, -0.5487396343758779]
    ]
}

block_params = {
    "user_defined_id": "North Block",
    "row_spacing_m": 1.5,
    "vine_spacing_m": 1.0,
    "date_start": "2024-01-01T00:00:00Z",
    "date_end": "2024-12-31T00:00:00Z",
    "geom_coordinates": [
        [53.227176516724036, -0.5490537449585962],
        [53.22715082571518, -0.5489410921784628],
        [53.22712754322504, -0.5491033658260358],
        [53.227084189589014, -0.5489384099694119]
    ]
}

vine_row_params = {
    "user_defined_id": "Vine Row 1",
    "orientation": 45,
    "geom_coordinates": [
        [[53.227176516724036, -0.5490537449585962], [53.22716326979953, -0.5488767191612437]],
        [[53.22715082571518, -0.5489410921784628], [53.22712834606973, -0.5489840075232755]],
        [[53.22712754322504, -0.5491033658260358], [53.22705608998665, -0.548782841844466]]
    ]
}

vine_params = {
    "user_defined_id": "Vine 1",
    "variety": "Merlot",
    "clone": "Chardonnay",
    "rootstock": "3309C",
    "location_coordinates": [53.227216007632244, -0.5493656119079906],
    "grapes_number": 5,
    "grapes_yield": 4.8
}

image_params = {
}

# Set the number of entities to create
num_vineyards = 1
num_blocks_per_vineyard = 2
num_vine_rows_per_block = 3
num_vines_per_row = 4
num_images_per_vine = 2

# Initialize ID counters
vineyard_counter = 1
block_counter = 1
vine_row_counter = 1
vine_counter = 1
image_counter = 1

# Loop to create vineyards
for i in range(num_vineyards):
    vineyard_params["vineyard_id"] = f"vineyard00{vineyard_counter}"
    create_vineyard(vineyard_params)
    
    # Loop to create blocks
    for j in range(num_blocks_per_vineyard):
        block_params["block_id"] = f"block00{block_counter}"
        block_params['vineyard_id'] = vineyard_params["vineyard_id"]
        create_block(block_params)
        
        # Loop to create vine rows
        for k in range(num_vine_rows_per_block):
            vine_row_params["vine_row_id"] = f"vinerow00{vine_row_counter}"
            vine_row_params['block_id'] = block_params["block_id"]
            create_vine_row(vine_row_params)
            
            # Loop to create vines
            for l in range(num_vines_per_row):
                vine_params["vine_id"] = f"vine00{vine_counter}"
                vine_params['vine_row_id'] = vine_row_params["vine_row_id"]
                create_vine(vine_params)
                
                # Loop to create images
                for m in range(num_images_per_vine):
                    image_params["photo_id"] = f"photo00{image_counter}"
                    image_params['vine_id'] = vine_params["vine_id"]
                    image_params['vineyard_name'] = vineyard_params["vineyard_id"]
                    image_params['block_name'] = block_params["block_id"]
                    image_params['vine_row_name'] = vine_row_params["vine_row_id"]
                    image_params['vine_name'] = vine_params["vine_id"]
                    image_params["file_name"] = f"photo00{image_counter}.jpg"
                    create_image(image_params)
                    
                    # Increment image counter
                    image_counter += 1
                
                # Increment vine counter
                vine_counter += 1
            
            # Increment vine row counter
            vine_row_counter += 1
        
        # Increment block counter
        block_counter +=1

    # Increment vineyard counter
    vineyard_counter +=1
