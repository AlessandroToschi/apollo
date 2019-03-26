load("//tools:cpplint.bzl", "cpplint")

package(default_visibility = ["//visibility:public"])

cc_binary(
    name = "libimage_provider_component.so",
    linkopts = ["-shared", "-lopencv_core",
        "-lopencv_imgproc",
        "-lopencv_highgui",
        "-lboost_system",],
    linkstatic = False,
    deps = [":image_provider_component_lib",
            ],
)

cc_library(
    name = "image_provider_component_lib",
    srcs = [
        "image_provider_component.cc",
    ],
    hdrs = [
        "image_provider_component.h",
    ],
    copts = [
        '-DMODULE_NAME=\\"image_provider\\"',
    ],
    deps = [
        "//cyber",
        "//modules/drivers/camera/proto:sensor_camera_proto",
        "//modules/drivers/proto:sensor_proto",
        "//modules/drivers/camera",
        ":image_provider_gflags",
    ],
)

cc_library(
    name = "image_provider_gflags",
    srcs = [
        "image_provider_component_gflags.cc",
    ],
    hdrs = [
        "image_provider_component_gflags.h",
    ],
    copts = [
        "-DMODULE_NAME=\\\"image_provider\\\"",
    ],
    deps = [
        "//external:gflags",
    ],
)

cpplint()