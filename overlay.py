import cv2
import numpy as np
import typing

DEFAULT_COLOR = (0, 255, 0)
ERROR_COLOR = (255, 0, 0)
ALIGN_TO_RIGHT = True

font_inner_padding_w = 5


def draw_bbox(
        frame: np.ndarray,
        bbox: typing.List[int],
        label=None,
        color=DEFAULT_COLOR,
        thickness=1,
):
    frame_avg = (frame.shape[1] + frame.shape[0]) / 2
    cv2.rectangle(
        frame,
        (bbox[0], bbox[1]),  # (left, top)
        (bbox[2], bbox[3]),  # (right, bottom)
        color,
        int(thickness * frame_avg / 1000),
    )

    if label is not None and label != '':
        strs = label.split('\n')
        str_w, str_h = 0, 0
        widths = []
        for i, line in enumerate(strs):
            lw, lh = _get_text_size(frame, line)
            str_w = max(str_w, lw)
            str_h = max(str_h, lh)
            widths.append(lw)
        str_h = int(str_h * 1.6)  # line height

        to_right = bbox[0] + str_w > frame.shape[1] - font_inner_padding_w
        top = max(str_h, bbox[1] - int((len(strs) - 0.5) * str_h))

        for i, line in enumerate(strs):
            if ALIGN_TO_RIGHT:
                # all align to right box border
                if to_right:
                    left = (bbox[2] - widths[i] - font_inner_padding_w)
                else:
                    left = bbox[0] + font_inner_padding_w
            else:
                # move left each string if it's ending not places on the frame
                if bbox[0] + widths[i] > frame.shape[1] - font_inner_padding_w:
                    left = frame.shape[1] - widths[i] - font_inner_padding_w
                else:
                    left = bbox[0] + font_inner_padding_w

            _put_text(frame, line, left, int(top + i * str_h), color=(0, 0, 0),
                      thickness_mul=3)
            _put_text(frame, line, left, int(top + i * str_h), color=color)


def _get_text_size(
        frame, text,
        thickness=None, thickness_mul=None,
        font_scale=None, font_face=None,
):
    font_face, font_scale, thickness = _get_text_props(
        frame, thickness, thickness_mul, font_scale, font_face
    )
    return cv2.getTextSize(text, font_face, font_scale, thickness)[0]


def _put_text(frame, text, left, top, color,
              thickness=None, thickness_mul=None,
              font_scale=None, font_face=None, line_type=cv2.LINE_AA):
    font_face, font_scale, thickness = _get_text_props(
        frame, thickness, thickness_mul, font_scale, font_face
    )
    cv2.putText(
        frame, text,
        (left, top),
        font_face, font_scale,
        color, thickness=thickness, lineType=line_type,
    )


def _get_text_props(
        frame,
        thickness=None, thickness_mul=None,
        font_scale=None, font_face=None,
):
    if font_scale is None or thickness is None:
        frame_avg = (frame.shape[1] + frame.shape[0]) / 2
        if font_scale is None:
            font_scale = frame_avg / 1600
        if thickness is None:
            thickness = int(font_scale * 2)
        if thickness_mul is not None:
            thickness_m = int(thickness * thickness_mul)
            thickness = thickness + 1 if thickness == thickness_m \
                else thickness_m
    if font_face is None:
        font_face = cv2.FONT_HERSHEY_SIMPLEX
    return font_face, font_scale, thickness
