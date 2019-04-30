import numpy as np
from cyber_py import cyber
from modules.drivers.proto.sensor_image_pb2 import Image
import cv2
import time
import os

DATASET_FOLDER = "/apollo/dataset/"
IMAGES_FOLDER = "images/"
OFFSET_X = 338
OFFSET_Y = 312

def blur(image, kernel_size, mode):
    if mode == "average":
        return cv2.blur(image, kernel_size)
    elif mode == "gaussian":
        return cv2.GaussianBlur(image, kernel_size, 0)
    elif mode == "median":
        return cv2.medianBlur(image, kernel_size)
    else:
        return image

def adjust_contrast_brightness(image, alpha, beta):
    return np.clip(alpha * image.astype("float") + beta, 0, 255).astype("uint8")

def launch_perception():
    os.system("cyber_launch start /apollo/modules/perception/production/launch/perception_camera.launch")
    time.sleep(30)

def clear_debug_output_folder():
    os.system("rm -rf /apollo/debug_output/*")
    time.sleep(0.1)

def clear_log_folder():
    os.system("rm -rf /apollo/data/log/*")
    time.sleep(0.1)

def read_image_list():
    with open(DATASET_FOLDER + IMAGES_FOLDER + "list.txt") as image_list_file:
        return [image_file.strip() for image_file in image_list_file.readlines()]

def main():
    cyber.init("fault_injector")
    fault_injector_node = cyber.Node("fault_injector")
    writer = fault_injector_node.create_writer("/apollo/sensor/camera/front_6mm/image", Image)

    for image_file in read_image_list():
        image = cv2.imread(DATASET_FOLDER + IMAGES_FOLDER + image_file)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        #image = cv2.resize(image, (1920, 1080), 1.0, 1.0, cv2.INTER_CUBIC)

        image = adjust_contrast_brightness(image, 2.0, 50.0)

        image_frame = np.zeros((1080, 1920, 3), dtype="uint8")
        image_frame[OFFSET_Y : OFFSET_Y + image.shape[0], OFFSET_X : OFFSET_X + image.shape[1]] = image

        proto_image = Image()
        proto_image.header.frame_id = "front_6mm"
        proto_image.header.timestamp_sec = cyber.time.time()
        proto_image.measurement_time = cyber.time.time()
        proto_image.width = image_frame.shape[1]
        proto_image.height = image_frame.shape[0]
        proto_image.encoding = "rgb8"
        proto_image.step = 3 * image_frame.shape[1]
        proto_image.data = image_frame.tobytes()

        writer.write(proto_image)

        time.sleep(0.2)
    cyber.shutdown()

if __name__ == "__main__":
    main()