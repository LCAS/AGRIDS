# VISTA

## Fiware Orion
To start Fiware Orion, Cygnus and MongoDB `cd` into `docker` directory and run the `./services cygnus` command this starts a docker compise file.

To test if they are running in browser go to `localhost:1026/version` this will print the running version of Orion and `localhost:5080/v1/version` will print the current version of Cygnus.

MongoDB can be checked and accessed via MongoDB Compass on port 27017.

### Python Scripts

#### Add data
- To popluate Orion with some vineyard data run `orion_add_all_vineyard_data.py` change the paramerts for the number of block, rows and vines.
- To add individual blocks, row, vines etc. run `orion_add_vineyard.py`, `orion_add_block.py`, `orion_add_vinerow.py`, `orion_add_vine.py` and `orion_add_image.py` change names and parameters as needed.

#### Delete Data

- `orion_delete_entity.py` delete individual entity by ID.
- `orion_delete_all_entities.py` delete all entities in Orion.

#### Subscriptions

 - `orion_new_subscription.py` creates new subscription for all entities and atrtibutes to notify Cygnus of any changes. (Currenty works by looping thought all entities and attributes and creates one subscriptions for all attributes).
 - `orion_new_subscription_all_data.py` the nicer way to create new subscription for all entities and atrtibutes. (Not currently working).
 - `orion_delete_all_subscriptions.py` deletes all subscriptions in orion.
 - `orion_check_subscription_status.py` prints the status of all the subscriptions in Orion.

#### Update Data

 - `orion_update_vine.py` updates data in vine entity.

#### Query Orion

 - `orion_query_images_in_vine_row.py` gets the URLs of all the images in a vine row.
 - `orion_query_vines_in_block.py`gets the vine IDs of all the vines in a block.

#### Web App
- Run the flask web server `flask_web_server.py` runs on port `5000`.

## MinIO
Download and install MinIO 
```
wget https://dl.min.io/server/minio/release/linux-amd64/archive/minio_20240204223613.0.0_amd64.deb -O minio.deb
sudo dpkg -i minio.deb
```

Make a directory to store the data. `mkdir ~/minio`.

To start MinIO run the command `nohup minio server ~/minio --console-address :9001 --ftp="address=:8021" --ftp="passive-port-range=30000-40000" &`

To access via browser go to `localhost:9000` default login and password is `minioadmin`.

### Python Scripts
Can upload data via the browser page or using `minio_file_uploader.py` change the server address, access keys and paramers as needed. Access keys can be created via the browser page.

## Mongo DB
MongoDB should start with the docker compose file along with Orion and Cugnus.
Can be accessed via MongoDB Compass on port 27017.

### Python Scripts
- `mongodb_access_vine_data_by_time.py` gets vine data between two timestamps.
- `mongodb_access_vine_data_last_values.py` gets the last X vaules for the vine data.