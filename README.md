# Whack-A-Mole
Welcome to the Virtual Whack-a-Mole Game! This is an augmented reality-based version of the classic whack-a-mole game where you use your hands to interact with moles that appear on the screen.

## Features
**AR Gameplay:** Use your hands to tap on moles in real-time using your webcam.
**Special Moles:** Different moles appear with various effects:
**Normal Mole (Gray):**  +1 point
**Golden Mole (Yellow):**  +5 points
**Bomb Mole (Red):** -1 life
**Power-Up Mole (Green):** +5 seconds to game time
Multiple Players: Supports 2 players in a turn-based multiplayer mode.
Difficulty Scaling: As the game progresses, the difficulty increases, spawning more moles.
Leaderboard: Tracks scores for each player and displays the top scores.
Instructions: Provides instructions for gameplay when the game starts.

## Requirements
1. Python 3.x
2. OpenCV
3. MediaPipe
4. NumPy
   
## Installation
1. Clone the repository:
2. git clone https://github.com/yourusername/Virtual-Whack-a-Mole.git
3. cd Whack-A-Mole

Install the required packages:

pip install opencv-python mediapipe numpy

## How to Play
Start the Game: Press any key to begin the game.
Tap the Moles: Point your index finger at the mole and tap to hit it.
Watch Out for Bombs: Hitting a bomb will cause you to lose a life.
Power-Up: If you hit a power-up mole, your game time will increase by 5 seconds.
Score and Lives: Earn points by hitting normal or golden moles and avoid bombs. You start with 3 lives.
End of Game: The game ends when your time runs out or you lose all your lives.

## Game Rules
Normal Mole: +1 point
Golden Mole: +5 points
Bomb Mole: -1 life
Power-Up Mole: +5 seconds of game time

## Instructions
Tap with your index finger: Use your finger to tap moles that appear on the screen.
Track your score and lives: The score is updated when you hit a mole, and your remaining lives are shown.
Game Time: The game has a time limit, but hitting power-up moles will increase the game duration.
Leaderboard: After all players take their turns, a leaderboard will be displayed.

## Multiplayer Mode
This game supports 2 players. Each player gets a turn to play, and their score is recorded. After both players finish their turns, the leaderboard is displayed.

## Screenshots

![Screenshot (333)](https://github.com/user-attachments/assets/2998826b-1cff-443f-9a24-18f235462ad7)



## Game End

The game ends when the timer reaches 0 or when a player runs out of lives.
The leaderboard will display the players and their scores.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

OpenCV for computer vision functionality.
MediaPipe for hand tracking.
NumPy for array operations.
