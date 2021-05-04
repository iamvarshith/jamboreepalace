const date_arrival = document.getElementById('date-arrival')
const date_departure = document.getElementById('date-departure')
const adults = document.getElementById('adults')

function printError(elemId, hintMsg) {
    document.getElementById(elemId).innerHTML = hintMsg;
}

function validate_homeform() {

    if ((Date.parse(date_arrival) >= Date.parse(date_departure))) {
        return(alert("Departure date should be greater than arrival date"));
        document.getElementById("date-departure").value = "";
    }
    if (adults.value == null) {
        return(alert("No. of guests can't be empty"));
    }
}

function home_valcall(){
    return(
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

    ))
}






