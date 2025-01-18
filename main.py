import cv2
import mediapipe as mp
import random
import time

# Initialize MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Set up the game window
WINDOW_WIDTH, WINDOW_HEIGHT = 640, 480
MOLE_WIDTH, MOLE_HEIGHT = 80, 50  # Default mole dimensions
score = 0
lives = 3
max_mole_time = 3  # Initial mole visibility time
mole_spawn_interval = 3  # Time between mole spawns
moles = []  # List of active moles
combo_hits = 0  # Counter for combo scoring
max_moles_on_screen = 1  # Start with 1 mole on screen
start_time = time.time()  # Game start time
game_duration = 60  # Total game time in seconds
difficulty_level = 1
power_up_active = False  # Track power-up state
power_up_duration = 5  # Duration for power-up effect
power_up_start_time = None  # Start time of power-up

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
    mole_color = (105, 58, 45) if special == "normal" else (0, 215, 255) if special == "golden" else (0, 0, 255) if special == "bomb" else (0, 255, 0)
    eye_color = (255, 255, 255)  # Eyes
    pupil_color = (0, 0, 0)  # Pupils
    nose_color = (0, 0, 0)  # Nose
    mouth_color = (0, 0, 0)  # Mouth

    # Draw body
    cv2.ellipse(frame, (x + MOLE_WIDTH // 2, y + MOLE_HEIGHT // 2), (MOLE_WIDTH // 2, MOLE_HEIGHT // 2),
                0, 0, 360, mole_color, -1)

    # Draw eyes
    cv2.circle(frame, (x + MOLE_WIDTH // 4, y + MOLE_HEIGHT // 3), 7, eye_color, -1)
    cv2.circle(frame, (x + 3 * MOLE_WIDTH // 4, y + MOLE_HEIGHT // 3), 7, eye_color, -1)

    # Draw pupils
    cv2.circle(frame, (x + MOLE_WIDTH // 4, y + MOLE_HEIGHT // 3), 3, pupil_color, -1)
    cv2.circle(frame, (x + 3 * MOLE_WIDTH // 4, y + MOLE_HEIGHT // 3), 3, pupil_color, -1)

    # Draw nose
    cv2.circle(frame, (x + MOLE_WIDTH // 2, y + MOLE_HEIGHT // 2), 5, nose_color, -1)

    # Draw mouth
    cv2.ellipse(frame, (x + MOLE_WIDTH // 2, y + 2 * MOLE_HEIGHT // 3), (15, 8), 0, 0, 180, mouth_color, 2)

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
    global score, combo_hits, lives, power_up_active, power_up_start_time

    if mole["special"] == "normal":
        score += 1
    elif mole["special"] == "golden":
        score += 5
    elif mole["special"] == "bomb":
        lives -= 1
    elif mole["special"] == "power-up":
        power_up_active = True
        power_up_start_time = time.time()

    combo_hits += 1

# Function to update game state
def update_game():
    global moles, combo_hits, max_mole_time, mole_spawn_interval, difficulty_level, max_moles_on_screen, power_up_active

    current_time = time.time()

    # Remove moles that timed out
    moles = [mole for mole in moles if current_time - mole["spawn_time"] < max_mole_time]

    # Gradually increase the number of moles on screen as the game progresses
    elapsed_time = current_time - start_time
    max_moles_on_screen = min(1 + elapsed_time // 10, 5)  # Increment every 10 seconds, up to 5 moles

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

# Function to display instructions on the frame
def display_instructions(frame):
    instructions = [
        "How to Play:",
        "1. Tap on normal moles (brown) for 1 point.",
        "2. Tap on golden moles (yellow) for 5 points!",
        "3. Avoid bomb moles (red); they cost 1 life!",
        "4. Tap on green moles for a power-up (extra time).",
        "5. Game ends when time runs out or lives reach 0.",
    ]
    y_offset = 100
    for instruction in instructions:
        cv2.putText(frame, instruction, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        y_offset += 30

# Main game loop
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame for a mirror effect
    frame = cv2.flip(frame, 1)

    # Convert the frame to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    # Update game state
    update_game()

    # Draw moles
    for mole in moles:
        draw_mole(frame, mole)

    # Detect hand gestures
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            tap_position = detect_tap(hand_landmarks.landmark)

            for mole in moles:
                if is_hit(tap_position, mole):
                    handle_mole_hit(mole)
                    moles.remove(mole)

    # Display score and lives
    cv2.putText(frame, f"Score: {score}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(frame, f"Lives: {lives}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Display time remaining
    elapsed_time = int(time.time() - start_time)
    remaining_time = max(game_duration - elapsed_time, 0)
    cv2.putText(frame, f"Time: {remaining_time}s", (WINDOW_WIDTH - 200, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                (255, 255, 255), 2)

    # Display instructions on the screen
    if elapsed_time < 5:  # Show instructions for the first 5 seconds
        display_instructions(frame)

    # End game if time is up or no lives remain
    if remaining_time == 0 or lives <= 0:
        cv2.putText(frame, "Game Over!", (WINDOW_WIDTH // 4, WINDOW_HEIGHT // 2), cv2.FONT_HERSHEY_SIMPLEX, 2,
                    (0, 0, 255), 3)
        cv2.imshow("Virtual Whack-a-Mole", frame)
        cv2.waitKey(3000)
        break

    # Display the frame
    cv2.imshow("Virtual Whack-a-Mole", frame)

    # Exit the game on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
