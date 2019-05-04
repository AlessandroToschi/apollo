load("//tools:cpplint.bzl", "cpplint")

package(default_visibility = ["//visibility:public"])

cc_library(
    name = "fast_point_cloud_provider",
    srcs = ["fast_point_cloud_provider.cc"],
    deps = [
        "//cyber",
        "//modules/drivers/camera/proto:sensor_camera_proto",
        "//modules/drivers/proto:sensor_proto",
    ],
)

cc_binary(
    name = "libfast_point_cloud_provider_component.so",
    linkshared = True,
    linkstatic = False,
    deps = [":fast_point_cloud_provider"],
)

cpplint()