import cv2
import numpy as np
from yolov4.tf import YOLOv4
#from tracker import Tracker


def image_detection(frame_read, yolo, num_frame, thresh):
    height, width, _ = frame_read.shape
    frame_read = cv2.cvtColor(frame_read, cv2.COLOR_BGR2RGB)
    pred_bboxes = yolo.predict(frame_read, thresh)
    pred_bboxes = pred_bboxes * np.array([width, height, width, height, 1, 1])
    centroids = pred_bboxes[:,0:2]
    centroids = np.insert(centroids, 0, num_frame, axis=1)
    return pred_bboxes, centroids


def create_model(obj_name="model_data/obj.names",parse_cfg="model_data/yolov4-tiny3L-zebrafish.cfg",load_weights="model_data/yolov4-tiny3L-zebrafish_best.weights"):
    yolo = YOLOv4()
    yolo.config.parse_names(obj_name)
    yolo.config.parse_cfg(parse_cfg)
    yolo.make_model()
    yolo.load_weights(load_weights, weights_type="yolo")
    return yolo

def tracking(video_name,max_fish):
    max_fish = int(max_fish)
    tracker = Tracker(300, 30, max_fish)
    yolo = create_model()
    cap = cv2.VideoCapture(video_name)

    ret, frame_read = cap.read()
    num_frame = 1

    x_list = np.empty((0,max_fish+1))
    y_list = np.empty((0,max_fish+1))
    vel_list = np.empty((0,max_fish+1))

    while frame_read is not None:
        pred_bboxes, centroids = image_detection(frame_read, yolo, num_frame, 0.4)
        tracker.update(centroids[:,1:3])
        x, y, vel = tracker.get_metrics()
        x_list = np.append(x_list, np.insert(x,0,num_frame,axis=1), axis=0)
        y_list = np.append(y_list, np.insert(y,0,num_frame,axis=1), axis=0)
        vel_list = np.append(vel_list, np.insert(vel,0,num_frame,axis=1), axis=0)
        ret, frame_read = cap.read()
        num_frame = num_frame + 1
    cap.release()

    x_list = np.array(x_list)
    y_list = np.array(y_list)
    vel_list = np.array(vel_list)
    x_list = x_list[:,1:max_fish+1]
    y_list = y_list[:,1:max_fish+1]
    vel_list = vel_list[:,1:max_fish+1]
    return x_list,y_list, vel_list
