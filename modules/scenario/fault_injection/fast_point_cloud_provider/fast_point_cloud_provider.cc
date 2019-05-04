#include <iostream>
#include <memory>
#include <string>

#include "cyber/cyber.h"
#include "cyber/component/component.h"
#include "modules/drivers/proto/sensor_image.pb.h"
#include "modules/drivers/proto/pointcloud.pb.h"

using apollo::drivers::Image;
using apollo::drivers::PointCloud;
using apollo::drivers::PointXYZIT;

class FastPointCloudProvider : public apollo::cyber::Component<>
{
    public:
    bool Init()
    {
        trigger_reader = node_->CreateReader<Image>("/apollo/fault_injector", 
        [this](const std::shared_ptr<Image> &trigger)
        {
            const std::string point_cloud_file_path = trigger->header().frame_id();
            const int sequence_num = trigger->header().sequence_num();
            std::ifstream point_cloud_file(point_cloud_file_path);

            point_cloud_file.seekg(0, point_cloud_file.end);
            int bytes = (int)point_cloud_file.tellg();
            point_cloud_file.seekg(0, point_cloud_file.beg);

            float *buffer = new float[bytes / sizeof(float)];
            point_cloud_file.read((char *)buffer, bytes);

            std::shared_ptr<PointCloud> point_cloud = std::make_shared<PointCloud>();

            for(int i = 0; i < bytes / 4; i += 4)
            {
                PointXYZIT *point_xyzit = point_cloud->add_point();
                point_xyzit->set_x(buffer[i]);
                point_xyzit->set_y(buffer[i + 1]);
                point_xyzit->set_z(buffer[i + 2]);
                point_xyzit->set_intensity(uint(buffer[i + 3]));
                point_xyzit->set_timestamp(ulong(apollo::cyber::Time::Now().ToNanosecond()));
            }

            point_cloud->mutable_header()->set_frame_id("velodyne128");
            point_cloud->mutable_header()->set_sequence_num(uint64_t(sequence_num));
            point_cloud->set_height(1);
            point_cloud->set_width(point_cloud->point_size());

            auto timestamp = point_cloud->point(point_cloud->point_size() - 1).timestamp();

            point_cloud->set_measurement_time(double(timestamp) / 1E9);
            point_cloud->mutable_header()->set_lidar_timestamp(timestamp);
            point_cloud->set_is_dense(true);

            point_cloud_writer->Write(point_cloud);

            delete[] buffer;
            point_cloud_file.close();
        });

        point_cloud_writer = node_->CreateWriter<PointCloud>("/apollo/sensor/lidar128/compensator/PointCloud2");

        return true;
    }

    bool Proc()
    {
        return true;
    }

    private:
    std::shared_ptr<apollo::cyber::Reader<Image>> trigger_reader = nullptr;
    std::shared_ptr<apollo::cyber::Writer<PointCloud>> point_cloud_writer = nullptr;
};

CYBER_REGISTER_COMPONENT(FastPointCloudProvider);