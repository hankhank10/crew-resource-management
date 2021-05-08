function run_tour() {
  introJs().setOptions({
  steps: [
    {
      element: document.querySelector('#card_current_location'),
      title: "Where am I? 📍",
      position: "right",
      intro: "This is a map of your plane's current location. It will update over time as your plane starts to move."
    },
    {
      element: document.querySelector('#card_flight_phase'),
      title: "Phases of flight",
      intro: "Your flight goes through various different phases. It will start at the gate, but will move through taxi, takeoff, cruise, descent and landing.<br><br>In many cases the simulator will automatically move flight phase for you, but you can also set the phase manually by clicking here."
    },
    {
      element: document.querySelector('#cabin-phase-status-card'),
      title: "Take your seats...",
      intro: "Your aircraft cabin starts empty. You can change the cabin phase by giving instructions to your cabin crew."
    },
    {
      element: document.querySelector('#tour_crew_instructions'),
      title: "Command your crew",
      position: 'right',
      intro: "You give your crew instructions - such as to start boarding, begin meal service, etc - through the crew messenger."
    },
    {
      element: document.querySelector('#door-status-card'),
      title: "Doors to manual...",
      intro: "Before you can let passengers on you need to open the aircraft doors.<br><br>You can do this in the simulator by connecting a jet bridge."
    },
    {
      element: document.querySelector('#card_sign_status'),
      title: "Some turbulence ahead...",
      intro: "Passengers will (usually) follow your instructions around seatbelts and no smoking.<br><br>You set these in the simulator using the relevant control."
    },
    {
      element: document.querySelector('#card_passenger_boarding_status'),
      title: "Where are my passengers?",
      position: 'left',
      intro: "Once you tell your crew to start boarding, this will show the overall status of the passenger boarding and whether they are seated or not."
    },
    {
      element: document.querySelector('#card_altitude'),
      title: "Altitude",
      position: 'right',
      intro: "An overview of your flight's altitude over time - it will also be annotated with key events that have occured."
    },
    {
      element: document.querySelector('#recent_events_iframe'),
      title: "What's going on?",
      position: 'left',
      intro: "Recent events that have occurred will be logged here."
    },
    {
      element: document.querySelector('#tour_seatmap_header'),
      title: "Your cabin",
      position: 'bottom',
      intro: "This is a graphical representation of your passengers on your plane.<br><br>You can get more information on a passenger by clicking their seat number."
    },
    {
      element: document.querySelector('#tour_seatmap_filter'),
      title: "Filter by status",
      position: 'left',
      intro: "You can choose how the seatmap is colored. The default is by class, but you can also show passengers by whether they are seated/standing or their hunger, thirst or bathroom need."
    },

  ]
  }).start();
}

