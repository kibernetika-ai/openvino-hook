# openvino-hook

## Models

### Detection

#### Face detection
* [face-detection-adas-0001](https://github.com/opencv/open_model_zoo/tree/master/models/intel/face-detection-adas-0001)
* [face-detection-retail-0004](https://github.com/opencv/open_model_zoo/tree/master/models/intel/face-detection-retail-0004)
* [face-detection-retail-0005](https://github.com/opencv/open_model_zoo/tree/master/models/intel/face-detection-retail-0005)

#### Person detection
* [person-detection-asl-0001](https://github.com/opencv/open_model_zoo/tree/master/models/intel/person-detection-asl-0001)
* [person-detection-adas-0002](https://github.com/opencv/open_model_zoo/tree/master/models/intel/person-detection-adas-0002)
* [person-detection-retail-0002](https://github.com/opencv/open_model_zoo/tree/master/models/intel/person-detection-retail-0002)
* [person-detection-retail-0013](https://github.com/opencv/open_model_zoo/tree/master/models/intel/person-detection-retail-0013)

### Configuration:

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
    "command": "kserving --driver openvino --model-path $MODEL_DIR/XXXX-detection-XXXX-XXXX.xml --hooks $SRC_DIR/hook_detect.py -o threshold=.1 -o object_name=OBJECT --http-enable --webrtc --input-name input --output-name output",
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
        "label": "Input image",
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

## Age and gender recognition

* [age-gender-recognition-retail-0013](https://github.com/opencv/open_model_zoo/tree/master/models/intel/age-gender-recognition-retail-0013)

```json
{
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
  "replicas": 1,
  "resources": {
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
  "images": {
    "cpu": "kuberlab/serving:latest-openvino",
    "gpu": "kuberlab/serving:latest-openvino-gpu"
  },
  "command": "kserving --driver openvino --model-path $FACE_DIR/face-detection-retail-0004.xml --driver openvino --model-path $MODEL_DIR/age-gender-recognition-retail-0013.xml --hooks $SRC_DIR/hook_age_gender.py -o threshold=.1 --http-enable --webrtc --input-name input --output-name output",
  "workDir": "$SRC_DIR",
  "spec": {
    "params": [
      {
        "name": "input",
        "type": "image_webrtc",
        "label": "Input image",
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
      },
      {
        "name": "age",
        "type": "int",
        "shape": [
          -1
        ],
        "description": "Ages"
      },
      {
        "name": "gender",
        "type": "int",
        "shape": [
          -1
        ],
        "description": "Genders"
      }
    ],
    "options": {
      "noCache": true
    },
    "model": "any",
    "template": "image"
  },
  "sources": [
    {
      "gitRepo": {
        "repository": "https://github.com/kibernetika-ai/openvino-hook"
      },
      "name": "src",
      "subPath": "openvino-hook"
    },
    {
      "model": {
        "workspace": "g-core",
        "model": "age-gender-recognition-retail-0013",
        "version": "1.0.0-cpu"
      },
      "name": "model",
      "mountPath": "/model"
    }
  ]
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