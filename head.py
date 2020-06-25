import cv2
import numpy as np
from ml_serving.drivers import driver

import images

MARGIN_COEF = .4


def head_pose(
        drv: driver.ServingDriver,
        frame: np.ndarray,
        bboxes: np.ndarray,
        rgb=True,
):
    img_size = list(drv.inputs.values())[0][2]
    imgs = np.stack(images.get_images(
        frame, np.array(bboxes).astype(int),
        img_size,
        face_crop_margin=0,
        normalization=None,
        face_crop_margin_coef=MARGIN_COEF
    ))

    if rgb:
        # Convert to BGR.
        imgs = imgs[:, :, :, ::-1]

    input_name = list(drv.inputs.keys())[0]
    outputs = drv.predict({input_name: np.array(imgs).transpose([0, 3, 1, 2])})

    yaw = - outputs["angle_y_fc"].reshape([-1])
    pitch = - outputs["angle_p_fc"].reshape([-1])
    roll = outputs["angle_r_fc"].reshape([-1])

    # Return shape [N, 3] as a result
    return np.array([yaw, pitch, roll]).transpose()


def _head_pose_to_axis(hp_ind: [float]):
    (yaw, pitch, roll) = hp_ind

    pitch = pitch * np.pi / 180
    yaw = -(yaw * np.pi / 180)
    roll = roll * np.pi / 180

    # X-Axis pointing to right
    x1 = np.cos(yaw) * np.cos(roll)
    y1 = np.cos(pitch) * np.sin(roll) + np.cos(roll) * np.sin(pitch) * np.sin(yaw)

    # Y-Axis pointing down
    x2 = -np.cos(yaw) * np.sin(roll)
    y2 = np.cos(pitch) * np.cos(roll) - np.sin(pitch) * np.sin(yaw) * np.sin(roll)

    # Z-Axis out of the screen
    x3 = np.sin(yaw)
    y3 = -np.cos(yaw) * np.sin(pitch)
    z_len = np.sqrt(x3 ** 2 + y3 ** 2)

    return (x1, y1), (x2, y2), (x3, y3), z_len


def draw_axis(frame: np.ndarray, bbox: [int], hp_ind, size: int = None):
    head_pose_axis = _head_pose_to_axis(hp_ind)

    tdx = (bbox[0] + bbox[2]) / 2
    tdy = (bbox[1] + bbox[3]) / 2

    if size is None:
        size = min(abs(bbox[0] - bbox[2]) * .4, abs(bbox[1] - bbox[3]) * .4)

    # X-Axis pointing to right, drawn in red
    x1 = size * head_pose_axis[0][0] + tdx
    y1 = size * head_pose_axis[0][1] + tdy
    c1 = (255, 0, 0)

    # Y-Axis pointing down, drawn in green
    x2 = size * head_pose_axis[1][0] + tdx
    y2 = size * head_pose_axis[1][1] + tdy
    c2 = (0, 255, 0)

    # Z-Axis pointing out of the screen, drawn in blue
    x3 = size * head_pose_axis[2][0] + tdx
    y3 = size * head_pose_axis[2][1] + tdy
    c3 = (0, 0, 255)

    cv2.line(frame, (int(tdx), int(tdy)), (int(x1), int(y1)), c1, 1)
    cv2.line(frame, (int(tdx), int(tdy)), (int(x2), int(y2)), c2, 1)
    cv2.line(frame, (int(tdx), int(tdy)), (int(x3), int(y3)), c3, 1)

    return frame
