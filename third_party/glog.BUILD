package(default_visibility = ["//visibility:public"])

licenses(["notice"])

cc_library(
    name = "glog",
    includes = [
        ".",
		"/usr/include/gperftools",
    ],
    linkopts = [
	"-L/usr/local/lib",
        "-lglog",
        "-lgflags",
    ],
)
