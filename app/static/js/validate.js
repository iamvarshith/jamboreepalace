const date_arrival = document.getElementById('date-arrival')
const date_departure = document.getElementById('date-departure')
const adults = document.getElementById('adults')
const locations = document.getElementById('locations')

$(document).ready(function () {
    $("#form_search").on('submit', function (e) {
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
    var LocErr = true;

    if (date_arrival.value == "") {
        printError("ArDateErr", "Arrival date can't be empty");
    } else {
            printError("ArDateErr", "");
            ArDateErr = false;
        }

    if (date_departure.value == "") {
        printError("DeDateErr", "Departure date can't be empty");
    } else {
            printError("DeDateErr", "");
            DeDateErr = false;
        }

    if (locations.value == "") {
        printError("LocErr", "Departure date can't be empty");
    } else {
            printError("LocErr", "");
            LocErr = false;
        }


    if ((Date.parse(date_arrival) >= Date.parse(date_departure))) {
        printError("DateErr", "Departure date can't be lesser than arrival date");

    } else {
            printError("DateErr", "");
            DateErr = false;
        }
    if (adults.value() == null) {
        printError("AdultErr", "No. of guests can't be empty");
    } else {
            printError("AdultErr", "");
            AdultErr = false;
        }

    if (DateErr || ArDateErr || DeDateErr || LocErr || AdultErr == true) {
        return false;
    } else {
        return true;
    }
}

function home_valcall(){  return(
        validate_homeform()
        &&
            $.ajax({
            type:'POST',
            url : '/api/search',
            data:{
                location: $('#location').val(),
                type: $('#type').val(),
				from: $('#from').val(),
				to: $('#to').val(),
				guest: $('#guest').val()
            },
            async: !1,
            cache: !1,
            },



    ));
}

function submitFormhome() {
    validate_homeform()
    alert(validate_homeform())

}





