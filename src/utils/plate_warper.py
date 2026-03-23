# This code is for warping plate image from the original plate image

import numpy as np
import cv2


def get_vertexes(img, result): # return vertexes of the plate
    default_vertexes = np.array([[0, 0], [img.shape[1], 0], [0, img.shape[0]], [img.shape[1], img.shape[0]]],
                                dtype=np.int32)
    vertexes = result[0].boxes

    for idx in range(4):
        if idx not in vertexes.cls.tolist():
            yield default_vertexes[idx][0], default_vertexes[idx][1]

    for vertex in vertexes:
        vertex = vertex.xyxy.tolist()[0]
        x1, y1, x2, y2 = vertex
        x = (x1 + x2) / 2
        y = (y1 + y2) / 2
        yield x, y


def warp(img, vertex_box): # return warped plate image
    vertex_list = list(get_vertexes(img, vertex_box))
    vertex_list = np.array(vertex_list, dtype=np.int32)
    sm = np.sum(vertex_list, axis=1)
    diff = np.diff(vertex_list, axis=1)

    # vertex 계산
    tl = vertex_list[np.argmin(sm)]
    br = vertex_list[np.argmax(sm)]
    tr = vertex_list[np.argmin(diff)]
    bl = vertex_list[np.argmax(diff)]

    # vertex 가 잘못된 경우
    if tl[0] >= tr[0] or tl[1] >= bl[1] or br[0] <= bl[0] or br[1] <= tr[1]:
        return None

    dst1 = np.array([tl, tr, br, bl], dtype=np.float32)

    # vertex 로 변환할 크기 계산
    w1 = abs(br[0] - bl[0])
    w2 = abs(tr[0] - tl[0])
    h1 = abs(tr[1] - br[1])
    h2 = abs(tl[1] - bl[1])

    # vertex 로 변환할 크기 설정
    width = max([w1, w2])
    height = max([h1, h2])
    dst2 = np.array([[0, 0], [width, 0], [width, height], [0, height]], dtype=np.float32)

    # 변환 행렬 계산
    M = cv2.getPerspectiveTransform(dst1, dst2)

    # 변환
    warped = cv2.warpPerspective(img, M, (width, height))

    return warped


class WarpPlate: # This class is for warping plate image from the original plate image
    def __init__(self, model):
        self.model = model

    def detect_and_warp(self, img): # return warped plate image
        vertex_box = self.model(img)
        warped = warp(img, vertex_box)
        return warped
