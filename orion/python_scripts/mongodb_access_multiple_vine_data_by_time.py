import pymongo
from datetime import datetime
import time

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
    results = collection.find(query, projection).sort("recvTime", pymongo.ASCENDING).limit(num_values)

    # Close connection
    client.close()

    return results

def aggregate_grapes_over_time(vine_ids, num_values):
    aggregated_results = {}
    earliest_timestamp = None

    for vine_id in vine_ids:
        results = query_recent_values(vine_id, "Vine", num_values)
        for result in results:
            timestamp = result['recvTime'].strftime('%Y-%m-%d %H:%M:%S')
            grapes = result['attrValue']
            if timestamp not in aggregated_results:
                aggregated_results[timestamp] = 0
            aggregated_results[timestamp] += grapes
            if earliest_timestamp is None or result['recvTime'] < earliest_timestamp:
                earliest_timestamp = result['recvTime']

    # Accumulate total grapes over time
    total_grapes = 0
    accumulated_results = {}
    for timestamp in sorted(aggregated_results.keys()):
        total_grapes += aggregated_results[timestamp]
        accumulated_results[timestamp] = total_grapes

    return accumulated_results, earliest_timestamp

# Example usage:
#vine_ids = ["vine001", "vine002", "vine003"]  # List of vine IDs to aggregate
#num_values = 10

#aggregated_results, earliest_timestamp = aggregate_grapes_over_time(vine_ids, num_values)

# Print the aggregated results
#for timestamp, total_grapes in aggregated_results.items():
#    unix_time = int(time.mktime(datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S').timetuple()))
#    print(f"Timestamp: {timestamp}, Unix Time: {unix_time}, Total Number of Grapes: {total_grapes}")

# Print the earliest timestamp
#if earliest_timestamp:
#    print(f"Earliest Timestamp: {earliest_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
#else:
#    print("No data found.")
