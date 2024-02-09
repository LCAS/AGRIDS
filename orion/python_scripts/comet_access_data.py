import requests
from datetime import datetime, timedelta

def read_comet(entity_type, entity_id, attr_name, agg_method, h_limit=3, h_offset=0, date_from=None, date_to=None):
    base_url = 'http://cabbage-xps-8900:8666/STH/v1/contextEntities'
    url = f'{base_url}/type/{entity_type}/id/{entity_id}/attributes/{attr_name}?hLimit=3&hOffset=0&dateFrom=2024-02-01T00:00:00.000Z&dateTo=2024-02-01T23:59:59.999Z'

    # http://cabbage-xps-8900:8666/STH/v1/contextEntities/type/Vine/id/vine001/attributes/grapes_number?hLimit=3&hOffset=0&dateFrom=2024-02-01T00:00:00.000Z&dateTo=2024-02-01T23:59:59.999Z

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")

def comet_to_time_series(comet_response, agg_method):
    data = []
    labels = []

    try:
        context_responses = comet_response.get('contextResponses', [])
        if not context_responses:
            raise Exception("Error: 'contextResponses' not found in the response.")

        context_element = context_responses[0].get('contextElement', {})
        if not context_element:
            raise Exception("Error: 'contextElement' not found in the response.")

        attributes = context_element.get('attributes', [])
        if not attributes:
            raise Exception("Error: 'attributes' not found in the response.")

        values = attributes[0].get('values', [])
        if not values:
            print("Warning: 'values' list is empty in the response.")
            return {'labels': labels, 'data': data}

        date = datetime.fromisoformat(values[0]['_id']['origin'][:-1])  # remove 'Z' from the end

        for element in values[0].get('points', []):
            data.append({'t': int(date.timestamp()) * 1000, 'y': element.get(agg_method, None)})
            labels.append(date.strftime('%H:%M'))
            date += timedelta(minutes=1)

        return {
            'labels': labels,
            'data': data
        }
    except Exception as e:
        raise Exception(f"Error: {e}")

# Example usage
entity_type = 'Vine'
entity_id = 'vine001'
attr_name = 'grapes_number'
agg_method = 'occur'
date_from = '2024-02-01T00:00:00.000Z'
date_to = '2016-02-01T23:59:59.999Z'

try:
    comet_response = read_comet(entity_type, entity_id, attr_name, agg_method, date_from=date_from, date_to=date_to)
    print("Response:", comet_response)  # Print the response for debugging
    time_series_data = comet_to_time_series(comet_response, agg_method)
    print(time_series_data)
except Exception as e:
    print(f"Error: {e}")
