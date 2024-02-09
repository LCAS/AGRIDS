import pymongo
from datetime import datetime

def query_recent_values(entity_id, entity_type, num_values):
    # Connect to MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")

    # Select database
    db = client["sth_default"]

    # Select collection
    collection = db["sth_/_" + entity_id + "_" + entity_type]

    # Define query to retrieve all documents
    query = {"attrName": "grapes_number"}

    # Define projection
    projection = {"recvTime": 1, "attrValue": 1, "_id": 0}

    # Sort the results by recvTime in descending order and limit to the specified number of values
    results = collection.find(query, projection).sort("recvTime", pymongo.DESCENDING).limit(num_values)

    # Close connection
    client.close()

    return results

# Example usage:
entity_id = "vine001"
entity_type = "Vine"
num_values = 10

results = query_recent_values(entity_id, entity_type, num_values)

# Print the results
for result in results:
    formatted_time = result['recvTime'].strftime('%Y-%m-%d %H:%M:%S')  # Format datetime
    print(f"Timestamp: {formatted_time}, Number of Grapes: {result['attrValue']}")
