# Zenoh with InfluxDB
`https://github.com/eclipse-zenoh/zenoh-backend-influxdb`

`https://github.com/eclipse-zenoh/zenoh-backend-influxdb/tree/main/v2`

## Native Install

### Install InfluxDB
`https://docs.influxdata.com/influxdb/v2/install/?t=Linux`

```
curl -O https://dl.influxdata.com/influxdb/releases/influxdb2_2.7.4-1_amd64.deb
sudo dpkg -i influxdb2_2.7.4-1_amd64.deb
```

## Install zenoh backend influxdb
`sudo apt update`

`sudo apt install zenoh-backend-influxdb-v1` OR depending on the influxdb version installed `sudo apt install zenoh-backend-influxdb-v2`.


## Start InfluxDB
`sudo service influxdb start`

## Start Zenoh

To start Zenoh `zenohd -c zenoh_influxdb.json5`.

## InfluxDB Admin settings
InfluxDB web interface `localhost:8086`
User `admin`.
Password `password`
Initial Organization name `vista`
Initial Bucket Name `vista`
API token `Yk4TdmYvo95inSvUT4ohlm3NPcSJ0nfvzBPwANtBEs2nu28fGjXauu4vs_zbvB7TedF1PqJYZzOvLTlzCz-GbA==`

## View data on InfluxDB wep app
1. Open `localhost:8086`
2. Click on Data Explorer
3. Click on zenoh_example
4. Cilck on text
5. Toggle raw data on
6. Under aggregate funciton click on last
7. CLick on blue submit button
