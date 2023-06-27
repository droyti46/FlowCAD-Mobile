import math

import cv2
import numpy as np

MIN_MATCHES = 120

class ArProcedure():

    def __init__(self, path_to_tracker, model):
        self.tracker = cv2.imread(path_to_tracker)
        self.model = model

        # ORB keypoint detector
        self.orb = cv2.ORB_create()              
        # create brute force  matcher object
        self.bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)  
        # Compute tracker keypoints and its descriptors
        self.kp_tracker, self.des_tracker = self.orb.detectAndCompute(self.tracker, None)

        # matrix of camera parameters (made up but works quite well for me) 
        self.camera_parameters = np.array([[800, 0, 320], [0, 800, 240], [0, 0, 1]])

    def calculate_and_display(self, cap):
        # Compute scene keypoints and its descriptors
        kp_frame, des_frame = self.orb.detectAndCompute(cap, None)
        # Match frame descriptors with tracker descriptors
        matches = self.bf.match(self.des_tracker, des_frame)
        # Sort them in the order of their distance
        matches = sorted(matches, key=lambda x: x.distance)

        if len(matches) > MIN_MATCHES:
            # Рисуем точки
            #cap = cv2.drawKeypoints(cap, kp_frame, None)

            # assuming matches stores the matches found and 
            # returned by bf.match(des_model, des_frame)
            # differenciate between source points and destination points
            src_pts = np.float32([self.kp_tracker[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp_frame[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
            # compute Homography
            matrix, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5)

            # Draw a rectangle that marks the found model in the frame
            h, w, c = self.tracker.shape
            pts = np.float32([[0, 0], [0, h], [w, h], [w, 0]]).reshape(-1, 1, 2)
            # project corners into frame
            dst = cv2.perspectiveTransform(pts, matrix)  
            # connect them with lines
            cap = cv2.polylines(cap, [np.int32(dst)], True, (255, 0, 255), 3)

            # if a valid matrix matrix was found render cube on model plane
            if matrix is not None:
                try:
                    # obtain 3D projection matrix from matrix matrix and camera parameters
                    projection = self.projection_matrix(self.camera_parameters, matrix)  
                    # project cube or model
                    cap = self.render(cap, self.model, projection, self.tracker)
                except:
                    pass
            

        return cap

    def projection_matrix(self, camera_parameters, homography):
        """
         From the camera calibration matrix and the estimated homography
         compute the 3D projection matrix
         """
        # Compute rotation along the x and y axis as well as the translation
        homography = homography * (-1)
        rot_and_transl = np.dot(np.linalg.inv(camera_parameters), homography)
        col_1 = rot_and_transl[:, 0]
        col_2 = rot_and_transl[:, 1]
        col_3 = rot_and_transl[:, 2]
        # normalise vectors
        l = math.sqrt(np.linalg.norm(col_1, 2) * np.linalg.norm(col_2, 2))
        rot_1 = col_1 / l
        rot_2 = col_2 / l
        translation = col_3 / l
        # compute the orthonormal basis
        c = rot_1 + rot_2
        p = np.cross(rot_1, rot_2)
        d = np.cross(c, p)
        rot_1 = np.dot(c / np.linalg.norm(c, 2) + d / np.linalg.norm(d, 2), 1 / math.sqrt(2))
        rot_2 = np.dot(c / np.linalg.norm(c, 2) - d / np.linalg.norm(d, 2), 1 / math.sqrt(2))
        rot_3 = np.cross(rot_1, rot_2)
        # finally, compute the 3D projection matrix from the model to the current frame
        projection = np.stack((rot_1, rot_2, rot_3, translation)).T
        return np.dot(camera_parameters, projection)

    def render(self, img, obj, projection, tracker, color=False):
        """
        Render a loaded obj model into the current video frame
        """
        vertices = obj[0]
        scale_matrix = np.eye(3) * 30
        h, w, c = tracker.shape

        for face in obj[1]:
            points = np.array([vertices[vertex - 1] for vertex in face])
            points = np.dot(points, scale_matrix)
            # render tracker in the middle of the reference surface. To do so,
            # tracker points must be displaced
            points = np.array([[p[0] + w / 2, p[1] + h / 2, p[2]] for p in points])
            dst = cv2.perspectiveTransform(points.reshape(-1, 1, 3), projection)
            imgpts = np.int32(dst)
            if color is False:
                cv2.fillConvexPoly(img, imgpts, (137, 27, 211))
            else:
                color = hex_to_rgb(face[-1])
                color = color[::-1]  # reverse
                cv2.fillConvexPoly(img, imgpts, color)

        return img
