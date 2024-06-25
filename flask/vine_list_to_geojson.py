import json

def vine_list_to_geojson(vine_list):
    features = []

    for item in vine_list:
        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': item['coordinates']
            },
            'properties': {
                'vine_id': item['vine_id']
            }
        }
        features.append(feature)

    feature_collection = {
        'type': 'FeatureCollection',
        'features': features
    }

    return json.dumps(feature_collection)

# Example usage:
# vine_data = [
#     {'vine_id': 'ba20_vine_0', 'coordinates': [-0.9774868006561149, 51.59721448064811]},
#     {'vine_id': 'ba20_vine_1', 'coordinates': [-0.977490153, 51.59721291]},
#     {'vine_id': 'ba20_vine_2', 'coordinates': [-0.9774983324021069, 51.59720907711307]},
#     {'vine_id': 'ba20_vine_3', 'coordinates': [-0.9775065118042139, 51.59720524422613]},
#     {'vine_id': 'ba20_vine_4', 'coordinates': [-0.9775146912063207, 51.5972014113392]},
#     {'vine_id': 'ba20_vine_5', 'coordinates': [-0.9775228706084277, 51.59719757845227]},
#     {'vine_id': 'ba20_vine_6', 'coordinates': [-0.977523802, 51.597197142]},
#     {'vine_id': 'ba20_vine_7', 'coordinates': [-0.9775319814294752, 51.597193309170656]}
# ]

# geojson_data = vine_list_to_geojson(vine_data)
# print(geojson_data)