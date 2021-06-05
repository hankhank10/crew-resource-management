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

    current_user.tutorial_viewed_equipment = True
    db.session.commit()

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


@equipment.route('/equipment/new', methods=['GET'])
@login_required
def new():

    return render_template('equipment/new_equipment.html',
                           new = True,
                           existing_equipment = None)


@equipment.route('/equipment/<equipment_id>/save', methods=['POST'])
@login_required
def save(equipment_id):

    full_name = request.form['operator'] + " " + \
                request.form['manufacturer'] + " " + \
                request.form['model'] + " " + \
                request.form['variant'] + " "

    try:
        maximum_cabin_crew = int(request.form['maximum_cabin_crew'])
    except:
        maximum_cabin_crew = 1

    try:
        number_of_toilets = int(request.form['number_of_toilets'])
    except:
        number_of_toilets = 6

    seatmap_text = request.form['seatmap_text_input']

    seatmap_object = seatmapper.load_seatmap(seatmap_text)
    number_of_seats_across, number_of_rows = seatmapper.get_size(seatmap_object)

    first_class_seats = seatmapper.count_seats(seatmap_object, "F")
    business_class_seats = seatmapper.count_seats(seatmap_object, "B")
    premium_class_seats = seatmapper.count_seats(seatmap_object, "P")
    economy_class_seats = seatmapper.count_seats(seatmap_object, "E")

    if maximum_cabin_crew < 0:
        maximum_cabin_crew = 1

    if equipment_id == "new":

        new_equipment = EquipmentType(
            operator=request.form['operator'].rstrip(),
            manufacturer=request.form['manufacturer'].rstrip(),
            model=request.form['model'].rstrip(),
            variant=request.form['variant'].rstrip(),
            full_name=full_name.rstrip(),
            first_class_seats=first_class_seats,
            business_class_seats=business_class_seats,
            premium_class_seats=premium_class_seats,
            economy_class_seats=economy_class_seats,
            maximum_cabin_crew=maximum_cabin_crew,
            seatmap_text=seatmap_text,
            number_of_seats_across=number_of_seats_across,
            number_of_rows=number_of_rows,
            number_of_toilets=number_of_toilets,
            created_by_user=current_user.id
        )

        db.session.add(new_equipment)
        db.session.commit()

        flash("New equipment created", "success")

    else:
        equipment = EquipmentType.query.filter_by(id=equipment_id).first_or_404()

        if not equipment:
            flash("Equipment ID error", "danger")
            return redirect(url_for('equipment.view_list'))

        equipment.operator = request.form['operator'].rstrip()
        equipment.manufacturer = request.form['manufacturer'].rstrip()
        equipment.model = request.form['model'].rstrip()
        equipment.variant = request.form['variant'].rstrip()
        equipment.full_name = full_name.rstrip()
        equipment.first_class_seats = first_class_seats
        equipment.business_class_seats = business_class_seats
        equipment.premium_class_seats = premium_class_seats
        equipment.economy_class_seats = economy_class_seats
        equipment.maximum_cabin_crew = maximum_cabin_crew
        equipment.seatmap_text = seatmap_text
        equipment.number_of_seats_across = number_of_seats_across
        equipment.number_of_rows = number_of_rows
        equipment.number_of_toilets = number_of_toilets

        db.session.commit()
        flash("Equipment saved", "success")

    return redirect(url_for('equipment.view_list'))


@equipment.route('/equipment/<equipment_id>/duplicate')
@login_required
def duplicate(equipment_id):

    old_equipment = EquipmentType.query.filter_by(id = equipment_id).first_or_404()

    new_equipment = EquipmentType(
        operator=old_equipment.operator,
        manufacturer=old_equipment.manufacturer,
        model=old_equipment.model,
        variant=old_equipment.variant + "(new variant)",
        full_name=old_equipment.full_name + "(new variant)",
        first_class_seats=old_equipment.first_class_seats,
        business_class_seats=old_equipment.business_class_seats,
        premium_class_seats=old_equipment.premium_class_seats,
        economy_class_seats=old_equipment.economy_class_seats,
        maximum_cabin_crew=old_equipment.maximum_cabin_crew,
        seatmap_text=old_equipment.seatmap_text,
        number_of_seats_across=old_equipment.number_of_seats_across,
        number_of_rows=old_equipment.number_of_rows,
        number_of_toilets=old_equipment.number_of_toilets,
        created_by_user=current_user.id
    )
    db.session.add(new_equipment)
    db.session.commit()

    flash("Equipment successfully copied", "success")
    return redirect(url_for('equipment.edit', equipment_id = new_equipment.id))


@equipment.route('/equipment/<equipment_id>/edit', methods=['GET'])
@login_required
def edit(equipment_id):

    equipment = EquipmentType.query.filter_by(id=equipment_id).first()

    if not equipment:
        flash("Equipment ID error", "danger")
        return redirect(url_for('equipment.view_list'))

    if equipment.created_by_user != current_user.id:
        flash("Not authorised to edit that equipment", "danger")
        return redirect(url_for('equipment.view_list'))

    return render_template('equipment/new_equipment.html',
                           new = False,
                           existing_equipment=equipment
                           )


@equipment.route('/equipment/<equipment_id>/delete', methods=['GET'])
@login_required
def delete(equipment_id):

    equipment = EquipmentType.query.filter_by(id=equipment_id).first()

    if not equipment:
        flash("Equipment ID error", "danger")
        return redirect(url_for('equipment.view_list'))

    if equipment.created_by_user != current_user.id:
        flash("Not authorised to delete that equipment", "danger")
        return redirect(url_for('equipment.view_list'))

    db.session.delete(equipment)
    db.session.commit()

    flash("Equipment deleted", "success")
    return redirect(url_for('equipment.view_list'))


@equipment.route('/api/equipment/operator_logo', endpoint="operator")
@equipment.route('/api/equipment/manufacturer_logo', endpoint="manufacturer")
@login_required
def lookup_logo_endpoint():

    lookup_name = request.args.get('search_term')

    if lookup_name is not None:

        if request.endpoint == "equipment.operator": look_for = "operator"
        if request.endpoint == "equipment.manufacturer": look_for = "manufacturer"

        logo_url = equipment_logos.lookup_logo(lookup_name, look_for)
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
        'manufacturer_logo_url': item.manufacturer_logo_url,
        'number_of_rows': item.number_of_rows,
        'number_of_seats_across': item.number_of_seats_across
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
