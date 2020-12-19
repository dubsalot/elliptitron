var net = require('net');
var jQuery = require('jquery');

jQuery(function () {
    let degrees = 0;
    let needle = $(".needle").first();
    
    $('#btn').on("click", function (e) {
        e.preventDefault();
        var client = net.connect({ port: 8484 }, function () {
            console.log('Connection established!');
        });

        client.on('data', function (data) {
            if (degrees >= 179) {
                degrees = 0;
            }
            else {
                degrees += 5;
            }
            client.end();
        });

        client.on('end', function () {
            //console.log('Disconnected :(');
        });
        // if (degrees >= 179) {
        //     degrees = 0;
        // }
        // else {
        //     degrees += 5;
        // }
        needle.css("transform", "rotate(" + degrees.toString() + "deg)");
        console.log("hello");
    });

    // setInterval(() => {
    //     if (degrees >= 179)
    //     {
    //         degrees = 0;
    //     }
    //     else { 
    //         degrees += 5;
    //     }
    //     needle.css("transform", "rotate(" + degrees.toString() + "deg)");            
    // }, 500);
});