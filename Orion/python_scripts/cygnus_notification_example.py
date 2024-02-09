import requests

url = 'http://localhost:5080/notify'

data = {
    "id": "vine001",
    "type": "Vine",
    "block_id": {
        "type": "String",
        "value": "block001",
        "metadata": {}
    },
    "clone": {
        "type": "String",
        "value": "Pinot Meunier",
        "metadata": {}
    },
    "location": {
        "type": "geo:json",
        "value": {
            "type": "Point",
            "coordinates": [
                53.227292304,
                -0.548678819
            ]
        },
        "metadata": {}
    },
    "photo": {
        "type": "URL",
        "value": "vineyard001/block001/vinerow001/vine001/photo001.jpg",
        "metadata": {}
    },
    "rootstock": {
        "type": "String",
        "value": "10114B",
        "metadata": {}
    },
    "user_defined_id": {
        "type": "String",
        "value": "Vine 1",
        "metadata": {}
    },
    "variety": {
        "type": "String",
        "value": "Pinot Noir",
        "metadata": {}
    },
    "vinerow_id": {
        "type": "String",
        "value": "vinerow001",
        "metadata": {}
    },
    "vineyard_id": {
        "type": "String",
        "value": "vineyard001",
        "metadata": {}
    }
}

headers = {
    'Content-Type': 'application/ld+json',
    'Fiware-service': 'closeiot7'
}

response = requests.post(url, json=data, headers=headers)

print(response.status_code)
print(response.text)
