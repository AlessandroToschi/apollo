#include "modules/scenario/profiler/profiler_component.h"

namespace apollo{
namespace scenario{
namespace profiler{

bool ProfilerComponent::Init()
{
    profiler_records = std::vector<ProfilerInfoEntry>(20);

    uint32_t device_count;
    nvmlReturn_t result = nvmlInit();

    if(result != NVML_SUCCESS)
    {
        AERROR << "Failed to initialize NVML. Reason: " << nvmlErrorString(result);
        return false;
    }

    result = nvmlDeviceGetCount(&device_count);

    if(result != NVML_SUCCESS)
    {
        AERROR << "Failed to retrieve the number of device(s). Reason: " << nvmlErrorString(result);
        return false;
    }

    if(device_count == 0)
    {
        AERROR << "No GPU(s) found!";
        return false;
    }

    result = nvmlDeviceGetHandleByIndex(0, &device);

    if(result != NVML_SUCCESS)
    {
        AERROR << "Failed to retrieve the device 0. Reason: " << nvmlErrorString(result);
        return false;
    }

    return true;
}

bool ProfilerComponent::Proc(const std::shared_ptr<ProfilerInfo> &profiler_info)
{
    std::array<uint32_t, 100> instant_powers;
    std::array<uint32_t, 100> instant_temperatures;
    nvmlReturn_t result;

    AINFO << "Entering for temperature and power profiling of frame " << profiler_info->frame_id();

    for(int i = 0; i < 100; i++)
    {
        result = nvmlDeviceGetPowerUsage(device, &instant_powers[i]);

        if(result != NVML_SUCCESS)
        {
            AERROR << "Unable to retrieve the power usage for frame " << profiler_info->frame_id() << " at sample " << i << ". Reason: " << nvmlErrorString(result);
            instant_powers[i] = 0;
        }

        result = nvmlDeviceGetTemperature(device, nvmlTemperatureSensors_enum::NVML_TEMPERATURE_GPU, &instant_temperatures[i]);

        if(result != NVML_SUCCESS)
        {
            AERROR << "Unable to retrieve the temperature for frame " << profiler_info->frame_id() << " at sample " << i << ". Reason: " << nvmlErrorString(result);
            instant_temperatures[i] = 0;
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }

    if(!write_samplings_to_file<100>(instant_powers, instant_temperatures, profiler_info->frame_id()))
    {
        AERROR << "Something went wrong while writing the samplings for frame " << profiler_info->frame_id();
        return false;
    }
    /*
    if(!profiler_info.action().compare("START"))
    {
        int entry_index = profiler_info.frame_id() % profiler_records.size();
    }
    else if(!profiler_info.action().compare("STOP"))
    {
        //stop profiling
    }
    else
    {
        //Unrecognized action
    }
    
    */
    return true;
}

template<size_t size> bool ProfilerComponent::write_samplings_to_file(std::array<uint32_t, size> &powers, std::array<uint32_t, size> &temperatures, uint32_t frame_id)
{
    std::string path = "/apollo/debug_output/" + std::to_string(frame_id) + "_gpu.txt";
    std::ofstream out_file(path, std::ofstream::out);

    if(!out_file.is_open())
    {
        AERROR << "Cannot open the output file for frame " << frame_id;
        return false;
    }

    out_file << "Power [W]; Temperature[C];" << std::endl;

    for(int i = 0; i < size; i++)
    {
        out_file << uint32_t(powers[i] / 1000) << ";";
        out_file << temperatures[i] << ";" << std::endl;
    }

    return true;
}

std::string ProfilerComponent::create_profile_command(uint32_t frame_id, uint64_t pid)
{
    return  "perf record -o /apollo/debug_output/perf.data." + std::to_string(frame_id) + " "
            "--call-graph dwarf --event cycles:P,instructions:P,cpu-clock:P,task-clock:P "
            "--F 4000";
}

}//profiler
}//scenario
}//apollo