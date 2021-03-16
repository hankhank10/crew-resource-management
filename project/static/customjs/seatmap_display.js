function get_seatmap_data_from_server(filter_by) {

    let ident = localStorage.getItem('current_flight_unique_reference')

    $.ajax({
        url: '/api/passengers/list/'+ident,
        type: 'GET',
        success: function (response) {

            draw_table(filter_by, response.number_of_seats_across, response.number_of_rows, response.occupied_seats, response.empty_seats)

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

        console.log(relevant_cell_id)

        if (seat.seat_type === " ") {
            $(relevant_cell_id).html("&nbsp")
        } else {


            let badge_color;
            if (filter_by === "class") {
                if (seat.seat_type === "F") { badge_color = "danger"}
                if (seat.seat_type === "B") { badge_color = "primary"}
                if (seat.seat_type === "P") { badge_color = "info"}
                if (seat.seat_type === "E") { badge_color = "success"}
                html_for_cell = '<h6><span data-toggle="tooltip" data-placement="top" title="tooltip on top" class="badge badge-'+ badge_color + '">' + seat.seat_number + '</span></h6>'

            }

            if (filter_by === "seated") {
                if (seat.is_seated === true) { badge_color = "success"}
                if (seat.is_seated === false) { badge_color = "danger"}
                html_for_cell = '<h6><span data-toggle="tooltip" data-placement="top" title="tooltip on top" class="badge badge-'+ badge_color + '">' + seat.seat_number + '</span></h6>'
            }


            $(relevant_cell_id).html(html_for_cell)
        }

    })

    empty_seatmap_object.forEach(function (seat) {

        let relevant_cell_id = "#seat-" + seat.x + "-" + seat.y

        console.log(relevant_cell_id)

        if (seat.seat_type === " ") {
            $(relevant_cell_id).html("&nbsp")
        } else {

            let badge_color = "light";

            html_for_cell = '<h6><span data-toggle="tooltip" data-placement="top" title="tooltip on top" class="badge badge-'+ badge_color + '">' + seat.seat_number + '</span></h6>'
            $(relevant_cell_id).html(html_for_cell)
        }

    })
}