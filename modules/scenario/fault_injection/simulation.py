from scenario import Scenario
from filter import *
import time
from cyber_py import cyber
from modules.drivers.proto.sensor_image_pb2 import Image
from modules.drivers.proto.pointcloud_pb2 import PointCloud, PointXYZIT
from modules.perception.proto.perception_obstacle_pb2 import PerceptionObstacles, PerceptionObstacle, BBox2D
import os
import os.path
import threading

OFFSET_X = 338
OFFSET_Y = 312

class Simulation(object):
    def __init__(self, scenario, filter):
        cyber.init("fault_injector")
        self.__fault_injector_node = cyber.Node("fault_injector")
        self.__perception_obstacles_reader = self.__fault_injector_node.create_reader("/apollo/perception/obstacles", PerceptionObstacles, self.listener_callback)
        self.__image_writer = self.__fault_injector_node.create_writer("/apollo/sensor/camera/front_6mm/image", Image)
        #self.__cloud_points_writer = self.__fault_injector_node.create_writer("/apollo/sensor/lidar128/compensator/PointCloud2", PointCloud)
        self.__scenario = scenario
        self.__scenario.prepare_point_cloud_provider()
        self.__filter = filter
        self.__oracle_run = False
        self.start_perception()
        threading.Thread(target=self.spin).start()
    
    def spin(self):
        self.__fault_injector_node.spin()
    
    def run(self):
        if len(os.listdir(self.__scenario.oracle_path)) == 0:
            self.__run_oracle()
        else:
            pass
        self.kill_perception()
        cyber.shutdown()
    
    def __run_oracle(self):
        self.__oracle_run = True
        os.system("cyber_launch start modules/scenario/launch/point_cloud.launch &")
        for i in range(len(self.__scenario)):
            start = time.time()
            image = self.__read_image(self.__scenario.images_paths[i])
            #cloud_points = self.__read_cloud_points(self.__scenario.cloud_points_paths[i])
            self.write_image(image)
            #self.write_cloud_points(cloud_points, i)
            
            #print((time.time() - start) * 1000)
            time_to_sleep = 0.2 - (time.time() - start)
            time.sleep(time_to_sleep)

    def __read_image(self, path):
        return cv2.imread(path, cv2.IMREAD_COLOR)
    
    def __read_cloud_points(self, path):
        return np.fromfile(path, dtype="float32").reshape(-1, 4)

    def start_perception(self):
        os.system("cyber_launch start /apollo/modules/perception/production/launch/perception_injection.launch &")
        time.sleep(30)
        print("Perception started.")

    def kill_perception(self):
        os.system("killall mainboard")
        time.sleep(5)
        print("Perception killed")
    
    def write_image(self, image):
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

        self.__image_writer.write(proto_image)
    
    def listener_callback(self, perception_obstacles):
        print(len(perception_obstacles.perception_obstacle))

if __name__ == "__main__":
    sim = Simulation(Scenario.get_scenarios()[0], None)
    sim.run()
