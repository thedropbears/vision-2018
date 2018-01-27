# vision-2018
The Drop Bears' vision code for FIRST Power Up (2018)



Guide to setting the code up on a Pi


DISCLAIMER: This program is intended for the Raspberry Pi 3, running on raspbian, and in this guide we assume that this is what you're using.


Step 1: Install OpenCV

To install OpenCV, we reccomend using this guide for the Raspi 3:

https://www.pyimagesearch.com/2016/04/18/install-guide-raspberry-pi-3-raspbian-jessie-opencv-3/


Step 2: Install the RobotPy Library

Run this command:

pip install pyfrc


Step 3: Get the vision.py code from the dropbears vision-2018 github page

git clone git@github.com:https://github.com/thedropbears/vision-2018

or copy/paste


Step 4: Make a .sh file which runs the python code.

If you are using a venv instead of running the code by running the command 'python', use the directory of the python executable in your venv.

Use the text editor of your choice(I used nano) to create a .sh file. This file look something like this:
#!/bin/bash
/path/to/python /path/to/vision.py

in our case, we used a virtual environment, so our python path was /home/pi/.virtualenvs/cv/bin/python3


Step 5: Run on Bootup

For this step, we reccommend the following guide:

https://learn.adafruit.com/running-programs-automatically-on-your-tiny-computer/systemd-writing-and-enabling-a-service

In this guide follow the steps, but replace the service name and Alias with cameraserver.service, and replace the file to be run with your .sh file. 