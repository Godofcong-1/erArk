/**
 * 新UI组件模块
 * 包含玩家信息面板、对话框、附加信息面板等组件
 */

function renderNewUIContent(container, gameState) {
    // 清空容器
    container.innerHTML = '';
    
    // 创建新UI布局
    const layout = document.createElement('div');
    layout.className = 'new-ui-layout';
    
    // ========== 顶部信息区 ==========
    const topInfoArea = document.createElement('div');
    topInfoArea.className = 'new-ui-top-info';
    
    // 玩家信息区
    if (gameState.player_info) {
        const playerInfo = createPlayerInfoPanel(gameState.player_info);
        topInfoArea.appendChild(playerInfo);
    }
    
    // 交互对象附加信息区
    // 只有存在交互对象（target_extra_info 不是空对象）时才创建
    if (gameState.target_extra_info && Object.keys(gameState.target_extra_info).length > 0) {
        const targetExtraInfo = createTargetExtraInfoPanel(gameState.target_extra_info);
        topInfoArea.appendChild(targetExtraInfo);
    }
    
    // 场景角色头像区（包括小对话框）
    if (gameState.scene_characters && gameState.scene_characters.length > 0) {
        // 获取小对话框数据（如果存在）
        const minorDialogs = gameState.dialog && gameState.dialog.minor_dialogs ? gameState.dialog.minor_dialogs : [];
        const avatarArea = createAvatarPanel(gameState.scene_characters, minorDialogs);
        topInfoArea.appendChild(avatarArea);
    }
    
    layout.appendChild(topInfoArea);
    
    // ========== 主画面区 ==========
    const mainScene = document.createElement('div');
    mainScene.className = 'new-ui-main-scene';
    
    // 场景背景
    if (gameState.scene && gameState.scene.background_image) {
        mainScene.style.backgroundImage = `url('${gameState.scene.background_image}')`;
        mainScene.style.backgroundSize = 'cover';
        mainScene.style.backgroundPosition = 'center';
    }
    
    // 交互类型栏（左侧）
    if (gameState.interaction_types) {
        // 支持新版嵌套结构（对象）和旧版数组格式
        const hasData = Array.isArray(gameState.interaction_types) 
            ? gameState.interaction_types.length > 0 
            : (gameState.interaction_types.major_types && gameState.interaction_types.major_types.length > 0);
        
        if (hasData) {
            const interactionPanel = createInteractionTypePanel(gameState.interaction_types);
            mainScene.appendChild(interactionPanel);
        }
    }
    
    // 无部位指令浮现按钮容器（交互面板右侧，角色立绘左侧）
    const floatingButtonsContainer = document.createElement('div');
    floatingButtonsContainer.className = 'interaction-floating-buttons';
    floatingButtonsContainer.id = 'floating-instruct-buttons';
    mainScene.appendChild(floatingButtonsContainer);
    
    // 角色立绘区（中央）
    // 检查是否有交互对象（target_info 不是空对象且有 image_data）
    const hasTargetCharacter = gameState.target_info && Object.keys(gameState.target_info).length > 0;
    // 存储到全局变量，供其他函数使用
    window.hasTargetCharacter = hasTargetCharacter;
    if (hasTargetCharacter && gameState.target_info.image_data && Object.keys(gameState.target_info.image_data).length > 0) {
        const showAllBodyParts = gameState.extra_info ? gameState.extra_info.show_all_body_parts : false;
        const characterDisplay = createCharacterDisplay(gameState.target_info, showAllBodyParts);
        mainScene.appendChild(characterDisplay);
    }
    
    // 交互对象信息区（右侧）
    // 只有存在交互对象（target_info 不是空对象）时才创建
    if (hasTargetCharacter) {
        const targetInfoPanel = createTargetInfoPanel(gameState.target_info);
        mainScene.appendChild(targetInfoPanel);
    }
    
    // 添加主场景空白区域点击事件（清空交互选择）
    mainScene.addEventListener('click', handleMainSceneClick);
    
    layout.appendChild(mainScene);
    
    // ========== 对话框区域（底部） ==========
    // 始终创建对话框元素，但根据状态决定是否可见
    const dialogData = gameState.dialog || { visible: false, speaker: '', text: '', text_color: 'standard' };
    const dialogBox = createDialogBox(dialogData);
    layout.appendChild(dialogBox);
    
    container.appendChild(layout);
    
    // ========== 顶部面板选项卡（添加到container顶部） ==========
    if (gameState.panel_tabs && gameState.panel_tabs.length > 0) {
        const panelTabs = createPanelTabsBar(gameState.panel_tabs);
        // 插入到container的最前面
        container.insertBefore(panelTabs, container.firstChild);
    }
    
    // ========== 顶部场景信息栏（添加到面板选项卡上面） ==========
    if (gameState.scene_info_bar) {
        const sceneInfoBar = createSceneInfoBar(gameState.scene_info_bar);
        // 插入到container的最前面（在面板选项卡之前）
        container.insertBefore(sceneInfoBar, container.firstChild);
    }
}

/**
 * 创建玩家信息面板
 */
function createPlayerInfoPanel(playerInfo) {
    const panel = document.createElement('div');
    panel.className = 'new-ui-player-info';
    
    // 第一行：玩家名字按钮 + 昵称
    const nameLine = document.createElement('div');
    nameLine.className = 'player-name-line';
    
    // 玩家名字作为可点击按钮，点击后执行"与自己交互"指令
    const nameBtn = document.createElement('button');
    nameBtn.className = 'player-name-btn';
    nameBtn.textContent = playerInfo.name || '';
    nameBtn.title = '点击与自己交互';
    nameBtn.onclick = () => {
        console.log('[DEBUG] Player name button clicked, executing target_to_self');
        if (window.socket && window.socket.connected) {
            window.socket.emit('execute_instruct', { instruct_id: 'target_to_self' });
        } else {
            console.warn('[DEBUG] Socket not connected, cannot execute target_to_self');
        }
    };
    nameLine.appendChild(nameBtn);
    
    if (playerInfo.nickname) {
        const nicknameSpan = document.createElement('span');
        nicknameSpan.className = 'player-nickname';
        nicknameSpan.textContent = playerInfo.nickname;
        nameLine.appendChild(nicknameSpan);
    }
    panel.appendChild(nameLine);
    
    // 第二行：状态条（使用图片）
    const bars = document.createElement('div');
    bars.className = 'player-bars';
    
    // HP条（使用图片）
    bars.appendChild(createImageStatusBar('体力', playerInfo.hp, playerInfo.hp_max, 'hp'));
    // MP条（使用图片）
    bars.appendChild(createImageStatusBar('气力', playerInfo.mp, playerInfo.mp_max, 'mp'));
    // 理智条（使用图片，带加号按钮）
    if (playerInfo.sanity !== undefined) {
        bars.appendChild(createImageStatusBarWithButton('理智', playerInfo.sanity, playerInfo.sanity_max, 'sanity', playerInfo.has_sanity_drug));
    }
    // 精液条（使用图片，带加号按钮）
    if (playerInfo.semen !== undefined) {
        bars.appendChild(createImageStatusBarWithButton('精液', playerInfo.semen, playerInfo.semen_max, 'semen', playerInfo.has_semen_drug));
    }
    
    panel.appendChild(bars);
    
    // 第三行：特殊状态标记（移至精液槽下面）
    if (playerInfo.special_states && playerInfo.special_states.length > 0) {
        const statesRow = document.createElement('div');
        statesRow.className = 'player-special-states-row';
        
        playerInfo.special_states.forEach(state => {
            if (state.text) {
                const stateSpan = document.createElement('span');
                stateSpan.className = `special-state style-${state.style || 'standard'}`;
                stateSpan.textContent = state.text;
                if (state.tooltip) {
                    stateSpan.title = state.tooltip;
                }
                statesRow.appendChild(stateSpan);
            }
        });
        
        panel.appendChild(statesRow);
    }
    
    // ========== 从后端传来的数值变化浮动文本 ==========
    if (playerInfo.value_changes && playerInfo.value_changes.length > 0) {
        // 延迟创建浮动文本，确保DOM已渲染
        setTimeout(() => {
            createPlayerFloatingValueChanges(panel, playerInfo.value_changes);
        }, 50);
    }
    
    return panel;
}

/**
 * 创建状态条（旧版本，暂时保留用于兼容）
 */
function createStatusBar(label, value, maxValue, type) {
    const bar = document.createElement('div');
    bar.className = `status-bar status-bar-${type}`;
    
    const percentage = maxValue > 0 ? (value / maxValue * 100) : 0;
    
    bar.innerHTML = `
        <span class="bar-label">${label}</span>
        <div class="bar-track">
            <div class="bar-fill" style="width: ${percentage}%"></div>
        </div>
        <span class="bar-value">${value}/${maxValue}</span>
    `;
    
    return bar;
}

/**
 * 创建使用图片的状态条
 * 参考右侧角色信息区的实现
 */
function createImageStatusBar(label, value, maxValue, type) {
    const bar = document.createElement('div');
    bar.className = `status-bar status-bar-${type}`;
    
    // 添加字段标识，用于浮动文本定位
    const fieldMap = {
        'hp': 'hit_point',
        'mp': 'mana_point',
        'sanity': 'sanity_point',
        'semen': 'semen_point'
    };
    if (fieldMap[type]) {
        bar.dataset.field = fieldMap[type];
    }
    
    const percentage = maxValue > 0 ? (value / maxValue * 100) : 0;
    
    // 创建标签
    const labelSpan = document.createElement('span');
    labelSpan.className = 'bar-label';
    labelSpan.textContent = label;
    
    // 创建条形容器（使用图片背景）
    const track = document.createElement('div');
    track.className = 'bar-track';
    
    // 创建填充部分（使用图片背景）
    const fill = document.createElement('div');
    fill.className = 'bar-fill';
    fill.style.width = `${percentage}%`;
    
    track.appendChild(fill);
    
    // 创建数值显示
    const valueSpan = document.createElement('span');
    valueSpan.className = 'bar-value';
    valueSpan.textContent = `${value}/${maxValue}`;
    
    bar.appendChild(labelSpan);
    bar.appendChild(track);
    bar.appendChild(valueSpan);
    
    return bar;
}

/**
 * 创建带快捷按钮的状态条（用于理智和精液）
 * @param {string} label - 标签文本
 * @param {number} value - 当前值
 * @param {number} maxValue - 最大值
 * @param {string} type - 类型（sanity 或 semen）
 * @param {boolean} hasDrug - 是否有对应的药剂
 * @returns {HTMLElement}
 */
function createImageStatusBarWithButton(label, value, maxValue, type, hasDrug) {
    const bar = document.createElement('div');
    bar.className = `status-bar status-bar-${type}`;
    
    // 添加字段标识，用于浮动文本定位
    const fieldMap = {
        'hp': 'hit_point',
        'mp': 'mana_point',
        'sanity': 'sanity_point',
        'semen': 'semen_point'
    };
    if (fieldMap[type]) {
        bar.dataset.field = fieldMap[type];
    }
    
    const percentage = maxValue > 0 ? (value / maxValue * 100) : 0;
    
    // 创建标签容器（包含标签和按钮）
    const labelContainer = document.createElement('span');
    labelContainer.className = 'bar-label-container';
    
    const labelSpan = document.createElement('span');
    labelSpan.className = 'bar-label';
    labelSpan.textContent = label;
    labelContainer.appendChild(labelSpan);
    
    // 如果有药剂，添加加号按钮
    if (hasDrug) {
        const plusBtn = document.createElement('button');
        plusBtn.className = `bar-quick-use-btn bar-quick-use-${type}`;
        plusBtn.textContent = '✚';
        plusBtn.title = type === 'sanity' ? '快速使用理智药' : '快速使用精力剂';
        plusBtn.onclick = (e) => {
            e.stopPropagation();
            handleQuickUseDrug(type);
        };
        labelContainer.appendChild(plusBtn);
    }
    
    // 创建条形容器
    const track = document.createElement('div');
    track.className = 'bar-track';
    
    // 创建填充部分
    const fill = document.createElement('div');
    fill.className = 'bar-fill';
    fill.style.width = `${percentage}%`;
    
    track.appendChild(fill);
    
    // 创建数值显示
    const valueSpan = document.createElement('span');
    valueSpan.className = 'bar-value';
    valueSpan.textContent = `${value}/${maxValue}`;
    
    bar.appendChild(labelContainer);
    bar.appendChild(track);
    bar.appendChild(valueSpan);
    
    return bar;
}

/**
 * 处理快速使用药剂
 * @param {string} type - 药剂类型（sanity 或 semen）
 */
/**
 * 处理快速使用药剂
 * @param {string} type - 药剂类型（sanity 或 semen）
 */
function handleQuickUseDrug(type) {
    console.log(`[快速使用药剂] 类型: ${type}`);
    
    fetch('/api/quick_use_drug', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ drug_type: type })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log(`[快速使用药剂] 成功: ${data.message}`);
            // 如果后端返回了更新后的玩家信息，更新UI
            if (data.player_info) {
                updatePlayerInfoUI(data.player_info);
            }
        } else {
            console.error(`[快速使用药剂] 失败: ${data.message}`);
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('[快速使用药剂] 错误:', error);
    });
}

/**
 * 更新玩家信息区UI
 * @param {Object} playerInfo - 更新后的玩家信息（包含 value_changes）
 */
function updatePlayerInfoUI(playerInfo) {
    console.log('[更新玩家信息UI]', playerInfo);
    
    // 查找玩家信息面板
    const playerInfoPanel = document.querySelector('.new-ui-player-info');
    if (!playerInfoPanel) {
        console.error('[更新玩家信息UI] 未找到玩家信息面板');
        return;
    }
    
    // 重新创建玩家信息面板（createPlayerInfoPanel 内部已经处理了 value_changes 的浮动文本）
    const newPanel = createPlayerInfoPanel(playerInfo);
    
    // 替换旧面板
    playerInfoPanel.parentNode.replaceChild(newPanel, playerInfoPanel);
    
    console.log('[更新玩家信息UI] 更新完成');
}

/**
 * 计算玩家数值变化
 * @param {HTMLElement} oldPanel - 旧的玩家信息面板
 * @param {Object} newPlayerInfo - 新的玩家信息
 * @returns {Array} 数值变化数组
 */
function calculatePlayerValueChanges(oldPanel, newPlayerInfo) {
    const changes = [];
    
    // 定义需要检测的字段
    const fields = [
        { key: 'hp', field: 'hit_point', name: '体力', color: 'hp_point' },
        { key: 'mp', field: 'mana_point', name: '气力', color: 'mp_point' },
        { key: 'sanity', field: 'sanity_point', name: '理智', color: 'sanity' },
        { key: 'semen', field: 'semen_point', name: '精液', color: 'semen' }
    ];
    
    fields.forEach(fieldDef => {
        const oldBar = oldPanel.querySelector(`[data-field="${fieldDef.field}"]`);
        if (!oldBar) return;
        
        // 从状态条的数值显示中提取当前值
        const valueSpan = oldBar.querySelector('.bar-value');
        if (!valueSpan) return;
        
        const valueText = valueSpan.textContent; // 格式: "50/100"
        const oldValue = parseInt(valueText.split('/')[0]);
        const newValue = newPlayerInfo[fieldDef.key];
        
        if (!isNaN(oldValue) && newValue !== undefined) {
            const diff = newValue - oldValue;
            if (diff !== 0) {
                changes.push({
                    field: fieldDef.field,
                    field_name: fieldDef.name,
                    value: diff,
                    color: fieldDef.color
                });
            }
        }
    });
    
    return changes;
}

/**
 * 创建对话框区域
 * 用于显示角色的台词描述文本
 * @param {Object} dialogData - 对话框数据
 * @returns {HTMLElement} - 对话框元素
 */
function createDialogBox(dialogData) {
    const dialogBox = document.createElement('div');
    dialogBox.className = 'new-ui-dialog-box';
    dialogBox.id = 'game-dialog-box';
    
    // 如果对话框可见，添加visible类
    if (dialogData.visible) {
        dialogBox.classList.add('visible');
    }
    
    // 说话者名称区域
    const speakerContainer = document.createElement('div');
    speakerContainer.className = 'dialog-speaker-container';
    
    const speakerName = document.createElement('span');
    speakerName.className = 'dialog-speaker-name';
    speakerName.textContent = dialogData.speaker || '';
    speakerContainer.appendChild(speakerName);
    
    dialogBox.appendChild(speakerContainer);
    
    // 对话文本区域
    const textContainer = document.createElement('div');
    textContainer.className = 'dialog-text-container';
    textContainer.id = 'dialog-text';
    
    // 设置文本颜色样式
    const textColor = dialogData.text_color || 'standard';
    textContainer.classList.add(`style-${textColor}`);
    
    // 设置对话文本 - 使用innerText正确处理换行符
    let displayText = dialogData.text || '';
    displayText = displayText.replace(/\\n/g, '\n');
    textContainer.innerText = displayText;
    
    dialogBox.appendChild(textContainer);
    
    // 底部提示（仅在等待输入时显示）
    if (dialogData.wait_input) {
        const hintContainer = document.createElement('div');
        hintContainer.className = 'dialog-hint';
        hintContainer.innerHTML = `<span class="dialog-hint-icon">▼</span> 点击任意位置继续`;
        if (dialogData.has_more) {
            hintContainer.innerHTML += ' (还有更多...)';
        }
        dialogBox.appendChild(hintContainer);
    }
    
    // 添加点击事件处理（推进对话）
    dialogBox.addEventListener('click', handleDialogClick);
    
    return dialogBox;
}

/**
 * 处理对话框点击事件
 * 点击后推进对话
 */
function handleDialogClick(event) {
    event.stopPropagation();  // 阻止事件冒泡
    
    console.log('[Dialog] 点击对话框，推进对话');
    
    // 发送对话推进请求到后端
    advanceDialog();
}

/**
 * 发送对话推进请求到后端
 */
function advanceDialog() {
    if (window.socket && window.socket.connected) {
        window.socket.emit('advance_dialog', {});
    } else {
        console.warn('Socket未连接，无法推进对话');
    }
}

/**
 * 跳过所有对话
 */
function skipAllDialogs() {
    if (window.socket && window.socket.connected) {
        window.socket.emit('skip_all_dialogs', {});
    }
}

/**
 * 更新对话框状态
 * @param {Object} dialogData - 新的对话框数据
 */
function updateDialogBox(dialogData) {
    const dialogBox = document.getElementById('game-dialog-box');
    if (!dialogBox) {
        console.warn('未找到对话框元素');
        return;
    }
    
    // 更新可见状态
    if (dialogData.visible) {
        dialogBox.classList.add('visible');
        dialogBox.classList.remove('hidden');
    } else {
        dialogBox.classList.remove('visible');
        dialogBox.classList.add('hidden');
        return;  // 隐藏时不需要更新其他内容
    }
    
    // 更新说话者名称
    const speakerName = dialogBox.querySelector('.dialog-speaker-name');
    if (speakerName) {
        speakerName.textContent = dialogData.speaker || '';
    }
    
    // 更新对话文本
    const textContainer = dialogBox.querySelector('.dialog-text-container');
    if (textContainer) {
        // 清除旧的样式类
        textContainer.className = 'dialog-text-container';
        // 添加新的颜色样式
        const textColor = dialogData.text_color || 'standard';
        textContainer.classList.add(`style-${textColor}`);
        // 更新文本 - 使用innerText正确处理换行符
        // 如果后端发送的是转义的\\n，需要转换为实际换行
        let displayText = dialogData.text || '';
        displayText = displayText.replace(/\\n/g, '\n');
        textContainer.innerText = displayText;
    }
    
    // 更新提示信息
    let hintContainer = dialogBox.querySelector('.dialog-hint');
    if (dialogData.wait_input) {
        if (!hintContainer) {
            hintContainer = document.createElement('div');
            hintContainer.className = 'dialog-hint';
            dialogBox.appendChild(hintContainer);
        }
        hintContainer.innerHTML = `<span class="dialog-hint-icon">▼</span> 点击任意位置继续`;
        if (dialogData.has_more) {
            hintContainer.innerHTML += ' (还有更多...)';
        }
    } else if (hintContainer) {
        hintContainer.remove();
    }
    
    // 更新其他角色的小对话框
    if (dialogData.minor_dialogs && dialogData.minor_dialogs.length > 0) {
        updateMinorDialogs(dialogData.minor_dialogs);
    }
}

/**
 * 初始化对话框键盘快捷键
 * Ctrl/右键快速跳过对话
 */
function initDialogKeyboardShortcuts() {
    // 跟踪Ctrl键和右键的按下状态
    let ctrlPressed = false;
    let rightMousePressed = false;
    let skipInterval = null;
    
    // 开始快速跳过
    function startSkipping() {
        if (skipInterval) return;  // 已经在跳过中
        
        const dialogBox = document.getElementById('game-dialog-box');
        if (!dialogBox || !dialogBox.classList.contains('visible')) return;
        
        // 添加跳过模式样式
        dialogBox.classList.add('skipping');
        
        // 每100ms推进一次对话
        skipInterval = setInterval(() => {
            advanceDialog();
        }, 100);
    }
    
    // 停止快速跳过
    function stopSkipping() {
        if (skipInterval) {
            clearInterval(skipInterval);
            skipInterval = null;
        }
        
        const dialogBox = document.getElementById('game-dialog-box');
        if (dialogBox) {
            dialogBox.classList.remove('skipping');
        }
    }
    
    // 监听键盘事件
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Control' && !ctrlPressed) {
            ctrlPressed = true;
            startSkipping();
        }
        // 空格键或回车键推进对话
        if ((event.key === ' ' || event.key === 'Enter') && !event.repeat) {
            const dialogBox = document.getElementById('game-dialog-box');
            if (dialogBox && dialogBox.classList.contains('visible')) {
                event.preventDefault();
                advanceDialog();
            }
        }
    });
    
    document.addEventListener('keyup', (event) => {
        if (event.key === 'Control') {
            ctrlPressed = false;
            if (!rightMousePressed) {
                stopSkipping();
            }
        }
    });
    
    // 监听右键事件（用于对话框区域）
    document.addEventListener('mousedown', (event) => {
        if (event.button === 2) {  // 右键
            rightMousePressed = true;
            const dialogBox = document.getElementById('game-dialog-box');
            if (dialogBox && dialogBox.classList.contains('visible')) {
                event.preventDefault();
                startSkipping();
            }
        }
    });
    
    document.addEventListener('mouseup', (event) => {
        if (event.button === 2) {  // 右键
            rightMousePressed = false;
            if (!ctrlPressed) {
                stopSkipping();
            }
        }
    });
}

/**
 * 创建交互对象附加信息面板
 * 包含服装栏、身体栏、群交栏、隐奸栏
 * @param {Object} extraInfo - 附加信息数据
 */
function createTargetExtraInfoPanel(extraInfo) {
    const panel = document.createElement('div');
    panel.className = 'new-ui-target-extra-info';
    panel.id = 'target-extra-info-panel';
    
    // 如果没有数据，显示占位符
    if (!extraInfo || (!extraInfo.clothing?.visible && !extraInfo.body?.visible && 
        !extraInfo.group_sex?.visible && !extraInfo.hidden_sex?.visible)) {
        panel.innerHTML = '<div class="extra-info-placeholder">[交互对象附加信息]</div>';
        return panel;
    }
    
    const container = document.createElement('div');
    container.className = 'extra-info-container';
    
    // 顶部按钮栏
    const buttonBar = document.createElement('div');
    buttonBar.className = 'extra-info-button-bar';
    
    // 创建左侧栏位按钮容器
    const leftButtons = document.createElement('div');
    leftButtons.style.display = 'flex';
    leftButtons.style.gap = '4px';
    leftButtons.style.flexWrap = 'wrap';
    
    // 创建各栏位按钮
    const sections = [
        { key: 'clothing', name: '服装', visible: extraInfo.clothing?.visible },
        { key: 'body', name: '身体', visible: extraInfo.body?.visible },
        { key: 'group_sex', name: '群交', visible: extraInfo.group_sex?.visible },
        { key: 'hidden_sex', name: '隐奸', visible: extraInfo.hidden_sex?.visible }
    ];
    
    sections.forEach(section => {
        if (section.visible) {
            const btn = document.createElement('button');
            btn.className = 'extra-info-tab-btn';
            btn.dataset.section = section.key;
            btn.textContent = section.name;
            if (extraInfo[section.key]?.expanded) {
                btn.classList.add('active');
            }
            btn.onclick = () => toggleExtraInfoSection(section.key);
            leftButtons.appendChild(btn);
        }
    });
    
    buttonBar.appendChild(leftButtons);
    
    // 创建右侧切换按钮容器
    const rightButtons = document.createElement('div');
    rightButtons.style.display = 'flex';
    rightButtons.style.gap = '4px';
    rightButtons.style.flexWrap = 'wrap';
    
    // 全部位显示切换按钮
    const bodyPartsToggle = document.createElement('button');
    bodyPartsToggle.className = 'extra-info-toggle-btn';
    bodyPartsToggle.id = 'toggle-all-body-parts';
    bodyPartsToggle.textContent = extraInfo.show_all_body_parts ? '收起全部位显示' : '展开全部位显示';
    bodyPartsToggle.onclick = () => toggleAllBodyParts();
    rightButtons.appendChild(bodyPartsToggle);
    
    // 详细污浊切换按钮
    const dirtyToggle = document.createElement('button');
    dirtyToggle.className = 'extra-info-toggle-btn';
    dirtyToggle.id = 'toggle-detailed-dirty';
    dirtyToggle.textContent = extraInfo.show_detailed_dirty ? '收起详细污浊' : '展开详细污浊';
    dirtyToggle.onclick = () => toggleDetailedDirty();
    rightButtons.appendChild(dirtyToggle);
    
    buttonBar.appendChild(rightButtons);
    
    container.appendChild(buttonBar);
    
    // 内容区域
    const contentArea = document.createElement('div');
    contentArea.className = 'extra-info-content';
    
    // 服装栏
    if (extraInfo.clothing?.visible && extraInfo.clothing?.expanded) {
        const clothingSection = createClothingSection(extraInfo.clothing.data, extraInfo.is_h_mode);
        contentArea.appendChild(clothingSection);
    }
    
    // 身体栏
    if (extraInfo.body?.visible && extraInfo.body?.expanded) {
        const bodySection = createBodySection(extraInfo.body.data);
        contentArea.appendChild(bodySection);
    }
    
    // 群交栏
    if (extraInfo.group_sex?.visible && extraInfo.group_sex?.expanded) {
        const groupSexSection = createGroupSexSection(extraInfo.group_sex.data);
        contentArea.appendChild(groupSexSection);
    }
    
    // 隐奸栏
    if (extraInfo.hidden_sex?.visible && extraInfo.hidden_sex?.expanded) {
        const hiddenSexSection = createHiddenSexSection(extraInfo.hidden_sex.data);
        contentArea.appendChild(hiddenSexSection);
    }
    
    container.appendChild(contentArea);
    panel.appendChild(container);
    return panel;
}

/**
 * 创建服装栏内容
 */
function createClothingSection(clothingData, isHMode) {
    const section = document.createElement('div');
    section.className = 'extra-info-section clothing-section';
    section.dataset.section = 'clothing';
    
    const title = document.createElement('div');
    title.className = 'section-title';
    title.textContent = '服装：';
    section.appendChild(title);
    
    if (!clothingData || !clothingData.items) {
        const empty = document.createElement('div');
        empty.className = 'section-empty';
        empty.textContent = '无数据';
        section.appendChild(empty);
        return section;
    }
    
    // 全裸检测
    if (clothingData.naked) {
        const nakedText = document.createElement('div');
        nakedText.className = 'clothing-naked';
        nakedText.textContent = '全裸';
        section.appendChild(nakedText);
        return section;
    }
    
    // 按衣服类型分组显示
    const typeGroups = {};
    clothingData.items.forEach(item => {
        const typeName = item.type_name;
        if (!typeGroups[typeName]) {
            typeGroups[typeName] = [];
        }
        typeGroups[typeName].push(item);
    });
    
    const itemsContainer = document.createElement('div');
    itemsContainer.className = 'clothing-items';
    
    Object.keys(typeGroups).forEach(typeName => {
        const group = typeGroups[typeName];
        const groupDiv = document.createElement('span');
        groupDiv.className = 'clothing-group';
        
        const typeLabel = document.createElement('span');
        typeLabel.className = 'clothing-type-label';
        typeLabel.textContent = `[${typeName}]:`;
        groupDiv.appendChild(typeLabel);
        
        group.forEach(item => {
            if (item.is_vacuum) {
                const vacuumSpan = document.createElement('span');
                vacuumSpan.className = 'clothing-vacuum';
                vacuumSpan.textContent = ' 真空';
                groupDiv.appendChild(vacuumSpan);
            } else if (isHMode && item.id !== -1) {
                // H模式下显示为可点击按钮
                const clothBtn = document.createElement('button');
                clothBtn.className = 'clothing-button';
                clothBtn.textContent = ` ${item.name}`;
                clothBtn.dataset.clothId = item.id;
                clothBtn.dataset.clothType = item.type;
                clothBtn.dataset.isWorn = item.is_worn;
                clothBtn.onclick = () => toggleCloth(item.id, item.type, item.is_worn);
                groupDiv.appendChild(clothBtn);
            } else {
                const clothSpan = document.createElement('span');
                clothSpan.className = 'clothing-name';
                clothSpan.textContent = ` ${item.name}`;
                groupDiv.appendChild(clothSpan);
            }
            
            // 精液污浊显示
            if (item.dirty_text) {
                const dirtySpan = document.createElement('span');
                dirtySpan.className = 'clothing-dirty semen-color';
                dirtySpan.textContent = `(${item.dirty_text})`;
                groupDiv.appendChild(dirtySpan);
            }
        });
        
        itemsContainer.appendChild(groupDiv);
    });
    
    section.appendChild(itemsContainer);
    
    // 脱下的衣服
    if (clothingData.off_items && clothingData.off_items.length > 0) {
        const offDiv = document.createElement('div');
        offDiv.className = 'clothing-off';
        
        const offLabel = document.createElement('span');
        offLabel.className = 'clothing-off-label';
        offLabel.textContent = '[已脱下]:';
        offDiv.appendChild(offLabel);
        
        clothingData.off_items.forEach(item => {
            if (isHMode) {
                const clothBtn = document.createElement('button');
                clothBtn.className = 'clothing-button clothing-off-btn';
                clothBtn.textContent = ` ${item.name}`;
                clothBtn.dataset.clothId = item.id;
                clothBtn.dataset.clothType = item.type;
                clothBtn.dataset.isWorn = 'false';
                clothBtn.onclick = () => toggleCloth(item.id, item.type, false);
                offDiv.appendChild(clothBtn);
            } else {
                const clothSpan = document.createElement('span');
                clothSpan.className = 'clothing-name clothing-off-name';
                clothSpan.textContent = ` ${item.name}`;
                offDiv.appendChild(clothSpan);
            }
        });
        
        section.appendChild(offDiv);
    }
    
    return section;
}

/**
 * 创建身体栏内容
 */
function createBodySection(bodyData) {
    const section = document.createElement('div');
    section.className = 'extra-info-section body-section';
    section.dataset.section = 'body';
    
    const title = document.createElement('div');
    title.className = 'section-title';
    title.textContent = '身体：';
    section.appendChild(title);
    
    if (!bodyData || (!bodyData.parts?.length && !bodyData.extra_info?.length)) {
        const empty = document.createElement('div');
        empty.className = 'section-empty';
        empty.textContent = '无数据';
        section.appendChild(empty);
        return section;
    }
    
    const content = document.createElement('div');
    content.className = 'body-content';
    
    // 部位信息
    if (bodyData.parts && bodyData.parts.length > 0) {
        bodyData.parts.forEach(part => {
            // 为每个部位创建一个分组
            const partGroup = document.createElement('span');
            partGroup.className = 'body-part-group';
            
            // 添加部位名称标签
            if (part.name) {
                const partLabel = document.createElement('span');
                partLabel.className = 'body-part-label';
                partLabel.textContent = `[${part.name}]:`;
                partGroup.appendChild(partLabel);
            }
            
            // 添加该部位的所有文本信息
            part.texts.forEach(textInfo => {
                const textSpan = document.createElement('span');
                textSpan.className = `body-text body-${textInfo.type}`;
                if (textInfo.type === 'semen') {
                    textSpan.classList.add('semen-color');
                } else if (textInfo.type === 'love_juice') {
                    textSpan.classList.add('lavender-color');
                } else if (textInfo.type === 'virgin_blood') {
                    textSpan.classList.add('blood-color');
                }
                textSpan.textContent = ` ${textInfo.text}`;
                partGroup.appendChild(textSpan);
            });
            
            content.appendChild(partGroup);
        });
    }
    
    // 额外信息
    if (bodyData.extra_info && bodyData.extra_info.length > 0) {
        bodyData.extra_info.forEach(info => {
            if (info.type === 'h_items' && info.items) {
                info.items.forEach(itemText => {
                    const itemSpan = document.createElement('span');
                    itemSpan.className = 'body-h-item';
                    itemSpan.textContent = ` <${itemText}>`;
                    content.appendChild(itemSpan);
                });
            } else if (info.text) {
                const infoSpan = document.createElement('span');
                infoSpan.className = `body-extra body-${info.type}`;
                if (info.type === 'semen' || info.type === 'abdomen_semen') {
                    infoSpan.classList.add('semen-color');
                }
                infoSpan.textContent = ` ${info.text}`;
                content.appendChild(infoSpan);
            }
        });
    }
    
    section.appendChild(content);
    return section;
}

/**
 * 创建群交栏内容
 */
function createGroupSexSection(groupSexData) {
    const section = document.createElement('div');
    section.className = 'extra-info-section group-sex-section';
    section.dataset.section = 'group_sex';
    
    const title = document.createElement('div');
    title.className = 'section-title';
    title.textContent = '：群交：';
    section.appendChild(title);
    
    if (!groupSexData || !groupSexData.active) {
        const empty = document.createElement('div');
        empty.className = 'section-empty';
        empty.textContent = '无数据';
        section.appendChild(empty);
        return section;
    }
    
    const content = document.createElement('div');
    content.className = 'group-sex-content';
    
    let textParts = [];
    if (groupSexData.player_name) {
        textParts.push(groupSexData.player_name);
    }
    
    if (groupSexData.body_parts && groupSexData.body_parts.length > 0) {
        groupSexData.body_parts.forEach(part => {
            if (part.part === 'wait_upon') {
                // 侍奉
                const names = part.target_names?.join('、') || '';
                const together = part.target_names?.length > 1 ? '一起' : '';
                textParts.push(`阴茎正在被${names}${together}${part.action_name}`);
            } else {
                textParts.push(`${part.part_name}-${part.action_name}-${part.target_name}`);
            }
        });
    }
    
    content.textContent = textParts.join(' ');
    section.appendChild(content);
    return section;
}

/**
 * 创建隐奸栏内容
 */
function createHiddenSexSection(hiddenSexData) {
    const section = document.createElement('div');
    section.className = 'extra-info-section hidden-sex-section';
    section.dataset.section = 'hidden_sex';
    
    const title = document.createElement('div');
    title.className = 'section-title';
    title.textContent = '：隐奸：';
    section.appendChild(title);
    
    if (!hiddenSexData || !hiddenSexData.active) {
        const empty = document.createElement('div');
        empty.className = 'section-empty';
        empty.textContent = '无数据';
        section.appendChild(empty);
        return section;
    }
    
    const content = document.createElement('div');
    content.className = 'hidden-sex-content';
    
    // 隐蔽程度
    const hiddenText = document.createElement('span');
    hiddenText.className = 'hidden-level';
    hiddenText.textContent = `隐蔽程度：${hiddenSexData.hidden_text || '未知'}`;
    content.appendChild(hiddenText);
    
    // 阴茎位置
    if (hiddenSexData.insert_text) {
        const insertText = document.createElement('span');
        insertText.className = 'hidden-insert';
        insertText.textContent = ` ${hiddenSexData.insert_text}`;
        content.appendChild(insertText);
    }
    
    section.appendChild(content);
    return section;
}

/**
 * 切换附加信息栏位的展开/收起状态
 * 立即更新前端UI，同时发送请求到后端保存状态
 */
function toggleExtraInfoSection(sectionKey) {
    // 立即更新前端UI
    const btn = document.querySelector(`.extra-info-tab-btn[data-section="${sectionKey}"]`);
    const section = document.querySelector(`.extra-info-section[data-section="${sectionKey}"]`);
    
    if (btn) {
        const isExpanded = btn.classList.contains('active');
        if (isExpanded) {
            // 收起：移除active样式，隐藏内容
            btn.classList.remove('active');
            if (section) {
                section.style.display = 'none';
            }
        } else {
            // 展开：添加active样式，显示内容
            btn.classList.add('active');
            if (section) {
                section.style.display = 'block';
            }
        }
    }
    
    // 同时发送请求到后端保存状态（不等待响应刷新）
    fetch('/api/toggle_extra_info_section', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ section: sectionKey })
    }).catch(err => console.error('保存栏位状态失败:', err));
}

/**
 * 切换详细污浊显示
 * 立即更新前端UI，同时发送请求到后端保存状态
 */
function toggleDetailedDirty() {
    // 立即更新按钮文本
    const toggleBtn = document.getElementById('toggle-detailed-dirty');
    if (!toggleBtn) return;
    
    const isDetailed = toggleBtn.textContent.includes('收起');
    toggleBtn.textContent = isDetailed ? '展开详细污浊' : '收起详细污浊';
    
    // 发送请求到后端保存状态并获取更新后的数据
    fetch('/api/toggle_detailed_dirty', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    }).then(response => response.json())
    .then(data => {
        if (data.success && data.extra_info) {
            // 立即重新渲染附加信息区域
            const extraInfoPanel = document.querySelector('.new-ui-target-extra-info');
            if (extraInfoPanel && extraInfoPanel.parentNode) {
                const newPanel = createTargetExtraInfoPanel(data.extra_info);
                extraInfoPanel.parentNode.replaceChild(newPanel, extraInfoPanel);
            }
        }
    }).catch(err => console.error('切换详细污浊失败:', err));
}

/**
 * 切换全部位显示
 * 立即更新前端UI，同时发送请求到后端保存状态，并控制身体部位按钮的显示
 */
function toggleAllBodyParts() {
    // 立即更新按钮文本
    const toggleBtn = document.getElementById('toggle-all-body-parts');
    if (!toggleBtn) return;
    
    const isExpanded = toggleBtn.textContent.includes('收起');
    toggleBtn.textContent = isExpanded ? '展开全部位显示' : '收起全部位显示';
    
    // 立即更新身体部位按钮的显示状态
    const bodyPartButtons = document.querySelectorAll('.body-part-button');
    if (isExpanded) {
        // 收起：移除always-visible类，恢复默认的悬停显示
        bodyPartButtons.forEach(btn => btn.classList.remove('always-visible'));
    } else {
        // 展开：添加always-visible类，始终显示所有部位
        bodyPartButtons.forEach(btn => btn.classList.add('always-visible'));
    }
    
    // 发送请求到后端保存状态并获取更新后的数据
    fetch('/api/toggle_all_body_parts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    }).then(response => response.json())
    .then(data => {
        if (data.success && data.extra_info) {
            // 重新渲染附加信息区域（更新按钮状态）
            const extraInfoPanel = document.querySelector('.new-ui-target-extra-info');
            if (extraInfoPanel && extraInfoPanel.parentNode) {
                const newPanel = createTargetExtraInfoPanel(data.extra_info);
                extraInfoPanel.parentNode.replaceChild(newPanel, extraInfoPanel);
                
                // 重新应用身体部位按钮的显示状态
                const updatedBodyPartButtons = document.querySelectorAll('.body-part-button');
                if (data.extra_info.show_all_body_parts) {
                    updatedBodyPartButtons.forEach(btn => btn.classList.add('always-visible'));
                } else {
                    updatedBodyPartButtons.forEach(btn => btn.classList.remove('always-visible'));
                }
            }
        }
        
        // 同时更新右侧的交互对象信息面板（包含可选部位列表）
        if (data.success && data.target_info) {
            const targetInfoPanel = document.querySelector('.new-ui-target-info');
            if (targetInfoPanel && targetInfoPanel.parentNode) {
                const newTargetPanel = createTargetInfoPanel(data.target_info);
                targetInfoPanel.parentNode.replaceChild(newTargetPanel, targetInfoPanel);
            }
        }
    }).catch(err => console.error('切换全部位显示失败:', err));
}

/**
 * 切换衣服穿脱状态
 */
function toggleCloth(clothId, clothType, isWorn) {
    fetch('/api/toggle_cloth', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            cloth_id: clothId, 
            cloth_type: clothType, 
            is_worn: isWorn 
        })
    }).then(response => response.json())
    .then(data => {
        if (data.success && data.extra_info) {
            // 立即重新渲染附加信息区域
            const extraInfoPanel = document.querySelector('.new-ui-target-extra-info');
            if (extraInfoPanel && extraInfoPanel.parentNode) {
                const newPanel = createTargetExtraInfoPanel(data.extra_info);
                extraInfoPanel.parentNode.replaceChild(newPanel, extraInfoPanel);
            }
        }
    }).catch(err => console.error('切换衣服状态失败:', err));
}

/**
 * 刷新游戏状态
 */
function refreshGameState() {
    // 如果使用socket.io，发送刷新请求
    if (typeof socket !== 'undefined' && socket.connected) {
        socket.emit('refresh_state');
    }
}

/**
 * 创建头像面板
 * 支持分页功能：当场景角色超过5人时显示分页按钮
 */
