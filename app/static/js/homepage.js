$(document).ready(function() {
  $('form').on('submit', function(e){
    // validation code here
    if(!valid) {
      e.preventDefault();
    }
  });
});

function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(sendLocation)
    } else {
        x.innerHTML = "Geolocation is not supported by this browser.";
    }
}

function sendLocation(position) {
    var y = document.getElementById("locations");
    var option = document.createElement("option");
    let x = position.coords.latitude
    $.ajax({
        type: "POST",
        url: "/api/location",
        data: {lat: position.coords.latitude, long: position.coords.longitude},
        async: !0,
        cache: !1,
        success: function (data) {
            option.text = data.city
            option.value = data.city
            y.add(option)
            $('#locations').val(data.city)
            console.log(data.city)
        },

    });
}

function searchspace() {


    $.ajax({
            type: "POST",
            url: "/api/search",
            data: {
                location: $('#locations').val(),
                type: $('#room').val(),
                arrival: $('#date-arrival').val(),
                depature: $('#date-departure').val(),
                guests: $('#adults').val()
            },
            async: !0,
            cache: !1,
            success: function (data) {
                option.text = data.city
                option.value = data.city
                y.add(option)
                $('#locations').val(data.city)
                console.log(data.city)
            },
        }
    )
}
