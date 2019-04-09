#include "modules/scenario/point_cloud_provider/point_cloud_provider_component_gflags.h"

DEFINE_string(dataset_root_folder, "/apollo/dataset/", "Dataset root folder.");
DEFINE_string(dataset_point_clouds_folder_name, "point_clouds/", "The point clouds' folder name.");
DEFINE_string(dataset_point_clouds_list_file_name, "list.txt", "A text file containing all the point clouds' names.");
DEFINE_bool(load_all, true, "Preload all the point clouds in memory.");
//DEFINE_string(camera_frame_id);
DEFINE_string(writer_channel, "/apollo/sensor/lidar128/compensator/PointCloud2", "Cyber writer channel name.");
DEFINE_bool(continuous_mode, false, "If true, at the end of the scenario it will restart from the beginning.");
DEFINE_string(velodyne_id, "velodyne64", "Velodyne ID.");