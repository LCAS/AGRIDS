# AGRIDS 

## Zenoh with MinIO
`https://github.com/eclipse-zenoh/zenoh-backend-s3/tree/main#tests-using-the-rest-api`

### Install
```
echo "deb [trusted=yes] https://download.eclipse.org/zenoh/debian-repo/ /" | sudo tee -a /etc/apt/sources.list > /dev/null
sudo apt update
sudo apt install zenoh 
```

#### Install S3 Storage Library
```
sudo apt update
sudo apt install zenoh-backend-s3
```

### Run Zenoh with MinIO Storage
Download and install MinIO 
```
wget https://dl.min.io/server/minio/release/linux-amd64/archive/minio_20240204223613.0.0_amd64.deb -O minio.deb
sudo dpkg -i minio.deb
```

Make a directory to store the data. `mkdir ~/minio`.

To start MinIO run the command `nohup minio server ~/minio --console-address :9001 --ftp="address=:8021" --ftp="passive-port-range=30000-40000" &`

To access via browser go to `localhost:9000` default login and password is `minioadmin`.

Change server IP, port number and access keys in `zenoh_minio.json5`.

To start Zenoh `zenohd -c zenoh_minio.json5`.

### Run Zenoh with ROS2 and MinIO
Save ROS2 images to MinIO via Zenoh.

On host computer/server setup a Zenoh router with this config - `zenohd -c zenoh_agrids.json5` - [zenoh_agrids.json5](https://github.com/LCAS/AGRIDS/blob/main/zenoh/minio/zenoh_agrids.json5)

Subscribe to ROS2 image topic, convert to jpg then publish on a Zenoh topic (jpg conversion can be done in the Zenoh listener script) - [zenoh_publish_ros2_image.py](https://github.com/LCAS/AGRIDS/blob/main/zenoh/minio/python_scripts/zenoh_publish_ros2_image.py)

Subscribe to Zeonh topic, get the image and store in MinIO - [zenoh_subscribe_store_image.py](https://github.com/LCAS/AGRIDS/blob/main/zenoh/minio/python_scripts/zenoh_subscribe_store_image.py)