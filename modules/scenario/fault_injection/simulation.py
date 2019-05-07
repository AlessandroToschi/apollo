from scenario import Scenario
from filter import *
import time
from cyber_py import cyber
from modules.drivers.proto.sensor_image_pb2 import Image
from modules.drivers.proto.pointcloud_pb2 import PointCloud, PointXYZIT
from modules.perception.proto.perception_obstacle_pb2 import PerceptionObstacles, PerceptionObstacle, BBox2D
from google.protobuf.json_format import MessageToJson
import os
import os.path
import shutil
import threading
import sys

OFFSET_X = 338
OFFSET_Y = 312

class Simulation(object):
    def __init__(self, scenario, filter, node):
        self.clear_debug_output_folder()
        self.clear_log_folder()
        self.__fault_injector_node = node
        self.__perception_obstacles_reader = self.__fault_injector_node.create_reader("/apollo/perception/obstacles", PerceptionObstacles, self.listener_callback)
        self.__image_writer = self.__fault_injector_node.create_writer("/apollo/sensor/camera/front_6mm/image", Image)
        self.__point_cloud_trigger = self.__fault_injector_node.create_writer("/apollo/fault_injector", Image)
        self.__scenario = scenario
        self.__scenario.prepare_point_cloud_provider()
        self.__filter = filter
        self.__oracle_run = False
        self.__prepare_simulation_folder()
        self.start_perception()
        os.system("cyber_launch start modules/scenario/fault_injection/fast_point_cloud_provider/fast_point_cloud_provider.launch &")
    
    def run(self):
        #if len(os.listdir(self.__scenario.oracle_path)) == 0:
        #    self.__run_oracle()
        for i in range(len(self.__scenario)):
            start = time.time()
            
            
            image = self.__read_image(self.__scenario.images_paths[i])
            self.write_image(self.__filter.apply(image), i)

            self.trigger_point_cloud(self.__scenario.cloud_points_paths[i], i)

            time_to_sleep = 0.3 - (time.time() - start)
            if time_to_sleep < 0:
                continue
            else:
                time.sleep(time_to_sleep)
        debug_files = os.listdir("/apollo/debug_output/")
        detection_files = [debug_file for debug_file in debug_files if "seg" not in debug_file]
        for detection_file in detection_files:
            shutil.copy2("/apollo/debug_output/" + detection_file, self.__simulation_folder)
        self.kill_perception()
        
    def __del__(self):
        self.kill_perception()
    
    def __run_oracle(self):
        self.__oracle_run = True
        #os.system("cyber_launch start modules/scenario/launch/point_cloud.launch &")
        for i in range(len(self.__scenario)):
            start = time.time()
            
            time.sleep(0.01)
            image = self.__read_image(self.__scenario.images_paths[i])
            self.write_image(image, i)
            self.trigger_point_cloud(self.__scenario.cloud_points_paths[i], i)
            
            time_to_sleep = 0.3
            if time_to_sleep < 0:
                continue
            else:
                time.sleep(time_to_sleep)
        debug_files = os.listdir("/apollo/debug_output/")
        detection_files = [debug_file for debug_file in debug_files if "seg" not in debug_file]
        for detection_file in detection_files:
            shutil.copy2("/apollo/debug_output/" + detection_file, self.__scenario.oracle_path)
    
    def clear_debug_output_folder(self):
        os.system("rm -rf /apollo/debug_output/*")
        time.sleep(0.1)

    def clear_log_folder(self):
        os.system("rm -rf /apollo/data/log/*")
        time.sleep(0.1)

    def __read_image(self, path):
        image = cv2.imread(path, cv2.IMREAD_COLOR)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image
    
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
    
    def write_image(self, image, index):
        image_frame = np.zeros((1080, 1920, 3), dtype="uint8")
        image_frame[OFFSET_Y : OFFSET_Y + image.shape[0], OFFSET_X : OFFSET_X + image.shape[1]] = image

        proto_image = Image()
        proto_image.header.sequence_num = index
        proto_image.header.frame_id = "front_6mm"
        proto_image.header.timestamp_sec = cyber.time.time()
        proto_image.measurement_time = cyber.time.time()
        proto_image.width = image_frame.shape[1]
        proto_image.height = image_frame.shape[0]
        proto_image.encoding = "rgb8"
        proto_image.step = 3 * image_frame.shape[1]
        proto_image.data = image_frame.tobytes()
        proto_image.header.camera_timestamp = int(cyber.time.time())

        self.__image_writer.write(proto_image)

    def trigger_point_cloud(self, path, index):
        proto_image = Image()
        proto_image.header.sequence_num = index
        proto_image.header.frame_id = path

        self.__point_cloud_trigger.write(proto_image)
    
    def __prepare_simulation_folder(self):
        self.__simulation_folder = self.__scenario.simulations_path + "/{}/".format(self.__filter)
        if not os.path.exists(self.__simulation_folder):
            os.mkdir(self.__simulation_folder)
    
    def listener_callback(self, perception_obstacles):
        #with open(self.__simulation_folder + "/fusion_{}.txt".format(perception_obstacles.header.sequence_num), "w") as log_txt:
        #with open(self.__scenario.oracle_path + "/fusion_{}.txt".format(perception_obstacles.header.sequence_num), "w") as log_txt:
        with open(self.__simulation_folder + "/fusion_{}.txt".format(perception_obstacles.header.sequence_num), "w") as log_txt:
            log_txt.write(MessageToJson(perception_obstacles))

if __name__ == "__main__":
    scenario_path = sys.argv[1]
    index = sys.argv[2]
    filter_name = sys.argv[3]
    print(scenario_path, index, filter_name)
    scenario = Scenario(scenario_path)
    filter = Filter.get_filter(filter_name)
    print(filter)
    cyber.init("fault_injector_scenario_{}".format(index))
    time.sleep(1)
    cyber_node = cyber.Node("fault_injector_node_{}".format(index))
    #scenario = Scenario(scenario_path)
    simulation = Simulation(scenario, filter, cyber_node)
    simulation.run()
    time.sleep(1)
    cyber.shutdown()
    time.sleep(1)

    #i = 0
    #
    #for scenario in Scenario.get_scenarios():
    #    cyber.init("ciao_{}".format(i))
    #    time.sleep(10)
    #    fault_injector_node = cyber.Node("fault_injector_{}".format(i))
    #    print(i)
    #    print(scenario.oracle_path)
    #    sim = Simulation(scenario, None, fault_injector_node)      
    #    sim.run()
    #    i += 1
    #    del fault_injector_node
    #    del sim
    #    cyber.shutdown()
    #    time.sleep(10)