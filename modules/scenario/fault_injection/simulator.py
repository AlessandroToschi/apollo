import os
import scenario
from filter import *

def main():
    #filter_names = ["contrast(1.2)"]#, "contrast(1.65)", "contrast(2.1)", "contrast(2.55)", "contrast(3.0)"]
    scenario_path = "/apollo/kitty/city/2011_09_26/2011_09_26_drive_0014_sync"
    index = 0
    #print(scenario_path)
    #command = "python2 /apollo/modules/scenario/fault_injection/simulation.py '{}' '{}'".format(scenario_path, str(index))
    #print(command)
    #os.system(command)

    #scenario_path = "/apollo/kitty/city/2011_09_26/2011_09_26_drive_0014_sync"
    #index = 0
#
    for filter_name in Filter.get_filters():
        print(scenario_path, filter_name)
        command = "python2 /apollo/modules/scenario/fault_injection/simulation.py '{}' '{}' '{}'".format(scenario_path, str(index), filter_name)
        print(command)
        os.system(command)
        index += 1

    #for filter_name in filter_names:
    #    print("{} - {}".format(scenario_path, filter_name))
    #    command = "python2 /apollo/modules/scenario/fault_injection/simulation.py '{}' '{}' '{}'".format(scenario_path, str(index), filter_name)
    #    os.system(command)
    #    index += 1
        #print(command)
    #for scenario_path in scenario.Scenario.get_scenarios():
    #    print("Scenario {}".format(index + 1))
    #    command = "python2 /apollo/modules/scenario/fault_injection/simulation.py '{}' '{}'".format(scenario_path, str(index))
    #    #print(command)
    #    os.system(command)
    #    index += 1

if __name__ == "__main__":
    main()