from flask import Flask, jsonify, request

import time

IDLE_DELTA = 10

api = Flask(__name__)

services_name_to_data = dict()


def timestamp_in_range(timestamp, start_time, end_time):
    return start_time - IDLE_DELTA <= timestamp <= end_time + IDLE_DELTA


def belongs(entry, state, timestamp):
    return entry['state'] == state and timestamp_in_range(timestamp, entry["start_time"], entry["end_time"])


# Search if the event belongs to an existing entry
def search(service_name, state, timestamp):
    for entry in services_name_to_data[service_name]:
        if belongs(entry, state, timestamp):
            return entry
    return None


def update_existing_entry(entry, timestamp):
    entry["start_time"] = min(entry["start_time"], timestamp)
    entry["end_time"] = max(entry["end_time"], timestamp)
    entry["timestamps"].append(timestamp)


def find_location_to_split(service_name, timestamp):
    service_data = services_name_to_data[service_name]
    for index in range(len(service_data)):
        entry = service_data[index]
        if entry["start_time"] <= timestamp <= entry["end_time"]:
            return index
    return -1


# find a location to insert a new entry
def find_location_to_insert(service_name, timestamp):
    service_data = services_name_to_data[service_name]
    for index in range(len(service_data)):
        entry = service_data[index]
        if entry["end_time"] < timestamp:
            return index
    return len(service_data)


def insert_entry(l, location, state, start_time, end_time, timestamps):
    l.insert(location, {
        "state": state,
        "start_time": start_time,
        "end_time": end_time,
        "timestamps": timestamps
    })


# find a location to split, if the current event needs to split a state into two different ones
def split(service_name, location, timestamp):
    service_data = services_name_to_data[service_name]
    entry = service_data[location]
    upper_timestamps = [t for t in service_data["timestamps"] if t > timestamp]
    lower_timestamps = [t for t in service_data["timestamps"] if t <= timestamp]
    service_data.remove(entry)
    insert_entry(service_data, location, entry["state"], min(upper_timestamps), max(upper_timestamps), upper_timestamps)
    insert_entry(service_data, location + 1, entry["state"], min(lower_timestamps), max(lower_timestamps),
                 lower_timestamps)
    return location + 1


def insert_new_entry(location, service_name, state, timestamp):
    service_data = services_name_to_data[service_name]
    service_data.insert(location, {
        "start_time": timestamp,
        "end_time": timestamp,
        "state": state,
        "timestamps": [timestamp]
    })


# check if we need to unify two entries with the same states
def unify_if_needed(service_name):
    service_data = services_name_to_data[service_name]
    for location in range(min(len(service_data), 1), len(service_data)):
        prev = service_data[location - 1]
        current = service_data[location]
        if prev["state"] == current["state"] and prev["start_time"] <= current["end_time"] + IDLE_DELTA:
            prev["start_time"] = current["start_time"]
            prev["timestamps"].extend(current["timestamps"])
            service_data.remove(current)
            return


@api.route('/event', methods=['POST'])
def post_event():
    req_json = request.get_json()
    service_name = req_json['service_name']
    state = req_json['state']
    timestamp = req_json['timestamp']
    if service_name not in services_name_to_data:
        services_name_to_data[service_name] = []

    entry = search(service_name, state, timestamp)
    if entry is not None:
        update_existing_entry(entry, timestamp)
    else:
        location = find_location_to_split(service_name, timestamp)
        if location != -1:
            location = split(service_name, location)
        else:
            location = find_location_to_insert(service_name, timestamp)
        insert_new_entry(location, service_name, state, timestamp)
    unify_if_needed(service_name)
    services_name_to_data[service_name] = services_name_to_data[service_name][:50]
    return '', 200


@api.route('/services', methods=['GET'])
def get_all_services():
    services_data = dict()
    for service_name, l in services_name_to_data.items():
        entry = l[0]
        if entry["end_time"] + IDLE_DELTA >= time.time():
            state = entry["state"]
            since = entry["start_time"]
        else:
            state = "idle"
            since = entry["end_time"] + IDLE_DELTA
        services_data[service_name] = {
            "state": state,
            "since": since,
        }
    return jsonify(services_data), 200


@api.route('/services/<service_name>/latest-events', methods=['GET'])
def get_latest_events(service_name):
    return_value = []
    if service_name not in services_name_to_data:
        return "service name not found", 404
    service_data = services_name_to_data[service_name]
    count = 0
    index = 0
    # run over every state entry and create events from it, no more than 50 events
    while count < 50 and index < len(service_data):
        entry = service_data[index]
        entry_end_time = entry["end_time"] + IDLE_DELTA
        if index == 0:
            end_time = entry_end_time if entry_end_time < time.time() else None
        else:
            prev = service_data[index - 1]
            end_time = prev["start_time"] if prev["start_time"] < entry_end_time else entry_end_time
        for i in range(min(50 - count, len(entry["timestamps"]))):
            return_value.append({
                "start_time": entry["start_time"],
                "end_time": end_time,
                "state": entry["state"]
            })
            count += 1

        index += 1
    return jsonify(return_value), 200


@api.route('/reset', methods=["GET"])
def perform_reset():
    global services_name_to_data
    services_name_to_data = dict()
    return '', 200


if __name__ == '__main__':
    api.run(host='0.0.0.0', port=8080)
