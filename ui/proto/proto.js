var net = require('net');
var jQuery = require('jquery');

function degToRad(degree) {
    var factor = Math.PI / 180;
    return degree * factor;
}


function Meter(percentage, val, label, canvas) {
    var canvas = document.getElementById(canvas);
    var ctx = canvas.getContext('2d');
    ctx.strokeStyle = '#28d1fa';

    
    ctx.lineCap = 'round';
    ctx.shadowBlur = 15;
    ctx.shadowColor = '#28d1fa';

          // Background
    gradient = ctx.createRadialGradient(200, 200, 5, 200, 200, 300);
    gradient.addColorStop(0, '#09303a');
    gradient.addColorStop(1, '#000000');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, 400, 400);

    var to = 140 + ((350 - 140) * (percentage / 100));
    var from = 140;

    if(to > 350)
    {
        to = 350;
    }

    if(from < 140)
    {
        from = 140;
    }

    console.log(from, "from");
    console.log(to, "to");
    console.log(percentage, "percentage");
    console.log(val, "val");
    console.log(label, "label");
    console.log(canvas, "canvas");


    console.log(degToRad(from), "degToRad(from)");
    console.log(degToRad(350), "degToRad(350)");
    console.log(degToRad((350 - 140) / 2), "degToRad((350 - 140) / 2)");

    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(200, 200, 180, degToRad(from), degToRad(350));
    ctx.stroke();
    
    ctx.lineWidth = 17;
    ctx.beginPath();
    ctx.arc(200, 200, 180, degToRad(from), degToRad(to));
    ctx.stroke();

    ctx.font = "100px Helvetica";
    ctx.fillStyle = '#28d1fa';
    ctx.fillText(val, 75, 220);

    // Time
    ctx.font = "15px Helvetica";
    ctx.fillStyle = '#28d1fa';
    ctx.fillText(label, 75, 250);
}

    // jQuery(function () {
    //     let degrees = 0;
    //     let needle = $(".needle").first();

    //     $('#btn').on("click", function (e) {
    //         e.preventDefault();
    //         var client = net.connect({ port: 8484 }, function () {
    //             console.log('Connection established!');
    //         });

    //         client.on('data', function (data) {
    //             if (degrees >= 179) {
    //                 degrees = 0;
    //             }
    //             else {
    //                 degrees += 5;
    //             }
    //             client.end();
    //         });

    //         client.on('end', function () {
    //             //console.log('Disconnected :(');
    //         });
    //         // if (degrees >= 179) {
    //         //     degrees = 0;
    //         // }
    //         // else {
    //         //     degrees += 5;
    //         // }
    //         needle.css("transform", "rotate(" + degrees.toString() + "deg)");
    //         console.log("hello");
    //     });

    //     // setInterval(() => {
    //     //     if (degrees >= 179)
    //     //     {
    //     //         degrees = 0;
    //     //     }
    //     //     else { 
    //     //         degrees += 5;
    //     //     }
    //     //     needle.css("transform", "rotate(" + degrees.toString() + "deg)");            
    //     // }, 500);
    // });