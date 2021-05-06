from flask import Blueprint, render_template, Flask, current_app, jsonify, request
import csv


api_airport_lookup = Blueprint('api_airport_lookup', __name__)
airport_list = []


def load_airports_from_csv():
    global airport_list
    with open('data_sources/airports.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['type'] == "large_airport" or row['type'] == "medium_airport" or row['type'] == "small airport":
                new_airport = {
                    'name': row['name'],
                    'ident': row['ident']
                }
                airport_list.append(new_airport)


@api_airport_lookup.route('/api/airport_lookup/code/<airport_code>')
def api_airport_lookup_by_code(airport_code):

    for airport in airport_list:
        if airport['ident'].upper() == airport_code.upper():
            airport_name = airport['name']

    if 'airport_name' in locals():
        return jsonify ({
            'status': "success",
            'airport_code': airport_code.upper(),
            'airport_name': airport_name
        })
    else:
        return jsonify ({
            'status': 'error'
        })


@api_airport_lookup.route('/api/airport_lookup/suggest_name')
def api_airport_lookup_by_name():

    airport_name = request.args.get('query')
    result_list = []

    for airport in airport_list:
        if airport_name.upper() in airport['name'].upper():
            result_list.append({
                'value': airport['name'],
                'data': airport['ident']
            })

    if len(result_list) > 0:
        return jsonify ({
            'suggestions': result_list
        })
    else:
        return jsonify ({
            'status': 'error'
        })


load_airports_from_csv()
