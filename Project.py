import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)

keyboard = [
    ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
    ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';'],
    ['z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/'],
    ['SPACE']
]

frame_width, frame_height = 800, 600

# Color scheme
COLORS = {
    'background': (45, 45, 48),
    'key': (60, 60, 65),
    'key_pressed': (0, 150, 255),
    'key_border': (80, 80, 85),
    'text': (255, 255, 255),
    'hand_landmarks': (0, 255, 0),
    'hand_connections': (255, 255, 255),
    'pinch_dot': (0, 0, 255), 
    'text_area': (30, 30, 30)  
}

typed_text = ""

def calculate_distance(point1, point2):
    return np.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)

# Function to draw keyboard on screen
def draw_keyboard(frame):
    key_width, key_height = frame_width // 10, frame_height // 4
    key_padding = 10
    
    # Draw background
    cv2.rectangle(frame, (0, 0), (frame_width, frame_height), COLORS['background'], -1)
    
    # Draw title
    cv2.putText(frame, "AI Virtual Keyboard", (frame_width//2 - 150, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, COLORS['text'], 2)
    cv2.putText(frame, "Touch keys with index finger and thumb", (frame_width//2 - 200, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLORS['text'], 1)
    
    # Draw text display area
    text_area_height = 100
    cv2.rectangle(frame, (10, 80), (frame_width - 10, 80 + text_area_height), 
                 COLORS['text_area'], -1)
    cv2.rectangle(frame, (10, 80), (frame_width - 10, 80 + text_area_height), 
                 COLORS['key_border'], 2)
    
    # Display typed text
    if typed_text:
        # Split text into lines if it's too long
        words = typed_text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= 40:  # 40 characters per line
                current_line.append(word)
                current_length += len(word) + 1
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Display each line
        for i, line in enumerate(lines):
            cv2.putText(frame, line, (20, 120 + i*30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLORS['text'], 2)
    
    # Draw keyboard keys
    for i in range(len(keyboard)):
        for j in range(len(keyboard[i])):
            key_x = j * key_width + key_padding
            key_y = i * key_height + key_padding + 80 + text_area_height  # Add offset for title and text area
            
            # Draw key with rounded corners
            if keyboard[i][j] != 'SPACE':
                # Draw key background
                cv2.rectangle(frame, (key_x, key_y), (key_x + key_width - 5, key_y + key_height - 5), 
                            COLORS['key'], -1)
                # Draw key border
                cv2.rectangle(frame, (key_x, key_y), (key_x + key_width - 5, key_y + key_height - 5), 
                            COLORS['key_border'], 2)
                # Draw key text
                cv2.putText(frame, keyboard[i][j].upper(), 
                           (key_x + key_width//3, key_y + key_height//2 + 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, COLORS['text'], 2)
            else:
                # Draw space bar
                cv2.rectangle(frame, (key_x, key_y), (key_x + 3 * key_width - 5, key_y + key_height - 5), 
                            COLORS['key'], -1)
                cv2.rectangle(frame, (key_x, key_y), (key_x + 3 * key_width - 5, key_y + key_height - 5), 
                            COLORS['key_border'], 2)
                cv2.putText(frame, 'SPACE', (key_x + key_width, key_y + key_height//2 + 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, COLORS['text'], 2)

# Main loop
cap = cv2.VideoCapture(0)
cap.set(3, frame_width)
cap.set(4, frame_height)

last_key_press_time = 0
key_press_delay = 0.3 
pinch_threshold = 0.15 
last_pressed_key = None

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame horizontally for a later selfie-view display
    frame = cv2.flip(frame, 1)

    # Convert the BGR image to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame with MediaPipe Hands
    results = hands.process(rgb_frame)

    # Draw the virtual keyboard on the screen
    draw_keyboard(frame)

    # If hands are detected, track the hand landmarks
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw hand landmarks and connections
            mp_drawing = mp.solutions.drawing_utils
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                                    mp_drawing.DrawingSpec(color=COLORS['hand_landmarks'], thickness=2, circle_radius=4),
                                    mp_drawing.DrawingSpec(color=COLORS['hand_connections'], thickness=2))

            # Get the index finger tip and thumb tip coordinates
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            
            # Calculate the distance between thumb and index finger
            pinch_distance = calculate_distance(thumb_tip, index_finger_tip)
            
            # Get the index finger position for key detection
            cx, cy = int(index_finger_tip.x * frame_width), int(index_finger_tip.y * frame_height)
            
            # Draw a dot at the midpoint between thumb and index finger
            mid_x = int((thumb_tip.x + index_finger_tip.x) * frame_width / 2)
            mid_y = int((thumb_tip.y + index_finger_tip.y) * frame_height / 2)
            cv2.circle(frame, (mid_x, mid_y), 5, COLORS['pinch_dot'], -1)
            
            current_time = time.time()
            # Check for key press based on finger position and pinch
            for i in range(len(keyboard)):
                for j in range(len(keyboard[i])):
                    key_x = j * (frame_width // 10) + 10
                    key_y = i * (frame_height // 4) + 90 + 100  # Add offset for title and text area
                    if keyboard[i][j] != 'SPACE':
                        if key_x < cx < key_x + (frame_width // 10) and key_y < cy < key_y + (frame_height // 4):
                            if pinch_distance < pinch_threshold:  # Check if fingers are pinched
                                if current_time - last_key_press_time >= key_press_delay:
                                    # Update typed text
                                    typed_text += keyboard[i][j]
                                    # Simulate key press
                                    pyautogui.press(keyboard[i][j])
                                    last_key_press_time = current_time
                                    last_pressed_key = keyboard[i][j]
                                    # Visual feedback for key press
                                    cv2.rectangle(frame, (key_x, key_y), 
                                                (key_x + (frame_width // 10) - 5, key_y + (frame_height // 4) - 5), 
                                                COLORS['key_pressed'], -1)
                    else:
                        if key_x < cx < key_x + 3 * (frame_width // 10) and key_y < cy < key_y + (frame_height // 4):
                            if pinch_distance < pinch_threshold:  # Check if fingers are pinched
                                if current_time - last_key_press_time >= key_press_delay:
                                    # Update typed text
                                    typed_text += " "
                                    # Simulate key press
                                    pyautogui.press(' ')
                                    last_key_press_time = current_time
                                    last_pressed_key = 'SPACE'
                                    # Visual feedback for space bar press
                                    cv2.rectangle(frame, (key_x, key_y), 
                                                (key_x + 3 * (frame_width // 10) - 5, key_y + (frame_height // 4) - 5), 
                                                COLORS['key_pressed'], -1)

    # Display the frame
    cv2.imshow('AI Virtual Keyboard', frame)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the VideoCapture object and close all windows
cap.release()
cv2.destroyAllWindows()
