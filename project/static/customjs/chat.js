var speech = new Speech();
let recording = false;

let final_transcript = '';

$('#recent_message_card').hide()
$('#recent_reply_card').hide()


function capitaliseFirstLetter(s) {
    return s.charAt(0).toUpperCase() + s.slice(1)
}

function Speech() {
  if ('webkitSpeechRecognition' in window) {
    // creating voice capture object
    this.recognition = new webkitSpeechRecognition();

    // settings
    this.recognition.continuous = true; // stop automatically
    this.recognition.interimResults = true;

    this.startCapture = function() {
        console.log("Started")
        this.recognition.start();

        $('#chat_input').val("Listening...")
        $('#start_button').addClass('btn-danger');
        $('#start_button').html('<i className="fas fa-spinner fa-spin"></i>')

        recording = true;
    }

    this.stopCapture = function() {
        this.recognition.stop();
        console.log("Stopped")
        $('#start_button').removeClass('btn-danger');
        recording = false;
    }

    this.recognition.onresult = function(event) {

        var interim_transcript = '';
        let current_portion = '';

        for (var i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
                current_portion = event.results[i][0].transcript
                final_transcript = final_transcript + current_portion + '.';
            } else {
                interim_transcript += event.results[i][0].transcript;
            }
        }

        $('#chat_input').val(final_transcript + interim_transcript)
    }

    this.recognition.onerror = function(event) {
        console.log(event.error);
    }

    console.log("webkitSpeechRecognition is available.");
  } else {
    console.log("webkitSpeechRecognition is not available.");
  }
}

function startButton(event) {
    console.log ("Button pressed")

    if (recording === false) {
        speech.startCapture();
    } else {
        speech.stopCapture();
    }
}

function sendMessage() {

    $.getJSON({
        url: '/api/inflight/messaging/send_message',
        type: 'GET',
        data : {
            message_to: 'crew',
            message_content: $('#chat_input').val()
        },

        success: function (response) {

            $('#recent_message_card').show();
            $('#recent_message_text').html($('#chat_input').val())
            $('#chat_input').val('')

            setTimeout(() => {$('#recent_reply_card').show();}, 1000);
            setTimeout(() => { location.reload()}, 4000)

        },
        contentType: 'application/json; charset=utf-8'
    });

}