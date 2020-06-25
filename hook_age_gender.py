import logging

import cv2
from ml_serving.utils import helpers

from age_gender import age_gender
from detect import detect_bboxes
from overlay import draw_bbox


PARAMS = {
    "detect_threshold": .5,
}

MARGIN_COEF = .4
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

    detect_driver = ctx.drivers[0]

    bboxes, probabilities = detect_bboxes(
        detect_driver,
        frame,
        PARAMS.get("threshold", .5),
    )

    age, gender = [], []

    if len(bboxes) > 0:

        age_gender_driver = ctx.drivers[1]
        age, gender = age_gender(age_gender_driver, frame, bboxes, rgb=False)

        for i, bbox in enumerate(bboxes):
            draw_bbox(
                frame,
                bbox.astype(int),
                label="Detected face\nprobability: {:.2f}\nage: {}, gender: {}".format(
                    probabilities[i], age[i], "male" if gender[i] == 1 else "female"),
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
        'age': age,
        'gender': gender,
    }
