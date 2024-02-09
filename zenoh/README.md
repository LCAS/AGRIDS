# Zenoh

## Install
```
echo "deb [trusted=yes] https://download.eclipse.org/zenoh/debian-repo/ /" | sudo tee -a /etc/apt/sources.list > /dev/null
sudo apt update
sudo apt install zenoh 
```

### Install S3 Storage Library
```
sudo apt update
sudo apt install zenoh-backend-s3
```

## Run Zenoh with MinIO Storage
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

