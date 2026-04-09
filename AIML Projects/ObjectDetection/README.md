# Object Detection

A real-time object detection application using YOLOv3 to identify objects from webcam feed through an interactive web interface.

## Features

- **Real-Time Detection**: Processes live webcam feed for instant object recognition
- **Adjustable Thresholds**: Confidence and NMS threshold sliders for fine-tuning
- **Visual Output**: Colored bounding boxes with confidence scores
- **Live Statistics**: Real-time count of detected object types
- **COCO Dataset**: Detects 80 different object classes (people, vehicles, animals, etc.)
- **User Control**: Toggle detection on/off with checkbox

## Dependencies

- Pillow
- numpy
- opencv-python
- streamlit

## How to Run

```bash
.\.venv\Scripts\python -m streamlit run App.py
```

## Model Details

- **Algorithm**: YOLOv3 (You Only Look Once v3)
- **Dataset**: Pre-trained on COCO dataset
- **Classes**: 80 object categories
- **Files**: yolov3.weights, yolov3.cfg, coco.names

## Interface Features

- **Confidence Threshold**: Filter detections by confidence level (0.0-1.0)
- **NMS Threshold**: Remove overlapping bounding boxes (0.0-1.0)
- **Statistics Panel**: Sidebar showing count of each detected object
- **Mirrored View**: Left-right flipped camera display

## Workflow

1. Adjust confidence and NMS thresholds as needed
2. Click "Run Detection" to start camera capture
3. YOLOv3 processes each frame and detects objects
4. Bounding boxes and labels appear on detected objects
5. Object statistics update in real-time