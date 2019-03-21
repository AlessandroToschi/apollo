import caffe
import numpy
import sys
import os.path

def network_size(network):
    total_parameters = 0
    for layer_name in network.params.keys():
        layer = network.params[layer_name]
        inner_parameters = 0
        for blob in layer:
            inner_parameters += blob.data.size
        total_parameters += inner_parameters
    print "Network has " + str(total_parameters) + " parameters"
    print "Network size is " + str(total_parameters * 4) + " bytes"
        

def main():
    if len(sys.argv) != 3:
        print "The estimator requires the network proto and the weight file."
        return False
    proto_file_path = sys.argv[1]
    weight_file_path = sys.argv[2]
    if not os.path.isfile(proto_file_path):
        print "The proto file does not exists."
        return False
    if not os.path.isfile(weight_file_path):
        print "The weight file does not exists."
        return False
    network = caffe.Net(proto_file_path, weight_file_path, caffe.TEST)
    network_size(network)
    return True


if __name__ == "__main__":
    main()