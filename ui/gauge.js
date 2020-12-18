var net = require('net');
var jQuery = require('jquery');

jQuery(function () {
    let degrees = 0;
    let needle = $(".needle").first();

    $('#btn').on("click", function () {
        var client = net.connect({ port: 8484 }, function () {
            console.log('Connection established!');
        });

        client.on('data', function (data) {
            document.write(data.toString());
            client.end();
        });

        client.on('end', function () {
            console.log('Disconnected :(');
        });
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