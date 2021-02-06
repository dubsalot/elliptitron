# elliptitron

Repository is a personal learning project for me. I have a bowflex [bxe216 elliptical machine](https://www.ellipticalreviews.com/bowflex/bxe216/) and I am not fond of it's dashboard or the way it syncs data with the app on my phone.

## I have three goals for this project other than learning: 
- sync data real-time as I workout to cloud storage: Google Drive, One Drive, or maybe an azure hosted webservice.
- imrpove the physical dashboard witb a nice UI on a large touch screen
- pause workout as soon as I stop for a break, and resume as soon as I start back


## to hack the hardware or not
I considered tying into the circuitry of the ellipitcal and control it with my own hardware. This style of machine uses a stepper motor to raise and lower a large magnet near a metal flywheel. i.e. If the user increases the resistance during the workout, a magnet is moved closer to the flywheel.

I could control that stepper motor with a raspberry pi. I could also use the pi to measure wheel speed I assume "incline" is handled a similar way, but I have not dug into it yet.

I chose to not wire into the machine and instead use sensors to read current state and display on the new UI. There are a couple of benefits here:
- Leave the machine in tact in case I need a warranty repair or in case I sell it.
- I likely can resuse what I build on a new elliptical 
