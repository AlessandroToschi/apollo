#include "modules/scenario/image_provider/image_provider_component.h"


namespace apollo {
namespace scenario{
namespace image_provider {

bool ImageProviderComponent::Init()
{
    AINFO << this->ConfigFilePath();
    AINFO << FLAGS_dataset_root_folder;
    AINFO << apollo::cyber::Binary::GetName();

    std::string image_list_content;

    if(!apollo::cyber::common::GetContent(FLAGS_dataset_root_folder + FLAGS_dataset_image_folder_name + FLAGS_dataset_image_list_file_name, &image_list_content))
    {
        AERROR << "Unable to open the image list: " << FLAGS_dataset_root_folder + FLAGS_dataset_image_folder_name + FLAGS_dataset_image_list_file_name;
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

    writer_ = node_->CreateWriter<Image>(FLAGS_writer_channel);

    return true;
}

bool ImageProviderComponent::Proc()
{
    if(images_index >= images_list.size() + 1)
    {
        if(FLAGS_continuous_mode)
        {
            AINFO << "ImageProvider will restart the scenario.";
            images_index = 0;
        }
        else
        {
            AINFO << "ImageProvider will end the scenario.";
            apollo::cyber::SetState(apollo::cyber::State::STATE_SHUTTING_DOWN);
            return true;
        }
    }

    cv::Mat image;
    auto proto_image = std::make_shared<Image>();

    if(images_index == images_list.size() && !FLAGS_continuous_mode)
    {
        
        proto_image->mutable_header()->set_frame_id("END");
    }
    else
    {
        image = cv::imread(FLAGS_dataset_root_folder + FLAGS_dataset_image_folder_name + images_list[images_index]);
        cv::cvtColor(image, image, cv::COLOR_BGR2RGB);
        cv::resize(image, image, cv::Size(1920, 1080), 1.0, 1.0, cv::INTER_CUBIC);

        change_contrast_brightness(image, 1.5, 20.0);

        proto_image->mutable_header()->set_frame_id(FLAGS_camera_frame_id);
        proto_image->mutable_header()->set_timestamp_sec(cyber::Time::Now().ToSecond());
        proto_image->set_width(image.cols);
        proto_image->set_height(image.rows);
        proto_image->mutable_data()->reserve(image.cols * image.rows * 3);
        proto_image->set_encoding("rgb8");
        proto_image->set_step(3 * image.cols);
        proto_image->set_measurement_time(cyber::Time::Now().ToSecond());
        proto_image->set_data(image.data, image.cols * image.rows * 3);
    }
    
    writer_->Write(proto_image);

    images_index++;

    if(image.data != nullptr)
    {
        image.release();
    }
    
    return true;
}

void change_contrast_brightness(cv::Mat &image, double alpha, double beta)
{
    image.convertTo(image, -1, alpha, beta);
}

}//image_provider
}//scenario
}//apollo