/**
 * 游戏主JavaScript文件（核心模块）
 * 实现游戏状态获取、渲染和用户交互
 *
 * 依赖模块（需要按顺序在此文件之前加载）：
 * - device_utils.js: 设备检测与缩放管理
 * - tooltip_manager.js: 工具提示管理
 * - ui_managers.js: UI管理器（横屏、等待、滚动）
 * - new_ui_components.js: 新UI组件（玩家信息、对话框、附加信息）
 * - new_ui_interaction.js: 新UI交互（头像、交互类型）
 * - new_ui_character.js: 新UI角色显示（立绘、身体部位、状态）
 */

const POLL_INTERVAL = 500;

// 用于跟踪上一个元素的类型和是否需要换行
let lastElementType = null;
let forceNewLine = false; // 标记是否强制换行
let isLastElementLinebreak = false; // 标记上一个元素是否为换行符
// 新增：标记上一条“文本元素”是否以换行符结尾，用于将紧随其后的 line_feed 作为“空白行”渲染
let isLastTextEndedWithNewline = false;

// 场景角色头像区分页管理
let sceneCharactersCurrentPage = 0;  // 当前页码（从0开始）
let sceneCharactersData = [];        // 当前场景的角色数据
let sceneCharactersMinorDialogs = []; // 当前场景的小对话框数据

// ========== 文本回溯缓存系统 ==========
const TEXT_HISTORY_MAX_LENGTH = 200;  // 文本历史缓存最大长度
let textHistoryCache = [];             // 文本历史缓存数组
let textHistoryContentSet = new Set(); // 文本内容去重集合（用于防止同一文本在不同状态更新中被重复添加）
let isTextHistoryMode = false;         // 是否处于文本回溯模式
let savedGameContent = null;           // 保存的游戏内容DOM状态

/**
 * 添加文本元素到历史缓存
 * 缓存所有文本类型元素（不含按钮），超过上限时移除最旧的
 * 支持的类型：text, line_feed, title, center_text, right_text, line_wait, dialog, value_change, settlement, description
 * 
 * @param {Object} item - 要缓存的文本元素
 */
function addToTextHistory(item) {
    // 支持的文本类型（不含按钮）
    const textTypes = ['text', 'line_feed', 'title', 'center_text', 'right_text', 'line_wait', 'dialog', 'value_change', 'settlement', 'description'];
    if (!textTypes.includes(item.type)) {
        return;
    }
    
    // 忽略空文本
    if ((item.type === 'text' || item.type === 'dialog' || item.type === 'value_change' || item.type === 'settlement' || item.type === 'description') && (!item.text || item.text.trim() === '')) {
        return;
    }
    
    // 基于内容的去重：使用 type + text 的组合作为唯一标识
    const contentKey = `${item.type}:${item.text}`;
    if (textHistoryContentSet.has(contentKey)) {
        // 已存在相同内容，跳过添加
        return;
    }
    
    // 添加到去重集合
    textHistoryContentSet.add(contentKey);
    
    // 添加到缓存
    textHistoryCache.push({
        ...item,
        timestamp: Date.now(),
        contentKey: contentKey  // 保存 contentKey 用于后续移除时同步更新 Set
    });
    
    // 超过上限时移除最旧的，同时从去重集合中移除
    while (textHistoryCache.length > TEXT_HISTORY_MAX_LENGTH) {
        const removed = textHistoryCache.shift();
        if (removed && removed.contentKey) {
            textHistoryContentSet.delete(removed.contentKey);
        }
    }
}

/**
 * 添加数值变化文本到历史缓存
 * 格式化数值变化为统一的文本历史格式
 * 
 * @param {Array} valueChanges - 数值变化数组，每项包含 field_name, value, color 等字段
 * @param {string} source - 来源标识（player_info / target_info）
 */
function addValueChangesToTextHistory(valueChanges, source) {
    if (!valueChanges || valueChanges.length === 0) {
        return;
    }
    
    // 将所有变化合并为一条文本
    const changeTexts = [];
    valueChanges.forEach(change => {
        if (change.value === 0) return;
        const sign = change.value > 0 ? '+' : '';
        const fieldName = change.field_name || change.field;
        changeTexts.push(`${fieldName} ${sign}${change.value}`);
    });
    
    if (changeTexts.length === 0) return;
    
    // 添加到历史缓存
    addToTextHistory({
        type: 'value_change',
        text: changeTexts.join('，'),
        font: 'standard',
        source: source
    });
}

/**
 * 获取文本历史缓存
 * @returns {Array} 文本历史缓存数组
 */
function getTextHistory() {
    return textHistoryCache;
}

/**
 * 清空文本历史缓存
 */
function clearTextHistory() {
    textHistoryCache = [];
}

/**
 * 进入文本回溯模式
 * 保存当前游戏内容，显示文本历史界面
 */
function enterTextHistoryMode() {
    if (isTextHistoryMode) return;
    
    isTextHistoryMode = true;
    const gameContent = document.getElementById('game-content');
    
    // 检查元素是否存在
    if (!gameContent) {
        console.error('[TextHistory] 找不到 game-content 元素');
        isTextHistoryMode = false;
        return;
    }
    
    // 隐藏当前游戏内容的所有子元素（保留DOM和事件监听器）
    Array.from(gameContent.children).forEach(child => {
        child.style.display = 'none';
        child.dataset.hiddenByTextHistory = 'true';
    });
    
    // 创建并显示文本历史界面
    const historyPanel = createTextHistoryPanel();
    historyPanel.id = 'text-history-panel';
    gameContent.appendChild(historyPanel);
    
    // 更新选项卡状态
    updateTextHistoryTabState(true);
    
    console.log('[TextHistory] 进入文本回溯模式，缓存条数:', textHistoryCache.length);
}

/**
 * 退出文本回溯模式
 * 恢复之前保存的游戏内容
 */
function exitTextHistoryMode() {
    if (!isTextHistoryMode) return;
    
    isTextHistoryMode = false;
    const gameContent = document.getElementById('game-content');
    
    // 检查元素是否存在
    if (!gameContent) {
        console.error('[TextHistory] 找不到 game-content 元素');
        return;
    }
    
    // 移除文本历史面板
    const historyPanel = document.getElementById('text-history-panel');
    if (historyPanel) {
        historyPanel.remove();
    }
    
    // 恢复之前隐藏的游戏内容子元素
    Array.from(gameContent.children).forEach(child => {
        if (child.dataset.hiddenByTextHistory === 'true') {
            child.style.display = '';
            delete child.dataset.hiddenByTextHistory;
        }
    });
    
    // 更新选项卡状态
    updateTextHistoryTabState(false);
    
    console.log('[TextHistory] 退出文本回溯模式');
}

/**
 * 更新文本回溯选项卡的激活状态
 * @param {boolean} active - 是否激活
 */
function updateTextHistoryTabState(active) {
    const textHistoryTab = document.querySelector('.panel-tab-btn[data-tab-id="__text_history__"]');
    if (textHistoryTab) {
        if (active) {
            textHistoryTab.classList.add('active');
        } else {
            textHistoryTab.classList.remove('active');
        }
    }
}

/**
 * 等待管理器
 * 负责处理需要用户确认后继续的绘制元素
 */
/**
 * 初始化字体配置字典
 * 从服务器获取所有字体配置并构建查找字典
 * 
 * @return {Promise} - 初始化完成的Promise
 */
async function initFontConfigDict() {
    try {
        // 从服务器获取所有字体配置的列表
        const response = await fetch('/api/get_font_config');
        if (!response.ok) {
            throw new Error('获取字体配置列表失败');
        }
        
        const fontConfigs = await response.json();
        
        // 重置字典
        fontConfigDict = {};
        
        // 构建查找字典
        fontConfigs.forEach(config => {
            // 将字体名称作为键，字体配置作为值存入字典
            fontConfigDict[config.name] = {
                foreground: config.foreground,
                background: config.background,
                font: config.font,
                font_size: config.font_size,
                bold: config.bold === 1,
                underline: config.underline === 1,
                italic: config.italic === 1,
                selectbackground: config.selectbackground
            };
        });
        
        console.log('字体配置字典初始化完成，共加载', Object.keys(fontConfigDict).length, '个字体配置');
    } catch (error) {
        console.error('初始化字体配置字典出错:', error);
    }
}

/**
 * 根据字体名称应用字体样式
 * 将字体配置应用到DOM元素上
 * 
 * @param {HTMLElement} element - 需要应用样式的DOM元素
 * @param {string} fontName - 字体名称
 * @return {HTMLElement} - 应用样式后的DOM元素
 */
function applyFontStyle(element, fontName) {
    // 如果字体名称无效或字典中不存在该字体配置，直接返回原元素
    if (!fontName || !fontConfigDict[fontName]) {
        return element;
    }
    
    // 获取字体配置
    const fontConfig = fontConfigDict[fontName];
    
    // 应用前景色（文字颜色）
    if (fontConfig.foreground) {
        element.style.color = fontConfig.foreground;
    }
    
    // 应用背景色
    if (fontConfig.background) {
        element.style.backgroundColor = fontConfig.background;
    }
    
    // 应用字体
    if (fontConfig.font) {
        element.style.fontFamily = fontConfig.font;
    }
    
    // 应用字体大小
    if (fontConfig.font_size) {
        element.style.fontSize = `${fontConfig.font_size}px`;
    }
    
    // 应用粗体
    if (fontConfig.bold) {
        element.style.fontWeight = 'bold';
    }
    
    // 应用下划线
    if (fontConfig.underline) {
        element.style.textDecoration = 'underline';
    }
    
    // 应用斜体
    if (fontConfig.italic) {
        element.style.fontStyle = 'italic';
    }
    
    return element;
}

/**
 * 初始化WebSocket连接
 * 建立与服务器的实时通信连接
 */
function initWebSocket() {
    // 创建WebSocket连接
    socket = io();
    // 同时设置到 window 上，确保全局可访问
    window.socket = socket;
    
    // 连接成功事件
    socket.on('connect', () => {
        console.log('WebSocket连接成功');
        // 隐藏加载消息
        document.getElementById('loading-message').classList.add('hidden');
    });
    
    // 连接错误事件
    socket.on('connect_error', (error) => {
        console.error('WebSocket连接失败:', error);
        // 连接失败时，回退到轮询模式
        fallbackToPolling();
    });
    
    // 断开连接事件
    socket.on('disconnect', (reason) => {
        console.log('WebSocket断开连接:', reason);
        // 断开连接时，尝试重连或回退到轮询模式
        if (reason === 'io server disconnect') {
            // 服务器主动断开，尝试重连
            socket.connect();
        }
    });
    
    // 接收游戏状态更新事件
    socket.on('game_state_update', (data) => {
        console.log('收到游戏状态更新:', data);
        // 渲染新的游戏状态
        renderGameState(data);
    });
    
    // 接收大类型选择结果事件
    socket.on('major_type_selected', (data) => {
        console.log('收到大类型选择结果:', data);
        if (data.success) {
            // 更新交互面板的小类按钮
            updateMinorTypeButtons(data.minor_types, data.remembered_minor_type, data.major_type_id);
        } else {
            console.error('选择大类型失败:', data.error);
        }
    });
    
    // 接收小类型选择结果事件
    socket.on('minor_type_selected', (data) => {
        console.log('收到小类型选择结果:', data);
        if (data.success) {
            // 检查返回的小类ID是否与当前前端激活的小类匹配
            // 这可以防止竞态条件：用户快速切换小类时，旧的响应覆盖新的选择
            const minorList = document.querySelector('.interaction-minor-list');
            const activeMinor = minorList ? minorList.querySelector('.minor-card.active:not(.floating-instruct)') : null;
            const currentActiveMinorId = activeMinor ? activeMinor.dataset.id : null;
            
            if (currentActiveMinorId && data.minor_type_id !== currentActiveMinorId) {
                console.log('[DEBUG] 忽略过期的 minor_type_selected 响应，返回ID:', data.minor_type_id, '当前激活ID:', currentActiveMinorId);
                return;
            }
            
            // 根据 target_info 更新 window.hasTargetCharacter 状态
            // 这确保在切换交互对象后，无部位指令能正确显示为浮现按钮
            if (data.target_info !== undefined) {
                window.hasTargetCharacter = data.target_info && Object.keys(data.target_info).length > 0;
                console.log('[DEBUG] minor_type_selected 更新 hasTargetCharacter:', window.hasTargetCharacter);
            }
            
            // 更新可交互的身体部位
            updateAvailableBodyParts(data.instructs);
            
            // 同时更新右侧的交互对象信息面板（包含可选部位列表）
            if (data.target_info) {
                const targetInfoPanel = document.querySelector('.new-ui-target-info');
                if (targetInfoPanel && targetInfoPanel.parentNode) {
                    const newTargetPanel = createTargetInfoPanel(data.target_info);
                    targetInfoPanel.parentNode.replaceChild(newTargetPanel, targetInfoPanel);
                }
            }
        } else {
            console.error('选择小类型失败:', data.error);
        }
    });
    
    // 接收臀部子菜单事件
    socket.on('hip_sub_menu', (data) => {
        console.log('收到臀部子菜单:', data);
        showHipSubMenu(data.sub_parts);
    });
    
    // 接收头部子菜单事件
    socket.on('head_sub_menu', (data) => {
        console.log('收到头部子菜单:', data);
        showHeadSubMenu(data.sub_parts, data.has_beast_ears, data.has_horn);
    });
    
    // 接收身体部位点击结果事件
    socket.on('body_part_clicked', (data) => {
        console.log('收到身体部位点击结果:', data);
        handleBodyPartClickResult(data);
    });
    
    // 接收对话推进结果事件
    socket.on('dialog_advanced', (data) => {
        console.log('收到对话推进结果:', data);
        if (data.success && data.dialog) {
            updateDialogBox(data.dialog);
            // 对话框文本已由 handle_talk_draw 统一收集到 web_settlement_texts，无需重复记录
        }
    });
    
    // 接收对话跳过结果事件
    socket.on('dialogs_skipped', (data) => {
        console.log('收到对话跳过结果:', data);
        if (data.success && data.dialog) {
            updateDialogBox(data.dialog);
            // 对话框文本已由 handle_talk_draw 统一收集到 web_settlement_texts，无需重复记录
        }
    });
    
    // 接收对话框状态更新事件（由talk.py触发）
    socket.on('dialog_state_update', (data) => {
        console.log('收到对话框状态更新:', data);
        if (data.success && data.dialog) {
            updateDialogBox(data.dialog);
            // 对话框文本已由 handle_talk_draw 统一收集到 web_settlement_texts，无需重复记录
        }
    });
    
    // 接收切换交互对象结果事件
    socket.on('target_switched', (data) => {
        console.log('收到切换交互对象结果:', data);
        if (data.success) {
            console.log(`成功切换到角色: ${data.character_name} (ID: ${data.character_id})`);
            // 清理前端图片缓存，因为切换了交互对象
            clearCroppedImageCache();
            // 请求完整状态刷新 - 通过发送一个空的按钮点击来触发状态更新
            // 后端在下一次主循环会检测到 web_need_full_refresh 标志并发送完整状态
            // 这里我们只需要等待后端推送新状态
        } else {
            console.error('切换交互对象失败:', data.error);
        }
    });
    
    // 接收清空交互选择结果事件
    socket.on('interaction_selection_cleared', (data) => {
        console.log('收到清空交互选择结果:', data);
        if (data.success) {
            // 更新右侧的交互对象信息面板（包含可选部位列表）
            if (data.target_info) {
                const targetInfoPanel = document.querySelector('.new-ui-target-info');
                if (targetInfoPanel && targetInfoPanel.parentNode) {
                    const newTargetPanel = createTargetInfoPanel(data.target_info);
                    targetInfoPanel.parentNode.replaceChild(newTargetPanel, targetInfoPanel);
                }
            }
        } else {
            console.error('清空交互选择失败:', data.error);
        }
    });
    
    // 接收场景内全部角色数据
    socket.on('all_scene_characters', (data) => {
        console.log('收到场景内全部角色:', data);
        if (data.success && data.characters) {
            createAllCharactersPanel(data.characters);
        } else {
            console.error('获取场景角色失败:', data.error);
        }
    });
}

/**
 * 清理前端裁切图片缓存
 * 在切换交互对象或需要刷新时调用
 */
function clearCroppedImageCache() {
    // 释放所有 blob URL 以避免内存泄漏
    for (const [url, data] of croppedImageCache) {
        if (data.blobUrl) {
            URL.revokeObjectURL(data.blobUrl);
        }
    }
    croppedImageCache.clear();
    console.log('[图片缓存] 前端裁切图片缓存已清理');
}

/**
 * 回退到轮询模式
 * 当WebSocket连接失败时，使用HTTP轮询方式获取游戏状态
 */
function fallbackToPolling() {
    console.log('回退到HTTP轮询模式');
    // 显示提示信息
    const loadingMessage = document.getElementById('loading-message');
    loadingMessage.classList.remove('hidden');
    loadingMessage.textContent = '实时连接失败，使用轮询模式...';
    
    // 设置定时获取游戏状态
    setInterval(getGameState, POLL_INTERVAL);
}

/**
 * 获取游戏状态
 * 从服务器API获取最新的游戏状态
 */
function getGameState() {
    // 发起API请求获取游戏状态
    fetch('/api/get_state')
        .then(response => response.json())
        .then(data => {
            // 使用获取的数据渲染游戏界面
            renderGameState(data);
            // 隐藏加载消息
            document.getElementById('loading-message').classList.add('hidden');
        })
        .catch(error => {
            console.error('获取游戏状态出错:', error);
            document.getElementById('loading-message').textContent = '连接服务器失败，请刷新页面重试...';
        });
}

/**
 * 检查是否需要换行
 * 根据当前元素和前一个元素的类型决定是否需要换行
 * 
 * @param {Object} item - 当前元素的数据
 * @return {boolean} 是否需要换行
 */
function shouldCreateNewLine(item) {
    // 如果是特殊类型的元素，总是需要换行
    if (['title', 'line', 'wait', 'line_wait'].includes(item.type)) {
        return true;
    }
    
    // 如果要强制换行（例如遇到了换行符），总是需要换行
    if (forceNewLine) {
        forceNewLine = false; // 重置标志
        return true;
    }
    
    // 如果内容包含换行符，需要换行
    if (item.text && item.text === '\n') {
        return true;
    }
    
    // 如果明确指定要块级显示，需要换行
    if (item.style && item.style.includes('block')) {
        return true;
    }
    
    // 默认情况下不换行，允许不同类型的元素显示在同一行
    return false;
}

/**
 * 确定换行符的特殊处理
 * 根据上一个元素类型决定当前换行符是否需要插入额外空行
 * 
 * @param {boolean} isLineBreak - 当前元素是否为换行符
 * @return {string} 换行符的CSS类名
 */
function determineLineBreakClass() {
    // 如果上一个元素也是换行符，或上一条文本以 \n 结尾，则使用额外空行样式
    if (isLastElementLinebreak || isLastTextEndedWithNewline) {
        return 'text-break extra-space';
    }
    
    // 否则使用普通换行样式
    return 'text-break';
}

/**
 * 为地图元素应用专用布局
 * @param {HTMLElement} element - 当前渲染的元素
 * @param {HTMLElement} container - 元素所在的行容器
 * @param {Object} options - 附加选项
 * @param {boolean} options.isText - 是否为文本类型元素
 */
function applyMapLayout(element, container, options = {}) {
    if (!element || !container) {
        return;
    }

    container.classList.add('map-line');
    element.classList.add('map-element');

    if (options.isText) {
        element.classList.add('map-text');
        element.style.whiteSpace = 'pre';
    }

    if (options.isPadding) {
        element.classList.add('map-padding');
        element.textContent = '';
        element.style.display = 'none';
        return;
    }
}

/**
 * 规范化地图块的宽度和居中显示
 * 将所有连续的map-line元素分组，计算组内最大宽度，统一设置min-width使各行对齐
 * @param {HTMLElement} root - 游戏内容根元素
 */
function normalizeMapBlocks(root) {
    if (!root) {
        return;
    }

    const children = Array.from(root.children || []);
    let currentGroup = [];

    const flushGroup = () => {
        if (!currentGroup.length) {
            return;
        }

        const groupLines = currentGroup.slice();
        let wrapper = null;
        let inner = null;

        const firstLine = groupLines[0];
        const parent = firstLine && firstLine.parentElement;

        if (parent) {
            if (parent.classList.contains('map-group')) {
                wrapper = parent;
                inner = wrapper.querySelector('.map-group-inner');
                if (!inner) {
                    inner = document.createElement('div');
                    inner.className = 'map-group-inner';
                    wrapper.appendChild(inner);
                }
            } else {
                wrapper = document.createElement('div');
                wrapper.className = 'map-group';
                inner = document.createElement('div');
                inner.className = 'map-group-inner';
                wrapper.appendChild(inner);
                parent.insertBefore(wrapper, firstLine);
            }
            groupLines.forEach(line => inner.appendChild(line));
        }

        // 清除之前的样式
        groupLines.forEach(line => {
            line.style.width = '';
            line.style.minWidth = '';
            line.style.marginLeft = '';
            line.style.marginRight = '';
        });

        if (wrapper) {
            wrapper.style.width = '100%';
        }

        if (inner) {
            inner.style.width = '';
        }

        // 使用requestAnimationFrame计算并同步所有行的宽度
        requestAnimationFrame(() => {
            // 获取所有行的实际渲染宽度
            const widths = groupLines.map(line => line.scrollWidth || line.offsetWidth || 0);
            const maxWidth = Math.max(...widths);
            
            if (maxWidth > 0) {
                // 为每行设置min-width使其达到最大宽度，保持各行起点一致
                groupLines.forEach(line => {
                    line.style.minWidth = `${maxWidth}px`;
                    line.style.marginLeft = '0';
                    line.style.marginRight = '0';
                });

                if (inner) {
                    inner.style.width = `${maxWidth}px`;
                }
            }
        });

        currentGroup = [];
    };

    children.forEach(child => {
        if (child.classList && child.classList.contains('map-line')) {
            currentGroup.push(child);
        } else {
            // 检查是否是换行/空元素（text-break、空div等）
            // 如果是，不要中断当前组
            const isBreakElement = child.classList && (
                child.classList.contains('text-break') ||
                child.classList.contains('line-break')
            );
            const isEmptyDiv = child.tagName === 'DIV' && 
                !child.textContent.trim() && 
                !child.querySelector('.map-line');
            
            // 只有遇到有实际内容的非地图元素时才中断组
            if (!isBreakElement && !isEmptyDiv) {
                flushGroup();
            }
        }
    });

    flushGroup();
}

/**
 * 渲染游戏状态
 * 根据服务器返回的状态数据渲染游戏界面
 * 
 * @param {Object} state - 游戏状态数据
 */
function renderGameState(state) {
    // 获取游戏内容和按钮容器
    const gameContent = document.getElementById('game-content');
    const gameButtons = document.getElementById('game-buttons');
    
    // 更新全局状态和活动输入请求
    currentGlobalState = state;
    activeInputRequest = state.input_request || null;
    
    // 调试日志：打印接收到的完整状态和 input_request
    console.log('Received state:', JSON.stringify(state, null, 2));
    console.log('Input request from state:', state.input_request);
    
    // 检查状态数据是否有效
    if (!state) {
        console.error('无效的游戏状态数据');
        return;
    }

    TooltipManager.hideImmediate(); // 渲染前先清空旧提示，避免残留浮层

    const skipWaitActive = !!state.skip_wait;
    if (WaitManager.skipMode !== skipWaitActive) {
        console.log('[renderGameState] sync skipMode from state:', skipWaitActive);
    }
    WaitManager.skipMode = skipWaitActive;
    if (WaitManager.skipMode && WaitManager.isWaiting && !WaitManager.waitResponsePending) {
        WaitManager.trigger();
    }
    
    // 渲染前重置等待元素绑定
    WaitManager.prepareForRender();

    // 清空内容容器
    gameContent.innerHTML = '';
    
    // 清空按钮容器（按钮将在游戏内容中直接渲染）
    gameButtons.innerHTML = '';
    // 隐藏独立的按钮容器
    gameButtons.classList.add('hidden');
    
    // ========== 子面板模式处理 ==========
    // 如果处于子面板模式，先渲染场景信息栏和选项卡
    if (state.sub_panel_mode && state.sub_panel_data) {
        console.log('[renderGameState] 子面板模式激活，渲染固定头部');
        
        // 添加子面板模式样式类
        gameContent.classList.add('sub-panel-mode');
        
        // 创建子面板模式的固定头部容器
        const subPanelHeader = document.createElement('div');
        subPanelHeader.className = 'sub-panel-header';
        
        // 渲染场景信息栏
        if (state.sub_panel_data.scene_info_bar) {
            const sceneInfoBar = createSceneInfoBar(state.sub_panel_data.scene_info_bar);
            subPanelHeader.appendChild(sceneInfoBar);
        }
        
        // 渲染面板选项卡（带禁用状态和临时选项卡）
        if (state.sub_panel_data.panel_tabs && state.sub_panel_data.panel_tabs.length > 0) {
            const panelTabs = createPanelTabsBar(state.sub_panel_data.panel_tabs);
            subPanelHeader.appendChild(panelTabs);
        }
        
        gameContent.appendChild(subPanelHeader);
        
        // 创建子面板内容容器
        const subPanelContent = document.createElement('div');
        subPanelContent.className = 'sub-panel-content';
        gameContent.appendChild(subPanelContent);
        
        // 后续内容将渲染到子面板内容容器中
        // 更新 gameContent 引用为子面板内容容器
        // 注意：需要确保后续代码使用这个新的容器
    } else {
        // 非子面板模式，移除样式类
        gameContent.classList.remove('sub-panel-mode');
    }

    // 重置状态变量
    lastElementType = null;
    forceNewLine = false;
    isLastElementLinebreak = false;
    isLastTextEndedWithNewline = false;
    
    // 创建当前行容器
    // 如果是子面板模式，将内容添加到子面板内容容器中
    const contentContainer = state.sub_panel_mode && state.sub_panel_data 
        ? gameContent.querySelector('.sub-panel-content') 
        : gameContent;
    let currentLine = document.createElement('div');
    currentLine.className = 'inline-container';
    contentContainer.appendChild(currentLine);
    let currentLineHasText = false;
    let currentLineButtons = [];
    let encounteredActiveWaitElement = false;

    const applyInlineButtonAlignment = (button) => {
        if (!button || !button.classList.contains('inline-button')) {
            return;
        }
        const alignMode = button.dataset.buttonAlign || 'center';
        switch (alignMode) {
            case 'left':
                button.style.justifyContent = 'flex-start';
                button.style.textAlign = 'left';
                break;
            case 'right':
                button.style.justifyContent = 'flex-end';
                button.style.textAlign = 'right';
                break;
            default:
                button.style.justifyContent = 'center';
                button.style.textAlign = 'center';
                break;
        }
    };
    
    // 按顺序渲染所有元素（包括文本和按钮）
    if (state.text_content && state.text_content.length > 0) {
        // 渲染每个元素
        state.text_content.forEach((item, index) => {
            if (
                (item.type === 'line_wait' && item.await_input !== false) ||
                item.type === 'wait'
            ) {
                console.log('[renderGameState] detected active wait element index=', index, 'payload=', item);
                encounteredActiveWaitElement = true;
            }
            
            // 检查是否需要创建新行
            if (shouldCreateNewLine(item)) {
                // 创建新的行容器
                currentLine = document.createElement('div');
                currentLine.className = 'inline-container';
                contentContainer.appendChild(currentLine);
                currentLineHasText = false;
                currentLineButtons = [];
            }
            
            // 创建适当的DOM元素
            let element = null;
            
            // 对按钮类型进行特殊处理
            if (item.type === 'button') {
                const isMapButton = item.web_type === 'map';
                const buttonTag = isMapButton ? 'span' : 'button';
                element = document.createElement(buttonTag);
                element.className = isMapButton
                    ? 'map-button'
                    : `game-button ${item.style || 'standard'}`;

                // 处理可能包含的<br>标签
                let processedTextButton = item.text || '';
                if (processedTextButton.includes('<br>')) {
                    processedTextButton = processedTextButton.replace(/<br>/g, '\n');
                }
                element.textContent = processedTextButton;

                // 设置按钮ID及交互
                const buttonId = item.return_text;
                element.dataset.id = buttonId;
                element.dataset.buttonAlign = item.align || 'center';

                if (isMapButton) {
                    element.setAttribute('role', 'button');
                    element.tabIndex = 0;
                    element.addEventListener('click', () => handleButtonClick(buttonId));
                    element.addEventListener('keydown', (event) => {
                        if (event.key === 'Enter' || event.key === ' ') {
                            event.preventDefault();
                            handleButtonClick(buttonId);
                        }
                    });
                    applyMapLayout(element, currentLine, { isText: false });
                } else {
                    element.onclick = () => handleButtonClick(buttonId);

                    // 设置按钮宽度
                    element.style.width = item.width ? `${item.width}ch` : 'auto';
                }

                // 如果是左对齐按钮，则改为左对齐
                if (item.align === 'left') {
                    element.style.textAlign = 'left';
                } else if (item.align === 'right') {
                    // 如果是右对齐按钮，则改为右对齐
                    element.style.textAlign = 'right';
                } else {
                    element.style.textAlign = 'center';
                }
                element.dataset.buttonAlign = item.align || 'center';

                if (item.tooltip) {
                    TooltipManager.attach(element, item.tooltip); // 为按钮绑定悬浮提示逻辑
                }
                
                // 如果需要块级显示，添加block类
                if (item.style && item.style.includes('block')) {
                    element.classList.add('block');
                }

                // 设置字体
                if (item.font) {
                    element = applyFontStyle(element, item.font);
                }

                // 记录当前行内的普通按钮；若当前行已有文本，则标记为内联按钮
                if (element.classList.contains('game-button')) {
                    currentLineButtons.push(element);
                    if (currentLineHasText) {
                        element.classList.add('inline-button');
                        applyInlineButtonAlignment(element);
                    }
                }

                // 更新上一个元素类型为按钮
                lastElementType = 'button';
                isLastElementLinebreak = false;
                // 按钮后重置“上一条文本以换行结尾”标记
                isLastTextEndedWithNewline = false;
            } else if (item.type === 'text' && item.text === '\n') {
                // 处理换行符：使用块级占位元素而非 <br>，以便样式（margin/height）生效
                element = document.createElement('div');
                
                // 根据上一个元素是否为换行符或上一条文本以换行结尾来决定样式
                element.className = determineLineBreakClass();
                
                // 标记需要在下一个元素前换行
                forceNewLine = true;
                
                // 更新上一个元素类型为换行符
                lastElementType = 'linebreak';
                isLastElementLinebreak = true;
                // 当前这一显式换行已经“消费”了上一条文本的结尾换行标记
                isLastTextEndedWithNewline = false;
            } else if (item.type === 'text' && item.text.includes('\n') && item.text !== '\n') {
                // 如果文本包含换行符（但不是纯换行符），需要特殊处理
                const lines = item.text.split('\n');
                lines.forEach((line, lineIndex) => {
                    if (lineIndex > 0) {
                        // 对于非第一行，创建新的行容器
                        currentLine = document.createElement('div');
                        currentLine.className = 'inline-container';
                        contentContainer.appendChild(currentLine);
                        currentLineHasText = false;
                        currentLineButtons = [];
                    }
                    
                    if (line !== '') {
                        // 创建文本元素
                        const textElement = createGameElement({ ...item, text: line });
                        if (textElement) {
                            if (item.web_type === 'map' || item.web_type === 'map-padding') {
                                applyMapLayout(textElement, currentLine, {
                                    isText: true,
                                    isPadding: item.web_type === 'map-padding'
                                });
                            }
                            currentLine.appendChild(textElement);
                            currentLineHasText = true;
                            currentLineButtons.forEach(btn => {
                                btn.classList.add('inline-button');
                                applyInlineButtonAlignment(btn);
                            });
                        }
                    }
                });
                
                // 如果文本以换行符结尾，标记需要在下一个元素前换行
                if (item.text.endsWith('\n')) {
                    forceNewLine = true;
                    // 额外标记：上一条文本以换行符结尾
                    isLastTextEndedWithNewline = true;
                } else {
                    // 否则清除标记
                    isLastTextEndedWithNewline = false;
                }
                
                // 更新上一个元素类型
                lastElementType = item.type;
                isLastElementLinebreak = false;
            } else {
                // 创建其他类型的元素（文本、标题等）
                element = createGameElement(item);

                if (element && (item.web_type === 'map' || item.web_type === 'map-padding')) {
                    applyMapLayout(element, currentLine, {
                        isText: true,
                        isPadding: item.web_type === 'map-padding'
                    });
                }

                // 更新上一个元素类型
                lastElementType = item.type;
                
                // 除非当前元素是换行符，否则重置isLastElementLinebreak
                if (!(item.type === 'text' && item.text === '\n')) {
                    isLastElementLinebreak = false;
                }
                // 对于其它类型或不含换行的文本，清除“上一条文本以换行结尾”标记
                if (!(item.type === 'text' && item.text.includes('\n'))) {
                    isLastTextEndedWithNewline = false;
                }

                if (
                    element &&
                    (
                        (item.type === 'text' && item.text && item.text.trim() !== '') ||
                        (item.type === 'line_wait' && item.text && (item.text || '').trim() !== '')
                    )
                ) {
                    currentLineHasText = true;
                    currentLineButtons.forEach(btn => {
                        btn.classList.add('inline-button');
                        applyInlineButtonAlignment(btn);
                    });
                }
            }
            
            // 将创建的元素添加到当前行容器
            if (element) {
                currentLine.appendChild(element);
            }
            
            // 检查下一个元素是否存在且是换行符，如果是，标记需要换行
            if (state.text_content[index + 1] && state.text_content[index + 1].text === '\n') {
                forceNewLine = true;
            }
        });
    }

    if (WaitManager.isWaiting && !encounteredActiveWaitElement) {
        console.log('[renderGameState] WaitManager waiting but no active wait element detected; performing cleanup');
        WaitManager.cleanup();
    }

    // 规范化地图渲染宽度
    normalizeMapBlocks(gameContent);
    
    // 更新对话框状态（如果状态数据中包含对话框信息）
    // 注意：不在此处添加对话框到历史缓存，因为 socket 事件已经处理
    if (state.dialog) {
        updateDialogBox(state.dialog);
    }
    
    // 处理结算文本（包括数值变化和行为描述，用于文本回溯）
    // settlement_texts 由后端 settle_behavior 和 handle_talk_draw 统一收集
    if (state.settlement_texts && state.settlement_texts.length > 0) {
        state.settlement_texts.forEach(text => {
            if (text && text.trim()) {
                addToTextHistory({
                    type: 'settlement',
                    text: text,
                    font: 'standard',
                    source: 'settle_behavior'
                });
            }
        });
    }
    
    // 确保滚动到底部在所有内容渲染后执行
    scrollToBottom();
}

/**
 * 创建游戏元素
 * 根据元素类型创建对应的DOM元素
 * 
 * @param {Object} item - 元素数据对象
 * @return {HTMLElement} 创建的DOM元素
 */
function createGameElement(item) {
    let element;
    
    // 根据不同类型创建不同元素
    switch(item.type) {
        case 'text':
            // 创建文本元素
            
            // 特殊处理换行符：如果文本仅为换行符，直接创建一个br元素而不是div
            if (item.text === '\n') {
                // 使用块级占位元素而非 <br>
                element = document.createElement('div');
                
                // 根据上一个元素是否为换行符或上一条文本以换行结尾来决定样式
                element.className = determineLineBreakClass();
                
                // 更新上一个元素类型为换行符
                lastElementType = 'linebreak';
                isLastElementLinebreak = true;
                // 纯换行不会设置“上一条文本以换行结尾”
                isLastTextEndedWithNewline = false;
                
                return element;
            }
            
            element = document.createElement('div');
            
            // 基础类名设置
            let className = `text ${item.style || ''}`;
            
            // 处理其他文本内容
            if (item.text.trim() === '' && item.text.length > 0) {
                // 空白文本但不是空字符串
                element.style.height = '1em';
                element.style.margin = '0';
            }
            
            // 如果明确指定块级显示或需要占用整行，添加block类
            if ((item.style && item.style.includes('block')) || item.width === 'auto') {
                className += ' block';
            } else {
                // 否则默认为内联显示
                className += ' text-inline';
            }
            
            element.className = className;
            
            // 设置宽度
            element.style.width = item.width ? `${item.width}ch` : 'auto';
            
            // 处理对齐方式
            if (item.align === 'center') {
                // 设置文本居中对齐
                element.style.textAlign = 'center';
                element.classList.add('text-center');
            } else if (item.align === 'right') {
                // 设置文本右对齐
                element.style.textAlign = 'right';
            }
            
            // 添加white-space: pre-wrap样式确保换行符能够正常显示
            element.style.whiteSpace = 'pre-wrap';
            // 使用textContent而不是innerText，以保留换行符
            element.textContent = item.text;
            
            // 检测是否为多行文本并添加相应的类
            if (element.classList.contains('text-inline') && item.text.includes('\n')) {
                element.classList.add('multi-line');
            }
            
            // 应用字体样式
            if (item.font) {
                element = applyFontStyle(element, item.font);
            }

            if (item.tooltip) {
                TooltipManager.attach(element, item.tooltip);
            }
            
            // 更新上一个元素类型为文本
            lastElementType = 'text';
            isLastElementLinebreak = false;
            // 设置“上一条文本是否以换行结尾”的标记
            isLastTextEndedWithNewline = !!item.text && item.text.endsWith('\n');
            break;
            
        case 'button':
            // 按钮元素在renderGameState中处理
            // 更新上一个元素类型
            lastElementType = 'button';
            isLastElementLinebreak = false;
            return null;
            
        case 'title':
            // 创建标题元素
            element = document.createElement('h2');
            element.className = `title ${item.style || ''}`;
            // 处理可能包含的<br>标签
            let processedTextTitle = item.text;
            if (processedTextTitle.includes('<br>')) {
                processedTextTitle = processedTextTitle.replace(/<br>/g, '\n');
            }
            element.textContent = processedTextTitle;
            // 更新上一个元素类型
            lastElementType = 'title';
            isLastElementLinebreak = false;
            break;
            
        case 'line':
            // 创建分隔线元素
            element = document.createElement('hr');
            element.className = `line ${item.style || ''}`;
            element.dataset.char = item.text; // 用于CSS生成特殊分隔线
            // 更新上一个元素类型
            lastElementType = 'line';
            isLastElementLinebreak = false;
            break;

        case 'line_wait': {
            console.log('[createGameElement] rendering line_wait element=', item);
            element = document.createElement('div');
            let className = `text ${item.style || ''}`;
            if ((item.style && item.style.includes('block')) || item.width === 'auto') {
                className += ' block';
            } else {
                className += ' text-inline';
            }
            element.className = className.trim();
            element.style.whiteSpace = 'pre-wrap';
            element.style.width = item.width ? `${item.width}ch` : 'auto';

            let displayText = item.text || '';
            if (displayText.includes('<br>')) {
                displayText = displayText.replace(/<br>/g, '\n');
            }
            element.textContent = displayText;

            if (item.font) {
                element = applyFontStyle(element, item.font);
            }

            if (item.tooltip) {
                TooltipManager.attach(element, item.tooltip);
            }

            const waitId = item.wait_id || `line_wait_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
            if (item.await_input === false) {
                WaitManager.resolve(waitId);
                console.log('[createGameElement] line_wait resolved immediately waitId=', waitId);
            } else {
                WaitManager.start(waitId, {
                    allowKeyboard: true,
                    bindElementClick: false
                });
                console.log('[createGameElement] line_wait waiting for input waitId=', waitId);
            }

            lastElementType = 'line_wait';
            isLastElementLinebreak = false;
            isLastTextEndedWithNewline = false;
            break;
        }
            
        case 'wait':
            element = document.createElement('div');
            let waitClassName = `text ${item.style || ''}`;
            if ((item.style && item.style.includes('block')) || item.width === 'auto') {
                waitClassName += ' block';
            } else {
                waitClassName += ' text-inline';
            }
            element.className = waitClassName.trim();
            element.style.whiteSpace = 'pre-wrap';
            element.style.width = item.width ? `${item.width}ch` : 'auto';

            let processedTextWait = item.text || '';
            if (processedTextWait.includes('<br>')) {
                processedTextWait = processedTextWait.replace(/<br>/g, '\n');
            }
            element.textContent = processedTextWait;

            if (item.font) {
                element = applyFontStyle(element, item.font);
            }

            if (item.tooltip) {
                TooltipManager.attach(element, item.tooltip);
            }

            WaitManager.start(item.wait_id || `wait_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`, {
                allowKeyboard: true,
                bindElementClick: false
            });

            lastElementType = 'wait';
            isLastElementLinebreak = false;
            break;
            
        // 新增的图片相关元素类型
        case 'image':
            // 创建图片元素
            element = document.createElement('img');
            element.className = 'game-image';
            // 使用getImagePath函数获取图片路径
            element.src = getImagePath(item.image_name);
            element.alt = item.image_name;
            
            // 如果有指定宽度，使用宽度
            if (item.width) {
                element.style.width = `${item.width}px`;
            }
            
            // 更新上一个元素类型
            lastElementType = 'image';
            isLastElementLinebreak = false;
            break;
            
        case 'bar':
            // 创建比例条容器
            element = document.createElement('div');
            element.className = 'bar-container';
            
            // 遍历并创建每个比例条元素
            if (item.bar_elements && item.bar_elements.length > 0) {
                item.bar_elements.forEach(barItem => {
                    const barElement = document.createElement('img');
                    barElement.className = 'bar-item';
                    // 使用getImagePath函数获取图片路径
                    barElement.src = getImagePath(barItem.image_name);
                    barElement.alt = barItem.image_name;
                    
                    // 如果有指定宽度，使用宽度
                    if (barItem.width) {
                        barElement.style.width = `${barItem.width}ch`;
                    }
                    
                    element.appendChild(barElement);
                });
            }
            
            // 更新上一个元素类型
            lastElementType = 'bar';
            isLastElementLinebreak = false;
            break;
            
        case 'character':
            // 创建人物图片容器
            element = document.createElement('div');
            element.className = 'character-container';
            
            // 遍历并创建每个人物图片元素
            if (item.character_elements && item.character_elements.length > 0) {
                item.character_elements.forEach(charaItem => {
                    const charaElement = document.createElement('img');
                    charaElement.className = 'character-item';
                    // 使用getImagePath函数获取图片路径
                    charaElement.src = getImagePath(charaItem.image_name);
                    charaElement.alt = charaItem.image_name;
                    
                    // 如果有指定宽度，使用宽度
                    if (charaItem.width) {
                        charaElement.style.width = `${charaItem.width}px`;
                    }
                    
                    element.appendChild(charaElement);
                });
            }
            
            // 更新上一个元素类型
            lastElementType = 'character';
            isLastElementLinebreak = false;
            break;
            
        case 'info_bar':
            // 创建带有文本和数值描述的比例条容器
            element = document.createElement('div');
            element.className = 'info-bar-container';
            
            // 遍历并创建每个子元素
            if (item.draw_list && item.draw_list.length > 0) {
                item.draw_list.forEach(drawItem => {
                    let childElement;
                    
                    // 根据子元素类型创建不同的DOM元素
                    switch(drawItem.type) {
                        case 'text':
                            childElement = document.createElement('span');
                            childElement.className = `info-bar-text ${drawItem.style || ''}`;
                            // 处理可能包含的<br>标签
                            let processedTextChild = drawItem.text;
                            if (processedTextChild.includes('<br>')) {
                                processedTextChild = processedTextChild.replace(/<br>/g, '\n');
                            }
                            childElement.textContent = processedTextChild;
                            break;
                            
                        case 'bar':
                            childElement = document.createElement('div');
                            childElement.className = 'info-bar-items';
                            
                            // 遍历并创建每个比例条元素
                            if (drawItem.bar_elements && drawItem.bar_elements.length > 0) {
                                drawItem.bar_elements.forEach(barItem => {
                                    const barElement = document.createElement('img');
                                    barElement.className = 'bar-item';
                                    // 使用getImagePath函数获取图片路径
                                    barElement.src = getImagePath(barItem.image_name);
                                    barElement.alt = barItem.image_name;
                                    
                                    // 如果有指定宽度，使用宽度
                                    if (barItem.width) {
                                        barElement.style.width = `${barItem.width}ch`;
                                    }
                                    
                                    childElement.appendChild(barElement);
                                });
                            }
                            break;
                            
                        case 'status_level':
                            childElement = document.createElement('span');
                            childElement.className = `status-level ${drawItem.style || ''}`;
                            // 处理可能包含的<br>标签
                            let processedTextStatus = drawItem.text;
                            if (processedTextStatus.includes('<br>')) {
                                processedTextStatus = processedTextStatus.replace(/<br>/g, '\n');
                            }
                            childElement.textContent = processedTextStatus;
                            break;
                    }
                    
                    if (childElement) {
                        element.appendChild(childElement);
                    }
                });
            }
            
            // 更新上一个元素类型
            lastElementType = 'info_bar';
            isLastElementLinebreak = false;
            break;
            
        case 'info_character':
            // 创建带有文本的人物图像容器
            element = document.createElement('div');
            element.className = 'info-character-container';
            
            // 遍历并创建每个子元素
            if (item.draw_list && item.draw_list.length > 0) {
                item.draw_list.forEach(drawItem => {
                    let childElement;
                    
                    // 根据子元素类型创建不同的DOM元素
                    switch(drawItem.type) {
                        case 'text':
                            childElement = document.createElement('span');
                            childElement.className = `info-character-text ${drawItem.style || ''}`;
                            // 处理可能包含的<br>标签
                            let processedTextChild = drawItem.text;
                            if (processedTextChild.includes('<br>')) {
                                processedTextChild = processedTextChild.replace(/<br>/g, '\n');
                            }
                            childElement.textContent = processedTextChild;
                            break;
                            
                        case 'bar':
                            childElement = document.createElement('div');
                            childElement.className = 'info-character-bar';
                            
                            // 遍历并创建每个比例条元素
                            if (drawItem.bar_elements && drawItem.bar_elements.length > 0) {
                                drawItem.bar_elements.forEach(barItem => {
                                    const barElement = document.createElement('img');
                                    barElement.className = 'bar-item';
                                    // 使用getImagePath函数获取图片路径
                                    barElement.src = getImagePath(barItem.image_name);
                                    barElement.alt = barItem.image_name;
                                    
                                    // 如果有指定宽度，使用宽度
                                    if (barItem.width) {
                                        barElement.style.width = `${barItem.width}px`;
                                    }
                                    
                                    childElement.appendChild(barElement);
                                });
                            }
                            break;
                    }
                    
                    if (childElement) {
                        element.appendChild(childElement);
                    }
                });
            }
            
            // 更新上一个元素类型
            lastElementType = 'info_character';
            isLastElementLinebreak = false;
            break;
            
        case 'image_button':
            // 创建图片按钮元素
            element = document.createElement('button');
            element.className = 'image-button';
            
            // 创建图片元素
            const buttonImage = document.createElement('img');
            // 使用getImagePath函数获取图片路径
            buttonImage.src = getImagePath(item.image_name);
            buttonImage.alt = item.image_name;
            
            // 如果有指定宽度，使用宽度
            if (item.width) {
                buttonImage.style.width = `${item.width}px`;
            }
            
            // 将图片添加到按钮中
            element.appendChild(buttonImage);
            
            // 设置按钮ID和点击事件
            const buttonId = item.return_text;
            element.dataset.id = buttonId;
            element.onclick = () => handleButtonClick(buttonId);

            if (item.tooltip) {
                TooltipManager.attach(element, item.tooltip); // 图片按钮同样需要工具提示
            }
            
            // 更新上一个元素类型
            lastElementType = 'image_button';
            isLastElementLinebreak = false;
            break;
            
        case 'center_image':
            // 创建居中图片容器
            element = document.createElement('div');
            element.className = 'center-image-container';
            
            // 创建图片元素
            const centerImage = document.createElement('img');
            centerImage.className = 'center-image';
            // 使用getImagePath函数获取图片路径
            centerImage.src = getImagePath(item.text); // item.text是图片名称
            centerImage.alt = item.text;
            
            // 设置样式
            element.classList.add(item.style || '');
            
            // 添加图片到容器
            element.appendChild(centerImage);
            
            // 更新上一个元素类型
            lastElementType = 'center_image';
            isLastElementLinebreak = false;
            break;
        
        case 'new_ui_container':
            // 创建新UI容器（用于IN_SCENE面板的新UI风格）
            element = document.createElement('div');
            element.className = 'new-ui-container';
            element.dataset.panelType = item.panel_type || 'default';
            
            // 渲染新UI内容
            if (item.game_state) {
                renderNewUIContent(element, item.game_state);
            }
            
            // 更新上一个元素类型
            lastElementType = 'new_ui_container';
            isLastElementLinebreak = false;
            break;
            
        default:
            console.warn('未知的元素类型:', item.type);
            return null;
    }
    
    return element;
}

/**
 * 渲染新UI内容（用于IN_SCENE面板的新UI风格）
 * @param {HTMLElement} container - 新UI容器元素
 * @param {Object} gameState - 游戏状态数据
 */
function createSceneInfoBar(sceneInfoBar) {
    const bar = document.createElement('div');
    bar.className = 'new-ui-scene-info-bar';
    
    // 左侧：场景名
    const sceneNameSpan = document.createElement('span');
    sceneNameSpan.className = 'scene-info-name';
    sceneNameSpan.textContent = sceneInfoBar.scene_name || '';
    bar.appendChild(sceneNameSpan);
    
    // 居中：游戏时间
    const gameTimeSpan = document.createElement('span');
    gameTimeSpan.className = 'scene-info-time';
    gameTimeSpan.textContent = sceneInfoBar.game_time || '';
    bar.appendChild(gameTimeSpan);
    
    return bar;
}

/**
 * 创建面板选项卡栏
 * 以网页选项卡样式展示，支持激活状态高亮
 * 
 * @param {Array} tabs - 选项卡数据数组，每个元素包含：
 *   - id: 选项卡ID
 *   - name: 显示名称
 *   - type: 类型（"main" 为主面板，"panel" 为其他面板，"temp" 为临时选项卡）
 *   - available: 是否可用
 *   - active: 是否为当前激活的选项卡
 *   - temp: 是否为临时选项卡（子面板模式下当前活动的面板）
 * @returns {HTMLElement} 选项卡栏元素
 */
function createPanelTabsBar(tabs) {
    const bar = document.createElement('div');
    bar.className = 'new-ui-panel-tabs';
    
    // 检查是否处于子面板模式（通过查找临时选项卡或禁用选项卡判断）
    const isSubPanelMode = tabs.some(tab => tab.type === 'temp' || tab.disabled);
    
    tabs.forEach(tab => {
        const btn = document.createElement('button');
        btn.className = 'panel-tab-btn';
        
        // 添加主面板特殊样式
        if (tab.type === 'main') {
            btn.classList.add('main-tab');
        }
        
        // 添加临时选项卡样式（子面板模式下当前活动的面板）
        if (tab.type === 'temp') {
            btn.classList.add('temp-tab');
        }
        
        // 添加激活状态
        if (tab.active) {
            btn.classList.add('active');
        }
        
        // 添加禁用状态
        if (!tab.available) {
            btn.classList.add('disabled');
            btn.disabled = true;
        }
        
        btn.textContent = tab.name || tab.id;
        btn.dataset.tabId = tab.id;
        
        // 禁用的选项卡不响应点击
        // 当前激活的选项卡也不响应点击（已经在这个面板了）
        // 只有可用且非激活的选项卡才响应点击
        if (tab.available && !tab.active) {
            btn.onclick = () => clickPanelTab(tab.id);
        }
        
        bar.appendChild(btn);
    });
    
    // ========== 添加文本回溯选项卡（纯前端功能） ==========
    // 仅在非子面板模式下显示
    if (!isSubPanelMode) {
        const textHistoryBtn = document.createElement('button');
        textHistoryBtn.className = 'panel-tab-btn text-history-tab';
        textHistoryBtn.textContent = '文本回溯';
        textHistoryBtn.dataset.tabId = '__text_history__';
        
        // 如果当前处于文本回溯模式，则激活
        if (isTextHistoryMode) {
            textHistoryBtn.classList.add('active');
        }
        
        textHistoryBtn.onclick = () => clickPanelTab('__text_history__');
        bar.appendChild(textHistoryBtn);
    }
    
    return bar;
}

/**
 * 切换交互对象
 */
function switchTarget(characterId) {
    if (socket && socket.connected) {
        socket.emit('switch_target', { character_id: characterId });
    }
}

/**
 * 选择交互类型
 */
function selectInteractionType(typeId) {
    if (socket && socket.connected) {
        socket.emit('select_interaction_type', { type_id: typeId });
    }
}

/**
 * 点击面板选项卡
 * 使用WebSocket事件来确保选项卡在任何面板都能正常触发
 * 
 * 注意：选项卡指令需要特殊处理，因为从非主面板点击时，
 * 当前面板的askfor_all的return_list不包含选项卡ID。
 * 因此我们使用WebSocket的execute_instruct事件，
 * 它会直接执行指令并设置刷新信号。
 */
function clickPanelTab(tabId) {
    console.log('[clickPanelTab] 点击面板选项卡，tabId:', tabId);
    
    // 文本回溯选项卡：纯前端处理，切换模式
    if (tabId === '__text_history__') {
        if (isTextHistoryMode) {
            exitTextHistoryMode();
        } else {
            enterTextHistoryMode();
        }
        return;
    }
    
    // 如果当前处于文本回溯模式，先退出
    if (isTextHistoryMode) {
        exitTextHistoryMode();
    }
    
    // 主面板选项卡使用普通按钮点击API（因为它只是保持在主面板）
    if (tabId === '__main_panel__') {
        handleButtonClick(tabId);
        return;
    }
    
    // 其他面板选项卡使用WebSocket事件，确保在任何面板都能触发
    if (socket && socket.connected) {
        socket.emit('execute_instruct', { instruct_id: tabId });
    } else {
        // 如果WebSocket不可用，回退到HTTP API
        console.warn('[clickPanelTab] WebSocket不可用，回退到HTTP API');
        handleButtonClick(tabId);
    }
}

/**
 * 获取图片路径
 * 根据图片名称查找对应的完整路径
 * 
 * @param {string} imageName - 图片名称（不含扩展名）
 * @return {string} 图片的完整路径，若未找到则返回默认路径
 */
function getImagePath(imageName) {
    // 检查字典中是否存在该图片
    if (imagePathDict[imageName]) {
        // 直接使用字典中存储的路径
        return imagePathDict[imageName];
    }
    
    // 若未找到，返回默认路径并输出警告
    console.warn(`未找到图片: ${imageName}`);
    return `/image/not_found.png`; // 默认的"图片未找到"图片
}

/**
 * 处理按钮点击
 * 发送按钮点击事件到服务器
 * 
 * @param {string} buttonId - 按钮ID
 */
function handleButtonClick(buttonId) {
    // 发送按钮点击事件到服务器
    fetch('/api/button_click', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            button_id: buttonId
        }),
    })
    .then(response => response.json())
    .then(data => {
        // 如果不使用WebSocket，且按钮点击成功，立即获取新状态
        if (data.success && !socket) {
            getGameState();
            
            // 使用智能滚动到底部功能
            scrollToBottom();
        }
    })
    .catch(error => console.error('按钮点击请求失败:', error));
}

/**
 * 发送等待响应
 * 用户点击继续时调用
 */
function sendWaitResponse() {
    // 发送等待响应到服务器
    console.log('[sendWaitResponse] POST /api/wait_response');
    return fetch('/api/wait_response', {
        method: 'POST',
    })
    .then(response => {
        console.log('[sendWaitResponse] raw response', response);
        return response.json();
    })
    .then(data => {
        // 如果不使用WebSocket，且等待响应成功，立即获取新状态
        if (data.success && !socket) {
            console.log('[sendWaitResponse] success without websocket, fetching state');
            getGameState();
            
            // 使用智能滚动到底部功能
            scrollToBottom();
        }
        return data;
    })
    .catch(error => console.error('等待响应请求失败:', error));
}

function sendSkipWaitRequest() {
    console.log('[sendSkipWaitRequest] POST /api/skip_wait');
    return fetch('/api/skip_wait', {
        method: 'POST',
    })
    .then(response => {
        console.log('[sendSkipWaitRequest] raw response', response);
        return response.json();
    })
    .then(data => {
        if (data.success && !socket) {
            console.log('[sendSkipWaitRequest] success without websocket, fetching state');
            getGameState();
        }
        return data;
    })
    .catch(error => {
        console.error('跳过等待请求失败:', error);
        throw error;
    });
}

/**
 * 初始化图片路径字典
 * 从服务器获取所有图片文件路径并构建查找字典
 * 
 * @return {Promise} - 初始化完成的Promise
 */
async function initImagePathDict() {
    try {
        // 从服务器获取所有图片文件路径的列表
        const response = await fetch('/api/get_image_paths');
        if (!response.ok) {
            throw new Error('获取图片路径列表失败');
        }
        
        const imagePaths = await response.json();
        
        // 重置字典
        imagePathDict = {};
        
        // 构建查找字典 - 修改结构以适应新的API响应格式
        imagePaths.forEach(item => {
            // 将图片名称作为键，完整路径作为值存入字典
            imagePathDict[item.name] = item.path;
        });
        
        console.log('图片路径字典初始化完成，共加载', Object.keys(imagePathDict).length, '个图片路径');
    } catch (error) {
        console.error('初始化图片路径字典出错:', error);
    }
}

/**
 * 智能滚动到底部功能
 * 确保内容完全滚动到底部，并处理可能的内容动态变化
 * 
 * @param {number} attempts - 当前尝试次数，用于递归调用
 * @param {number} maxAttempts - 最大尝试次数，防止无限递归
 */
function scrollToBottom(attempts = 0, maxAttempts = 5) {
    // 标记正在滚动
    ScrollManager.isScrolling = true;
    
    // 获取游戏容器元素
    const gameContainer = document.getElementById('game-container');
    
    // 如果找不到容器或已达到最大尝试次数，则退出
    if (!gameContainer || attempts >= maxAttempts) {
        ScrollManager.isScrolling = false;
        return;
    }
    
    // 检查是否处于子面板模式（存在.sub-panel-content元素）
    const subPanelContent = gameContainer.querySelector('.sub-panel-content');
    const isSubPanelMode = subPanelContent !== null;
    
    // 检查是否处于新UI模式（game-container包含new-ui-container）
    // 新UI模式下，game-container的overflow设为visible，需要滚动整个页面
    const hasNewUI = gameContainer.querySelector('.new-ui-container') !== null;
    
    // 根据模式选择滚动目标
    let scrollTarget, scrollBefore, scrollHeight, clientHeight;
    
    if (isSubPanelMode) {
        // 子面板模式：滚动.sub-panel-content容器
        scrollTarget = subPanelContent;
        scrollBefore = subPanelContent.scrollTop;
        scrollHeight = subPanelContent.scrollHeight;
        clientHeight = subPanelContent.clientHeight;
    } else if (hasNewUI) {
        // 新UI模式：滚动整个页面
        scrollTarget = document.documentElement;
        scrollBefore = window.pageYOffset || document.documentElement.scrollTop;
        scrollHeight = document.documentElement.scrollHeight;
        clientHeight = window.innerHeight;
    } else {
        // 传统模式：滚动game-container
        scrollTarget = gameContainer;
        scrollBefore = gameContainer.scrollTop;
        scrollHeight = gameContainer.scrollHeight;
        clientHeight = gameContainer.clientHeight;
    }
    
    // 执行滚动
    if (isSubPanelMode) {
        subPanelContent.scrollTop = scrollHeight;
    } else if (hasNewUI) {
        window.scrollTo({ top: scrollHeight, behavior: 'auto' });
    } else {
        gameContainer.scrollTop = scrollHeight;
    }
    
    // 隐藏指示器
    ScrollManager.hideIndicator();
    
    // 记录当前时间，用于调试
    const timestamp = new Date().toISOString().substr(11, 8);
    
    // 输出调试信息
    let currentScrollTop;
    if (isSubPanelMode) {
        currentScrollTop = subPanelContent.scrollTop;
    } else if (hasNewUI) {
        currentScrollTop = window.pageYOffset || document.documentElement.scrollTop;
    } else {
        currentScrollTop = gameContainer.scrollTop;
    }
    const scrollMode = isSubPanelMode ? '子面板' : (hasNewUI ? '新UI' : '传统');
    console.log(`[${timestamp}] 尝试滚动 #${attempts+1}: 模式=${scrollMode}, 高度=${scrollHeight}, 滚动位置=${currentScrollTop}`);
    
    // 使用短暂延时再次检查，确保最终滚动到位
    setTimeout(() => {
        // 获取当前滚动位置
        let currentTop, currentHeight, currentClient;
        if (isSubPanelMode) {
            currentTop = subPanelContent.scrollTop;
            currentHeight = subPanelContent.scrollHeight;
            currentClient = subPanelContent.clientHeight;
        } else if (hasNewUI) {
            currentTop = window.pageYOffset || document.documentElement.scrollTop;
            currentHeight = document.documentElement.scrollHeight;
            currentClient = window.innerHeight;
        } else {
            currentTop = gameContainer.scrollTop;
            currentHeight = gameContainer.scrollHeight;
            currentClient = gameContainer.clientHeight;
        }
        
        // 检查滚动是否已经到底（或接近底部）
        const isAtBottom = (currentHeight - currentTop - currentClient) < 20;
        ScrollManager.isAtBottom = isAtBottom;
        
        // 如果未滚动到底部，且滚动位置有变化，则再次尝试
        if (!isAtBottom && (currentTop > scrollBefore || attempts === 0)) {
            scrollToBottom(attempts + 1, maxAttempts);
        } else {
            // 最后一次强制滚动，确保到底
            if (isSubPanelMode) {
                subPanelContent.scrollTop = subPanelContent.scrollHeight;
            } else if (hasNewUI) {
                window.scrollTo({ top: document.documentElement.scrollHeight, behavior: 'auto' });
            } else {
                gameContainer.scrollTop = gameContainer.scrollHeight;
            }
            
            let finalScrollTop;
            if (isSubPanelMode) {
                finalScrollTop = subPanelContent.scrollTop;
            } else if (hasNewUI) {
                finalScrollTop = window.pageYOffset || document.documentElement.scrollTop;
            } else {
                finalScrollTop = gameContainer.scrollTop;
            }
            console.log(`[${timestamp}] 滚动完成: 最终位置=${finalScrollTop}`);
            
            // 完成滚动
            ScrollManager.isScrolling = false;
            ScrollManager.isAtBottom = true;
        }
    }, 50 * (attempts + 1)); // 随着尝试次数增加延时时间
}

/**
 * 优化图片加载完成后的滚动处理
 * 确保图片加载完成后正确计算内容高度并滚动
 */
function setupImageLoadObserver() {
    // 获取游戏容器
    const gameContainer = document.getElementById('game-container');
    
    // 创建一个交叉观察器，监控所有图片元素
    const observer = new MutationObserver((mutations) => {
        mutations.forEach(mutation => {
            if (mutation.type === 'childList') {
                // 检查是否添加了新节点
                mutation.addedNodes.forEach(node => {
                    // 如果是元素节点
                    if (node.nodeType === 1) {
                        // 查找所有图片元素
                        const images = node.querySelectorAll('img');
                        if (images.length > 0) {
                            images.forEach(img => {
                                // 如果图片已经有src但还没有完全加载
                                if (img.src && !img.complete) {
                                    img.addEventListener('load', () => {
                                        // 图片加载完成后，如果应该在底部则滚动
                                        if (ScrollManager.isAtBottom) {
                                            scrollToBottom();
                                        }
                                    });
                                }
                            });
                        }
                    }
                });
            }
        });
    });
    
    // 配置观察器
    if (gameContainer) {
        observer.observe(gameContainer, {
            childList: true,
            subtree: true
        });
        console.log('图片加载观察器已设置');
    }
}

/**
 * 新增或修改的辅助函数来发送输入到服务器
 * 
 * @param {string} inputType - 输入类型（string 或 integer）
 * @param {string|number} value - 用户输入的值
 */
function sendInputToServer(inputType, value) {
    let endpoint = '';
    if (inputType === 'string') {
        endpoint = '/api/string_input';
    } else if (inputType === 'integer') {
        endpoint = '/api/integer_input';
    } else {
        console.error('Unknown input type:', inputType);
        return;
    }

    fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ value: value }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 输入成功后，后端会清除 input_request 并更新游戏状态。
            // 如果不是WebSocket模式，前端可能需要主动获取新状态。
            if (!socket) {
                getGameState();
            }
        } else {
            console.error('Input submission failed:', data);
            alert('提交输入失败: ' + (data.error || '未知错误'));
        }
    })
    .catch(error => {
        console.error('Error submitting input:', error);
        alert('提交输入时发生错误。');
    });
}

/**
 * 新增：处理持久输入框提交的函数
 */
function handlePersistentInputSubmit() {
    const persistentInput = document.getElementById('persistent-input');
    if (!persistentInput) return;

    const inputValue = persistentInput.value.trim();
    if (inputValue === '') {
        return; // 如果输入为空，则不执行任何操作
    }

    // 1. 尝试匹配按钮
    const buttons = document.querySelectorAll('.game-button[data-id]');
    for (const button of buttons) {
        if (button.dataset.id === inputValue) {
            console.log(`Input '${inputValue}' matches button with data-id. Simulating click.`);
            handleButtonClick(inputValue);
            persistentInput.value = ''; // 清空输入框
            return;
        }
    }

    // 2. 如果没有按钮匹配，并且存在活动的通用输入请求
    if (activeInputRequest) {
        console.log(`Input '${inputValue}' submitted for activeInputRequest type: ${activeInputRequest.type}`);
        sendInputToServer(activeInputRequest.type, inputValue);
        persistentInput.value = ''; // 清空输入框
        return;
    }

    // 3. 如果既不匹配按钮，也没有活动的通用输入请求
    console.log(`Input '${inputValue}' did not match any button and no active input request.`);
    persistentInput.value = ''; // 清空输入框
}

/**
 * 初始化函数
 * 页面加载完成后初始化游戏
 */
async function initialize() {
    console.log('初始化游戏界面');
    
    // 首先初始化设备检测和横屏提示
    console.log('设备检测结果:', {
        isMobile: DeviceDetector.isMobile(),
        isTablet: DeviceDetector.isTablet(),
        isPhone: DeviceDetector.isPhone(),
        orientation: DeviceDetector.getOrientation(),
        shouldShowLandscapeHint: DeviceDetector.shouldShowLandscapeHint()
    });
    
    // 初始化横屏管理器
    LandscapeManager.init();
    
    // 初始化自动缩放管理器
    AutoScaleManager.init();
    
    // 获取持久输入框和提交按钮的引用
    const persistentInput = document.getElementById('persistent-input');
    const persistentSubmitButton = document.getElementById('persistent-submit-button');

    // 为持久输入框添加 'Enter' 键监听
    if (persistentInput) {
        persistentInput.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') {
                event.preventDefault(); // 防止默认的回车行为（如表单提交）
                handlePersistentInputSubmit();
            }
        });
    }

    // 为持久提交按钮添加点击监听
    if (persistentSubmitButton) {
        persistentSubmitButton.addEventListener('click', () => {
            handlePersistentInputSubmit();
        });
    }
    
    // 先初始化图片路径字典
    await initImagePathDict();
    
    // 初始化字体配置字典
    await initFontConfigDict();
    
    // 初始化滚动管理器
    ScrollManager.init();
    
    // 设置图片加载观察器
    setupImageLoadObserver();

    const gameContainer = document.getElementById('game-container');
    if (gameContainer) {
        gameContainer.addEventListener('contextmenu', (event) => {
            event.preventDefault();
            WaitManager.requestSkipUntilMain();
        });
        gameContainer.addEventListener('mousedown', (event) => {
            if (event.button === 2) {
                event.preventDefault();
                WaitManager.requestSkipUntilMain();
            }
        });
    }
    
    // 添加对话框键盘快捷键支持
    initDialogKeyboardShortcuts();
    
    // 优先使用WebSocket连接
    try {
        initWebSocket();
    } catch (error) {
        console.error('WebSocket初始化失败:', error);
        // WebSocket初始化失败时，回退到轮询模式
        fallbackToPolling();
    }
    
    // 首次获取游戏状态，确保有初始数据
    getGameState();
    
    // 监听窗口大小变化，重新调整滚动位置
    window.addEventListener('resize', () => {
        // 延迟执行滚动，等待DOM更新
        setTimeout(() => {
            if (ScrollManager.isAtBottom) {
                scrollToBottom();
            }
        }, 100);
    });
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', initialize);