
function get_live_data(ident) {


    $.ajax({
        url: 'https://findmyplane.live/api/plane/'+ident,
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

            localStorage.setItem('last_updated_data', Date.now().toString())

        },
        contentType: 'application/json; charset=utf-8'
    });

}

