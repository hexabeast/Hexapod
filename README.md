WARNING : If you want to reproduce it, the guide is not 100% complete, you'll need to figure out how to achieve some parts of the creation on your own.

Things needed to build the robot:

- A 3D Printer
- 2 LEGO Technic Steel Ball Caster
- 21 servos (standard size, like the MG996R on Amazon)
- A Raspberry Pi 2
- A Breadboard and wires
- 18650 battery cases and li-ion batteries (2x3.7V)
- Any slim portable smartphone battery (for the Pi)

To build the robot, refer to the schematic picture "robot.png" in this repository. 
You'll need additional materials (tape, glue...) to assemble the robot.

The slim portable smartphone battery should supply power directly to the Pi, and the li-ion batteries are for the 21 servos. 
Use the breadboard to do that and add 2 interruptors (one for the Pi, one for the servos).

Each servo needs to be connected to a GPIO pin on the raspberry.
For each leg clockwise, starting from the back-left leg, and starting from the motor at the extremity of the legs, here is are the GPIO numbers on which the servos should be connected:

4
17
27

22
5
11

13
19
26

18
23
24

25
8
12

16
20
21

wheel servos:
7
2

camera servo:
15

You also need to install pi-blaster ( https://github.com/sarfata/pi-blaster ), flask for Python 3, and ffmpeg on the Raspberry Pi, and put the content of the "code" folder in your home directory. 
Configure the Pi to run "sudo python3 script.py" on boot.
Configure the Pi to connect to your wifi network, or generate its own network.
Then, connect to your_pi_local_ip_adress:8000 on any browser on any device connected to the same network as the Pi, and you should be able ton control the robot.
