from flask import Blueprint, render_template, Flask, current_app, jsonify, request, flash, redirect, url_for
import json
import os.path


equipment = Blueprint('equipment', __name__)


def write_equipment_to_json():
    with open(equipment_filename, "w") as write_file:
        json.dump(equipment_list, write_file)


def load_equipment_from_json():
    global equipment_list

    if not os.path.isfile(equipment_filename):
        write_equipment_to_json()
        return

    with open(equipment_filename, "r") as read_file:
        equipment_list = json.load(read_file)

    for item in equipment_list:
        item['manufacturer']


def load_logos_from_json():
    global logo_list

    with open(logo_filename, "r") as read_file:
        logo_list = json.load(read_file)


@equipment.route('/equipment')
def view_list():

    add_logos_to_json()
    load_equipment_from_json()

    return render_template('equipment/equipment_list.html', equipment_list = equipment_list)


@equipment.route('/equipment/new', methods=['GET', 'POST'])
def new():

    if request.method == "GET":
        return render_template('equipment/new_equipment.html')

    if request.method == "POST":

        full_name = request.form['operator'] + " " + \
                    request.form['manufacturer'] + " " + \
                    request.form['model'] + " " + \
                    request.form['variant'] + " "

        if check_if_already_exists(full_name):
            flash ("Name already exists", "danger")
            return redirect(url_for('equipment.create_new'))

        try:
            first_class_seats = int(request.form['first_class_seats'])
        except:
            first_class_seats = 0

        try:
            business_class_seats = int(request.form['business_class_seats'])
        except:
            business_class_seats = 0

        try:
            premium_class_seats = int(request.form['premium_class_seats'])
        except:
            premium_class_seats = 0

        try:
            economy_class_seats = int(request.form['economy_class_seats'])
        except:
            economy_class_seats = 0

        try:
            maximum_cabin_crew = int(request.form['maximum_cabin_crew'])
        except:
            maximum_cabin_crew = 1

        if maximum_cabin_crew < 0: maximum_cabin_crew = 1

        new_equipment = {
            'operator': request.form['operator'].rstrip(),
            'manufacturer': request.form['manufacturer'].rstrip(),
            'model': request.form['model'].rstrip(),
            'variant': request.form['variant'].rstrip(),
            'full_name': full_name.rstrip(),
            'first_class_seats': first_class_seats,
            'business_class_seats': business_class_seats,
            'premium_class_seats': premium_class_seats,
            'economy_class_seats': economy_class_seats,
            'maximum_cabin_crew': maximum_cabin_crew
        }

        load_equipment_from_json()
        global equipment_list
        equipment_list.append(new_equipment)
        write_equipment_to_json()

        flash("New equipment created", "success")

        return redirect(url_for('equipment.view_list'))


def lookup_logo(lookup_name, look_for):

    relevant_list = logo_list

    for logo in relevant_list:
        if lookup_name.upper() == logo['name'].upper():
            return logo['logo_url']

    return ""


def add_logos_to_json():
    global equipment_list

    load_logos_from_json()
    load_equipment_from_json()

    for item in equipment_list:
        item['operator_logo_url'] = lookup_logo(item['operator'], "operator")
        item['manufacturer_logo_url'] = lookup_logo(item['manufacturer'], "manufacturer")

    write_equipment_to_json()


@equipment.route('/api/equipment/operator_logo', endpoint="operator")
@equipment.route('/api/equipment/manufacturer_logo', endpoint="manufacturer")
def lookup_logo_endpoint():

    lookup_name = request.args.get('search_term')

    if lookup_name is not None:

        if request.endpoint == "equipment.operator": look_for = "operator"
        if request.endpoint == "equipment.manufacturer": look_for = "manufacturer"

        relevant_list = logo_list

        logo_url = lookup_logo (lookup_name, look_for)
        if logo_url == "":
            return jsonify({'status': 'error'})

        return jsonify ({
            'status': 'success',
            'name': lookup_name,
            'logo_url': logo_url
        })


@equipment.route('/api/equipment/suggest_name')
def api_suggest_name():

    equipment_name = request.args.get('query')
    result_list = []

    for item in equipment_list:
        if equipment_name.upper() in item['full_name'].upper():
            result_list.append({
                'value': item['full_name'],
            })

    if len(result_list) > 0:
        return jsonify({
            'suggestions': result_list
        })
    else:
        return jsonify({
            'status': 'error'
        })


@equipment.route('/api/equipment/details')
def api_details():

    equipment_name = request.args.get('search_term')
    print(equipment_name)

    for item in equipment_list:
        if equipment_name.upper() == item['full_name'].upper():
            return jsonify(item)


def check_if_already_exists(lookup_name):
    load_equipment_from_json()

    for item in equipment_list:
        if item['full_name'].rstrip() == lookup_name.rstrip():
            return True

    return False


@equipment.route('/api/equipment/check_if_exists')
def check_if_exists_endpoint():

    lookup_name = request.args.get('search_term')

    if lookup_name is None:
        return jsonify ({'status': 'error'})

    return jsonify({
        'status': 'success',
        'already_exists': check_if_already_exists(lookup_name)
    })



equipment_filename = "equipment_list.json"
equipment_list = []

logo_filename = "logos.json"
logo_list = []

load_equipment_from_json()
load_logos_from_json()
