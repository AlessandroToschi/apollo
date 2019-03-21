import numpy as np
import os
import os.path
import matplotlib.pyplot as plt
from statistics import mean

oracle_folder = "/home/apolloxps/full_output_backup"
debug_folder = "/home/apolloxps/apollo/debug_output"

assert os.path.isdir(oracle_folder)
assert os.path.isdir(debug_folder)

oracle_files_names = sorted(os.listdir(oracle_folder))
debug_files_names = sorted(os.listdir(debug_folder))

def get_rects(file_path):
    rects = []
    with open(file_path) as pred_file:
        lines = pred_file.readlines()
        detected_objects = int(lines[1])
        for i in range(2, detected_objects + 2):
            obj = lines[i].strip()
            params = obj.split(" ")
            rect = params[:4]
            rects.append([int(x) for x in rect])
    return rects

def compare_rects(oracle_rects, debug_rects):
    count_accuracy = len(debug_rects) / len(oracle_rects)
    oracle_count = len(oracle_rects)
    raster = np.zeros((oracle_count, 1920, 1080), dtype='int')
    areas = np.zeros(oracle_count, dtype="int")
    final_overlaps = []
    for i in range(oracle_count):
        x, y, w, h = oracle_rects[i]
        raster[i, y : y + h, x : x + w] = 1
        areas[i] = w * h
    for j in range(len(debug_rects)):
        x, y, w, h = debug_rects[j]
        overlaps = []
        for i in range(oracle_count):
            raster[i, y : y + h, x : x + w] += 1
            equals = np.count_nonzero(raster[i, :, :] == 2)
            if equals / areas[i] > 0:
                overlaps.append((i, j, equals / areas[i]))
            raster[i, y : y + h, x : x + w] -= 1
            if equals / areas[i] > 1.0:
                pass
        maxx = 0
        ind = -1
        for k in range(len(overlaps)):
            a, b, o = overlaps[k]
            if o > maxx:
                maxx = o
                ind = k
        if ind != -1:
            final_overlaps.append(overlaps[ind])
    #print(final_overlaps)
    return (len(final_overlaps) / oracle_count, final_overlaps)
                
            

assert oracle_files_names == debug_files_names
acca = []
for fn in oracle_files_names:
    print(fn)
    cc = compare_rects(get_rects(os.path.join(oracle_folder, fn)),
                  get_rects(os.path.join(debug_folder, fn)))
    print(cc)
    print("\n")
    acca.append(cc)

plt.figure(figsize=(40, 20))
plt.subplot(2, 1, 1)
plt.plot(range(1, len(acca) + 1), [cc[0] for cc in acca], "-o")
plt.subplot(2, 1, 2)
plt.plot(range(1, len(acca) + 1), [mean([a[2] for a in cc[1]]) for cc in acca], "-o")
plt.yticks([0.1 * i for i in range(1, 11)])
plt.show()