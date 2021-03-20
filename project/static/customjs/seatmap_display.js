//hide_passenger_details()


function show_passenger_details (seat_number) {

    let ident = localStorage.getItem('current_flight_unique_reference')

    //window.alert(seat_number)

    $.ajax({
        url: '/api/passengers/'+ ident +'/'+ seat_number,
        type: 'GET',
        success: function (response) {

            $('#passenger_detail_name').text(response.full_name)

            travel_class = response.seat_type_text
            if (travel_class === "First") { badge_color = "danger"}
            if (travel_class === "Business") { badge_color = "primary"}
            if (travel_class === "Premium") { badge_color = "info"}
            if (travel_class === "Economy") { badge_color = "success"}
            html_for_cell = '<h6><span class="badge badge-'+ badge_color + '">' + travel_class + '</span></h6>'

            $('#passenger_detail_class').html(html_for_cell)
            $('#passenger_detail_frequent_flyer').html('<h6><span class="badge badge-success">' + response.frequent_flyer_status_text + '</span></h6>')
            $('#passenger_detail_seat_number').html('<h6><span class="badge badge-light">' + response.seat_number + '</span></h6>')

            console.log(response.status_hunger_text)
            if (response.status_hunger_text === "") {
                $('#passenger_detail_hunger').hide()
            } else {
                $('#passenger_detail_hunger').html(response.status_hunger_text)
                $('#passenger_detail_hunger').show()
            }

            if (response.status_bladder_need_text === "") {
                $('#passenger_detail_bladder').hide()
            } else {
                $('#passenger_detail_bladder').html(response.status_bladder_need_text)
                $('#passenger_detail_bladder').show()
            }

            if (response.status_thirst_text === "") {
                $('#passenger_detail_thirst').hide()
            } else {
                $('#passenger_detail_thirst').html(response.status_thirst_text)
                $('#passenger_detail_thirst').show()
            }

            random_photo = "https://fakeface.rest/thumb/view?gender=male&minimum_age=26&random_nonsense=" + Math.random();
            $('#passenger_detail_photo').attr("src", random_photo);

            passenger_details_box = document.getElementById('passenger_details_outer');

            let instance = tippy(document.querySelector('#seat_badge_'+seat_number), {
                content: passenger_details.innerHTML,
                allowHTML: true,
                placement: 'right',
                theme: 'light',
            });
            instance.show()

            //$('#passenger_details').show()

        },
        contentType: 'application/json; charset=utf-8'
    });

}

function hide_passenger_details () {
    $('#passenger_details').hide()
}

function get_seatmap_data_from_server(filter_by) {

    let ident = localStorage.getItem('current_flight_unique_reference')

    $.ajax({
        url: '/api/passengers/list/'+ident,
        type: 'GET',
        success: function (response) {

            draw_table(filter_by, response.number_of_seats_across, response.number_of_rows, response.occupied_seats, response.empty_seats)

            $('#first_class_count').text(response.passengers_first_class)
            $('#business_class_count').text(response.passengers_business_class)
            $('#premium_class_count').text(response.passengers_premium_class)
            $('#economy_class_count').text(response.passengers_economy_class)
            $('#empty_seat_count').text(response.seat_count_empty)


        },
        contentType: 'application/json; charset=utf-8'
    });

}

function draw_table(filter_by, max_x, max_y, occupied_seatmap_object, empty_seatmap_object) {

    let table = document.querySelector("#seatmap_table");

    while ( table.rows.length > 0 ) {
      table.deleteRow(0);
    }

    for (let y = 1; y <= max_y; y++) {
        let row = table.insertRow();

        for (let x = 1; x <= max_x; x++) {
            let cell = row.insertCell();
            //let text = document.createTextNode('<button class="btn brn-primary">Seat</button>');

            html_for_cell = ' ';

            cell.innerHTML = html_for_cell;
            cell.classList.add('individual_seat');
            cell.id = "seat-" + x + "-" + y
        }
    }

    occupied_seatmap_object.forEach(function (seat) {

        let relevant_cell_id = "#seat-" + seat.x + "-" + seat.y

        if (seat.seat_type === " ") {
            $(relevant_cell_id).html("&nbsp")
        } else {

            let badge_color;
            if (filter_by === "class") {
                if (seat.seat_type === "F") {
                    badge_color = "danger"
                }
                if (seat.seat_type === "B") {
                    badge_color = "primary"
                }
                if (seat.seat_type === "P") {
                    badge_color = "info"
                }
                if (seat.seat_type === "E") {
                    badge_color = "success"
                }
            }

            if (filter_by === "seated") {
                if (seat.is_seated === true) {
                    badge_color = "success"
                }
                if (seat.is_seated === false) {
                    badge_color = "danger"
                }
                if (seat.status === "Waiting to Board") {
                    badge_color = "warning"
                }
            }

            let onclick_html = "show_passenger_details('" + seat.seat_number + "')"
            html_for_cell = '<h6><span id="seat_badge_'+ seat.seat_number +'" onclick="' + onclick_html + '" data-tippy-seat="' + seat.seat_number + '" class="badge badge-' + badge_color + '">' + seat.seat_number + '</span></h6>'
            $(relevant_cell_id).html(html_for_cell)
        }

        //$(".seat_badge").each(function() {
        //    tippy($(this)[0], {
        //        content: "Hi " + $(this).attr("data-tippy-seat"),
        //    });
        //});

    })

    empty_seatmap_object.forEach(function (seat) {

        let relevant_cell_id = "#seat-" + seat.x + "-" + seat.y

        //console.log(relevant_cell_id)

        if (seat.seat_type === " ") {
            $(relevant_cell_id).html("&nbsp")
        } else {

            let badge_color = "light";

            html_for_cell = '<h6><span data-toggle="tooltip" data-placement="top" title="tooltip on top" class="badge badge-'+ badge_color + '">' + seat.seat_number + '</span></h6>'
            $(relevant_cell_id).html(html_for_cell)
        }

    })
}
