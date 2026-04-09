# Action Reflection

A real-time motion capture and visualization application that creates an animated "clone" of your body movements using AI-powered pose detection.

## Features

- **Real-time Pose Detection**: Uses MediaPipe's Pose solution to detect 33 body landmarks from webcam feed
- **2D Skeleton Visualization**: Draws skeleton in real-time with glowing neon effects, motion trails, and smooth joint rendering
- **3D Skeleton Visualization**: Simultaneously renders a 3D model of your skeleton using matplotlib
- **Neon/Glow Effects**: Animated gradient colors cycling through hue spectrum with pulsing intensity and trail effects
- **Visual Feedback**: Displays "SCANNING..." when no pose detected and FPS counter

## Dependencies

- matplotlib
- mediapipe
- numpy
- opencv-python

## How to Run

```bash
.\.venv\Scripts\python AR.py
```

**Requirements:**
- Windows system with a webcam
- Python virtual environment (`.venv`) with dependencies installed
- Camera must be accessible and working

**Controls:**
- Press **'q'** to quit the application

## Technical Details

- Tracks 14 pose connections from shoulders to fingers and legs
- Uses HSV to RGB conversion for smooth gradient color transitions
- 3D updates happen every 6 frames for optimization
- Includes fallback imports for different MediaPipe versions
- Anti-aliased lines with layered rendering for visual polish