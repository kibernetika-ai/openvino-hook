import numpy as np
from ml_serving.drivers import driver

import images

MARGIN_COEF = .4


def age_gender(
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

    age = (outputs["age_conv3"].reshape([-1]) * 100).round().astype(int)
    # gender: 0 - female, 1 - male
    gender = outputs['prob'].reshape([-1, 2]).argmax(1)

    return age, gender
