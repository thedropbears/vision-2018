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
    camera.getProperty('vertical_flip').set(True)
    camera.getProperty('horizontal_flip').set(True)
    camera.getProperty('gain_automatic').set(False)
    sink = cs.getVideo(camera=camera)

    nt = NetworkTables.getTable('/vision')
    entry = nt.getEntry('info')

    # Allocating memory is expensive. Preallocate arrays for the camera images.
    frame = np.zeros(shape=(240, 320, 3), dtype=np.uint8)
    mask = np.zeros(shape=(240, 320), dtype=np.uint8)
    hsv = np.zeros(shape=(240, 320, 3), dtype=np.uint8)

    while True:
        time, frame = sink.grabFrame(frame)
        if time == 0:
            # TODO: handle error
            pass
        else:
            start_time = monotonic()
            info = process(frame, mask, hsv)
            info.append(monotonic() - start_time)

            entry.setNumberArray(info)
            NetworkTables.flush()


def process(frame, mask=None, hsv=None,
            lower=(15, 100, 100), upper=(35, 255, 255),
            min_radius_prop=0.0625, min_area_prop=0.0625,
            fov=75, focal_length=208.5):

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV, dst=hsv)

    # construct a mask for the colour "yellow", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, lower, upper, dst=mask)
    cv2.erode(mask, None, dst=mask)
    cv2.dilate(mask, None, dst=mask)

    # find resolution of mask/image
    height, width = mask.shape

    min_area = width * min_area_prop

    # find contours in the mask and initialize the current
    # x center of the cube

    contours = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)[1]

    output = []
    # only proceed if at least one contour was founda
    if contours:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        contours.sort(key=cv2.contourArea, reverse=True)

        for contour in contours:
            contour_area = cv2.contourArea(contour)

            # only proceed if the contours are big enough
            # since the contours are sorted, we can stop once we find one too small
            if contour_area <= min_area:
                break

            M = cv2.moments(contour)
            x, y = M["m10"] / M["m00"], M["m01"] / M["m00"]

            distance_x = x - width / 2
            distance_y = y - height / 2

            angle_x = math.atan2(-distance_x, focal_length)
            angle_y = math.atan2(-distance_y, focal_length)

            output.extend([angle_x, angle_y])

    return output
