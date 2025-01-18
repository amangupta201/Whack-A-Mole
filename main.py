import cv2
import mediapipe as mp
import random
import time

import numpy as np

# Initialize MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Set up the game window
WINDOW_WIDTH, WINDOW_HEIGHT = 640, 480
MOLE_WIDTH, MOLE_HEIGHT = 80, 50
score = 0
lives = 3
max_mole_time = 3
mole_spawn_interval = 3
moles = []
combo_hits = 0
max_moles_on_screen = 1
start_time = time.time()
game_duration = 60
difficulty_level = 1
power_up_active = False
power_up_duration = 5
power_up_start_time = 0.0
leaderboard = []
multiplayer_scores = []
current_player = 1
num_players = 2

# Function to generate a random mole position
def spawn_mole():
    x = random.randint(0, WINDOW_WIDTH - MOLE_WIDTH)
    y = random.randint(0, WINDOW_HEIGHT - MOLE_HEIGHT)
    return {
        "position": (x, y),
        "spawn_time": time.time(),
        "special": random.choices(["normal", "golden", "bomb", "power-up"], weights=[70, 15, 10, 5])[0]
    }

# Function to draw a mole on the frame
def draw_mole(frame, mole):
    x, y = mole["position"]
    special = mole["special"]

    # Define colors based on mole type
    mole_colors = {
        "normal": (105, 58, 45),   # Brown
        "golden": (0, 215, 255),  # Yellow
        "bomb": (0, 0, 255),      # Red
        "power-up": (0, 255, 0)   # Green
    }

    mole_color = mole_colors.get(special, (255, 255, 255))  # Default to white if undefined
    eye_color = (255, 255, 255)
    pupil_color = (0, 0, 0)
    nose_color = (0, 0, 0)
    mouth_color = (0, 0, 0)

    # Draw mole body
    cv2.ellipse(frame, (x + MOLE_WIDTH // 2, y + MOLE_HEIGHT // 2), (MOLE_WIDTH // 2, MOLE_HEIGHT // 2),
                0, 0, 360, mole_color, -1)

    # Draw eyes
    cv2.circle(frame, (x + MOLE_WIDTH // 4, y + MOLE_HEIGHT // 3), 10, eye_color, -1)
    cv2.circle(frame, (x + 3 * MOLE_WIDTH // 4, y + MOLE_HEIGHT // 3), 10, eye_color, -1)

    # Draw pupils
    cv2.circle(frame, (x + MOLE_WIDTH // 4, y + MOLE_HEIGHT // 3), 4, pupil_color, -1)
    cv2.circle(frame, (x + 3 * MOLE_WIDTH // 4, y + MOLE_HEIGHT // 3), 4, pupil_color, -1)

    # Draw nose
    cv2.circle(frame, (x + MOLE_WIDTH // 2, y + MOLE_HEIGHT // 2), 6, nose_color, -1)

    # Draw mouth
    cv2.ellipse(frame, (x + MOLE_WIDTH // 2, y + 2 * MOLE_HEIGHT // 3), (12, 6), 0, 0, 180, mouth_color, 2)

# Function to detect a tap gesture
def detect_tap(landmarks):
    x_tip = int(landmarks[8].x * WINDOW_WIDTH)
    y_tip = int(landmarks[8].y * WINDOW_HEIGHT)
    return (x_tip, y_tip)

# Function to check if a tap hits a mole
def is_hit(tap_position, mole):
    x, y = mole["position"]
    return x <= tap_position[0] <= x + MOLE_WIDTH and y <= tap_position[1] <= y + MOLE_HEIGHT

# Function to handle mole hit effects
def handle_mole_hit(mole):
    global score, combo_hits, lives, power_up_active, power_up_start_time, game_duration

    if mole["special"] == "normal":
        score += 1
    elif mole["special"] == "golden":
        score += 5
    elif mole["special"] == "bomb":
        lives -= 1
    elif mole["special"] == "power-up":
        power_up_active = True
        power_up_start_time = time.time()  # Start the power-up timer
        game_duration += 5  # Add 5 seconds to the game

    combo_hits += 1

# Function to update game state
def update_game():
    global moles, combo_hits, max_mole_time, mole_spawn_interval, difficulty_level, max_moles_on_screen, power_up_active

    current_time = time.time()

    # Remove moles that timed out
    moles = [mole for mole in moles if current_time - mole["spawn_time"] < max_mole_time]

    # Gradually increase the number of moles on screen as the game progresses
    elapsed_time = current_time - start_time
    max_moles_on_screen = min(1 + elapsed_time // 10, 5)

    # Spawn new moles if below the max limit
    while len(moles) < max_moles_on_screen:
        moles.append(spawn_mole())

    # Adjust difficulty dynamically
    if score >= 10 and difficulty_level == 1:
        difficulty_level = 2
        max_mole_time = 2
        mole_spawn_interval = 2
    elif score >= 20 and difficulty_level == 2:
        difficulty_level = 3
        max_mole_time = 1
        mole_spawn_interval = 1

    # Deactivate power-up after its duration
    if power_up_active and current_time - power_up_start_time > power_up_duration:
        power_up_active = False

# Function to display leaderboard
def display_leaderboard():
    print("\nLeaderboard:")
    sorted_leaderboard = sorted(leaderboard, key=lambda x: x[1], reverse=True)
    for rank, (player, score) in enumerate(sorted_leaderboard, 1):
        print(f"{rank}. {player}: {score} points")

# Main game loop
def display_instructions():
    instructions = [
        "Welcome to Virtual Whack-a-Mole!",
        "",
        "How to Play:",
        "1. Tap the moles by pointing at them with your index finger.",
        "2. Effects of different moles:",
        "   - Normal (Gray): +1 point",
        "   - Golden (Yellow): +5 points",
        "   - Bomb (Red): -1 life",
        "   - Power-Up (Green): +5 seconds",
        "3. The game ends when the timer reaches 0 or you run out of lives.",
        "",
        "Press any key to start the game!"
    ]

    # Set window size (larger for better readability)
    window_width = 800
    window_height = 600
    frame = np.zeros((window_height, window_width, 3), dtype=np.uint8)

    # Add semi-transparent background
    overlay = frame.copy()
    alpha = 0.6
    cv2.rectangle(overlay, (20, 20), (window_width - 20, window_height - 20), (50, 50, 50), -1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    # Display instructions on the frame
    y_offset = 100
    for line in instructions:
        color = (255, 255, 255)  # White text
        cv2.putText(frame, line, (50, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        y_offset += 40  # Adjust line spacing for readability

    # Display the title prominently
    cv2.putText(frame, "Game Instructions", (200, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)

    # Show the instructions
    cv2.imshow("Instructions", frame)
    cv2.waitKey(0)  # Wait for any key press to continue
    cv2.destroyWindow("Instructions")



for player in range(1, num_players + 1):
    print(f"Player {player}'s turn!")
    # Display the instructions before the game starts
    display_instructions()

    score = 0
    lives = 3
    start_time = time.time()

    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        update_game()

        for mole in moles:
            draw_mole(frame, mole)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                tap_position = detect_tap(hand_landmarks.landmark)

                for mole in moles:
                    if is_hit(tap_position, mole):
                        handle_mole_hit(mole)
                        moles.remove(mole)

        elapsed_time = int(time.time() - start_time)
        remaining_time = max(game_duration - elapsed_time, 0)

        cv2.putText(frame, f"Score: {score}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, f"Lives: {lives}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, f"Time: {remaining_time}s", (WINDOW_WIDTH - 200, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        if remaining_time == 0 or lives <= 0:
            cv2.putText(frame, "Game Over!", (WINDOW_WIDTH // 4, WINDOW_HEIGHT // 2), cv2.FONT_HERSHEY_SIMPLEX, 2,
                        (0, 0, 255), 3)
            cv2.imshow("Virtual Whack-a-Mole", frame)
            cv2.waitKey(3000)
            break

        cv2.imshow("Virtual Whack-a-Mole", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    print(f"Player {player} scored {score} points!")
    leaderboard.append((f"Player {player}", score))

display_leaderboard()
