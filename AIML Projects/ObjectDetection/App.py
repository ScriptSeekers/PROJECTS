import cv2
import numpy as np
import streamlit as st
from PIL import Image
import os
import time

# Set page config
st.set_page_config(page_title="Real-Time Object Detection", layout="wide")

st.title("🛡️ Real-Time Object Detection with YOLOv3")
st.sidebar.title("Settings")

# YOLO model paths - Fixed to script directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEIGHTS_PATH = os.path.join(BASE_DIR, "yolov3.weights")
CFG_PATH = os.path.join(BASE_DIR, "yolov3.cfg")
NAMES_PATH = os.path.join(BASE_DIR, "coco.names")

@st.cache_resource
def load_yolo():
    if not all(os.path.exists(p) for p in [WEIGHTS_PATH, CFG_PATH, NAMES_PATH]):
        st.error("Missing YOLO files (yolov3.weights, yolov3.cfg, coco.names). Please download them.")
        return None, None, None
    
    net = cv2.dnn.readNet(WEIGHTS_PATH, CFG_PATH)
    
    # Load class names
    with open(NAMES_PATH, "r") as f:
        classes = [line.strip() for line in f.readlines()]
    
    layer_names = net.getLayerNames()
    unconnected_layers = net.getUnconnectedOutLayers()
    
    if hasattr(unconnected_layers, 'flatten'):
        output_layers = [layer_names[i - 1] for i in unconnected_layers.flatten()]
    else:
        output_layers = [layer_names[i - 1] for i in unconnected_layers]
        
    return net, classes, output_layers

net, classes, output_layers = load_yolo()

# Colors for bounding boxes
if classes:
    colors = np.random.uniform(0, 255, size=(len(classes), 3))

# Sidebar controls
confidence_threshold = st.sidebar.slider("Confidence Threshold", 0.0, 1.0, 0.5, 0.05)
nms_threshold = st.sidebar.slider("NMS Threshold", 0.0, 1.0, 0.4, 0.05)

run_detection = st.sidebar.checkbox("Run Detection", value=False)

# UI Elements
FRAME_WINDOW = st.image([])
STATS_WINDOW = st.sidebar.empty()

if run_detection:
    if net is None:
        st.warning("Model not loaded. Using camera in preview mode only.")
        cap = cv2.VideoCapture(0)
    else:
        cap = cv2.VideoCapture(0)
    
    while run_detection:
        ret, frame = cap.read()
        if not ret:
            st.error("Failed to read from camera.")
            break
        
        # Mirror effect
        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape
        
        if net is not None:
            # Detection
            blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
            net.setInput(blob)
            outs = net.forward(output_layers)
            
            class_ids = []
            confidences = []
            boxes = []
            
            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    if confidence > confidence_threshold:
                        center_x = int(detection[0] * w)
                        center_y = int(detection[1] * h)
                        box_w = int(detection[2] * w)
                        box_h = int(detection[3] * h)
                        x = int(center_x - box_w / 2)
                        y = int(center_y - box_h / 2)
                        boxes.append([x, y, box_w, box_h])
                        confidences.append(float(confidence))
                        class_ids.append(class_id)
            
            indices = cv2.dnn.NMSBoxes(boxes, confidences, confidence_threshold, nms_threshold)
            
            detected_objects = {}
            if len(indices) > 0:
                for i in indices.flatten():
                    x, y, bw, bh = boxes[i]
                    label = str(classes[class_ids[i]])
                    color = colors[class_ids[i]]
                    
                    detected_objects[label] = detected_objects.get(label, 0) + 1
                    
                    cv2.rectangle(frame, (x, y), (x + bw, y + bh), color, 2)
                    cv2.putText(frame, f"{label} {confidences[i]:.2f}", (x, y - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Update stats
            stats_html = "### Detected Objects\n"
            if detected_objects:
                for obj, count in detected_objects.items():
                    stats_html += f"- **{obj}**: {count}\n"
            else:
                stats_html += "_No objects detected_"
            STATS_WINDOW.markdown(stats_html)
            
        # Convert to RGB for streamlit
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        FRAME_WINDOW.image(frame)
        
        # Small delay to keep UI responsive
        time.sleep(0.01)
    
    cap.release()
else:
    st.info("👈 Check 'Run Detection' in the sidebar to start.")
    st.image("https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format", caption="Object Detection Preview")