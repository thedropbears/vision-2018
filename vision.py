import cscore
import numpy as np
import cv2
from networktables import NetworkTables
import time
import math

yellowLower = (15, 100, 100)
yellowUpper = (35, 255, 255)

frame_width = 320
frame_height = 240
min_radius = frame_height * 0.0625
min_area = frame_width * 0.0625
fov = 75
focal_length = 208.5
fps = 50


def loop():
    cs = cscore.CameraServer.getInstance()
    camera = cs.startAutomaticCapture()  # TODO: specify path if multiple cameras
    camera.setVideoMode(cscore.VideoMode.PixelFormat.kYUYV, 320, 240, 60)
    sink = cs.getVideo(camera=camera)

    nt = NetworkTables.getTable('/vision')
    entry = nt.getEntry('info')
    frame = np.zeros(shape=(frame_height, frame_width, 3), dtype=np.uint8)

    while True:
        info = process(sink.grabFrame(frame)[1])
        info = np.array(info).flatten()
        entry.setNumberArray(info)
        NetworkTables.flush()


def process(frame):
    start_time = time.monotonic()

#     blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)


    # construct a mask for the colour "yellow", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, yellowLower, yellowUpper)
    cv2.erode(mask, None, mask, iterations=2)
    cv2.dilate(mask, None, mask, iterations=2)

    # find resolution of mask
    mask_height, mask_width = mask.shape

    min_radius = mask_height * 0.0625
    min_area = mask_width * 0.0625

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
        contours.sort(key=cv2.contourArea, reverse=True)]

        

        for contour in contours:
            # contour = max(contours, key=cv2.contourArea)
            
            contour_area = cv2.contourArea(contour)

            ((x, y), radius) = cv2.minEnclosingCircle(contour)
            M = cv2.moments(contour)

        # only proceed if the radius meets a minimum size
            if contour_area > min_area  and radius > min_radius:

                x = int(M["m10"] / M["m00"])

                distance = x - mask_width / 2
                # convert x-axis location to -1 to 1
                #position = -distance / (mask_width / 2)
                angle = math.atan(-distance / focal_length)

                output.extend([angle, position, contour_area])

    end_time = time.monotonic() - start_time
    output.append(end_time)

    return output


if __name__ == '__main__':
    loop()
