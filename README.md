# openvino-hook

Run serving:

```shell script
kserving \
  --driver openvino \
  --model-path /opt/intel/openvino/deployment_tools/intel_models/face-detection-adas-0001/FP32/face-detection-adas-0001.xml \
  --hooks hook_detect.py \
  -o threshold=.8
  --http-enable
```

Request:

```shell script
curl http://0.0.0.0:9001/predict/ -F "bytes_input=@input.jpg"
```