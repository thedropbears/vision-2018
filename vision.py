import math

import cv2
import numpy as np


def main():
    import cscore
    from networktables import NetworkTables
    from time import monotonic

    cs = cscore.CameraServer.getInstance()
    camera = cs.startAutomaticCapture()  # TODO: specify path if multiple cameras
    camera.setVideoMode(cscore.VideoMode.PixelFormat.kYUYV, 320, 240, 50)
    sink = cs.getVideo(camera=camera)

    nt = NetworkTables.getTable('/vision')
    entry = nt.getEntry('info')

    # Allocating memory is expensive. Preallocate an array for the camera image.
    frame = np.zeros(shape=(240, 320, 3), dtype=np.uint8)

    while True:
        time, frame = sink.grabFrame(frame)
        if time == 0:
            # TODO: handle error
            pass
        else:
            start_time = monotonic()
            info = process(frame)
            info.append(monotonic() - start_time)

            entry.setNumberArray(info)
            NetworkTables.flush()


def process(frame, lower=(15, 100, 100), upper=(35, 255, 255),
            min_radius_prop=0.0625, min_area_prop=0.0625,
            fov=75, focal_length=208.5):

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # construct a mask for the colour "yellow", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, lower, upper)
    cv2.erode(mask, None, mask, iterations=2)
    cv2.dilate(mask, None, mask, iterations=2)

    # find resolution of mask/image
    height, width = mask.shape

    min_radius = height * min_radius_prop
    min_area = width * min_area_prop

    # find contours in the mask and initialize the current
    # x center of the cube

    contours = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)[-2]

    output = []
    # only proceed if at least one contour was founda
    if contours:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        contours.sort(key=cv2.contourArea, reverse=True)

        for contour in contours:
            contour_area = cv2.contourArea(contour)

            ((x, y), radius) = cv2.minEnclosingCircle(contour)
            M = cv2.moments(contour)

            # only proceed if the radius meets a minimum size
            if contour_area > min_area and radius > min_radius:
                x = M["m10"] / M["m00"]

                distance = x - width / 2
                # convert x-axis location to -1 to 1
                position = -distance / (width / 2)
                angle = math.atan(-distance / focal_length)

                output.extend([angle, position, contour_area])

    return output
