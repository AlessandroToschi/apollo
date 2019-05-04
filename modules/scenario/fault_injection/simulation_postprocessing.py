import os
import json
import math

def find_scenarios(path):
    return [path + folder + "/" for folder in os.listdir(path)]

def main():
    simulation_path = "/apollo/modules/scenario/fault_injection/city_2011_09_26_0014/"

    files = os.listdir(simulation_path)
    camera_files = [camera_file for camera_file in files if "fusion" not in camera_file]
    fusion_files = [fusion_file for fusion_file in files if "fusion" in fusion_file]

    print("Camera files: {}".format(len(camera_files)))
    print("Fusion files: {}".format(len(fusion_files)))

    camera_ids = [int(camera_file.strip().split(".")[0]) for camera_file in camera_files]
    fusion_ids = [int(fusion_file.strip().split(".")[0].split("_")[-1]) for fusion_file in fusion_files]
    common_ids = list(set(camera_ids).intersection(set(fusion_ids)))

    print("Common ids: {}".format(len(common_ids)))

    velodyne_obstacles = []
    camera_obstacles = []
    new_camera_obstacles = []
    new_velodyne_obstacles = []

    for i in common_ids:
        with open(simulation_path + "fusion_{}.txt".format(i), "r+") as fusion_file:
            fusion_json = json.loads(fusion_file.read())
            velodyne_obstacle = 0
            camera_obstacle = 0
            new_camera_obstacle = 0
            new_velodyne_obstacle = 0
            if "perceptionObstacle" in fusion_json:
                obstacles = fusion_json["perceptionObstacle"]
                for obstacle in obstacles:
                    if obstacle["measurements"][0]["sensorId"] == "front_6mm":
                        if obstacle["trackingTime"] == 0.0:
                            new_camera_obstacle += 1
                        camera_obstacle += 1
                    elif obstacle["measurements"][0]["sensorId"] == "velodyne128":
                        if obstacle["trackingTime"] == 0.0:
                            new_velodyne_obstacle += 1
                        velodyne_obstacle += 1
                    else:
                        print("Unrecognized obstacle")
                    if "pointCloud" in obstacle:
                        obstacle["pointCloud"] = []
                #fusion_file.seek(0)
                #fusion_file.truncate()
                #fusion_file.write(json.dumps(fusion_json, indent=2, separators=(",", ":")))
            velodyne_obstacles.append(velodyne_obstacle)
            camera_obstacles.append(camera_obstacle)
            new_camera_obstacles.append(new_camera_obstacle)
            new_velodyne_obstacles.append(new_velodyne_obstacle)
    print("Velodyne obstacles: {}".format(sum(velodyne_obstacles)))
    print("Camera obstacles: {}".format(sum(camera_obstacles)))
    unique_obstacles = sum(new_camera_obstacles) + sum(new_velodyne_obstacles)
    print("Unique obstacles: {}".format(unique_obstacles))
    print("Unique camera obstacles: {}".format(sum(new_camera_obstacles) / unique_obstacles))
    print("Unique velodyne obstacles: {}".format(sum(new_velodyne_obstacles) / unique_obstacles))

def remove_outliers(scenario_path, scenario_name):
    files = os.listdir(scenario_path)
    camera_files = [camera_file for camera_file in files if "fusion" not in camera_file]
    fusion_files = [fusion_file for fusion_file in files if "fusion" in fusion_file]

    #print("Scenario name: {}".format(scenario_name))
    print("Camera files: {}".format(len(camera_files)))
    print("Fusion files: {}".format(len(fusion_files)))

    camera_ids = [int(camera_file.strip().split(".")[0]) for camera_file in camera_files]
    fusion_ids = [int(fusion_file.strip().split(".")[0].split("_")[-1]) for fusion_file in fusion_files]
    common_ids = list(set(camera_ids).intersection(set(fusion_ids)))

    print("Common ids: {}".format(len(common_ids)))

    camera_ids_to_remove = set(camera_ids).difference(set(common_ids))
    fusion_ids_to_remove = set(fusion_ids).difference(set(common_ids))

    for camera_id in camera_ids_to_remove:
        os.remove(scenario_path + "{}.txt".format(camera_id))
    
    for fusion_id in fusion_ids_to_remove:
        os.remove(scenario_path + "fusion_{}.txt".format(fusion_id)) 

def remove_point_cloud(scenario_path, scenario_name):
    fusion_files = [fusion_file for fusion_file in os.listdir(scenario_path) if "fusion" in fusion_file]
    for fusion_file in fusion_files:
        with open(scenario_path + fusion_file, "r+") as fusion:
            fusion_json = json.loads(fusion.read())
            if "perceptionObstacle" in fusion_json:
                obstacles = fusion_json["perceptionObstacle"]
                for obstacle in obstacles:
                    if "pointCloud" in obstacle:
                        obstacle["pointCloud"] = []
            fusion.seek(0)
            fusion.truncate()
            fusion.write(json.dumps(fusion_json, indent=2, separators=(",", ":")))
    print("Deleted cloud point for {}".format(scenario_name))

def count_obstacles(scenario_path):
    fusion_files = [fusion_file for fusion_file in os.listdir(scenario_path) if "fusion" in fusion_file]
    camera_obstacles = 0
    velodyne_obstacles = 0
    unknown_obstacles = 0
    print("Frames: {}".format(len(fusion_files)))
    for fusion_file in fusion_files:
        with open(scenario_path + fusion_file, "r+") as fusion:
            fusion_json = json.loads(fusion.read())
            if "perceptionObstacle" in fusion_json:
                obstacles = fusion_json["perceptionObstacle"]
                for obstacle in obstacles:
                    if obstacle["measurements"][0]["sensorId"] == "front_6mm":
                        camera_obstacles += 1
                    else:
                        velodyne_obstacles += 1
                    if obstacle["type"] == "UNKNOWN":
                        unknown_obstacles += 1
    print("Total obstacles: {}".format(camera_obstacles + velodyne_obstacles))
    print("Camera obstacles: {}, {}".format(camera_obstacles, round(camera_obstacles / (camera_obstacles + velodyne_obstacles), 3)))
    print("Velodyne obstacles: {}, {}".format(velodyne_obstacles, round(velodyne_obstacles / (camera_obstacles + velodyne_obstacles), 3)))
    print("Unknown obstacles: {}, {}".format(unknown_obstacles, round(unknown_obstacles / (camera_obstacles + velodyne_obstacles), 3)))   

if __name__ == "__main__":
    simulation_path = "/apollo/modules/scenario/fault_injection/simulations/road_2011_09_29_0004/"
    for filter in os.listdir(simulation_path):
        remove_point_cloud(simulation_path + filter + "/", filter)
    #scenario_paths = find_scenarios("/apollo/modules/scenario/fault_injection/oracle/")
    #for scenario_path in scenario_paths:
    #    scenario_name = scenario_path.strip().split("/")[-2]
    #    print(scenario_name)
    #    #remove_outliers(scenario_path, scenario_name)
    #    #remove_point_cloud(scenario_path, scenario_name)
    #    count_obstacles(scenario_path)
    #    print()
