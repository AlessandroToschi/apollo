load("//tools:cpplint.bzl", "cpplint")

package(default_visibility = ["//visibility:public"])

cc_binary(
    name = "libpoint_cloud_provider_component.so",
    linkopts = ["-shared"],
    linkstatic = False,
    deps = [":point_cloud_provider_component_lib",],
)

cc_library(
    name = "point_cloud_provider_component_lib",
    srcs = [
        "point_cloud_provider_component.cc",
    ],
    hdrs = [
        "point_cloud_provider_component.h",
    ],
    copts = [
        '-DMODULE_NAME=\\"point_cloud_provider\\"',
    ],
    deps = [
        "//cyber",
        "//modules/drivers/proto:sensor_proto",
        ":point_cloud_provider_gflags",
    ],
)

cc_library(
    name = "point_cloud_provider_gflags",
    srcs = [
        "point_cloud_provider_component_gflags.cc",
    ],
    hdrs = [
        "point_cloud_provider_component_gflags.h",
    ],
    copts = [
        "-DMODULE_NAME=\\\"point_cloud_provider\\\"",
    ],
    deps = [
        "//external:gflags",
    ],
)

cpplint()