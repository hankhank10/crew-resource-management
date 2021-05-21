function get_live_data() {

    //console.log ("Updating data")
    let ident = localStorage.getItem('current_flight_unique_reference')

    if (ident === null) { return }

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

            localStorage.setItem('passenger_count_waiting_to_board', response.passenger_status.waiting_to_board);
            localStorage.setItem('passenger_count_boarding', response.passenger_status.boarding);
            localStorage.setItem('passenger_count_on_board', response.passenger_status.on_board);
            localStorage.setItem('passenger_count_deboarding', response.passenger_status.deboarding);
            localStorage.setItem('passenger_count_deboarded', response.passenger_status.deboarded);

            localStorage.setItem('passenger_count_seated_true', response.passenger_status.seated_true);
            localStorage.setItem('passenger_count_seated_false', response.passenger_status.seated_false);

            localStorage.setItem('passenger_count_total', response.passenger_status.occupied_seats);
            localStorage.setItem('seat_count_occupied', response.passenger_status.occupied_seats);
            localStorage.setItem('seat_count_empty', response.passenger_status.empty_seats);
            localStorage.setItem('seat_count_total', response.passenger_status.total_seats);

            localStorage.setItem('current_crew_task', response.crew_task.current_crew_task)
            localStorage.setItem('percent_done_with_task', response.crew_task.percent_done_with_task)

            // Check if new notifications
            if (localStorage.getItem('notification_count') != response.unread_flight_messages) {
                new PNotify({
                    title: 'New crew message',
                    text: 'New message received from crew',
                    type: 'default'
                });

                localStorage.setItem('notification_count', response.unread_flight_messages);

                update_notifications(response.unread_flight_messages);
            }

            if (response.new_event !== null) {
                new PNotify({
                    title: 'New flight event',
                    text: 'New event: '+response.new_event,
                    type: 'default'
                });
                document.getElementById('recent_events_iframe').src = document.getElementById('recent_events_iframe').src
            }

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
