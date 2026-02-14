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

## CI/CD Release Structure

The GitHub Actions workflow (`.github/workflows/python-app.yml`) produces 4 release packages:

| Package | Description | Contents |
| ------- | ----------- | -------- |
| `erArk_{version}.zip` | Complete game package | Full game with all resources |
| `erArk_Lite_{version}.zip` | Lightweight game package | Game without large image assets (portraits, scenes, etc.) |
| `erArk_Images_{version}.zip` | Image resource package | All image folders except `image/状态条` |
| `erArkEditor.zip` | Talk/Event editor | Standalone editor tool |

**Image folder distribution:**
- **Included in Images package only**: `image/场景`, `image/断面图`, `image/立绘`
- **Included in both Full & Lite**: `image/状态条`, `image/logo.png` and other root files

**Note:** Lite version + Images package = Full version

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

The `.github/prompts/数据处理工作流` directory contains 47 detailed system documentation files. These documents explain the relationships between different systems and code components. When working on related features, refer to these documents for understanding system interconnections, dependencies, and data flow.

### 🏗️ Core System Architecture Documents
- **[角色行为系统](./github/prompts/数据处理工作流/角色行为系统.md)** - Core behavior loop, time management, status changes
- **[结算系统](./github/prompts/数据处理工作流/结算系统.md)** - Behavior settlement, numerical calculations, status updates
- **[前提系统](./github/prompts/数据处理工作流/前提系统.md)** - Condition verification for behaviors and events
- **[口上系统](./github/prompts/数据处理工作流/口上系统.md)** - Text and dialogue system
- **[事件系统](./github/prompts/数据处理工作流/事件系统.md)** - Story events and special trigger mechanisms

### 🔧 Technical & Tool Systems
- **[CSV数据加载机制说明](./github/prompts/数据处理工作流/CSV数据加载机制说明.md)** - CSV data loading and processing
- **[AI文本生成系统](./github/prompts/数据处理工作流/AI文本生成系统.md)** - AI text generation functionality
- **[存档系统](./github/prompts/数据处理工作流/存档系统.md)** - Save system and cross-version compatibility
- **[通用结算函数函数](./github/prompts/数据处理工作流/通用结算函数函数.md)** - Universal calculation functions
- **[多周目结算与继承系统](./github/prompts/数据处理工作流/多周目结算与继承系统.md)** - Multi-playthrough data inheritance
- **[ArkEditor编辑器系统说明](./github/prompts/数据处理工作流/ArkEditor编辑器系统说明.md)** - Built-in editor system

### 🎮 User Interface Systems
- **[主场景互动界面](./github/prompts/数据处理工作流/主场景互动界面.md)** - Main scene interaction interface
- **[指令面板系统](./github/prompts/数据处理工作流/指令面板系统.md)** - Player instruction panels
- **[通用NPC选择面板](./github/prompts/数据处理工作流/通用NPC选择面板.md)** - Universal NPC selection panels
- **[系统设置系统](./github/prompts/数据处理工作流/系统设置系统.md)** - System configuration interface
- **[全干员位置面板](./github/prompts/数据处理工作流/全干员位置面板.md)** - All character position panel
- **[PRTS系统](./github/prompts/数据处理工作流/PRTS系统.md)** - PRTS communication system

### 🗺️ Scene & Map Systems
- **[地图系统](./github/prompts/数据处理工作流/地图系统.md)** - Map data structure and management
- **[导航系统](./github/prompts/数据处理工作流/导航系统.md)** - Navigation and scene transitions

### 👥 Character Creation & Growth
- **[角色创建流程](./github/prompts/数据处理工作流/角色创建流程.md)** - Character creation workflow
- **[能力升级面板](./github/prompts/数据处理工作流/能力升级面板.md)** - Ability upgrade interface

### 👗 Appearance & Decoration Systems
- **[服装系统说明](./github/prompts/数据处理工作流/服装系统说明.md)** - Clothing system details
- **[衣柜检查功能](./github/prompts/数据处理工作流/衣柜检查功能.md)** - Wardrobe inspection features
- **[收藏品系统](./github/prompts/数据处理工作流/收藏品系统.md)** - Collectible management
- **[角色图片系统](./github/prompts/数据处理工作流/角色图片系统.md)** - Character image resources

### 👨‍⚕️ Body Status Systems
- **[身体信息面板系统](./github/prompts/数据处理工作流/身体信息面板系统.md)** - Body information display
- **[射精面板系统](./github/prompts/数据处理工作流/射精面板系统.md)** - Ejaculation status panels
- **[妊娠系统](./github/prompts/数据处理工作流/妊娠系统.md)** - Pregnancy state management

### 🎯 Rhodes Island Department Systems
- **[管理罗德岛系统](./github/prompts/数据处理工作流/管理罗德岛系统.md)** - Rhodes Island base management
- **[助理系统](./github/prompts/数据处理工作流/助理系统.md)** - Assistant character functions
- **[基建系统](./github/prompts/数据处理工作流/基建系统.md)** - Construction and building management
- **[农业生产系统](./github/prompts/数据处理工作流/农业生产系统.md)** - Agricultural production
- **[工业生产系统](./github/prompts/数据处理工作流/工业生产系统.md)** - Industrial production
- **[资源交易系统](./github/prompts/数据处理工作流/资源交易系统.md)** - Resource trading and markets
- **[招募系统](./github/prompts/数据处理工作流/招募系统.md)** - Character recruitment mechanisms
- **[外勤委托系统](./github/prompts/数据处理工作流/外勤委托系统.md)** - External mission commissioning
- **[邀请访客系统](./github/prompts/数据处理工作流/邀请访客系统.md)** - Visitor invitation system
- **[势力外交系统](./github/prompts/数据处理工作流/势力外交系统.md)** - Faction diplomacy
- **[载具管理系统](./github/prompts/数据处理工作流/载具管理系统.md)** - Vehicle management
- **[读书系统](./github/prompts/数据处理工作流/读书系统.md)** - Reading and learning functionality
- **[身体检查与管理系统](./github/prompts/数据处理工作流/身体检查与管理系统.md)** - Body examination and health management

### 🛍️ Items & Equipment Systems
- **[道具背包系统](./github/prompts/数据处理工作流/道具背包系统.md)** - Item inventory management
- **[礼物系统](./github/prompts/数据处理工作流/礼物系统.md)** - Gift giving and receiving
- **[食物系统](./github/prompts/数据处理工作流/食物系统.md)** - Food preparation and consumption

### 🌟 Originium Arts Systems
- **[源石技艺系统](./github/prompts/数据处理工作流/源石技艺系统.md)** - Originium arts learning and management
- **[时间停止系统](./github/prompts/数据处理工作流/时间停止系统.md)** - Time stop special functionality
- **[催眠系统](./github/prompts/数据处理工作流/催眠系统.md)** - Hypnosis functionality and mechanisms

### 🎭 Special H-Mode Systems
- **[群交系统](./github/prompts/数据处理工作流/群交系统.md)** - Group interaction functionality
- **[监禁调教系统](./github/prompts/数据处理工作流/监禁调教系统.md)** - Confinement and training
- **[睡眠系统](./github/prompts/数据处理工作流/睡眠系统.md)** - Sleep state management
- **[隐奸系统](./github/prompts/数据处理工作流/隐奸系统.md)** - Hidden behavior system

### Usage Guidelines
1. **Browse by Category**: Select the appropriate category based on the system type you're working on
2. **System Dependencies**: Many systems are interconnected - refer to related system documentation
3. **Document Structure**: Each document typically contains system overview, core components, data structures, workflow explanations, configuration details, technical implementation, and extension guides