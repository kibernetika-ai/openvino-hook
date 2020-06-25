import logging

import cv2
from ml_serving.utils import helpers

from detect import detect_bboxes
from overlay import draw_bbox

PARAMS = {
    "threshold": .5,
    "object_name": "object",
}

LOG = logging.getLogger(__name__)


def init_hook(ctx, **params):
    LOG.info('Init params: {}'.format(params))
    _apply_params(params)


def update_hook(ctx, **params):
    LOG.info('Update params: {}'.format(params))
    _apply_params(params)


def _apply_params(params):
    PARAMS.update(params)
    PARAMS["threshold"] = float(PARAMS["threshold"])


def process(inputs, ctx, **kwargs):
    frame, is_streaming = helpers.load_image(inputs, 'input', rgb=False)
    LOG.info("frame shape: {}".format(frame.shape))
    bboxes, probabilities = detect_bboxes(
        ctx.drivers[0],
        frame,
        PARAMS.get("threshold", .5),
    )
    for i, bbox in enumerate(bboxes):
        draw_bbox(
            frame,
            bbox.astype(int),
            label="Detected {}\nprobability: {:.2f}".format(
                PARAMS["object_name"], probabilities[i]),
        )

    if is_streaming:
        output = frame[:, :, ::-1]
    else:
        _, buf = cv2.imencode('.jpg', frame)
        output = buf.tostring()

    return {
        'output': output,
        'bboxes': bboxes.tolist(),
        'probabilities': probabilities.tolist(),
    }
