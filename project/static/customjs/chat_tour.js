function run_tour() {
  introJs().setOptions({
  steps: [
    {
      element: document.querySelector('#tour_confused'),
      title: "Command your crew 📞",
      position: "bottom",
      intro: "This is the crew messenger where you can give your cabin crew commands and they will feed back information to you."
    },
    {
      element: document.querySelector('#tour_messages'),
      title: "Message log",
      position: "left",
      intro: "Messages to and from your crew will appear here."
    },
    {
      element: document.querySelector('#chat_input'),
      title: "Message input",
      position: "top",
      intro: "You can type messages to your crew here - there are no commands to learn, just use natural language such as 'start boarding' or 'start meal service'."
    },
    {
      element: document.querySelector('#send_button'),
      title: "Send",
      intro: "Once you've typed your message you can send it here."
    },
    {
      element: document.querySelector('#start_button'),
      title: "Voice recognition",
      intro: "Rather than typing you can also press the microphone button to use voice recognition.<br><br>This will depend on your browser (Chrome works best) and you will need to grant permission for use of your microphone by clicking the 🔒 key in the address bar."
    },
    {
      element: document.querySelector('#tour_cabin_announcement'),
      title: "Address the passengers",
      position: "right",
      intro: "You can address the passengers in the cabin by clicking here."
    }

  ]
  }).start();
}

