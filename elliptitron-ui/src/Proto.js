import '../node_modules/material-icons/css/material-icons.css'
import './proto.css'
import React, { useState, ReactDOM, useEffect } from 'react';
import {AccessAlarm, Fullscreen, RoundedCorner} from '@material-ui/icons'


function Buttons() {

    document.querySelector('#btnrefresh').addEventListener('click', () => {
        // var win = BrowserWindow.getFocusedWindow();
        // console.log(win);
    })
}



function Meter(canvas) {
    var hlc = getComputedStyle(document.documentElement).getPropertyValue('--highlight-color');

    var canvas = document.getElementById(canvas);
    var ctx = canvas.getContext('2d');
    ctx.strokeStyle = hlc;

    ctx.lineCap = 'round';
    ctx.shadowBlur = 15;
    ctx.shadowColor = hlc;

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
    return this;
}

function Proto() {
    var def = {
        "paused": 0.0,
        "currentTime": 0.0,               
        "totalElapsedTimeInSeconds": 0.0, 
        "totalElapsedTimeInHours": 0.0,   
        "elapsedSinceLastOnStateInSeconds": 0.0,   
        "stepsPerMinute": 0.0,            
        "distanceInFeet": 0.0,            
        "distanceInMiles": 0.0,           
        "speedInMph": 0.0,                
        "calories": 0.0,                  
        "caloriesPerMinute": 0.00,
        "containerClass": "flex-container"
    };    
    const [stats, setStats] = useState(def);
    const getStats = () => {
        fetch("http://192.168.1.85:9001/state")
          .then(res => res.json())
          .then(
            (result) => {
              console.log(result);
              result.containerClass="flex-container";
              document.documentElement.style.setProperty('--highlight-color', '#28d1fa');              
              document.documentElement.style.setProperty('--background-color', '#041a1e'); 
              if(result.paused == true)
              {
                document.documentElement.style.setProperty('--highlight-color', '#cedd6d');              
                document.documentElement.style.setProperty('--background-color', '#1e1e16'); 
                result.containerClass += " paused";
              }
              Meter("calsPerMinute");
              Meter("speed");                   
              setStats(result);

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
      }, []);

    return (
       
        <div className={stats.containerClass}>
            {/* <div className="menu flex-item">
                <AccessAlarm />
                <Fullscreen />
            </div> */}
            <div className="flex-item">
                <div className="extlabel">{stats.calories}</div>
                <div className="inddescrip">Calories</div>
                <canvas id="calsPerMinute" width="800" height="800" className="gauge"></canvas>
                <span>calories/minute: {stats.caloriesPerMinute}</span>
            </div>
            <div className="flex-item">
                <div id="SpeedMetricLabel" className="extlabel">{stats.speedInMph}</div>
                <div className="inddescrip">MPH</div>
                <canvas id="speed" width="800" height="800" className="gauge"></canvas>
                <span>Paused: {(stats.paused == true).toString()}</span>
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
