#include "modules/image_provider/image_provider_component_gflags.h"

DEFINE_string(dataset_root_folder, "/apollo/dataset/", "Dataset root folder.");
DEFINE_string(dataset_image_folder_name, "data/", "The image's folder name.");
DEFINE_string(dataset_image_list_file_name, "lists.txt", "A text file containing all the images' name.");
DEFINE_string(camera_frame_id, "camera_front_6mm", "Camera ID");
DEFINE_string(writer_channel, "/apollo/sensor/camera/front_6mm/image", "Cyber writer channel.");
DEFINE_bool(continuous_mode, false, "If true, at the end of the scenario it will restart from the beginning.");