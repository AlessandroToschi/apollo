import os

class Scenario(object):

    @staticmethod
    def get_scenarios():
        with open("/apollo/modules/scenario/fault_injection/scenarios.txt") as scenarios_path_file:
            return [Scenario(scenario_path) for scenario_path in scenarios_path_file.readlines()]

    def __init__(self, scenario_path):
        self.__scenario_path = scenario_path.strip()
        self.__name = self.__extract_name(self.__scenario_path)
        self.__images_paths = sorted(self.__find_images_paths(self.__scenario_path))
        self.__cloud_points_paths = sorted(self.__find_cloud_points_paths(self.__scenario_path))
        if len(self.__images_paths) != len(self.__cloud_points_paths):
            self.__ensure_frames_consistency(self.__scenario_path)
    
    def __extract_name(self, scenario_path):
        components = scenario_path.strip().split("/")
        return components[3] + "_" + components[4] + "_" + (components[5].strip().split("_"))[-2]
    
    def __find_images_paths(self, scenario_path):
        images_names = os.listdir(scenario_path + "/image_02/data/")
        return [scenario_path + "/image_02/data/" + image_name for image_name in images_names]
    
    def __find_cloud_points_paths(self, scenario_path):
        cloud_points_names = os.listdir(scenario_path + "/velodyne_points/data/")
        return [scenario_path + "/velodyne_points/data/" + cloud_points_name for cloud_points_name in cloud_points_names]
    
    def __ensure_frames_consistency(self, scenario_path):
        images_frame_id = set([int(image_path.split("/")[-1].split(".")[0]) for image_path in self.__images_paths])
        cloud_points_frame_id = set([int(cloud_points_path.split("/")[-1].split(".")[0]) for cloud_points_path in self.__cloud_points_paths])
        valid_frame_id = sorted(list(images_frame_id.intersection(cloud_points_frame_id)))
        self.__images_paths = [scenario_path + "/image_02/data/" + str(frame_id).rjust(10, '0') + ".png" for frame_id in valid_frame_id]
        self.__cloud_points_paths = [scenario_path + "/valodyne_points/data/" + str(frame_id).rjust(10, '0') + ".bin" for frame_id in valid_frame_id]
        
                

    name = property(lambda self: self.__name)
    images_paths = property(lambda self: self.__images_paths[:])
    cloud_points_paths = property(lambda self: self.__cloud_points_paths[:])

if __name__ == "__main__":
    for scenario in Scenario.get_scenarios():
        print(scenario.name)
    scenario_0 = Scenario.get_scenarios()[0]
    print(scenario_0.images_paths)
    print(scenario_0.cloud_points_paths)