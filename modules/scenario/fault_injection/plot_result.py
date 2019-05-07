import matplotlib.pyplot as plt
from collections import OrderedDict
import numpy as np

def plot_results(camera_results, fusion_results, fusion_fusion_result, labels):
    x = list(range(1, len(camera_results) + 1))
    _, axes = plt.subplots(figsize=(20,10))
    axes.grid(True, which="major", axis='y', zorder=-1.0, linestyle="--")
    camera_f = [camera_results[key][0] for key in camera_results.keys()]
    fusion_f = [fusion_results[key][0] for key in fusion_results.keys()]
    ffusion_f = [fusion_fusion_result[key][0] for key in fusion_fusion_result.keys()]
    min_value = min(min(camera_f), min(fusion_f))
    bottom = ((int(min_value * 100) // 5) * 5.0) / 100.0
    y_ticks = np.linspace(bottom, 1.0, num=10)
    camera_bar = axes.bar(np.array(x) - 0.2, camera_f, width=0.2, color="b", align="center")
    fusion_bar = axes.bar(np.array(x), fusion_f, width=0.2, color="r", align="center")
    fusion_fusion_bar = axes.bar(np.array(x) + 0.2, ffusion_f, width=0.2, color="g", align="center")
    axes.set_xticks(x)
    axes.set_xticklabels(labels)
    axes.set_ylim([bottom, 1.0])
    axes.legend([camera_bar, fusion_bar, fusion_fusion_bar], ["camera", "fusion camera", "fusion lidar"])
    plt.show()

def load_result_file(file_name, labels):
    with open(file_name) as result_file:
        lines = result_file.readlines()
        camera_lines = [line for line in lines if line.startswith("Camera")]
        fusion_lines = [line for line in lines if line.startswith("Fusion")]
        assert len(camera_lines) == len(fusion_lines)
        camera_results = OrderedDict()
        fusion_results = OrderedDict()
        for label in labels:
            camera_line = [line for line in camera_lines if label in line][0]
            fusion_line = [line for line in fusion_lines if label in line][0]
            camera_results[label] = [float(accuracy.strip()) for accuracy in camera_line.strip().split("-")[-2:]]
            fusion_results[label] = [float(accuracy.strip()) for accuracy in fusion_line.strip().split("-")[-2:]]
        return (camera_results, fusion_results)

def main():
    labels = ["contrast(1.5)", "contrast(2.0)", "contrast(2.5)",
        "brightness(30.0)", "brightness(60.0)", "brightness(90.0)",
        "gaussian(7)", "rain", "snow", "occlusion"]
    camera_file_name = "/apollo/modules/scenario/fault_injection/city_0014_camera.txt"
    fusion_file_name = "/apollo/modules/scenario/fault_injection/city_0014_fusion.txt"
    camera_camera_results, camera_fusion_result = load_result_file(camera_file_name, labels)
    _, fusion_fusion_result = load_result_file(fusion_file_name, labels)
    plot_results(camera_camera_results, camera_fusion_result, fusion_fusion_result, labels)


if __name__ == "__main__":
    main()