# Arcade Game Collection

A collection of unique arcade-style games built with Pygame, featuring different gameplay mechanics and visual styles.

## Table of Contents
- [Overview](#overview)
- [Game Theory](#game-theory)
- [Games Included](#games-included)
  - [Gravity Flip](#gravity-flip)
  - [Color Match](#color-match)
  - [Echo Maze](#echo-maze)
  - [Time Loop](#time-loop)
- [Installation](#installation)
- [How to Play](#how-to-play)
- [Controls](#controls)
- [Settings](#settings)
- [Technical Details](#technical-details)
- [Credits](#credits)

## Overview

This project is a collection of arcade-style games with a unified launcher interface. Each game offers unique gameplay mechanics, visual styles, and challenges. The launcher provides a seamless way to navigate between games, adjust settings, and track high scores.

## Game Theory

The collection is designed around several core game design principles:

1. **Accessibility**: Simple controls that are easy to learn but offer depth
2. **Escalating Challenge**: Difficulty that increases as players progress
3. **Immediate Feedback**: Visual and audio cues provide instant feedback on player actions
4. **Varied Mechanics**: Each game explores different gameplay concepts
5. **Replayability**: Procedural generation and scoring systems encourage multiple playthroughs

## Games Included

### Gravity Flip

**Concept**: Navigate through obstacles by flipping gravity.

**Theory**: Gravity Flip explores spatial reasoning and timing by allowing players to invert gravity at will. This creates a unique movement system where players must plan their trajectory while accounting for momentum and the environment.

**Gameplay**: 
- Control a character that can flip gravity up or down
- Navigate through procedurally generated obstacles
- Collect points while avoiding hazards
- Difficulty increases with speed over time

### Color Match

**Concept**: Match your projectile color to targets for maximum points.

**Theory**: Color Match tests reaction time and pattern recognition. Players must quickly identify colors and make split-second decisions about which targets to prioritize.

**Gameplay**:
- Shoot colored projectiles at matching colored targets
- Switch between different colored ammunition
- Matching colors scores points, mismatches lose points
- Special targets provide power-ups and multipliers

### Echo Maze

**Concept**: Navigate a dark maze using sound echoes to reveal the environment.

**Theory**: Echo Maze explores spatial awareness and memory by limiting visual information. Players must use sound echoes to temporarily reveal the environment and remember the layout to navigate effectively.

**Gameplay**:
- Move through a maze that's mostly hidden in darkness
- Use limited "echo" abilities to reveal surroundings temporarily
- Collect keys to unlock doors and find treasures
- Manage echo resources while avoiding getting lost

### Time Loop

**Concept**: Create time loops of yourself to solve puzzles and defeat enemies.

**Theory**: Time Loop explores cause and effect through temporal mechanics. Players create copies of their past actions that repeat in loops, requiring planning and coordination between present and past selves.

**Gameplay**:
- Record your movements and actions to create time loops
- Your past selves repeat recorded actions
- Coordinate with multiple time loops to solve puzzles
- Defend against waves of enemies using strategic positioning

## Installation

### Requirements
- Python 3.7+
- Pygame 2.0.0+
- NumPy 1.19.0+

### Steps

1. Clone the repository:
```
git clone https://github.com/yourusername/arcade-game-collection.git
cd arcade-game-collection
```

2. Create and activate a virtual environment (optional but recommended):
```
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Run the game:
```
python main_menu.py
```

## How to Play

1. Launch the game by running `main_menu.py`
2. Use the main menu to select a game
3. Each game has its own tutorial screen that explains the specific controls and objectives
4. Press ESC at any time to return to the main menu
5. Access settings to adjust audio, display, and control options

## Controls

### Main Menu
- **Mouse**: Navigate and select options
- **ESC**: Exit game

### Gravity Flip
- **Space**: Flip gravity
- **Left/Right Arrow Keys**: Move left/right
- **ESC**: Return to main menu

### Color Match
- **Left/Right Arrow Keys**: Aim
- **Space**: Shoot
- **1-4 Number Keys**: Switch ammunition color
- **ESC**: Return to main menu

### Echo Maze
- **Arrow Keys**: Move character
- **Space**: Send echo pulse
- **E**: Use special ability
- **ESC**: Return to main menu

### Time Loop
- **Arrow Keys**: Move character
- **Space**: Record/stop recording time loop
- **R**: Reset all time loops
- **1-3 Number Keys**: Select time loop slot
- **ESC**: Return to main menu

## Settings

The game includes customizable settings:

- **Audio**: Adjust music and sound effect volume
- **Display**: Toggle fullscreen, adjust resolution
- **Controls**: Customize key bindings
- **Accessibility**: Toggle visual effects, color blind mode

## Technical Details

### Architecture
The game is built using a modular architecture with the following components:

- **Main Menu**: Central hub for game selection and settings
- **Game Modules**: Individual games as separate Python modules
- **Utility Classes**: Shared functionality for UI, audio, and game mechanics
- **Asset Management**: Centralized system for loading and managing game assets

### Technologies Used
- **Pygame**: Core game engine and rendering
- **NumPy**: Mathematical operations and array handling
- **Python Standard Library**: File I/O, randomization, and system integration

## Credits

- **Programming**: [Your Name]
- **Game Design**: [Your Name]
- **Graphics**: Created using Pygame primitives
- **Sound Effects**: [Source of sound effects]
- **Music**: [Source of music]

## License

[Include your license information here]
