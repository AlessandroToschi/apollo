import os
import numpy as np
import json
import math
import matplotlib.pyplot as plt

def plot_camera_fusion(camera, fusion):
    ordering = {"contrast(1.5)" : 1, "contrast(2.0)" : 2, "contrast(2.5)" : 3,
                "brightness(30.0)" : 4, "brightness(60.0)" : 5, "brightness(90.0)" : 6,
                "gaussian(7)" : 7, "rain" : 8, "snow" : 9, "occlusion" : 10}
    
    camera.sort(key=lambda x: ordering[x[0]])
    fusion.sort(key=lambda x: ordering[x[0]])

    _, axes1 = plt.subplots(figsize=(20,10))
    ff = [c[1] for c in camera]
    #i = 1
    #for s, f, _ in camera:
    axes1.bar(range(1, 11), ff, color='blue', width=1)
    plt.show()


def get_corner_points(x, y, l, w):
    x1, x2, y1, y2 = 0, 0, 0, 0
    if l % 2 == 0:
        l_2 = l // 2
        x1 = x - l_2
        x2 = x + l_2
    else:
        l_2 = l // 2
        x1 = x - l_2
        x2 = x + l_2 + 1
    if w % 2 == 0:
        w_2 = w // 2
        y1 = y - w_2
        y2 = y + w_2
    else:
        w_2 = w // 2
        y1 = y - w_2
        y2 = y + w_2 + 1
    return (x1, x2, y1, y2)

def iou_3D(oracle_box, simulation_box):
    l_o, w_o = oracle_box[3], oracle_box[4]
    x_o, y_o = oracle_box[0], oracle_box[1]
    x1_o, x2_o, y1_o, y2_o = get_corner_points(x_o, y_o, l_o, w_o)

    l_d, w_d = simulation_box[3], simulation_box[4]
    x_d, y_d = simulation_box[0], simulation_box[1]
    x1_d, x2_d, y1_d, y2_d = get_corner_points(x_d, y_d, l_d, w_d)

    x_min = min(x1_o, x1_d)

    if x_min < 0:
        x_min = abs(x_min)
        x1_o += x_min
        x2_o += x_min
        x1_d += x_min
        x2_d += x_min

    y_min = min(y1_o, y2_o)

    if y_min < 0:
        y_min = abs(y_min)
        y1_o += y_min
        y2_o += y_min
        y1_d += y_min
        y2_d += y_min

    x1_i, y1_i = max(x1_o, x1_d), max(y1_o, y1_d)
    x2_i, y2_i = min(x2_o, x2_d), min(y2_o, y2_d)

    intersection_area = max(0, x2_i - x1_i + 1) * max(0, y2_i - y1_i + 1)
    union_area = (x2_o - x1_o + 1) * (y2_o - y1_o + 1) + (x2_d - x1_d + 1) * (y2_d - y1_d + 1)

    return intersection_area / (union_area - intersection_area)

def evaluate_detection_3D(oracle_boxes, simulation_boxes):
    taken = []
    taken_iou = []

    for i in range(len(oracle_boxes)):
        max_taken_iou = 0
        max_taken = -1
        for j in range(len(simulation_boxes)):
            if j in taken:
                continue
            current_iou = iou_3D(oracle_boxes[i], simulation_boxes[j])
            if current_iou > max_taken_iou:
                max_taken_iou = current_iou
                max_taken = j
        if max_taken_iou > 0.5:
            taken.append(max_taken)
            taken_iou.append(max_taken_iou)
    
    if len(taken_iou) > 0:
        tp = len(taken_iou)
        fn, fp = len(oracle_boxes) - tp, len(simulation_boxes) - tp
        p, r = tp / (tp + fp), tp / (tp + fp)
        f = 2.0 * ((p * r) / (p + r))
        mean_iou = np.mean(taken_iou)
        return (f, mean_iou)
    else:
        return (0.0, 0.0)

def load_boxes(box_path):
    with open(box_path) as box_file:
        box_json = json.loads(box_file.read())
        boxes = []
        if "perceptionObstacle" in box_json:
            for obstacle in box_json["perceptionObstacle"]:
                boxes.append((
                    math.trunc(float(obstacle["position"]["x"]) * 1E3),
                    math.trunc(float(obstacle["position"]["y"]) * 1E3),
                    math.trunc(float(obstacle["position"]["z"]) * 1E3),
                    math.trunc(float(obstacle["length"]) * 1E3),
                    math.trunc(float(obstacle["width"]) * 1E3),
                    math.trunc(float(obstacle["height"]) * 1E3)
                ))
        return boxes

def load_boxes_polygon(box_path):
    with open(box_path) as box_file:
        box_json = json.loads(box_file.read())
        boxes = []
        if "perceptionObstacle" in box_json:
            for obstacle in box_json["perceptionObstacle"]:
                x_min = 1E12
                x_max = -1E12
                y_min = 1E12
                y_max = -1E12
                for polygon in obstacle["polygonPoint"]:
                    if float(polygon["x"]) < x_min:
                        x_min = float(polygon["x"])
                    if float(polygon["x"]) > x_max:
                        x_max = float(polygon["x"])
                    if float(polygon["y"]) < y_min:
                        y_min = float(polygon["y"])
                    if float(polygon["y"]) > y_max:
                        y_max = float(polygon["y"])
                boxes.append((x_min, x_max, y_min))
                #boxes.append((
                #    math.trunc(float(obstacle["position"]["x"]) * 1E6),
                #    math.trunc(float(obstacle["position"]["y"]) * 1E6),
                #    math.trunc(float(obstacle["position"]["z"]) * 1E6),
                #    math.trunc(float(obstacle["length"]) * 1E6),
                #    math.trunc(float(obstacle["width"]) * 1E6),
                #    math.trunc(float(obstacle["height"]) * 1E6)
                #))
        return boxes


def iou(oracle_rect, simulation_rect):
    x_o, y_o, w_o, h_o = oracle_rect
    x1_o, x2_o, y1_o, y2_o = x_o, x_o + w_o, y_o, y_o + h_o
    x_d, y_d, w_d, h_d = simulation_rect
    x1_d, x2_d, y1_d, y2_d = x_d, x_d + w_d, y_d, y_d + h_d

    x1_i, y1_i = max(x1_o, x1_d), max(y1_o, y1_d)
    x2_i, y2_i = min(x2_o, x2_d), min(y2_o, y2_d)

    intersection_area = max(0, x2_i - x1_i + 1) * max(0, y2_i - y1_i + 1)
    union_area = (x2_o - x1_o + 1) * (y2_o - y1_o + 1) + (x2_d - x1_d + 1) * (y2_d - y1_d + 1)

    return intersection_area / (union_area - intersection_area)

def evaluate_detection(oracle_rects, simulation_rects):
    taken = []
    taken_iou = []

    for i in range(len(oracle_rects)):
        max_taken_iou = 0
        max_taken = -1
        for j in range(len(simulation_rects)):
            if j in taken:
                continue
            current_iou = iou(oracle_rects[i], simulation_rects[j])
            if current_iou > max_taken_iou:
                max_taken_iou = current_iou
                max_taken = j
        if max_taken_iou > 0.5:
            taken.append(max_taken)
            taken_iou.append(max_taken_iou)
    
    if len(taken_iou) > 0:
        tp = len(taken_iou)
        fn, fp = len(oracle_rects) - tp, len(simulation_rects) - tp
        p, r = tp / (tp + fp), tp / (tp + fp)
        f = 2.0 * ((p * r) / (p + r))
        mean_iou = np.mean(taken_iou)
        return (f, mean_iou)
    else:
        return (0.0, 0.0)

def load_rects(rect_path):
    with open(rect_path) as rect_file:
        lines = rect_file.readlines()
        rect_count = int(lines[1])
        rects = []
        if rect_count > 0:
            for i in range(rect_count):
                components = lines[i + 2].strip().split(" ")
                rects.append((float(components[0]), float(components[1]), float(components[2]), float(components[3])))
        return rects

def load_oracle_ids(oracle_path):
    oracle_files = os.listdir(oracle_path)
    fusion_files = [fusion_file for fusion_file in oracle_files if "fusion" in fusion_file]
    return sorted([int(fusion_file.strip().split("_")[1].split(".")[0]) for fusion_file in fusion_files])

def main():
    scenario = "city_2011_09_26_0014"
    oracle_path = "/apollo/modules/scenario/fault_injection/oracle/" + scenario + "/"
    simulations_path = "/apollo/modules/scenario/fault_injection/simulations/" + scenario + "/"
    simulations = os.listdir(simulations_path)

    metrics = {}
    metrics_3D = {}
    for simulation in simulations:
        metrics[simulation] = []
        metrics_3D[simulation] = []

    print("There are {} simulations".format(len(simulations)))

    oracle_ids = load_oracle_ids(oracle_path)

    print("The oracle has {} frames".format(len(oracle_ids)))

    for id in oracle_ids:
        oracle_rects = load_rects(oracle_path + "{}.txt".format(id))
        for simulation in simulations:
            file_name = simulations_path + simulation + "/{}.txt".format(id)
            if not os.path.exists(file_name):
                continue
            simulation_rects = load_rects(file_name)
            metrics[simulation].append(evaluate_detection(oracle_rects, simulation_rects))
    
    for id in oracle_ids:
        oracle_boxes = load_boxes(oracle_path + "fusion_{}.txt".format(id))
        for simulation in simulations:
            file_name = simulations_path + simulation + "/fusion_{}.txt".format(id)
            if not os.path.exists(file_name):
                continue
            simulation_boxes = load_boxes(file_name)
            metrics_3D[simulation].append(evaluate_detection_3D(oracle_boxes, simulation_boxes))

    camera = []
    
    for simulation in simulations:
        f = [t[0] for t in metrics[simulation]]
        mean_iou = [t[1] for t in metrics[simulation]]
        mean_f = np.round(np.mean(f), decimals=3)
        mean_mean_iou = np.round(np.mean(mean_iou), decimals=3)
        camera.append((simulation, mean_f, mean_mean_iou))
        #print("Camera - {} - {} - {}".format(simulation, mean_f, mean_mean_iou))
        #print()
    
    camera.sort(key=lambda x: x[1], reverse=True)

    for sim, f, i in camera:
        print("Camera - {} - {} - {}".format(sim, f, i))
    
    print()

    fusion = []

    for simulation in simulations:
        f = [t[0] for t in metrics_3D[simulation]]
        mean_iou = [t[1] for t in metrics_3D[simulation]]
        mean_f = np.round(np.mean(f), decimals=3)
        mean_mean_iou = np.round(np.mean(mean_iou), decimals=3)
        fusion.append((simulation, mean_f, mean_mean_iou))
        #print("Fusion - {} - {} - {}".format(simulation, mean_f, mean_mean_iou))
        #print()
    
    fusion.sort(key=lambda x: x[1], reverse=True)

    for sim, f, i in fusion:
        print("Fusion - {} - {} - {}".format(sim, f, i))
    
    #plot_camera_fusion(camera, fusion)

if __name__ == "__main__":
    main()
    #oracle_rect = (10, 20, 5, 10)
    #d_rect = (12, 35, 6, 5)
    #print(iou(oracle_rect, d_rect))