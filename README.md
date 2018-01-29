# vision-2018
The Drop Bears' vision code for _FIRST_ Power Up (2018)

## RPi3 setup
Our Raspberry Pi 3 is currently running Debian buster for ARMv8, as this
provides a precompiled OpenCV.

We also tried Arch Linux ARM and Fedora 27 for ARMv7, but both resulted in
compile errors in wpiutil.  We're still investigating these, and I have an open
issue for this.

If you have a prebuilt wheel of robotpy-cscore, this should get you up and running:
```bash
sudo apt install python3-opencv python3-pip
pip install --user ./robotpy_cscore-*-linux_aarch64.whl
```

You will also need the `libopencv-dev` package on Debian to compile robotpy-cscore.
To compile robotpy-cscore on a RPi3, you'll need swap, as 1 GB of RAM won't be enough.
(Using swap on zram should be enough.  I had a maximum of 512 MB for my zram.)

Make sure the vision user is in the video group so it can access the webcam.

Install the `vision.service` file to `/etc/systemd/system` and enable and start
it with `systemctl enable --now vision`.

I have a robotpy-cscore wheel (for Debian buster for ARMv8).
Ping @auscompgeek on the RobotPy Gitter if you would like a copy.
