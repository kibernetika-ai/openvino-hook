# openvino-hook

## Models

### Face detection

* [face-detection-retail-0004](https://github.com/opencv/open_model_zoo/tree/master/models/intel/face-detection-retail-0004)
* [face-detection-retail-0005](https://github.com/opencv/open_model_zoo/tree/master/models/intel/face-detection-retail-0005)
* [face-detection-adas-0001](https://github.com/opencv/open_model_zoo/tree/master/models/intel/face-detection-adas-0001)

## Configuration:

```json
{
  "serving": {
    "sources": [
      {
        "gitRepo": {
          "repository": "https://github.com/kibernetika-ai/openvino-hook"
        },
        "name": "src",
        "subPath": "openvino-hook"
      }
    ],
    "command": "kserving --driver openvino --model-path $MODEL_DIR/face-detection-XXXX-XXXX.xml --hooks $SRC_DIR/hook_detect.py -o threshold=.1 -o object_name=face --http-enable --webrtc --input-name input --output-name output",
    "ports": [
      {
        "name": "grpc",
        "protocol": "TCP",
        "port": 9000,
        "targetPort": 9000
      },
      {
        "name": "webrtc",
        "protocol": "TCP",
        "port": 5004,
        "targetPort": 5004
      }
    ],
    "images": {
      "cpu": "kuberlab/serving:latest-openvino",
      "gpu": "kuberlab/serving:latest-openvino-gpu"
    },
    "replicas": 1,
    "workDir": "$SRC_DIR",
    "accelerators": {
      "gpu": 0
    },
    "requests": {
      "cpu": "500m",
      "memory": "64Mi"
    },
    "limits": {
      "cpu": "2",
      "memory": "1Gi"
    }
  },
  "servingSpec": {
    "params": [
      {
        "name": "input",
        "type": "image_webrtc",
        "label": "Image with face",
        "value": ""
      }
    ],
    "response": [
      {
        "name": "output",
        "type": "bytes",
        "shape": [
          -1
        ],
        "description": "Output image"
      },
      {
        "name": "bboxes",
        "type": "double",
        "shape": [
          -1,
          4
        ],
        "description": "Boundary boxes"
      },
      {
        "name": "probabilities",
        "type": "double",
        "shape": [
          -1
        ],
        "description": "Detection probabilities"
      }
    ],
    "options": {
      "noCache": true
    },
    "model": "any",
    "template": "image"
  }
}
```

## Testing

Run serving:

```shell script
kserving \
  --driver openvino \
  --model-path /opt/intel/openvino/deployment_tools/intel_models/face-detection-adas-0001/FP32/face-detection-adas-0001.xml \
  --hooks hook_detect.py \
  -o threshold=.8
  --http-enable
```

Make request:

```shell script
curl http://0.0.0.0:9001/predict/ -F "bytes_input=@input.jpg"
```