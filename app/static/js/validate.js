const date_arrival = document.getElementById('date-arrival')
const date_departure = document.getElementById('date-departure')
const adults = document.getElementById('adults')
const locations = document.getElementById('locations')

$(document).ready(function () {
    $("#form_enlist").on('submit', function (e) {
        e.preventDefault();
    });
});

function printError(elemId, hintMsg) {
    document.getElementById(elemId).innerHTML = hintMsg;
}

function validate_homeform() {
    var DateErr = true;
    var ArDateErr = true;
    var DeDateErr = true;
    var AdultErr = true;
    var alerts = []

    if (date_arrival.value == "") {
        printError("ArDateErr", "Arrival date can't be empty");
    }

    if (date_departure.value == "") {
        printError("DeDateErr", "Departure date can't be empty");
    }

    if (locations.value == "") {
        printError("DeDateErr", "Departure date can't be empty");
    }


    if ((Date.parse(date_arrival) >= Date.parse(date_departure))) {
        printError("DateErr", "Departure date can't be lesser than arrival date");

    }
    if (adults.value() == null) {
        printError("AdultErr", "No. of guests can't be empty");
    }

    if (alerts == []){
         return('Validated')
    }
    else {
        return (alerts.values())
    }


    return((document.write(alerts[0], alerts[1])))

}

function home_valcall(){  return(
        validate_homeform()
        &&
            $.ajax({
            type:'POST',
            url : '/',
            data:{
                location: $('#location').val(),
                type: $('#type').val(),
				from: $('#from').val(),
				to: $('#to').val(),
				guest: $('#guest').val()
            }},

    ));
}






