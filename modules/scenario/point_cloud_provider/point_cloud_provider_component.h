#include <iostream>
#include <memory>
#include <string>
//#include <opencv2/opencv.hpp>
//#include <opencv2/imgproc/imgproc.hpp>
//#include <opencv2/core/core.hpp>
//#include <opencv2/core/types_c.h>
#include "cyber/cyber.h"
#include "cyber/class_loader/class_loader.h"
#include "cyber/component/component.h"
#include "cyber/component/timer_component.h"
//#include "modules/drivers/camera/usb_cam.h"
//#include "modules/drivers/camera/proto/config.pb.h"
//#include "modules/drivers/proto/sensor_image.pb.h"
#include "point_cloud_provider_component_gflags.h"
#include "modules/drivers/proto/pointcloud.pb.h"

using apollo::cyber::Component;
using apollo::cyber::ComponentBase;
using apollo::cyber::TimerComponent;
using apollo::cyber::Writer;
using apollo::drivers::PointCloud;
using apollo::drivers::PointXYZIT;

//using apollo::drivers::camera::CameraImagePtr;
//using apollo::drivers::camera::CameraImage;
//using apollo::drivers::Image;

namespace apollo {
namespace scenario{
namespace point_cloud_provider {

class PointCloudProviderComponent : public TimerComponent
{
    public:
    bool Init() override;
    bool Proc() override;

    private:
    std::vector<std::string> point_clouds_list;
    std::vector<std::shared_ptr<PointCloud>> point_clouds;
    uint point_clouds_index;
    std::shared_ptr<Writer<PointCloud>> writer_ = nullptr;
};

CYBER_REGISTER_COMPONENT(PointCloudProviderComponent)

}//point_cloud_provider
}//scenario
}//apollo