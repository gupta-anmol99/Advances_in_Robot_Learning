import pyrealsense2 as rs
import numpy as np
import cv2
import sys
sys.path.append('./yolov7/')
from detect_fast import Yolov7_detect_person

# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()

# Get device product line for setting a supporting resolution
pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)
device = pipeline_profile.get_device()
device_product_line = str(device.get_info(rs.camera_info.product_line))

found_rgb = False
for s in device.sensors:
    if s.get_info(rs.camera_info.name) == 'RGB Camera':
        found_rgb = True
        break
if not found_rgb:
    print("The demo requires Depth camera with Color sensor")
    exit(0)

config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

if device_product_line == 'L500':
    config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
else:
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start streaming
pipeline.start(config)
object_detector = Yolov7_detect_person()

def get_state():
    # Wait for a coherent pair of frames: depth and color
    output=0
    while output!=1:
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            continue
        else:
            output=1
    #print(depth_frame.get_distance(240, 240))

    # Convert images to numpy arrays
    depth_image = np.asanyarray(depth_frame.get_data())
    color_image = np.asanyarray(color_frame.get_data())
    from pdb import set_trace as bp
    #bp()

    # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
    depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

    depth_colormap_dim = depth_colormap.shape
    color_colormap_dim = color_image.shape

    name = './data/frame.jpg'
    cv2.imwrite(name, color_image)

    detection, bbs = object_detector.detect_person(name)
    pixels = []
    depth_pix = []
    for bb in bbs:
        print(bb)
        center_x = (bb[0] + bb[2])/2
        center_y = (bb[1] + bb[3])/2
        pixels.append((center_x, center_y))
        depth_pix.append(depth_frame.get_distance(center_x, center_y))
    
    detection_shape = detection.shape 

    print(pixels, depth_pix)
    angle1 = 0
    angle2 = 0
    #Also have to send the position of the gun (angle) wrt the camera
    return [pixels, depth_pix, angle1, angle2]

def take_random_action():
    angle1 = random.randint(-60, 60)
    angle2 = random.randint(-30, 30)

    return angle1, angle2
