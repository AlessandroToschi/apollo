import matplotlib.pyplot as plt
import os.path
import math

def get_object_detected_count(frame_id):
    file_name = "../debug_output/{}.txt".format(int(frame_id) - 1)
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
    with open("./perception.log") as perception_log_file:
        log_lines = perception_log_file.readlines()
        response_time_lines = [log_line for log_line in log_lines if "Response time" in log_line][1:]
        for response_time_line in response_time_lines:
            components = response_time_line.strip().split()
            frames_ids.append(components[7][: -1]) 
            response_times.append(float((components[-1])))
            obj_detects_per_frame.append(get_object_detected_count(frames_ids[-1]))
        
        figure, axes1 = plt.subplots()
        axes1.plot(frames_ids, response_times, "-o", color="blue")
        #axes1.xticks(range(2, 107, 5))
        axes1.set_ylabel("Response time [ms]", color="blue")

        axes2 = axes1.twinx()
        axes2.plot(frames_ids, obj_detects_per_frame, "-o", color="red")
        #axes2.xticks(range(2, 107, 5))
        axes2.set_ylabel("objects detected per frame", color="red")
        #figure.show()
        plt.xticks(range(2, len(frames_ids) + 1, int(math.sqrt(len(frames_ids) - 1))))
        plt.show()

if __name__ == "__main__":
    main()