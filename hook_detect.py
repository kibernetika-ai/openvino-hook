import logging

import cv2
from ml_serving.utils import helpers

from detect import detect_bboxes

PARAMS = {
    "threshold": .5,
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
    bboxes, probabilities = detect_bboxes(ctx.drivers[0], frame, PARAMS.get("threshold", .5))
    for bbox in bboxes.astype(int):
        cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 1)

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
