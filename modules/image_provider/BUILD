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
    deps = [
        "//cyber",
        "//modules/drivers/camera/proto:sensor_camera_proto",
        "//modules/drivers/proto:sensor_proto",
        "//modules/drivers/camera"
    ],
)

cpplint()