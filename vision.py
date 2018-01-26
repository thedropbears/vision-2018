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
min_radius = frame_height * 0.125
fov = 75
focal_length = 208.5
fps = 50


def loop():
    cs = cscore.CameraServer.getInstance()
    camera = cs.startAutomaticCapture()  # TODO: specify path if multiple cameras
    camera.setVideoMode(cscore.VideoMode.PixelFormat.kYUYV, 320, 240, 60)
    sink = cs.getVideo(camera=camera)

    NetworkTables.initialize(server="roborio-4774-frc.local")
    nt = NetworkTables.getTable('/vision')
    entry = nt.getEntry('info')
    
    while True:
        frame = np.zeros(shape=(frame_height, frame_width, 3), dtype=np.uint8)
        info = process(sink.grabFrame(frame)[1])
        info = np.array(info).flatten()
        entry.setNumberArray(info)
        NetworkTables.flush()


def process(frame):
    start_time = time.time()

#     blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    bgr = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)


    # construct a mask for the colour "yellow", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, yellowLower, yellowUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None
    output = None
    angle = None
    
    output = []
    # only proceed if at least one contour was found
    if contours:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        contours.sort(key=cv2.contourArea, reverse=True)

        for contour in contours:
            # contour = max(contours, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(contour)
            M = cv2.moments(contour)

        # only proceed if the radius meets a minimum size
            if cv2.contourArea(contour) > (radius * 0.7)**2 and radius > min_radius:
                width, height = center = (
                    int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                mask_height, mask_width = mask.shape  # find resolution of mask

                distance = width - mask_width / 2
                # convert x-axis location to -1 to 1
                #position = -distance / (mask_width / 2)
                angle = math.atan(-distance / focal_length)

                output.extend([angle, position, cv2.contourArea(contour)])

    end_time = time.time() - start_time
    output.append(end_time)

    return output


if __name__ == '__main__':
    loop()
