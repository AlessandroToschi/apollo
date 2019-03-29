#include <iostream>
#include <memory>
#include <string>
#include <vector>
#include <chrono>
#include <thread>
#include <array>

#include "cyber/cyber.h"
#include "cyber/class_loader/class_loader.h"
#include "cyber/component/component.h"
#include "modules/scenario/proto/profiler_info.pb.h"
#include "nvml.h"

namespace apollo{
namespace scenario{
namespace profiler{

using apollo::cyber::Component;
using apollo::cyber::ComponentBase;
using apollo::scenario::profiler::proto::ProfilerInfo;

struct ProfilerInfoEntry
{
    uint32_t frame_id;
    uint64_t pid;
};

class ProfilerComponent : public Component<ProfilerInfo>
{
    public:
    bool Init() override;
    bool Proc(const std::shared_ptr<ProfilerInfo> &profiler_info) override;

    private:
    std::string create_profile_command(uint32_t frame_id, uint64_t pid);
    template<size_t size> bool write_samplings_to_file(std::array<uint32_t, size> &powers, std::array<uint32_t, size> &temperatures, uint32_t frame_id);

    std::vector<ProfilerInfoEntry> profiler_records;
    nvmlDevice_t device;
};

CYBER_REGISTER_COMPONENT(ProfilerComponent)

}//profiler
}//scenario
}//apollo