let current_notifications = 0;

//This will be deprecated
function notification_check() {

    $.getJSON({
        url: '/api/inflight/messaging/check_messages',
        type: 'GET',

        success: function (response) {

            if (response.unread_flight_messages !== current_notifications) {
                update_notifications(response.unread_flight_messages);
            }

        },
        contentType: 'application/json; charset=utf-8'
    });

}

function update_notifications(number_of_notifications) {

    current_notifications = number_of_notifications;

    if (current_notifications === 0) {
        $('#navbar_new_crew_message_notification_card').hide()
        $('#navbar_notification_bell').html('<i class="far fa-bell"></i>')

        $('#sidebar_unread_crew_messages').hide()

    } else {
        $('#navbar_new_crew_message_notification_card').show()
        $('#navbar_notification_bell').html('<i style="color: red" class="fas fa-bell"></i>')
        $("#navbar_notification_bell").effect("pulsate");

        $('#sidebar_unread_crew_messages').text(current_notifications)
        $('#sidebar_unread_crew_messages').show()

    }

}



function shake(thing) {
  var interval = 100;
  var distance = 10;
  var times = 6;

  for (var i = 0; i < (times + 1); i++) {
    $(thing).animate({
      left:
        (i % 2 == 0 ? distance : distance * -1)
    }, interval);
  }
  $(thing).animate({
    left: 0,
    top: 0
  }, interval);
}



$('#navbar_new_crew_message_notification_card').hide()
$('#sidebar_unread_crew_messages').hide()

