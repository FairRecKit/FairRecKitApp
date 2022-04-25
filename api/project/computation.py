# This program has been developed by students from the bachelor Computer Science at
# Utrecht University within the Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)
import json
import threading
import time
from datetime import datetime

from fairreckitlib.experiment.parsing.run import parse_experiment_config_from_yml
from fairreckitlib.recommender_system import RecommenderSystem
from fairreckitlib.experiment.config import *

from flask import (Blueprint, request)

from . import result_storage
from .options_formatter import create_available_options, config_dict_from_settings

compute_bp = Blueprint('computation', __name__, url_prefix='/api/computation')

recommender_system = RecommenderSystem('../../../datasets', 'results')
options = create_available_options(recommender_system)

computation_queue = []


def calculate_first():
    # TODO We need this delay for the queue to work fsr
    time.sleep(0.1)
    run_experiment()
    #mock_computation()


computation_thread = threading.Thread(target=calculate_first)


def run_experiment():
    # Get the oldest computation from the queue.
    computation = computation_queue.pop()
    print(computation)
    config_dict, id = config_dict_from_settings(computation)

    config_file_path = 'config_files/' + id
    with open(config_file_path + '.yml', 'w+') as config_file:
        yaml.dump(config_dict, config_file)

    recommender_system.run_experiment_from_yml(config_file_path, num_threads=4)
    result_storage.save_result(computation, mock_result(computation['settings']))  # TODO get real recs&eval result


def mock_computation():
    # Get the oldest computation from the queue.
    computation = computation_queue.pop() # TODO double code, refactor
    # Mock computation duration
    time.sleep(2.5)
    result_storage.save_result(computation, mock_result(computation['settings']))


def mock_result(settings):
    # Mocks result computation.
    result = []
    datasets = settings['datasets']
    for dataset in datasets:
        recs = []
        for approach in settings['approaches']:
            recommendation = {'approach': approach['name'], 'recommendation': recommend(dataset, approach), 'evals': []}
            for metric in settings['metrics']:
                evaluation = evaluate_all(dataset['settings'], approach, metric)

                recommendation['evals'].append({'name': metric['name'], 'evaluation': evaluation})
            recs.append(recommendation)
        result.append({'dataset': dataset, 'recs': recs})
    return result


# Route: Send selection options.
@compute_bp.route('/options', methods=['GET'])
def params():
    response = {'options': options}
    # print(response)
    return response


# Route: Do a calculation.
@compute_bp.route('/calculation', methods=['GET', 'POST'])
def calculate():
    response = {}
    if request.method == 'POST':
        data = request.get_json()
        settings = data.get('settings')
        # print(data)
        append_queue(data.get('metadata'), settings)

        # response = {'status': 'success'}
        response = json.dumps(computation_queue)
    else:
        # Wait until the current computation is done
        global computation_thread
        if computation_thread.is_alive():
            computation_thread.join()
        response['calculation'] = result_storage.newest_result()
    print('/calculation response:',response)
    return response


@compute_bp.route('/queue', methods=['GET', 'POST'])
def queue():
    # Handle computation thread.
    global computation_thread
    # If the thread is running, wait until it's done.
    if computation_thread.is_alive():
        computation_thread.join()
    # Else, if the queue isn't empty, start a thread to compute the oldest entry.
    elif computation_queue:
        print('Starting computation thread')
        computation_thread = threading.Thread(target=calculate_first)
        computation_thread.start()
    else:
        print('error')

    print('queue:',computation_queue)
    return json.dumps(computation_queue)


@compute_bp.route('/queue/delete', methods=['POST'])
# Pop the selected index from the queue
def deleteItem():
    data = request.get_json()
    index = data.get('index')
    computation_queue.pop(index)
    return "Removed index"


def recommend(dataset, approach):
    return dataset['name'] + approach['name'][::-1]  # Mock recommendation


def evaluate_all(settings, approach, metric):
    base_eval = evaluate(approach, metric)
    evaluation = {'global': base_eval, 'filtered': []}

    for setting in settings:
        # Evaluate per filter
        if setting['filters']:
            for filter in setting['filters']:
                evals = []
                for parameter in filter['parameter']:
                    value = parameter['value']
                    # Just use the value if it's a number, otherwise use the length of the word.
                    filter_eval = value if type(value) == int else len(value)
                    val = "%.2f" % (base_eval * len(filter['name']) / filter_eval)
                    evals.append({parameter['name'] + ' ' + str(value): val})
                evaluation['filtered'].append({filter['name']: evals})

    return evaluation


def evaluate(approach, metric):
    # Mock evaluation
    value = len(approach['name']) * len(metric['name'])

    # Do something with the metrics parameters.
    if hasattr(metric, 'parameter') and metric['parameter']:
        for parameter in metric['parameter']:
            value *= len(parameter['name'])

    return value


# add a computation request to the queue
def append_queue(metadata, settings):
    timestamp = time.time()
    now = datetime.now()
    current_dt = now.strftime('%Y-%m-%dT%H:%M:%S') + ('-%02d' % (now.microsecond / 10000))
    current_request = {'timestamp': {'stamp': str(int(timestamp)), 'datetime': current_dt}, 'metadata': metadata,
                       'settings': settings}
    computation_queue.append(current_request)
