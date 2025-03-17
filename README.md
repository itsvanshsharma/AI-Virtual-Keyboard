# AI Virtual Keyboard

A virtual keyboard that uses hand gestures to type. This project uses computer vision to detect hand movements and convert them into keyboard inputs.

## Prerequisites

- Python 3.8 or higher
- A webcam
- Required Python packages (listed in requirements.txt)

## Installation

1. Clone this repository or download the project files
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## How to Run

1. Open a terminal/command prompt
2. Navigate to the project directory
3. Run the following command:
   ```bash
   python Project.py
   ```

## How to Use

1. Once the program starts, you'll see a window with the virtual keyboard interface
2. Position your hand in front of the camera
3. Use your thumb to press keys:
   - Extend your thumb and point it at a key to press it
   - Keep other fingers closed
   - The key will highlight in orange when pressed
4. To exit the program, press 'q' on your physical keyboard

## Features

- Real-time hand tracking
- Visual feedback for key presses
- Support for all basic keyboard inputs
- Space bar support
- Modern dark theme interface

## Troubleshooting

If you encounter any issues:
1. Make sure your webcam is properly connected and accessible
2. Ensure good lighting conditions for better hand detection
3. Check that all required packages are installed correctly
4. Make sure you're using Python 3.8 or higher
