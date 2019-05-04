import os
import scenario

def main():
    filter_names = ["contrast(1.2)"]#, "contrast(1.65)", "contrast(2.1)", "contrast(2.55)", "contrast(3.0)"]
    scenario_path = "/apollo/kitty/road/2011_09_29/2011_09_29_drive_0004_sync"
    index = 0
    for filter_name in filter_names:
        print("{} - {}".format(scenario_path, filter_name))
        command = "python2 /apollo/modules/scenario/fault_injection/simulation.py '{}' '{}' '{}'".format(scenario_path, str(index), filter_name)
        os.system(command)
        index += 1
        #print(command)
    #for scenario_path in scenario.Scenario.get_scenarios():
    #    print("Scenario {}".format(index + 1))
    #    command = "python2 /apollo/modules/scenario/fault_injection/simulation.py '{}' '{}'".format(scenario_path, str(index))
    #    #print(command)
    #    os.system(command)
    #    index += 1

if __name__ == "__main__":
    main()