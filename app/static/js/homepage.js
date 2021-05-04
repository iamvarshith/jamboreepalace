function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(sendLocation)
    } else {
        x.innerHTML = "Geolocation is not supported by this browser.";
    }
}

function sendLocation(position) {
    let x = position.coords.latitude
    $.ajax({
        type: "POST",
        url: "/api/location",
        data: {lat: position.coords.latitude, long: position.coords.longitude},
        async: !0,
        cache: !1,
        success: function (data) {
            $('#address').val(data.line1) & $('#address').addClass('filled');
            $('#pincode').val(data.pincode).addClass('filled');
            $('#landmark').val(data.landmark).addClass('filled');
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
        }
    )
}
