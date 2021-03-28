function update_notifications(number_of_crew_messages) {

    let number_of_notifications = number_of_crew_messages;

    if (number_of_crew_messages === 0) {
        $('#navbar_new_crew_message_notification_card').hide()
        $('#sidebar_unread_crew_messages').hide()

    } else {
        $('#navbar_new_crew_message_notification_card').show()
        $('#sidebar_unread_crew_messages').text(number_of_crew_messages)
        $('#sidebar_unread_crew_messages').show()
    }

    if (number_of_notifications === 0) {
        $('#navbar_notification_bell').html('<i class="far fa-bell"></i>')
    } else {
        $('#navbar_notification_bell').html('<i style="color: red" class="fas fa-bell"></i>')
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

