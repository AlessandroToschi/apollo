package(default_visibility = ["//visibility:public"])

licenses(["notice"])

cc_library(
    name = "gperf",
    hdrs = [
        "heap-checker.h",
        "heap-profiler.h",
        "malloc_extension_c.h",
        "malloc_extension.h",
        "malloc_hook_c.h",
        "malloc_hook.h",
        "nallocx.h",
        "profiler.h",
        "stacktrace.h",
    ],
    linkopts = [
        "-L/usr/lib -lprofiler",
    ],
)