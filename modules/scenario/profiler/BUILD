load("//tools:cpplint.bzl", "cpplint")

package(default_visibility = ["//visibility:public"])

cc_binary(
    name = "libprofiler.so",
    linkopts = ["-shared"],
    linkstatic = False,
    deps = ["profiler_component_lib"],
)

cc_library(
    name = "profiler_component_lib",
    srcs = ["profiler_component.cc"],
    hdrs = ["profiler_component.h"],
    includes = ["/usr/local/cuda-8.0/include"],
    copts = [
        '-DMODULE_NAME=\\"profiler\\"',
    ],
    deps = ["//cyber", "//modules/scenario/proto:profiler_proto_library", "@cuda"],
)

cpplint()