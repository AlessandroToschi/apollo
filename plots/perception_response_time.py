import matplotlib.pyplot as plt
import os.path
import math
import numpy as np

def plot_power_temps(powers, temps):
    figure, axes1 = plt.subplot(figsize=(20, 10))
    axes1.plot(range(1, len(powers) + 1), powers, color="blue")
    axes1.set_yticks(range(20, 120, 5))
    axes1.set_ylabel("GPU Power [W]")
    axes2 = axes1.twinx()
    axes2.plot(range(1, len(temps) + 1), temps, color="red")
    axes1.set_yticks(range(30, 100, 5))
    axes1.set_ylabel("GPU Temp [C]")
    plt.xticks(range(1, len(temps) + 1, int(math.sqrt(len(temps) - 1))))
    plt.savefig("power_temp.svg") 

def get_powers_temps(frame_id):
    file_name = "../debug_output/{}_gpu.txt".format(frame_id)
    if not os.path.exists(file_name):
        print("The {} does not exists.".format(file_name))
        return ([], [])
    powers = []
    temps = []
    with open(file_name) as times_file:
        lines = times_file.readlines()
        lines = lines[1:]
        for line in lines:
            components = line.strip().split(';')
            powers.append(int(components[0][:-1]))
            temps.append(int(components[1][:-1]))
    return (powers, temps)

def plot_gant_timess(timess):
    figure, axes1 = plt.subplots(figsize=(20,10))
    ld_p =      np.round(np.average(np.array([time["LaneDetector::Detect:"] for time in timess])), decimals=2)
    lp_p2d =    np.round(np.average(np.array([time["LanePostprocessor::Process2D:"] for time in timess])), decimals=2)
    cs_u =      np.round(np.average(np.array([time["CalibrationService::Update:"] for time in timess])), decimals=2)
    lp_p3d =    np.round(np.average(np.array([time["LanePostprocessor::Process3D:"] for time in timess])), decimals=2)
    t_p =       np.round(np.average(np.array([time["Tracker::Predict:"] for time in timess])), decimals=2)
    yod_d =     np.round(np.average(np.array([time["YoloObstacleDetector::Detect:"] for time in timess])), decimals=2)
    fe_e =      np.round(np.average(np.array([time["FeatureExtractor::Extract:"] for time in timess])), decimals=2)
    t_a2d =     np.round(np.average(np.array([time["Tracker::Associate2D:"] for time in timess])), decimals=2)
    t_t =       np.round(np.average(np.array([time["Transformer::Transform:"] for time in timess])), decimals=2)
    op_p =      np.round(np.average(np.array([time["ObstaclePostprocessor::Process:"] for time in timess])), decimals=2)
    t_a3d =     np.round(np.average(np.array([time["Tracker::Associate3D:"] for time in timess])), decimals=2)
    tr_t =      np.round(np.average(np.array([time["Tracker::Track:"] for time in timess])), decimals=2)
    fop =       np.round(np.average(np.array([time["FillObjectPolygon:"] for time in timess])), decimals=2)
    seq =   [("LaneDetector::Detect", ld_p), ("LanePostprocessor::Process2D", lp_p2d), ("CalibrationService::Update", cs_u),
             ("LanePostprocessor::Process3D", lp_p3d), ("Tracker::Predict", t_p), ("YoloObstacleDetector", yod_d),
             ("FeatureExtractor::Extract", fe_e), ("Tracker::Associate2D", t_a2d), ("Transformer::Transform", t_t),
             ("ObstaclePostprocessor::Process", op_p), ("Tracker::Associate3D", t_a3d), ("Tracker::Track", tr_t),
             ("FillObjectPolygon", fop)]
    last_time = 0.0
    i = 1
    for name, time in seq:
        #axes1.broken_barh([(last_time, i), (last_time + time, i)], (i, i))
        axes1.plot([last_time, last_time + time], [i, i], marker="|", markersize=15)
        i += 1
        last_time += time
    axes1.set_yticks(range(1, len(seq)))
    axes1.set_yticklabels([x[0] for x in seq])
    plt.savefig("gannt.svg")    

def plot_response_time_obstracles(response_times, frames_ids, obj_detects_per_frame):
    figure, axes1 = plt.subplots(figsize=(20,10))
    axes1.bar(frames_ids, response_times, 0.35, color="blue")
    axes1.set_ylabel("Response time [ms]", color="blue")
    plt.yticks(range(60, 100, 5))
    axes2 = axes1.twinx()
    axes2.plot(frames_ids, obj_detects_per_frame, "o", color="red")
    axes2.set_ylabel("objects detected per frame", color="red")
    plt.xticks(range(2, len(frames_ids) + 1, int(math.sqrt(len(frames_ids) - 1))))
    avg_response_time = np.mean(np.array(response_times))
    axes1.plot([2, len(frames_ids)], [np.round(avg_response_time, decimals=2), np.round(avg_response_time, decimals=2)], color="green")
    plt.title("Avg Response Time {} ms".format(np.round(avg_response_time, decimals=2)))
    plt.savefig("resp_obj_plot.svg")

def plot_times_obstacles(timess, frames_ids, obj_detects_per_frame):
    figure, axes1 = plt.subplots(figsize=(20,10))
    ld_p = [time["LaneDetector::Detect:"] for time in timess]
    lp_p2d = [time["LanePostprocessor::Process2D:"] for time in timess]
    cs_u = [time["CalibrationService::Update:"] for time in timess]
    lp_p3d = [time["LanePostprocessor::Process3D:"] for time in timess]
    t_p = [time["Tracker::Predict:"] for time in timess]
    yod_d = [time["YoloObstacleDetector::Detect:"] for time in timess]
    fe_e = [time["FeatureExtractor::Extract:"] for time in timess]
    t_a2d = [time["Tracker::Associate2D:"] for time in timess]
    t_t = [time["Transformer::Transform:"] for time in timess]
    op_p = [time["ObstaclePostprocessor::Process:"] for time in timess]
    t_a3d = [time["Tracker::Associate3D:"] for time in timess]
    tr_t = [time["Tracker::Track:"] for time in timess]
    fop = [time["FillObjectPolygon:"] for time in timess]

    width = 0.5
    p = []
    others = np.zeros_like(ld_p)
    if np.mean(ld_p) > 1:
        p.append(("LaneDetector::Detect", axes1.bar(frames_ids, ld_p, width)))
    else:
        others += ld_p
    if np.mean(lp_p2d) > 1:
        p.append(("LanePostprocessor::Process2D", axes1.bar(frames_ids, lp_p2d, width)))
    else:
        others += lp_p2d
    if np.mean(cs_u) > 1:
        p.append(("CalibrationService::Update", axes1.bar(frames_ids, cs_u, width)))
    else:
        others += cs_u
    if np.mean(lp_p3d) > 1:
        p.append(("LanePostprocessor::Process3D", axes1.bar(frames_ids, lp_p3d, width)))
    else:
        others += lp_p3d
    if np.mean(t_p) > 1:
        p.append(("Tracker::Predict", axes1.bar(frames_ids, t_p, width)))
    else:
        others += t_p
    if np.mean(yod_d) > 1:
        p.append(("YoloObstacleDetector::Detect", axes1.bar(frames_ids, yod_d, width)))
    else:
        others += yod_d
    if np.mean(fe_e) > 1:
        p.append(("FeatureExtractor::Extract", axes1.bar(frames_ids, fe_e, width)))
    else:
        others += fe_e
    if np.mean(t_a2d) > 1:
        p.append(("Tracker::Associate2D", axes1.bar(frames_ids, t_a2d, width)))
    else:
        others += t_a2d
    if np.mean(t_t) > 1:
        p.append(("Transformer::Transform", axes1.bar(frames_ids, t_t, width)))
    else:
        others += t_t
    if np.mean(op_p) > 1:
        p.append(("ObstaclePostprocessor::Process", axes1.bar(frames_ids, op_p, width)))
    else:
        others += op_p
    if np.mean(t_a3d) > 1:
        p.append(("Tracker::Associate3D", axes1.bar(frames_ids, t_a3d, width)))
    else:
        others += t_a3d
    if np.mean(tr_t) > 1:
        p.append(("Tracker::Track", axes1.bar(frames_ids, tr_t, width)))
    else:
        others += tr_t
    if np.mean(fop) > 1:
        p.append(("FillObjectPolygon", axes1.bar(frames_ids, fop, width)))
    else:
        others += fop
    p.append(("Others", axes1.bar(frames_ids, others, width)))
    avg_oth = np.round(np.average(others), decimals=2)
    avg_yod = np.round(np.average(yod_d), decimals=2)
    avg_ld = np.round(np.average(ld_p), decimals=2)
    axes1.plot([1, len(frames_ids)], [avg_oth, avg_oth], color="purple")
    axes1.plot([1, len(frames_ids)], [avg_yod, avg_yod], color="purple")
    axes1.plot([1, len(frames_ids)], [avg_ld, avg_ld], color="purple")
    axes1.set_ylabel("Step Times [ms]")
    plt.yticks(range(0, 100, 10))
    axes2 = axes1.twinx()
    axes2.plot(frames_ids, obj_detects_per_frame, "o", color="red")
    plt.xticks(range(2, len(frames_ids) + 1, int(math.sqrt(len(frames_ids) - 1))))
    plt.title("Avg. LaneDetector::Detect {} ms; Avg YoloObstacleDetector::Detect {} ms; Avg Others {} ms".format(avg_ld, avg_yod, avg_oth))
    plt.legend([pp[1][0] for pp in p], [pp[0] for pp in p])
    plt.savefig("times.svg")

def get_times(frame_id):
    file_name = "../debug_output/{}_times.txt".format(int(frame_id))
    if not os.path.exists(file_name):
        print("The {} does not exists.".format(file_name))
        return {}
    times = {}
    with open(file_name) as times_file:
        lines = times_file.readlines()
        for line in lines:
            components = line.strip().split()
            key = components[0]
            value = float(components[1])
            times[key] = value
    return times

def get_object_detected_count(frame_id):
    file_name = "../debug_output/{}.txt".format(int(frame_id))
    if not os.path.exists(file_name):
        print("The {} does not exists.".format(file_name))
        return 0
    obj_detected = 0
    with open(file_name) as obj_det_frame_id:
        obj_detected = int(obj_det_frame_id.readlines()[1])
    return obj_detected

def main():
    if not os.path.exists("./perception.log"):
        print("The perception's log does not exists.")
        return
    frames_ids = []
    response_times = []
    obj_detects_per_frame = []
    timess = []
    powerss = []
    tempss = []
    with open("./perception.log") as perception_log_file:
        log_lines = perception_log_file.readlines()
        response_time_lines = [log_line for log_line in log_lines if "Response time" in log_line][1:]
        for response_time_line in response_time_lines:
            components = response_time_line.strip().split()
            frames_ids.append(components[7][: -1]) 
            response_times.append(float((components[-1])))
            obj_detects_per_frame.append(get_object_detected_count(frames_ids[-1]))
            timess.append(get_times(frames_ids[-1]))
            powers, temps = get_powers_temps(frames_ids[-1])
            powerss += powers
            tempss += temps
    plot_response_time_obstracles(response_times, frames_ids, obj_detects_per_frame)
    plot_times_obstacles(timess, frames_ids, obj_detects_per_frame)
    plot_gant_timess(timess)
    plot_power_temps(powerss, tempss)


if __name__ == "__main__":
    main()