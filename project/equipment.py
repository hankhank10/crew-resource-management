from flask import Blueprint, render_template, Flask, current_app, jsonify, request, flash, redirect, url_for
from flask_login import login_required, current_user

from . import db
from . import app
from project import seatmapper, equipment_logos
from .models import EquipmentType



equipment = Blueprint('equipment', __name__)



@equipment.route('/equipment')
@login_required
def view_list():

    equipment_list = EquipmentType.query.all()

    return render_template('equipment/equipment_list.html', equipment_list = equipment_list)


@equipment.route('/api/equipment/seatmap_parser')
@login_required
def api_seatmap_parser():

    received_data = request.args.get('seatmap_text')
    seatmap = seatmapper.load_seatmap(received_data)

    number_of_seats_across, number_of_rows = seatmapper.get_size(seatmap)

    return jsonify({
        'status': 'ok',
        'seat_count_total': seatmapper.count_seats(seatmap),
        'seat_count_first_class': seatmapper.count_seats(seatmap, "F"),
        'seat_count_business_class': seatmapper.count_seats(seatmap, "B"),
        'seat_count_premium_class': seatmapper.count_seats(seatmap, "P"),
        'seat_count_economy_class': seatmapper.count_seats(seatmap, "E"),
        'number_of_seats_across': number_of_seats_across,
        'number_of_rows': number_of_rows,
        'seatmap_object': seatmap
    })


@equipment.route('/equipment/new', methods=['GET', 'POST'])
@login_required
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
            maximum_cabin_crew = int(request.form['maximum_cabin_crew'])
        except:
            maximum_cabin_crew = 1

        seatmap_text = request.form['seatmap_text_input']

        seatmap_object = seatmapper.load_seatmap(seatmap_text)

        first_class_seats = seatmapper.count_seats(seatmap_object, "F")
        business_class_seats = seatmapper.count_seats(seatmap_object, "B")
        premium_class_seats = seatmapper.count_seats(seatmap_object, "P")
        economy_class_seats = seatmapper.count_seats(seatmap_object, "E")

        if maximum_cabin_crew < 0: maximum_cabin_crew = 1

        new_equipment = EquipmentType(
            operator= request.form['operator'].rstrip(),
            manufacturer= request.form['manufacturer'].rstrip(),
            model= request.form['model'].rstrip(),
            variant= request.form['variant'].rstrip(),
            full_name= full_name.rstrip(),
            first_class_seats= first_class_seats,
            business_class_seats= business_class_seats,
            premium_class_seats= premium_class_seats,
            economy_class_seats= economy_class_seats,
            maximum_cabin_crew= maximum_cabin_crew,
            seatmap_text= seatmap_text,
            created_by_user= current_user.id,
        )

        db.session.add(new_equipment)
        db.session.commit()

        #load_equipment_from_json()
        #global equipment_list
        #equipment_list.append(new_equipment)
        #write_equipment_to_json()

        flash("New equipment created", "success")

        return redirect(url_for('equipment.view_list'))


@equipment.route('/api/equipment/operator_logo', endpoint="operator")
@equipment.route('/api/equipment/manufacturer_logo', endpoint="manufacturer")
@login_required
def lookup_logo_endpoint():

    lookup_name = request.args.get('search_term')

    if lookup_name is not None:

        if request.endpoint == "equipment.operator": look_for = "operator"
        if request.endpoint == "equipment.manufacturer": look_for = "manufacturer"

        logo_url = equipment_logos.lookup_logo (lookup_name, look_for)
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

    equipment_list = EquipmentType.query.all()

    result_list = []

    for item in equipment_list:
        if equipment_name.upper() in item.full_name.upper():
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

    item = EquipmentType.query.filter_by(full_name = equipment_name).first_or_404()

    return jsonify({
        'manufacturer': item.manufacturer,
        'variant': item.variant,
        'full_name': item.full_name,
        'operator': item.operator,
        'first_class_seats': item.first_class_seats,
        'business_class_seats': item.business_class_seats,
        'premium_class_seats': item.premium_class_seats,
        'economy_class_seats': item.economy_class_seats,
        'maximum_cabin_crew': item.maximum_cabin_crew,
        'approved_for_general_use': item.approved_for_general_use,
        'created_by_user': item.created_by_user,
        'seatmap_text': item.seatmap_text,
        'operator_logo_url': item.operator_logo_url,
        'manufacturer_logo_url': item.manufacturer_logo_url
    })


def check_if_already_exists(lookup_name):

    item_count = EquipmentType.query.filter_by(full_name = lookup_name).count()

    if item_count > 0: return True
    if item_count == 0: return False


@equipment.route('/api/equipment/check_if_exists')
def check_if_exists_endpoint():

    lookup_name = request.args.get('search_term')

    if lookup_name is None:
        return jsonify ({'status': 'error'})

    return jsonify({
        'status': 'success',
        'already_exists': check_if_already_exists(lookup_name)
    })



#equipment_filename = "equipment_list.json"
#equipment_list = []

