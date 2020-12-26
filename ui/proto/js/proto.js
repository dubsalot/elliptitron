var net = require('net');
var jQuery = require('jquery');
const { app, BrowserWindow } = require('electron')

function degToRad(degree) {
    var factor = Math.PI / 180;
    return degree * factor;
}

function getStats() {
    jQuery.get("http://raspberrypi:9001/state", function (data) {
        console.log(data);
        if(data && data.mph)
            jQuery("#SpeedMetricLabel").html(data.mph)
    });
}

// var electron = require('electron');
// var window = electron.remote.getCurrentWindow();
// window.setFullScreen(true);

function Buttons() { 
    document.querySelector('#btnrefresh').addEventListener('click', () => {
        var win = BrowserWindow.getFocusedWindow();
        console.log(win);
    })
}

function Meter(canvas) {

    var canvas = document.getElementById(canvas);
    var ctx = canvas.getContext('2d');
    ctx.strokeStyle = '#28d1fa';

    ctx.lineCap = 'round';
    ctx.shadowBlur = 15;
    ctx.shadowColor = '#28d1fa';

    // Background
    gradient = ctx.createRadialGradient(400, 400, 5, 400, 400, 300);
    gradient.addColorStop(0, '#09303a');
    gradient.addColorStop(1, '#000000');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, 800, 800);

    var to = 140 + ((350 - 140) * .75);
    var from = 140;

    if (to > 350) {
        to = 350;
    }

    if (from < 140) {
        from = 140;
    }

    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(400, 400, 360, degToRad(from), degToRad(400));
    ctx.stroke();

    //speed goes here
    // ctx.font = "100px Helvetica";
    // ctx.fillStyle = '#28d1fa';
    // ctx.fillText(val, 200, 220);

    //label goes here
    // ctx.font = "15px Helvetica";
    // ctx.fillStyle = '#28d1fa';
    // ctx.fillText(label, 75, 250);
    return this;
}