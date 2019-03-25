echo $1
nvprof  --export-profile /apollo/debug_output/perception_analysis.nvvp -f \
        --timeout 200 \
        $1 \
