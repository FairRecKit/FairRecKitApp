"""
This program has been developed by students from the bachelor Computer Science at
Utrecht University within the Software Project course.
© Copyright Utrecht University (Department of Information and Computing Sciences)
"""
import json
import os

# Global current result variables
current_result = {}
current_recs = None

# Storage paths
RESULTS_OVERVIEW_PATH = 'results.json'


def save_result(computation, result):
    """Save result to overview.

    Args:
        computation(dict): the computation settings
        result(dict): the computed result
    """
    global current_result
    computation['result'] = result

    # Parse tags
    if 'tags' in computation['metadata']:
        computation['metadata']['tags'] = parse_tags(computation['metadata']['tags'])

    current_result = computation
    add_result(current_result)
    print(current_result)


def result_by_id(result_id):
    """Set the current result to a result in the results overview by its id.

    Args:
        result_id(int): the result id
    """
    results = load_json(RESULTS_OVERVIEW_PATH)

    # Filter: Loop through all results and find the one with the matching ID.
    for result in results['all_results']:
        global current_result
        if 'timestamp' in result:
            if result['timestamp']['stamp'] == result_id:
                # print('result', result)
                current_result = result
        else:
            # If there is an incorrectly formatted result, return nothing.
            current_result = None

    # print('current result',current_result)


def load_json(path):
    """Load a JSON file to a dictionary using its path.

    Args:
        path(string): the path to the JSON file
    Returns:
        (dict) the JSON as a dictionary
    """
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)  # Load existing data into a dict.


def load_results_overview():
    """Load the results overview.

    Returns:
        (dict) the loaded results
    """
    # Ensure the results overview exists.
    create_results_overview()
    return load_json(RESULTS_OVERVIEW_PATH)


def write_results_overview(results):
    """Write (store) results to the overview.

    Args:
        results(dict): the results to store
    """
    # Open the file in write mode.
    with open(RESULTS_OVERVIEW_PATH, 'w', encoding='utf-8') as file:
        # Store it as json data.
        json.dump(results, file, indent=4)


def add_result(result):
    """Add a result at the end of the results overview.

    Args:
        result(dict): the (new) result
    """
    file_results = load_results_overview()
    file_results['all_results'].append(result)
    write_results_overview(file_results)


def delete_result(index):
    """Delete a result by its index.

    Args:
        index(int): the index of the result
    """
    file_results = load_results_overview()
    file_results['all_results'].pop(index)
    write_results_overview(file_results)


def edit_result(index, new_name, new_tags, new_email):
    """Edit a result.

    Args:
        index(int): the result index
        new_name(string): the new metadata name of the result
        new_tags(string): the new metadata tags of the result
        new_email(string): the new metadata email of the result
    """
    file_results = load_results_overview()
    to_edit_result = file_results['all_results'][index]
    print(new_tags)

    def edit_metadata(attr, new_val):
        # Don't change the attribute if the input field has been left empty
        if new_val != '':  #
            to_edit_result['metadata'][attr] = new_val
            print('changed '+attr, to_edit_result['metadata'][attr])

    for (data_name, new_data) in [('name', new_name), ('tags', new_tags), ('email', new_email)]:
        edit_metadata(data_name, new_data)

    # TODO Add more editable values
    file_results['all_results'][index] = to_edit_result

    write_results_overview(file_results)


def create_results_overview():
    """Create a results file if it doesn't exist yet or is empty."""
    if not os.path.exists(RESULTS_OVERVIEW_PATH) or os.stat(RESULTS_OVERVIEW_PATH).st_size == 0:
        with open(RESULTS_OVERVIEW_PATH, 'w', encoding='utf-8') as file:  # Open the file in write mode.
            json.dump({'all_results': []}, file, indent=4)


def parse_tags(tags_string):
    """Parse result tags (given by user as metadata)

    Args:
        tags_string(string): the tags as raw string input (comma-separated)

    Returns:
        the split list of tags
    """
    # Split tags by comma and get the unique tags
    unique = list(set(tags_string.split(',')))
    # Remove empty tags
    return [tag for tag in unique if tag]
