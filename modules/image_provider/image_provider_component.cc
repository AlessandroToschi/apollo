#include "modules/image_provider/image_provider_component.h"


namespace apollo {
namespace image_provide {

bool ImageProviderComponent::Init()
{
    std::string image_list_content;

    if(!apollo::cyber::common::GetContent("/apollo/dataset/list.txt", &image_list_content))
    {
        AERROR << "Unable to open the image list.";
        return false;
    }

    std::string line;
    char delimiter = '\n';
    std::istringstream token_stream(image_list_content);

    while(std::getline(token_stream, line, delimiter))
    {
        images_list.push_back(line);
    }

    AINFO << "There are " << images_list.size() << " images.";

    images_index = 0;

    writer_ = node_->CreateWriter<Image>("/apollo/sensor/camera/front_6mm/image");

    return true;
}

bool ImageProviderComponent::Proc()
{
    if(images_index >= images_list.size())
    {
        AINFO << "Saro uscito?";
        //apollo::cyber::AsyncShutdown();
        return false;
    }

    cv::Mat image = cv::imread("/apollo/dataset/data/" + images_list[images_index]);
    cv::cvtColor(image, image, cv::COLOR_BGR2RGB);
    cv::resize(image, image, cv::Size(1920, 1080), 1.0, 1.0, cv::INTER_CUBIC);

    AINFO << image.rows << "    " << image.cols;
    
    CameraImagePtr raw_image;
    raw_image.reset(new CameraImage);
    raw_image->width = image.cols;
    raw_image->height = image.rows;
    raw_image->bytes_per_pixel = 3;
    raw_image->image_size =  raw_image->width * raw_image->height * 3;
    raw_image->is_new = 1;
    raw_image->image = reinterpret_cast<char*>(calloc(raw_image->image_size, sizeof(char)));


    auto proto_image = std::make_shared<Image>();
    proto_image->mutable_header()->set_frame_id("camera_front_6mm");
    proto_image->mutable_header()->set_timestamp_sec(cyber::Time::Now().ToSecond());
    proto_image->set_width(raw_image->width);
    proto_image->set_height(raw_image->height);
    proto_image->mutable_data()->reserve(raw_image->image_size);
    proto_image->set_encoding("rgb8");
    proto_image->set_step(3 * raw_image->width);
    proto_image->set_measurement_time(cyber::Time::Now().ToSecond());

    memcpy(raw_image->image, image.data, raw_image->image_size);

    proto_image->set_data(raw_image->image, raw_image->image_size);

    images_index++;

    writer_->Write(proto_image);

    images_index = (uint)images_list.size();
    
    return true;
}

}
}