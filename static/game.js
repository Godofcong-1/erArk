/**
 * 游戏主要JavaScript文件
 * 实现游戏状态获取、渲染和用户交互
 */

// WebSocket连接对象
let socket;

// 新增：用于存储活动输入请求和当前全局状态
let activeInputRequest = null;
let currentGlobalState = null;

// 存储所有图片路径的字典
// 键：图片名称（不含扩展名）
// 值：图片的完整相对路径
let imagePathDict = {};

// 存储所有字体配置的字典
// 键：字体名称
// 值：字体配置对象（包含前景色、背景色、字体、字体大小、加粗、下划线、斜体等属性）
let fontConfigDict = {};

// 游戏状态轮询间隔（毫秒），当WebSocket连接失败时使用
const POLL_INTERVAL = 500;

// 用于跟踪上一个元素的类型和是否需要换行
let lastElementType = null;
let forceNewLine = false; // 标记是否强制换行
let isLastElementLinebreak = false; // 标记上一个元素是否为换行符

/**
 * 高级滚动管理器
 * 负责处理滚动状态、指示器显示和事件监听
 */
const ScrollManager = {
    /**
     * 滚动状态标志
     */
    isScrolling: false,
    
    /**
     * 是否已经在底部
     */
    isAtBottom: true,
    
    /**
     * 指示器引用
     */
    indicator: null,
    
    /**
     * 初始化滚动管理器
     * 设置事件监听和初始状态
     */
    init() {
        // 获取滚动指示器元素
        this.indicator = document.getElementById('scroll-indicator');
        
        // 获取容器和按钮元素
        const gameContainer = document.getElementById('game-container');
        const scrollButton = document.getElementById('scroll-to-bottom-btn');
        
        // 监听容器滚动事件
        if (gameContainer) {
            gameContainer.addEventListener('scroll', () => {
                // 计算是否在底部(允许20px的误差)
                this.isAtBottom = (gameContainer.scrollHeight - gameContainer.scrollTop - gameContainer.clientHeight) < 20;
                
                // 根据滚动位置更新指示器显示状态
                this.updateIndicatorVisibility();
            });
            
            // 监听容器内容变化，使用防抖处理
            this.setupScrollObserver(gameContainer);
        }
        
        // 为指示器添加点击事件
        if (this.indicator) {
            this.indicator.addEventListener('click', () => {
                scrollToBottom();
                this.hideIndicator();
            });
        }
        
        // 为滚动按钮添加点击事件
        if (scrollButton) {
            scrollButton.addEventListener('click', () => {
                scrollToBottom();
            });
        }
        
        // 初始隐藏指示器
        this.hideIndicator();
        
        console.log('滚动管理器初始化完成');
    },
    
    /**
     * 设置滚动观察器
     * 使用MutationObserver监听内容变化
     * 
     * @param {HTMLElement} container - 要观察的容器元素
     */
    setupScrollObserver(container) {
        // 创建一个防抖函数
        let debounceTimer = null;
        const debounce = (callback, time) => {
            if (debounceTimer) clearTimeout(debounceTimer);
            debounceTimer = setTimeout(callback, time);
        };
        
        // 创建观察器
        const observer = new MutationObserver((mutations) => {
            // 如果已经在底部或正在滚动，则自动滚动
            if (this.isAtBottom) {
                debounce(() => scrollToBottom(), 100);
            } else {
                // 否则显示指示器
                this.showIndicator();
            }
        });
        
        // 配置观察器
        observer.observe(container, {
            childList: true,
            subtree: true,
            attributes: true,
            characterData: true
        });
    },
    
    /**
     * 显示滚动指示器
     */
    showIndicator() {
        if (this.indicator) {
            this.indicator.style.display = 'block';
        }
    },
    
    /**
     * 隐藏滚动指示器
     */
    hideIndicator() {
        if (this.indicator) {
            this.indicator.style.display = 'none';
        }
    },
    
    /**
     * 根据滚动位置更新指示器显示状态
     */
    updateIndicatorVisibility() {
        if (this.isAtBottom) {
            this.hideIndicator();
        }
    }
};

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
    loadingMessage.innerText = '实时连接失败，使用轮询模式...';
    
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
            document.getElementById('loading-message').innerText = '连接服务器失败，请刷新页面重试...';
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
    if (['title', 'line', 'wait'].includes(item.type)) {
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
    // 如果上一个元素也是换行符，则使用额外空行样式
    if (isLastElementLinebreak) {
        return 'text-break extra-space';
    }
    
    // 否则使用普通换行样式
    return 'text-break';
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
    
    // 清空内容容器
    gameContent.innerHTML = '';
    
    // 清空按钮容器（按钮将在游戏内容中直接渲染）
    gameButtons.innerHTML = '';
    // 隐藏独立的按钮容器
    gameButtons.classList.add('hidden');
    
    // 重置状态变量
    lastElementType = null;
    forceNewLine = false;
    isLastElementLinebreak = false;
    
    // 创建当前行容器
    let currentLine = document.createElement('div');
    currentLine.className = 'inline-container';
    gameContent.appendChild(currentLine);
    
    // 按顺序渲染所有元素（包括文本和按钮）
    if (state.text_content && state.text_content.length > 0) {
        // 渲染每个元素
        state.text_content.forEach((item, index) => {
            // 检查是否需要创建新行
            if (shouldCreateNewLine(item)) {
                // 创建新的行容器
                currentLine = document.createElement('div');
                currentLine.className = 'inline-container';
                gameContent.appendChild(currentLine);
            }
            
            // 创建适当的DOM元素
            let element = null;
            
            // 对按钮类型进行特殊处理
            if (item.type === 'button') {
                // 创建按钮元素
                element = document.createElement('button');
                element.className = `game-button ${item.style || 'standard'}`;
                element.innerText = item.text;
                
                // 设置按钮ID和点击事件
                const buttonId = item.return_text;
                element.dataset.id = buttonId;
                element.onclick = () => handleButtonClick(buttonId);
                
                // 设置按钮宽度
                element.style.width = item.width ? `${item.width}ch` : 'auto';

                // 如果是地图类按钮，则特殊处理
                if (item.web_type === 'map') {
                    element.className = 'map-button';
                    element.style.width = 'auto';
                }

                // 如果是左对齐按钮，则改为左对齐
                if (item.align === 'left') {
                    element.style.textAlign = 'left';
                } else if (item.align === 'right') {
                    // 如果是右对齐按钮，则改为右对齐
                    element.style.textAlign = 'right';
                }
                
                // 如果需要块级显示，添加block类
                if (item.style && item.style.includes('block')) {
                    element.classList.add('block');
                }

                // 设置字体
                if (item.font) {
                    element = applyFontStyle(element, item.font);
                }

                // 更新上一个元素类型为按钮
                lastElementType = 'button';
                isLastElementLinebreak = false;
            } else if (item.type === 'text' && item.text === '\n') {
                // 处理换行符
                element = document.createElement('br');
                
                // 根据上一个元素是否为换行符来决定样式
                element.className = determineLineBreakClass();
                
                // 标记需要在下一个元素前换行
                forceNewLine = true;
                
                // 更新上一个元素类型为换行符
                lastElementType = 'linebreak';
                isLastElementLinebreak = true;
            } else {
                // 创建其他类型的元素（文本、标题等）
                element = createGameElement(item);

                // 更新上一个元素类型
                lastElementType = item.type;
                
                // 除非当前元素是换行符，否则重置isLastElementLinebreak
                if (!(item.type === 'text' && item.text === '\n')) {
                    isLastElementLinebreak = false;
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
                element = document.createElement('br');
                
                // 根据上一个元素是否为换行符来决定样式
                element.className = determineLineBreakClass();
                
                // 更新上一个元素类型为换行符
                lastElementType = 'linebreak';
                isLastElementLinebreak = true;
                
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
            element.innerText = item.text;
            
            // 应用字体样式
            if (item.font) {
                element = applyFontStyle(element, item.font);
            }
            
            // 更新上一个元素类型为文本
            lastElementType = 'text';
            isLastElementLinebreak = false;
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
            element.innerText = item.text;
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
            
        case 'wait':
            // 创建等待元素
            element = document.createElement('div');
            element.className = 'wait-text';
            element.innerText = item.text;
            
            // 添加点击继续的提示
            const continueHint = document.createElement('div');
            continueHint.className = 'continue-hint';
            continueHint.innerText = '点击继续...';
            element.appendChild(continueHint);
            
            // 添加点击事件
            element.onclick = () => sendWaitResponse();
            
            // 更新上一个元素类型
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
                            childElement.innerText = drawItem.text;
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
                            childElement.innerText = drawItem.text;
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
                            childElement.innerText = drawItem.text;
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
            
        default:
            console.warn('未知的元素类型:', item.type);
            return null;
    }
    
    return element;
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
    fetch('/api/wait_response', {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        // 如果不使用WebSocket，且等待响应成功，立即获取新状态
        if (data.success && !socket) {
            getGameState();
            
            // 使用智能滚动到底部功能
            scrollToBottom();
        }
    })
    .catch(error => console.error('等待响应请求失败:', error));
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
    
    // 记录滚动前的位置
    const scrollBefore = gameContainer.scrollTop;
    
    // 执行滚动
    gameContainer.scrollTop = gameContainer.scrollHeight;
    
    // 隐藏指示器
    ScrollManager.hideIndicator();
    
    // 记录当前时间，用于调试
    const timestamp = new Date().toISOString().substr(11, 8);
    
    // 输出调试信息
    console.log(`[${timestamp}] 尝试滚动 #${attempts+1}: 高度=${gameContainer.scrollHeight}, 滚动位置=${gameContainer.scrollTop}`);
    
    // 使用短暂延时再次检查，确保最终滚动到位
    setTimeout(() => {
        // 检查滚动是否已经到底（或接近底部）
        const isAtBottom = (gameContainer.scrollHeight - gameContainer.scrollTop - gameContainer.clientHeight) < 20;
        ScrollManager.isAtBottom = isAtBottom;
        
        // 如果未滚动到底部，且滚动位置有变化，则再次尝试
        if (!isAtBottom && (gameContainer.scrollTop > scrollBefore || attempts === 0)) {
            scrollToBottom(attempts + 1, maxAttempts);
        } else {
            // 最后一次强制滚动，确保到底
            gameContainer.scrollTop = gameContainer.scrollHeight;
            console.log(`[${timestamp}] 滚动完成: 最终位置=${gameContainer.scrollTop}`);
            
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