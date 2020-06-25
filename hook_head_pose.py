import logging

import cv2
from ml_serving.utils import helpers

from age_gender import age_gender
from detect import detect_bboxes
import head
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

    head_poses = []

    if len(bboxes) > 0:

        head_pose_driver = ctx.drivers[1]
        head_poses = head.head_pose(head_pose_driver, frame, bboxes, rgb=False)

        for i, bbox in enumerate(bboxes):
            draw_bbox(
                frame,
                bbox.astype(int),
                label="Detected face\n"
                      "probability: {:.2f}\n"
                      "yaw: {:.2f}\n"
                      "pitch: {:.2f}\n"
                      "roll: {:.2f}".format(
                    probabilities[i], head_poses[i][0], head_poses[i][1], head_poses[i][2]),
            )
            head.draw_axis(frame, bbox, head_poses[i])

        head_poses = head_poses.tolist()

    if is_streaming:
        output = frame[:, :, ::-1]
    else:
        _, buf = cv2.imencode('.jpg', frame)
        output = buf.tostring()

    return {
        'output': output,
        'bboxes': bboxes.tolist(),
        'probabilities': probabilities.tolist(),
        'poses': head_poses,
    }
