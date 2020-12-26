import '../node_modules/material-icons/css/material-icons.css'
import './css/proto.css'
import React, { useState, ReactDOM, useEffect } from 'react';
import {AccessAlarm, Fullscreen} from '@material-ui/icons'
//var jQuery = require('jquery');



// var electron = require('electron');
// var window = electron.remote.getCurrentWindow();
// window.setFullScreen(true);

function Buttons() {

    document.querySelector('#btnrefresh').addEventListener('click', () => {
        // var win = BrowserWindow.getFocusedWindow();
        // console.log(win);
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
    var gradient = ctx.createRadialGradient(400, 400, 5, 400, 400, 300);
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

function Proto() {
    const [stats, setStats] = useState({"TotalElapsedTime": 50.7156662940979, "distance": 0.003472222222222222, "calories": 8.191355562210083, "mph": 0.31, "totalCountOnState": 10.0, "caloriesPerMinute": 0.0});
    const getStats = () => {
        fetch("http://192.168.1.85:9001/state")
          .then(res => res.json())
          .then(
            (result) => {
              console.log(result);
              setStats(result)          
            },
            // Note: it's important to handle errors here
            // instead of a catch() block so that we don't swallow
            // exceptions from actual bugs in components.
            (error) => {
              console.error(error, "error");
            }
          )
    };

    useEffect(() => {
        const interval = setInterval(() => {
            getStats();
          }, 1000);
          return () => clearInterval(interval);

        Meter("calsPerMinute");
        Meter("speed");
      }, []);

    return (
        <div className="flex-container">
            <div className="menu flex-item">
                <AccessAlarm />
                <Fullscreen />
            </div>
            <div className="flex-item">
                <div className="extlabel">{stats.caloriesPerMinute}</div>
                <div className="inddescrip">Calories/Minute</div>
                <canvas id="calsPerMinute" width="800" height="800" className="gauge"></canvas>
            </div>
            <div className="flex-item">
                <div id="SpeedMetricLabel" className="extlabel">{stats.mph}</div>
                <div className="inddescrip">MPH</div>
                <canvas id="speed" width="800" height="800" className="gauge"></canvas>
            </div>
        </div>
    );  
}

function degToRad(degree) {
    var factor = Math.PI / 180;
    return degree * factor;
}



function getd() {

  }

export default Proto;
