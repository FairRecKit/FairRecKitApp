# This program has been developed by students from the bachelor Computer Science at
# Utrecht University within the Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)
import csv  # TODO fix this import
import json
import os
from csv import writer
import time
import datetime

# Results overview format
# timestamp (ID)
# metadata: name, tag
# settings: datasets, approaches, metrics, per metric: name, k value

# Result detail format
# timestamp (ID), per dataset: recommendations result, per recs result: metrics evaluations

current_result = {}
results_path = 'results.json'
recommendations_path = 'recs.json'
evaluations_path = 'evals.json'

def save_result(metadata, settings, result):
    timestamp = time.time()
    now = datetime.datetime.now()
    currentDt = now.strftime('%Y-%m-%dT%H:%M:%S') + ('-%02d' % (now.microsecond / 10000))

    global current_result  # TODO use class instead of global?
    current_result = {'timestamp': {'stamp': timestamp, 'datetime' : currentDt}, 'metadata': metadata, 'settings': settings, 'result': result}
    update_results(current_result)


def newest_result():
    return current_result


def load_results():
    with open(results_path, 'r') as file:
        return json.load(file)  # Load existing data into a dict.


def update_results(new_result):
    create_results()
    file_data = load_results()
    file_data['all_results'].append(new_result)
    with open(results_path, 'w') as file:  # Open the file in write mode.
        # Rewind file pointer's position.
        file.seek(0)
        # Store it as json data.
        json.dump(file_data, file, indent=4)


# Create results file if it doesn't exist yet or is empty
def create_results():
    if not os.path.exists(results_path) or os.stat(results_path).st_size == 0:
        with open(results_path, 'w') as file:  # Open the file in write mode.
            json.dump({'all_results': []}, file, indent=4)
