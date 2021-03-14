

function get_live_data() {

    //console.log ("Updating data")
    let ident = localStorage.getItem('current_flight_unique_reference')

    $.ajax({
        url: '/api/inflight/update_plane_data/'+ident,
        type: 'GET',
        success: function (response) {

            localStorage.setItem('current_altitude', response.my_plane.current_altitude);
            localStorage.setItem('current_compass', response.my_plane.current_compass);
            localStorage.setItem('current_latitude', response.my_plane.current_latitude);
            localStorage.setItem('current_longitude', response.my_plane.current_longitude);
            localStorage.setItem('current_speed', response.my_plane.current_speed);

            localStorage.setItem('door_status', response.my_plane.door_status);
            localStorage.setItem('gear_handle_position', response.my_plane.gear_handle_position);
            localStorage.setItem('parking_brake', response.my_plane.parking_brake);
            localStorage.setItem('no_smoking_sign', response.my_plane.no_smoking_sign);
            localStorage.setItem('seatbelt_sign', response.my_plane.seatbelt_sign);
            localStorage.setItem('on_ground', response.my_plane.on_ground);

            localStorage.setItem('phase_flight_name', response.phase_flight_name);
            localStorage.setItem('phase_cabin_name', response.phase_cabin_name);

            localStorage.setItem('last_updated_data', Date.now().toString());

            localStorage.setItem('passenger_status_waiting_to_board', response.passenger_status.waiting_to_board);
            localStorage.setItem('passenger_status_boarding', response.passenger_status.boarding);
            localStorage.setItem('passenger_status_seated', response.passenger_status.seated);
            localStorage.setItem('passenger_status_unseated', response.passenger_status.unseated);
            localStorage.setItem('passenger_status_deboarded', response.passenger_status.deboarded);
            localStorage.setItem('passenger_status_total', response.passenger_status.total);


            update_notifications(response.unread_flight_messages);
            update_display();

        },
        contentType: 'application/json; charset=utf-8'
    });

}

function regular_checks() {

    get_live_data()

}

function set_card_status(card_name, card_color, card_data) {

    full_card_name = '#'+card_name+'-status-card'
    full_label_name = '#'+card_name+'-status-label'

    $(full_card_name).removeClass('bg-c-yellow').removeClass('bg-c-red').removeClass('bg-c-green').removeClass('bg-c-blue')
    $(full_card_name).addClass('bg-c-'+card_color)
    $(full_label_name).text(card_data)

}

function set_icon(icon_name, fontawesome_icon_code) {




}