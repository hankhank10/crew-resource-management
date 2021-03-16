function send_input() {

    $.getJSON({
        url: '/api/equipment/seatmap_parser',
        type: 'GET',
        data : {
            seatmap_text: $('#seatmap_text_input').val()
        },

        success: function (response) {

            $('#seat_count_total').text(response.seat_count_total)
            $('#seat_count_first_class').text(response.seat_count_first_class)
            $('#seat_count_business_class').text(response.seat_count_business_class)
            $('#seat_count_premium_class').text(response.seat_count_premium_class)
            $('#seat_count_economy_class').text(response.seat_count_economy_class)

            $('#number_of_seats_across').text(response.number_of_seats_across)
            $('#number_of_rows').text(response.number_of_rows)

            draw_table(response.number_of_seats_across, response.number_of_rows, response.seatmap_object)

            //console.log(response.seatmap_object)

        },
        contentType: 'application/json; charset=utf-8'
    });

}

function draw_table(max_x, max_y, seatmap_object) {

    let table = document.querySelector("#seatmap_table");

    while ( table.rows.length > 0 ) {
      table.deleteRow(0);
    }

    for (let y = 1; y <= max_y; y++) {
        let row = table.insertRow();

        for (let x = 1; x <= max_x; x++) {
            let cell = row.insertCell();
            //let text = document.createTextNode('<button class="btn brn-primary">Seat</button>');

            html_for_cell = 'X';

            cell.innerHTML = html_for_cell;
            cell.classList.add('individual_seat');
            cell.id = "seat-" + x + "-" + y
        }
    }

    seatmap_object.forEach(function (seat) {

        let relevant_cell_id = "#seat-" + seat.x + "-" + seat.y

        console.log(relevant_cell_id)

        if (seat.seat_type === " ") {
            $(relevant_cell_id).html("&nbsp")
        } else {

            //<h6>Example heading <span className="badge badge-secondary">New</span></h6>

            let badge_color;
            if (seat.seat_type === "F") { badge_color = "danger"}
            if (seat.seat_type === "B") { badge_color = "primary"}
            if (seat.seat_type === "P") { badge_color = "info"}
            if (seat.seat_type === "E") { badge_color = "success"}

            html_for_cell = '<h6><span data-toggle="tooltip" data-placement="top" title="tooltip on top" class="badge badge-'+ badge_color + '">' + seat.seat_number + '</span></h6>'
            $(relevant_cell_id).html(html_for_cell)
        }

    })
}