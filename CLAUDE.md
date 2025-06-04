# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

erArk is an R18 adult game focused on Arknights characters, developed in Python. The game is a text-based simulation with character interactions, events, and various gameplay systems.

## Core Development Commands

### Running the Game
```bash
python game.py
```

### Building Game Data
Before running the game, you need to build the configuration data:
```bash
python buildconfig.py  # Build CSV configurations and JSON data
python buildpo.py      # Build localization PO files
python buildmo.py      # Build MO files from PO files
```

### Dependencies Installation
```bash
pip install -r requirements.txt
```

### Testing Individual Components
The game uses a debug mode (configured in config.ini) for testing. Set `debug = 1` to enable debug features.

## High-Level Architecture

### Core Game Flow
1. **Entry Point**: `game.py` - Initializes the game, loads configurations, and starts either GUI or Web mode
2. **Game Initialization**: `Script/Core/game_init.py` - Sets up the game environment, styles, and main flow
3. **Main Frame Loop**: `Script/Design/start_flow.py` - Contains UI handling and panel management
4. **Main Behavior Loop**: `Script/Design/character_behavior.py` - The actual game simulation loop

### Key Systems

#### Configuration System
- **CSV Data**: Game data is stored in CSV files under `data/csv/`
- **Build Process**: `buildconfig.py` reads CSVs and generates:
  - JSON data files (`data/*.json`)
  - Python config definitions (`Script/Config/config_def.py`)
  - Localization PO files (`data/po/`)

#### Character System
- **Character Templates**: Stored in `data/character/` as CSV files
- **Character Management**: `Script/Design/character.py` and `character_handle.py`
- **Character Behaviors**: `Script/Design/character_behavior.py`
- **AI System**: `Script/Design/handle_npc_ai.py` and `handle_npc_ai_in_h.py`

#### Event System
- **Event Data**: JSON files in `data/event/`
- **Event Processing**: `Script/Design/event.py`
- **Talk System**: CSV files in `data/talk/` for character dialogues

#### UI System
- **Flow Management**: `Script/Core/flow_handle.py` (GUI) and `flow_handle_web.py` (Web)
- **Drawing System**: `Script/UI/Moudle/draw.py` with web adapters in `Script/UI/web_draw_adapter.py`
- **Panels**: Various UI panels in `Script/UI/Panel/`

#### Save System
- **Save Management**: `Script/Core/save_handle.py`
- **Cache Control**: `Script/Core/cache_control.py` manages game state

### Web Mode
The game supports a web-based interface:
- Set `web_draw = 1` in `config.ini` to enable
- Web server implementation in `Script/Core/web_server.py`
- Web IO adapter in `Script/Core/io_web.py`

## Code Guidelines

1. **Comments**: All comments should be in Chinese
2. **Function Documentation**: Every function must have Chinese comments describing:
   - Input parameters and types
   - Return values and types
   - Function purpose
3. **Code Sections**: Each code section should have comments explaining its purpose
4. **Code Style**: Use Black formatter with line width 200

## Key Configuration Files

- `config.ini`: Main game configuration
- `data/data.json`: Compiled game data from CSVs
- `data/Character.json`: Character template data
- `data/Character_Talk.json`: Character dialogue data
- `data/Character_Event.json`: Character event data

## Development Workflow

1. Edit CSV files in `data/csv/`, `data/talk/`, or `data/character/`
2. Run `python buildconfig.py` to rebuild game data
3. Run `python game.py` to test changes
4. For localization changes, run `python buildpo.py` and `python buildmo.py`

## Important Notes

- The game is in alpha stage with some features not yet implemented
- The game requires Sarasa Mono SC font for proper display
- Only Windows is officially supported
- Memory requirement: ~1GB peak usage, ensure 2GB free memory

## Main Behavior Loop (`character_behavior.init_character_behavior()`)

This is the core game loop that manages character behaviors and time progression:

### 1. Player Phase
- Player selects an action (instruction) through UI panels
- Action sets behavior ID, duration, and start time on player character
- Loop processes player behavior until completion (`0 not in cache.over_behavior_character`)
- Special handling for time stop mode - time is rolled back after player action

### 2. NPC Phase
- After player action completes, all NPCs in `cache.npc_id_got` are processed
- Each NPC's behavior is calculated based on:
  - Current state (tired, following, in H-mode, unconscious, etc.)
  - AI decision making (`handle_npc_ai.find_character_target()`)
  - Available actions and targets in their location
- NPCs continue their behaviors until all complete

### 3. Time Management
- Time progresses based on behavior durations
- Each character has `behavior.start_time` and `behavior.duration`
- When behavior completes, character enters idle state (`SHARE_BLANKLY`)
- New day triggers at midnight with `past_day_settle.update_new_day()`
- Player sleep triggers auto-save through `sleep_settle.update_save()`

### 4. Behavior Processing (`character_behavior()`)
For each character:
- **Pre-behavior checks**: tired/sleep, movement restrictions, assistant mode, follow mode, H-state
- **Status settlement**: `judge_character_status()` handles events and numerical changes
- **Real-time updates**: `realtime_settle.character_aotu_change_value()` applies time-based changes
- **State persistence**: Updates ongoing states and conditions
- **Completion check**: `judge_character_status_time_over()` determines if behavior is finished
- **Talent acquisition**: Automatic talent gains based on actions

### 5. Settlement System
- **Behavior effects**: `settle_behavior.handle_settle_behavior()` calculates numerical changes
- **Event system**: Events can trigger before or after instructions
- **Change accumulation**: All changes are tracked in `CharacterStatusChange` objects
- **Display to player**: Changes are formatted and shown after player actions
- **Special handling**: Group activities, hidden actions, and complex interactions

### 6. Key Variables
- `cache.over_behavior_character`: Set of characters who completed their current behavior
- `cache.game_time`: Current game time
- `pl_start_time`: Player's behavior start time (reference for NPC timing)
- `cache.time_stop_mode`: Special mode where time doesn't advance

### 7. Loop Exit Conditions
- All characters (player + NPCs) have completed their behaviors
- Time stop mode is active (only player acts, then loop breaks)
- Special events or state changes that interrupt normal flow

## Drawing System - Two Rendering Modes

The game supports two rendering modes: Normal (Tkinter) and Web. The mode is determined by `web_draw` in `config.ini`.

### Normal Drawing Mode (Tkinter)

When `web_draw = 0`, the game uses Tkinter for GUI rendering:

1. **Drawing Classes** (`Script/UI/Moudle/draw.py`):
   - `NormalDraw`: Basic text drawing with width constraints
   - `CenterDraw`: Center-aligned text
   - `RightDraw`: Right-aligned text
   - `Button`: Interactive button elements
   - `FullDraw`: Draw text without truncation
   - `WaitDraw`: Draw text and wait for player input
   - `LineFeedWaitDraw`: Wait on each line break

2. **IO Operations** (`Script/Core/io_init.py`):
   - Uses `main_frame` from Tkinter for display
   - Commands are handled through event queues
   - Direct rendering to Tkinter text widgets

3. **Flow Control** (`Script/Core/flow_handle.py`):
   - `askfor_all()`: Wait for player to select from options
   - `askfor_wait()`: Simple wait for player input
   - Direct event handling through Tkinter bindings

### Web Drawing Mode

When `web_draw = 1`, the game runs as a web server:

1. **Web Drawing Classes** (`Script/UI/web_draw.py`):
   - `WebDrawBase`: Base class for web elements
   - `WebNormalDraw`: Text elements as HTML
   - `WebButton`: Interactive buttons as HTML
   - All drawing objects generate HTML element dictionaries

2. **Drawing Adaptation** (`Script/UI/web_draw_adapter.py`):
   - `WebDrawAdapter`: Converts Tkinter draw objects to web elements
   - Adapts all drawing types (normal, center, right, buttons, etc.)
   - Elements stored in `cache.current_draw_elements`

3. **Web IO Operations** (`Script/Core/io_web.py`):
   - `era_print()`: Converts text to HTML elements
   - `clear_screen()`: Clears element cache and updates web state
   - Commands handled through web API requests
   - No direct rendering, all output buffered as HTML elements

4. **Web Flow Control** (`Script/Core/flow_handle_web.py`):
   - `askfor_all()`: Polls for web API responses
   - Updates game state through `update_game_state()`
   - Asynchronous command handling via HTTP requests

### Key Differences

1. **Output Handling**:
   - Normal: Direct write to Tkinter widgets
   - Web: Buffer HTML elements in `cache.current_draw_elements`

2. **Input Handling**:
   - Normal: Tkinter event bindings and queues
   - Web: HTTP API polling and response handling

3. **State Management**:
   - Normal: Immediate UI updates
   - Web: Batch updates sent to client via `update_game_state()`

4. **Command Processing**:
   - Normal: Synchronous event handling
   - Web: Asynchronous request/response cycle

### Development Considerations

- All UI components should use the abstract drawing classes
- Avoid direct Tkinter or HTML manipulation
- Use `io_init.era_print()` for all text output
- Test both modes when making UI changes
- Web mode requires the web server running on port 5000

## Data Processing Workflow Documentation

The `.github/prompts/数据处理工作流` directory contains important MD files that explain relationships between different systems and code components. When working on related features, refer to these documents for understanding:
- System interconnections and dependencies
- Code component relationships
- Data flow between different modules