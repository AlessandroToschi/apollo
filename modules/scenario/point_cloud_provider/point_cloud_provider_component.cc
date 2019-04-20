#include "modules/scenario/point_cloud_provider/point_cloud_provider_component.h"

namespace apollo{
namespace scenario {
namespace point_cloud_provider{

bool PointCloudProviderComponent::Init()
{
    std::string point_clouds_list_content;

    if(!apollo::cyber::common::GetContent(FLAGS_dataset_root_folder + FLAGS_dataset_point_clouds_folder_name + FLAGS_dataset_point_clouds_list_file_name, &point_clouds_list_content))
    {
        AERROR << "Unable to open point clouds list file: " << FLAGS_dataset_root_folder + FLAGS_dataset_point_clouds_folder_name + FLAGS_dataset_point_clouds_list_file_name;
        return false;
    }

    std::string line;
    char delimiter = '\n';
    std::istringstream token_stream(point_clouds_list_content);

    while(std::getline(token_stream, line, delimiter))
    {
        point_clouds_list.push_back(line);
    }

    AINFO << "There are " << point_clouds_list.size() << " point clouds.";

    if(FLAGS_load_all)
    {
        for(std::string point_clouds_file_name : point_clouds_list)
        {
            std::ifstream point_clouds_file;
            point_clouds_file.open(FLAGS_dataset_root_folder + FLAGS_dataset_point_clouds_folder_name + point_clouds_file_name);

            if(!point_clouds_file.is_open())
            {
                AERROR << "Unable to open the point clouds file: " << point_clouds_file_name;
                return false;
            }

            point_clouds_file.seekg(0, point_clouds_file.end);
            int bytes = (int)point_clouds_file.tellg();
            point_clouds_file.seekg(0, point_clouds_file.beg);
            
            if(bytes % 16 != 0)
            {
                AERROR << "Unvalid file size: " << point_clouds_file_name;
                return false;
            }

            float *buffer = new float[bytes / sizeof(float)];

            point_clouds_file.read((char *)buffer, bytes);

            auto point_cloud = std::make_shared<PointCloud>();

            for(int i = 0; i < bytes / 16; i += 4)
            {
                PointXYZIT *point_xyzit = point_cloud->add_point();
                point_xyzit->set_x(buffer[i]);
                point_xyzit->set_y(buffer[i + 1]);
                point_xyzit->set_z(buffer[i + 2]);
                point_xyzit->set_intensity(uint(buffer[i + 3]));
                //point_xyzit->set_timestamp(ulong(apollo::cyber::Time::Now().ToSecond()));
            }

            point_clouds.push_back(point_cloud);

            delete[] buffer;

            point_clouds_file.close();
        }
    }

    point_clouds_index = 0;

    writer_ = node_->CreateWriter<PointCloud>(FLAGS_writer_channel);

    return true;
}

bool PointCloudProviderComponent::Proc()
{
    if(point_clouds_index >= point_clouds_list.size())
    {
        if(FLAGS_continuous_mode)
        {
            AINFO << "PointCloudProvider will restart the scenario.";
            point_clouds_index = 0;
        }
        else
        {
            AINFO << "PointCloudProvider will end the scenario.";
            apollo::cyber::SetState(apollo::cyber::State::STATE_SHUTTING_DOWN);
            return true;
        }
    }

    std::shared_ptr<PointCloud> point_cloud;

    if(FLAGS_load_all)
    {
        point_cloud = point_clouds[point_clouds_index];
    }
    else
    {
        std::ifstream point_clouds_file;
        point_clouds_file.open(FLAGS_dataset_root_folder + FLAGS_dataset_point_clouds_folder_name + point_clouds_list[point_clouds_index]);
        
        if(!point_clouds_file.is_open())
        {
            AERROR << "Unable to open the point clouds file: " << point_clouds_list[point_clouds_index];
            return false;
        }

        point_clouds_file.seekg(0, point_clouds_file.end);
        int bytes = (int)point_clouds_file.tellg();
        point_clouds_file.seekg(0, point_clouds_file.beg);
        
        if(bytes % 16 != 0)
        {
            AERROR << "Unvalid file size: " << point_clouds_list[point_clouds_index];
            return false;
        }

        float *buffer = new float[bytes / sizeof(float)];
        point_clouds_file.read((char *)buffer, bytes);
        
        point_cloud = std::make_shared<PointCloud>();

        for(int i = 0; i < bytes / 16; i += 4)
        {
            PointXYZIT *point_xyzit = point_cloud->add_point();
            point_xyzit->set_x(buffer[i]);
            point_xyzit->set_y(buffer[i + 1]);
            point_xyzit->set_z(buffer[i + 2]);
            point_xyzit->set_intensity(uint(buffer[i + 3]));
            point_xyzit->set_timestamp(ulong(apollo::cyber::Time::Now().ToNanosecond()));
        }
        //point_clouds.push_back(point_cloud);
        delete[] buffer;
        point_clouds_file.close();
    }
    
    for(int i = 0; i < point_cloud->point_size(); i++)
    {
        point_cloud->mutable_point(i)->set_timestamp(ulong(apollo::cyber::Time::Now().ToNanosecond()));
    }

    point_cloud->mutable_header()->set_frame_id(FLAGS_velodyne_id);
    point_cloud->mutable_header()->set_sequence_num(uint64_t(point_clouds_index));
    point_cloud->set_height(1);
    point_cloud->set_width(point_cloud->point_size());

    auto timestamp = point_cloud->point(point_cloud->point_size() - 1).timestamp();

    point_cloud->set_measurement_time(double(timestamp) / 1E9);
    point_cloud->mutable_header()->set_lidar_timestamp(timestamp);
    point_cloud->set_is_dense(true);


    writer_->Write(point_cloud);

    point_clouds_index++;

    return true;
}

}
}
}