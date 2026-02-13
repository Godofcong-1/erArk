/**
 * 游戏主要JavaScript文件
 * 实现游戏状态获取、渲染和用户交互
 */

/**
 * 设备检测工具
 * 检测当前设备类型和屏幕方向
 */
const DeviceDetector = {
    /**
     * 检测是否为移动设备
     * @return {boolean} 是否为移动设备
     */
    isMobile() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    },
    
    /**
     * 检测是否为平板设备
     * @return {boolean} 是否为平板设备
     */
    isTablet() {
        const userAgent = navigator.userAgent.toLowerCase();
        const isIpad = /ipad/.test(userAgent);
        const isAndroidTablet = /android/.test(userAgent) && !/mobile/.test(userAgent);
        const isLargeScreen = window.innerWidth >= 768 && window.innerWidth <= 1024;
        return isIpad || isAndroidTablet || (this.isMobile() && isLargeScreen);
    },
    
    /**
     * 检测是否为手机设备
     * @return {boolean} 是否为手机设备
     */
    isPhone() {
        return this.isMobile() && !this.isTablet();
    },
    
    /**
     * 检测当前屏幕方向
     * @return {string} 'portrait' 或 'landscape'
     */
    getOrientation() {
        if (window.screen && window.screen.orientation) {
            return window.screen.orientation.angle === 0 || window.screen.orientation.angle === 180 
                ? 'portrait' : 'landscape';
        }
        // 兼容性处理
        return window.innerHeight > window.innerWidth ? 'portrait' : 'landscape';
    },
    
    /**
     * 检测是否需要显示横屏提示
     * @return {boolean} 是否需要显示横屏提示
     */
    shouldShowLandscapeHint() {
        const orientation = this.getOrientation();
        return (this.isPhone() || this.isTablet()) && orientation === 'portrait';
    },
    
    /**
     * 获取设备屏幕信息
     * @return {object} 包含屏幕尺寸、DPI、设备类型等信息
     */
    getScreenInfo() {
        const width = window.innerWidth;
        const height = window.innerHeight;
        const dpr = window.devicePixelRatio || 1;
        const physicalWidth = width * dpr;
        const physicalHeight = height * dpr;
        
        return {
            width,
            height,
            dpr,
            physicalWidth,
            physicalHeight,
            orientation: this.getOrientation(),
            isMobile: this.isMobile(),
            isTablet: this.isTablet(),
            isPhone: this.isPhone(),
            isSmallScreen: width < 768,
            isMediumScreen: width >= 768 && width < 1024,
            isLargeScreen: width >= 1024
        };
    },
      /**
     * 获取推荐的缩放比例
     * 基于屏幕尺寸和设备类型计算合适的缩放比例
     * 注意：自动缩放最大不会超过100%，如需更大缩放请使用手动调整
     * @return {number} 推荐的缩放比例（自动缩放最大为1.0）
     */
    getRecommendedScale() {
        const screenInfo = this.getScreenInfo();
        let scale = 1.0;
        
        // 基准宽度（桌面版游戏的标准宽度）
        const baseWidth = 1200;
        const currentWidth = screenInfo.width;
        
        if (screenInfo.isPhone) {
            // 手机设备：根据屏幕宽度调整，最小0.6，最大1.0
            if (screenInfo.orientation === 'portrait') {
                scale = Math.max(0.6, Math.min(1.0, currentWidth / 600));
            } else {
                // 横屏时适当减小缩放
                scale = Math.max(0.7, Math.min(1.0, currentWidth / baseWidth));
            }
        } else if (screenInfo.isTablet) {
            // 平板设备：根据屏幕宽度调整，最小0.8，最大1.0（自动缩放不超过100%）
            scale = Math.max(0.8, Math.min(1.0, currentWidth / baseWidth));
        } else {
            // 桌面设备：根据屏幕宽度调整，自动缩放最大不超过100%
            if (currentWidth < 1024) {
                scale = Math.max(0.8, Math.min(1.0, currentWidth / baseWidth));
            } else {
                // 大屏幕桌面设备自动缩放也限制在100%
                scale = 1.0;
            }
        }
        
        // 考虑DPI因素，但确保自动缩放不超过100%
        if (screenInfo.dpr > 2) {
            scale = Math.min(1.0, scale * 1.1); // 高DPI设备略微增加缩放，但不超过100%
        }
        
        return Math.round(scale * 100) / 100; // 保留两位小数
    }
};

/**
 * 自动缩放管理器
 * 基于设备屏幕大小自动调整游戏界面缩放
 */
const AutoScaleManager = {
    /**
     * 当前缩放比例
     */
    currentScale: 1.0,
    
    /**
     * 是否启用自动缩放
     */
    autoScaleEnabled: true,
    
    /**
     * 缩放变化阈值（超过此值才应用新缩放）
     */
    scaleThreshold: 0.05,
    
    /**
     * 初始化自动缩放管理器
     */
    init() {
        this.bindEvents();
        this.initScaleControls();
        this.applyAutoScale();
        console.log('自动缩放管理器初始化完成');
    },
    
    /**
     * 绑定事件监听器
     */
    bindEvents() {
        // 监听窗口大小变化
        window.addEventListener('resize', () => {
            // 防抖处理，避免频繁调整
            clearTimeout(this.resizeTimeout);
            this.resizeTimeout = setTimeout(() => {
                if (this.autoScaleEnabled) {
                    this.applyAutoScale();
                }
            }, 300);
        });
        
        // 监听屏幕方向变化
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                if (this.autoScaleEnabled) {
                    this.applyAutoScale();
                }
            }, 500);
        });
    },
    
    /**
     * 应用自动缩放
     */
    applyAutoScale() {
        const recommendedScale = DeviceDetector.getRecommendedScale();
        const screenInfo = DeviceDetector.getScreenInfo();
        
        // 检查缩放变化是否超过阈值
        if (Math.abs(recommendedScale - this.currentScale) > this.scaleThreshold) {
            this.setScale(recommendedScale, screenInfo);
        }
    },
    
    /**
     * 设置界面缩放
     * @param {number} scale - 缩放比例
     * @param {object} screenInfo - 屏幕信息
     */
    setScale(scale, screenInfo) {
        this.currentScale = scale;
        
        const gameWrapper = document.querySelector('.game-wrapper');
        if (!gameWrapper) return;
        
        // 通过调整根字体大小来缩放所有元素，而不改变容器尺寸
        if (scale !== 1.0) {
            // 添加缩放状态类
            gameWrapper.classList.add('scaled');
            
            // 计算新的基准字体大小
            const baseFontSize = 16; // 基准字体大小（px）
            const newFontSize = baseFontSize * scale;
            
            // 应用到根元素，这样所有基于em/rem的尺寸都会按比例缩放
            document.documentElement.style.fontSize = `${newFontSize}px`;
            
            // 同时设置body的字体大小，确保兼容性
            document.body.style.fontSize = `${newFontSize}px`;
            
        } else {
            // 重置样式
            gameWrapper.classList.remove('scaled');
            document.documentElement.style.fontSize = '';
            document.body.style.fontSize = '';
        }
        
        console.log(`应用缩放: ${scale} (设备: ${screenInfo.isPhone ? '手机' : screenInfo.isTablet ? '平板' : '桌面'}, 尺寸: ${screenInfo.width}x${screenInfo.height})`);
        
        // 触发缩放变化事件
        this.onScaleChanged(scale, screenInfo);
    },
    
    /**
     * 缩放变化回调
     * @param {number} scale - 新的缩放比例
     * @param {object} screenInfo - 屏幕信息
     */
    onScaleChanged(scale, screenInfo) {
        // 缩放变化后，可能需要重新调整滚动位置
        setTimeout(() => {
            if (window.ScrollManager && ScrollManager.isAtBottom) {
                scrollToBottom();
            }
        }, 100);
        
        // 发送自定义事件，允许其他组件响应缩放变化
        const event = new CustomEvent('scaleChanged', {
            detail: { scale, screenInfo }
        });
        window.dispatchEvent(event);
    },
    
    /**
     * 手动设置缩放比例
     * @param {number} scale - 缩放比例
     */
    setManualScale(scale) {
        this.autoScaleEnabled = false;
        const screenInfo = DeviceDetector.getScreenInfo();
        this.setScale(scale, screenInfo);
    },
    
    /**
     * 启用自动缩放
     */
    enableAutoScale() {
        this.autoScaleEnabled = true;
        this.applyAutoScale();
    },
    
    /**
     * 禁用自动缩放
     */
    disableAutoScale() {
        this.autoScaleEnabled = false;
    },
    
    /**
     * 重置缩放到1.0
     */
    resetScale() {
        const screenInfo = DeviceDetector.getScreenInfo();
        this.setScale(1.0, screenInfo);
    },
    
    /**
     * 获取当前缩放比例
     * @return {number} 当前缩放比例
     */
    getCurrentScale() {
        return this.currentScale;
    },
    
    /**
     * 初始化缩放控制面板
     */
    initScaleControls() {
        const resetBtn = document.getElementById('scale-reset-btn');
        const decreaseBtn = document.getElementById('scale-decrease-btn');
        const increaseBtn = document.getElementById('scale-increase-btn');
        const autoToggleBtn = document.getElementById('auto-scale-toggle-btn');
        const scaleDisplay = document.getElementById('scale-display');
        
        // 重置缩放按钮
        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                this.resetScale();
                this.updateScaleDisplay();
            });
        }
        
        // 缩小按钮
        if (decreaseBtn) {
            decreaseBtn.addEventListener('click', () => {
                const newScale = Math.max(0.5, this.currentScale - 0.1);
                this.setManualScale(newScale);
                this.updateScaleDisplay();
            });
        }
        
        // 放大按钮
        if (increaseBtn) {
            increaseBtn.addEventListener('click', () => {
                const newScale = Math.min(2.0, this.currentScale + 0.1);
                this.setManualScale(newScale);
                this.updateScaleDisplay();
            });
        }
        
        // 自动缩放切换按钮
        if (autoToggleBtn) {
            autoToggleBtn.addEventListener('click', () => {
                if (this.autoScaleEnabled) {
                    this.disableAutoScale();
                    autoToggleBtn.classList.remove('active');
                    autoToggleBtn.textContent = '手动';
                } else {
                    this.enableAutoScale();
                    autoToggleBtn.classList.add('active');
                    autoToggleBtn.textContent = '自动';
                }
                this.updateScaleDisplay();
            });
            
            // 初始状态
            if (this.autoScaleEnabled) {
                autoToggleBtn.classList.add('active');
                autoToggleBtn.textContent = '自动';
            }
        }
        
        // 监听缩放变化事件来更新显示
        window.addEventListener('scaleChanged', () => {
            this.updateScaleDisplay();
        });
        
        // 初始更新显示
        this.updateScaleDisplay();
    },
    
    /**
     * 更新缩放显示
     */
    updateScaleDisplay() {
        const scaleDisplay = document.getElementById('scale-display');
        if (scaleDisplay) {
            const percentage = Math.round(this.currentScale * 100);
            scaleDisplay.textContent = `${percentage}%`;
        }
    }
};

/**
 * 工具提示管理器
 * 管理按钮悬停时的提示文本展示
 */
const TooltipManager = (() => {
    /**
     * 工具提示管理器
     * 功能：负责在 Web 端按钮悬停、聚焦或触摸时显示说明文本
     * 输入：外部通过 attach 传入 DOM 元素与文本
     * 输出：在页面上渲染/隐藏提示浮层，无返回值
     */
    const SHOW_DELAY = 300; // 提示显示前的延迟（毫秒），避免轻微划过立即触发
    const HIDE_DELAY = 90; // 鼠标离开后的延迟，提供更顺滑的关闭体验
    let tooltipEl = null; // 当前提示浮层 DOM 引用
    let showTimer = null; // 延迟显示的定时器句柄
    let hideTimer = null; // 延迟隐藏的定时器句柄

    const ensureElement = () => {
        // 确保提示浮层只创建一次，后续复用同一元素
        if (tooltipEl) {
            return;
        }
        tooltipEl = document.createElement('div');
        tooltipEl.className = 'tooltip-layer';
        tooltipEl.setAttribute('role', 'tooltip');
        tooltipEl.style.left = '0px';
        tooltipEl.style.top = '0px';
        document.body.appendChild(tooltipEl);
    };

    const clearTimers = () => {
        // 清除所有定时器，防止快速进出造成状态错乱
        if (showTimer !== null) {
            window.clearTimeout(showTimer);
            showTimer = null;
        }
        if (hideTimer !== null) {
            window.clearTimeout(hideTimer);
            hideTimer = null;
        }
    };

    const positionTooltip = (clientX, clientY) => {
        // 根据鼠标或触摸位置动态调整提示浮层，避免溢出屏幕
        if (!tooltipEl) {
            return;
        }
        const offsetX = 16; // 水平方向偏移，保证浮层不遮挡指针
        const offsetY = 20; // 垂直方向偏移，让浮层位于指针下方
        let left = clientX + offsetX;
        let top = clientY + offsetY;

        const rect = tooltipEl.getBoundingClientRect();
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;

        if (left + rect.width + 16 > viewportWidth) {
            left = Math.max(16, viewportWidth - rect.width - 16);
        }
        if (top + rect.height + 16 > viewportHeight) {
            top = clientY - rect.height - offsetY;
            if (top < 16) {
                top = Math.max(16, viewportHeight - rect.height - 16);
            }
        }

        tooltipEl.style.left = `${left}px`;
        tooltipEl.style.top = `${top}px`;
    };

    const showTooltip = (text, clientX, clientY) => {
        // 真正渲染提示浮层，并在必要时重新定位
        const normalized = typeof text === 'string' ? text.trim() : '';
        if (!normalized) {
            hideImmediate();
            return;
        }
        ensureElement();
        tooltipEl.textContent = normalized;
        tooltipEl.classList.add('visible');
        tooltipEl.style.left = '0px';
        tooltipEl.style.top = '0px';
        positionTooltip(clientX, clientY);
    };

    const scheduleShow = (text, clientX, clientY) => {
        // 先清除旧定时器，再安排新的延迟显示
        clearTimers();
        showTimer = window.setTimeout(() => {
            showTooltip(text, clientX, clientY);
        }, SHOW_DELAY);
    };

    const hideImmediate = () => {
        // 立即隐藏提示浮层，并清理状态
        clearTimers();
        if (tooltipEl) {
            tooltipEl.classList.remove('visible');
        }
    };

    const hideWithDelay = () => {
        // 提供一点缓冲时间，避免快速移入移出造成闪烁
        if (hideTimer !== null) {
            window.clearTimeout(hideTimer);
        }
        hideTimer = window.setTimeout(() => {
            hideImmediate();
        }, HIDE_DELAY);
    };

    const attach = (element, text) => {
        // 功能：为指定元素绑定提示逻辑
        // 输入：element 为目标 DOM 节点，text 为提示文本
        // 输出：无返回值，内部注册事件监听
        const normalized = typeof text === 'string' ? text.trim() : '';
        if (!element || !normalized) {
            return;
        }
        if (element.dataset.tooltipBound === '1') {
            return; // 避免重复绑定多套监听
        }

        const handleMouseEnter = (event) => {
            // 鼠标进入时启动延迟显示
            scheduleShow(normalized, event.clientX, event.clientY);
        };

        const handleMouseMove = (event) => {
            // 鼠标移动时持续更新浮层位置
            if (tooltipEl && tooltipEl.classList.contains('visible')) {
                positionTooltip(event.clientX, event.clientY);
            }
        };

        const handleMouseLeave = () => {
            // 鼠标离开时延迟关闭浮层
            hideWithDelay();
        };

        const handleFocus = () => {
            // 键盘焦点也需要显示提示，使用元素中心位置
            const rect = element.getBoundingClientRect();
            scheduleShow(normalized, rect.left + rect.width / 2, rect.top);
        };

        const handleBlur = () => {
            hideImmediate();
        };

        const handleClick = () => {
            // 点击按钮后立即隐藏，避免遮挡
            hideImmediate();
        };

        const handleTouchStart = (event) => {
            // 移动端长按或触摸时同样展示提示
            if (!event.touches || event.touches.length === 0) {
                return;
            }
            const touch = event.touches[0];
            scheduleShow(normalized, touch.clientX, touch.clientY);
        };

        const handleTouchMove = (event) => {
            if (!tooltipEl || !tooltipEl.classList.contains('visible')) {
                return;
            }
            if (event.touches && event.touches.length > 0) {
                const touch = event.touches[0];
                positionTooltip(touch.clientX, touch.clientY);
            }
        };

        const handleTouchEnd = () => {
            hideImmediate();
        };

        element.addEventListener('mouseenter', handleMouseEnter);
        element.addEventListener('mousemove', handleMouseMove);
        element.addEventListener('mouseleave', handleMouseLeave);
        element.addEventListener('focus', handleFocus);
        element.addEventListener('blur', handleBlur);
        element.addEventListener('click', handleClick);
        element.addEventListener('touchstart', handleTouchStart, { passive: true });
        element.addEventListener('touchmove', handleTouchMove, { passive: true });
        element.addEventListener('touchend', handleTouchEnd);
        element.addEventListener('touchcancel', handleTouchEnd);

        element.dataset.tooltipBound = '1'; // 标记已绑定，避免重复注册
        if (!element.hasAttribute('aria-label')) {
            element.setAttribute('aria-label', normalized); // 补充无障碍信息
        }
    };

    return {
        attach,
        hideImmediate,
    };
})();

/**
 * 横屏提示管理器
 * 管理横屏提示的显示和隐藏
 */
const LandscapeManager = {
    /**
     * 初始化横屏提示
     */
    init() {
        this.createLandscapeOverlay();
        this.bindEvents();
        this.checkOrientation();
    },
    
    /**
     * 创建横屏提示覆盖层
     */
    createLandscapeOverlay() {
        // 检查是否已存在覆盖层
        if (document.getElementById('landscape-overlay')) {
            return;
        }
        
        const overlay = document.createElement('div');
        overlay.id = 'landscape-overlay';
        overlay.className = 'landscape-overlay';
        
        overlay.innerHTML = `
            <h2>建议横屏游玩</h2>
            <div class="rotate-icon">📱</div>
            <p>为了获得更好的游戏体验，建议将设备旋转至横屏模式。</p>
            <p>横屏模式下可以显示更多内容，操作也更加便利。</p>
        `;
        
        document.body.appendChild(overlay);
    },
    
    /**
     * 绑定方向变化事件
     */
    bindEvents() {
        // 监听屏幕方向变化
        window.addEventListener('orientationchange', () => {
            // 延迟检查，等待方向变化完成
            setTimeout(() => {
                this.checkOrientation();
            }, 500);
        });
        
        // 监听窗口大小变化（兼容性处理）
        window.addEventListener('resize', () => {
            // 防抖处理
            clearTimeout(this.resizeTimeout);
            this.resizeTimeout = setTimeout(() => {
                this.checkOrientation();
            }, 300);
        });
    },
    
    /**
     * 检查屏幕方向并显示/隐藏提示
     */
    checkOrientation() {
        const overlay = document.getElementById('landscape-overlay');
        const gameWrapper = document.querySelector('.game-wrapper');
        
        if (!overlay || !gameWrapper) {
            return;
        }
        
        if (DeviceDetector.shouldShowLandscapeHint()) {
            // 显示横屏提示
            this.showLandscapeHint(overlay, gameWrapper);
        } else {
            // 隐藏横屏提示
            this.hideLandscapeHint(overlay, gameWrapper);
        }
    },
    
    /**
     * 显示横屏提示
     * @param {HTMLElement} overlay - 覆盖层元素
     * @param {HTMLElement} gameWrapper - 游戏主容器元素
     */
    showLandscapeHint(overlay, gameWrapper) {
        // 根据设备类型添加相应的CSS类
        overlay.className = 'landscape-overlay';
        
        if (DeviceDetector.isPhone()) {
            overlay.classList.add('show-for-phone');
        } else if (DeviceDetector.isTablet()) {
            overlay.classList.add('show-for-tablet');
        } else {
            overlay.classList.add('show-for-mobile');
        }
        
        // 隐藏游戏主内容
        gameWrapper.classList.add('hide-for-portrait');
        
        console.log('显示横屏提示 - 设备类型:', DeviceDetector.isPhone() ? '手机' : '平板');
    },
    
    /**
     * 隐藏横屏提示
     * @param {HTMLElement} overlay - 覆盖层元素
     * @param {HTMLElement} gameWrapper - 游戏主容器元素
     */
    hideLandscapeHint(overlay, gameWrapper) {
        // 移除所有显示类
        overlay.className = 'landscape-overlay';
        
        // 显示游戏主内容
        gameWrapper.classList.remove('hide-for-portrait');
        
        console.log('隐藏横屏提示 - 当前方向:', DeviceDetector.getOrientation());
    }
};

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
// 新增：标记上一条“文本元素”是否以换行符结尾，用于将紧随其后的 line_feed 作为“空白行”渲染
let isLastTextEndedWithNewline = false;

// 场景角色头像区分页管理
let sceneCharactersCurrentPage = 0;  // 当前页码（从0开始）
let sceneCharactersData = [];        // 当前场景的角色数据
let sceneCharactersMinorDialogs = []; // 当前场景的小对话框数据

/**
 * 等待管理器
 * 负责处理需要用户确认后继续的绘制元素
 */
const WaitManager = {
    currentWaitId: null,
    isWaiting: false,
    pendingElement: null,
    pendingHint: null,
    allowKeyboard: true,
    waitResponsePending: false,
    clickHandler: null,
    keyHandler: null,
    globalClickHandler: null,
    skipMode: false,
    skipRequestPending: false,

    /**
     * 渲染开始前调用，移除旧DOM引用但保留等待状态
     */
    prepareForRender() {
        if (this.pendingElement && this.clickHandler) {
            this.pendingElement.removeEventListener('click', this.clickHandler);
        }
        this.pendingElement = null;
        this.pendingHint = null;
    },

    /**
     * 启动或更新等待状态
     * @param {string} waitId 唯一等待编号
     * @param {object} options 配置项
     */
    start(waitId, options = {}) {
        if (!waitId) {
            waitId = `wait-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
        }
        if (options.awaitInput === false) {
            console.log('[WaitManager] awaiting skipped, auto-resolving waitId=', waitId);
            this.resolve(waitId);
            return;
        }

        if (this.currentWaitId !== waitId) {
            this.cleanup();
            this.currentWaitId = waitId;
        }

        this.isWaiting = true;
        this.prepareForRender();

        console.log('[WaitManager] start waitId=', waitId, 'allowKeyboard=', options.allowKeyboard !== false, 'skipMode=', this.skipMode);

        this.pendingElement = options.element || null;
        this.pendingHint = options.hintElement || null;
        this.allowKeyboard = options.allowKeyboard !== false;

        const skipActive = this.skipMode;

        if (!skipActive && this.pendingElement) {
            this.pendingElement.classList.add('waiting-active');
        }
        if (!skipActive && this.pendingHint) {
            this.pendingHint.classList.add('active');
        }

        const shouldBindElementClick = !skipActive && this.pendingElement && options.bindElementClick !== false;
        if (shouldBindElementClick) {
            this.clickHandler = () => this.trigger();
            this.pendingElement.addEventListener('click', this.clickHandler);
        }

        if (!this.globalClickHandler) {
            this.globalClickHandler = (event) => {
                if (!this.isWaiting || this.waitResponsePending) {
                    return;
                }
                if (event.target && typeof event.target.closest === 'function') {
                    if (event.target.closest('.game-button')) {
                        return;
                    }
                }
                const container = document.getElementById('game-container');
                if (container && !container.contains(event.target)) {
                    return;
                }
                this.trigger();
            };
            document.addEventListener('click', this.globalClickHandler);
        }

        if (!skipActive && !this.keyHandler && this.allowKeyboard) {
            this.keyHandler = (event) => {
                if (!this.isWaiting || !this.allowKeyboard) {
                    return;
                }
                const tagName = event.target && event.target.tagName;
                if (tagName && ['INPUT', 'TEXTAREA'].includes(tagName)) {
                    return;
                }
                if (event.key === 'Enter' || event.key === ' ' || event.key === 'Spacebar') {
                    event.preventDefault();
                    this.trigger();
                }
            };
            document.addEventListener('keydown', this.keyHandler);
        }

        if (skipActive && !this.waitResponsePending) {
            console.log('[WaitManager] skipMode active, auto-trigger waitId=', waitId);
            this.trigger();
        }
    },

    /**
     * 标记等待完成
     * @param {string} waitId 唯一等待编号
     */
    resolve(waitId) {
        if (waitId && this.currentWaitId && this.currentWaitId !== waitId) {
            return;
        }
        console.log('[WaitManager] resolve waitId=', this.currentWaitId);
        this.cleanup();
    },

    /**
     * 触发继续
     */
    trigger() {
        if (this.waitResponsePending) {
            return;
        }
        this.waitResponsePending = true;
        console.log('[WaitManager] trigger waitId=', this.currentWaitId);
        if (this.pendingElement) {
            this.pendingElement.classList.add('waiting-submitted');
        }
        sendWaitResponse()
            .finally(() => {
                this.waitResponsePending = false;
            });
    },

    /**
     * 清理当前等待状态
     */
    cleanup() {
        if (this.pendingElement && this.clickHandler) {
            this.pendingElement.removeEventListener('click', this.clickHandler);
        }
        if (this.pendingElement) {
            this.pendingElement.classList.remove('waiting-active', 'waiting-submitted');
        }
        if (this.pendingHint) {
            this.pendingHint.classList.remove('active');
        }
        if (this.keyHandler) {
            document.removeEventListener('keydown', this.keyHandler);
        }

        this.pendingElement = null;
        this.pendingHint = null;
        this.clickHandler = null;
        this.keyHandler = null;
        if (this.globalClickHandler) {
            document.removeEventListener('click', this.globalClickHandler);
            this.globalClickHandler = null;
        }
        this.currentWaitId = null;
        this.isWaiting = false;
        this.waitResponsePending = false;
    },

    /**
     * 请求跳过所有等待直到主界面
     */
    requestSkipUntilMain() {
        if (this.skipMode && this.isWaiting && !this.waitResponsePending) {
            this.trigger();
        }
        if (this.skipRequestPending) {
            return;
        }
        this.skipMode = true;
        this.skipRequestPending = true;
        sendSkipWaitRequest()
            .then((data) => {
                if (this.isWaiting && !this.waitResponsePending) {
                    this.trigger();
                }
                return data;
            })
            .catch((error) => {
                console.error('[WaitManager] skip request failed', error);
            })
            .finally(() => {
                this.skipRequestPending = false;
            });
    }
};

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
    const skipWaitButton = document.getElementById('skip-wait-btn');
        
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

        if (skipWaitButton) {
            skipWaitButton.addEventListener('click', () => {
                WaitManager.requestSkipUntilMain();
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
        }
    });
    
    // 接收对话跳过结果事件
    socket.on('dialogs_skipped', (data) => {
        console.log('收到对话跳过结果:', data);
        if (data.success && data.dialog) {
            updateDialogBox(data.dialog);
        }
    });
    
    // 接收对话框状态更新事件（由talk.py触发）
    socket.on('dialog_state_update', (data) => {
        console.log('收到对话框状态更新:', data);
        if (data.success && data.dialog) {
            updateDialogBox(data.dialog);
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
    
    // 重置状态变量
    lastElementType = null;
    forceNewLine = false;
    isLastElementLinebreak = false;
    isLastTextEndedWithNewline = false;
    
    // 创建当前行容器
    let currentLine = document.createElement('div');
    currentLine.className = 'inline-container';
    gameContent.appendChild(currentLine);
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
                gameContent.appendChild(currentLine);
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
                        gameContent.appendChild(currentLine);
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
    if (state.dialog) {
        updateDialogBox(state.dialog);
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
        if (data.success) {
            refreshGameState();
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
function createAvatarPanel(characters, minorDialogs = []) {
    // 保存数据到全局变量
    sceneCharactersData = characters || [];
    sceneCharactersMinorDialogs = minorDialogs || [];
    
    const panel = document.createElement('div');
    panel.className = 'new-ui-avatar-panel';
    
    // 计算分页
    const pageSize = 5;
    const totalCharacters = sceneCharactersData.length;
    const totalPages = Math.ceil(totalCharacters / pageSize);
    
    // 确保当前页码有效
    if (sceneCharactersCurrentPage >= totalPages) {
        sceneCharactersCurrentPage = 0;
    }
    if (sceneCharactersCurrentPage < 0) {
        sceneCharactersCurrentPage = totalPages > 0 ? totalPages - 1 : 0;
    }
    
    // 获取当前页的角色
    const startIndex = sceneCharactersCurrentPage * pageSize;
    const endIndex = Math.min(startIndex + pageSize, totalCharacters);
    const currentPageCharacters = sceneCharactersData.slice(startIndex, endIndex);
    
    // 创建头像容器
    const avatarsContainer = document.createElement('div');
    avatarsContainer.className = 'avatar-items-container';
    
    currentPageCharacters.forEach(char => {
        const avatarItem = document.createElement('div');
        avatarItem.className = 'avatar-item';
        avatarItem.dataset.characterId = char.id;
        
        // 头像名称
        const avatarName = document.createElement('span');
        avatarName.className = 'avatar-name';
        avatarName.textContent = char.name || '';
        avatarItem.appendChild(avatarName);
        
        // 检查是否有该角色的小对话框
        const minorDialog = sceneCharactersMinorDialogs.find(d => d.character_id === char.id);
        if (minorDialog) {
            const miniDialog = document.createElement('div');
            miniDialog.className = 'avatar-mini-dialog';
            miniDialog.textContent = minorDialog.text;
            miniDialog.title = minorDialog.full_text || minorDialog.text; // 鼠标悬停显示完整文本
            avatarItem.appendChild(miniDialog);
        }
        
        avatarItem.onclick = () => switchTarget(char.id);
        avatarsContainer.appendChild(avatarItem);
    });
    
    panel.appendChild(avatarsContainer);
    
    // 当角色总数大于5时显示分页按钮
    if (totalCharacters > pageSize) {
        const paginationRow = document.createElement('div');
        paginationRow.className = 'avatar-pagination-row';
        
        // 上一页按钮
        const prevBtn = document.createElement('button');
        prevBtn.className = 'avatar-page-btn';
        prevBtn.textContent = '上一页';
        prevBtn.onclick = (e) => {
            e.stopPropagation();
            sceneCharactersPrevPage();
        };
        paginationRow.appendChild(prevBtn);
        
        // 下一页按钮
        const nextBtn = document.createElement('button');
        nextBtn.className = 'avatar-page-btn';
        nextBtn.textContent = '下一页';
        nextBtn.onclick = (e) => {
            e.stopPropagation();
            sceneCharactersNextPage();
        };
        paginationRow.appendChild(nextBtn);
        
        // 显示全部按钮
        const showAllBtn = document.createElement('button');
        showAllBtn.className = 'avatar-page-btn avatar-show-all-btn';
        showAllBtn.textContent = '显示全部';
        showAllBtn.onclick = (e) => {
            e.stopPropagation();
            showAllSceneCharacters();
        };
        paginationRow.appendChild(showAllBtn);
        
        panel.appendChild(paginationRow);
    }
    
    return panel;
}

/**
 * 场景角色头像区翻到上一页
 */
function sceneCharactersPrevPage() {
    const pageSize = 5;
    const totalPages = Math.ceil(sceneCharactersData.length / pageSize);
    if (totalPages <= 1) return;
    
    // 循环翻页：第一页的上一页是最后一页
    sceneCharactersCurrentPage--;
    if (sceneCharactersCurrentPage < 0) {
        sceneCharactersCurrentPage = totalPages - 1;
    }
    
    refreshAvatarPanel();
}

/**
 * 场景角色头像区翻到下一页
 */
function sceneCharactersNextPage() {
    const pageSize = 5;
    const totalPages = Math.ceil(sceneCharactersData.length / pageSize);
    if (totalPages <= 1) return;
    
    // 循环翻页：最后一页的下一页是第一页
    sceneCharactersCurrentPage++;
    if (sceneCharactersCurrentPage >= totalPages) {
        sceneCharactersCurrentPage = 0;
    }
    
    refreshAvatarPanel();
}

/**
 * 显示场景内全部角色面板
 */
function showAllSceneCharacters() {
    // 向后端请求所有场景角色
    if (socket && socket.connected) {
        socket.emit('get_all_scene_characters', {});
    }
}

/**
 * 创建并显示全部角色面板（弹出层）
 * @param {Array} characters - 角色数据列表
 */
function createAllCharactersPanel(characters) {
    // 如果已存在面板，先移除
    const existingPanel = document.querySelector('.all-characters-overlay');
    if (existingPanel) {
        existingPanel.remove();
    }
    
    // 创建遮罩层
    const overlay = document.createElement('div');
    overlay.className = 'all-characters-overlay';
    overlay.onclick = (e) => {
        if (e.target === overlay) {
            closeAllCharactersPanel();
        }
    };
    
    // 创建面板容器
    const panel = document.createElement('div');
    panel.className = 'all-characters-panel';
    
    // 创建标题栏
    const header = document.createElement('div');
    header.className = 'all-characters-header';
    
    const title = document.createElement('span');
    title.className = 'all-characters-title';
    title.textContent = `场景内全部角色 (${characters.length}人)`;
    header.appendChild(title);
    
    const closeBtn = document.createElement('button');
    closeBtn.className = 'all-characters-close-btn';
    closeBtn.textContent = '×';
    closeBtn.onclick = closeAllCharactersPanel;
    header.appendChild(closeBtn);
    
    panel.appendChild(header);
    
    // 创建角色网格容器
    const gridContainer = document.createElement('div');
    gridContainer.className = 'all-characters-grid-container';
    
    const grid = document.createElement('div');
    grid.className = 'all-characters-grid';
    
    // 渲染所有角色
    characters.forEach(char => {
        const avatarItem = document.createElement('div');
        avatarItem.className = 'all-characters-item';
        avatarItem.dataset.characterId = char.id;
        
        // 头像名称
        const avatarName = document.createElement('span');
        avatarName.className = 'all-characters-name';
        avatarName.textContent = char.name || '';
        avatarItem.appendChild(avatarName);
        
        // 点击切换交互对象并关闭面板
        avatarItem.onclick = () => {
            switchTarget(char.id);
            closeAllCharactersPanel();
        };
        
        grid.appendChild(avatarItem);
    });
    
    gridContainer.appendChild(grid);
    panel.appendChild(gridContainer);
    
    overlay.appendChild(panel);
    document.body.appendChild(overlay);
}

/**
 * 关闭全部角色面板
 */
function closeAllCharactersPanel() {
    const overlay = document.querySelector('.all-characters-overlay');
    if (overlay) {
        overlay.remove();
    }
}

/**
 * 刷新头像面板（分页后重新渲染）
 */
function refreshAvatarPanel() {
    const oldPanel = document.querySelector('.new-ui-avatar-panel');
    if (!oldPanel) return;
    
    const newPanel = createAvatarPanel(sceneCharactersData, sceneCharactersMinorDialogs);
    oldPanel.replaceWith(newPanel);
}

/**
 * 更新头像下方的小对话框
 * @param {Array} minorDialogs - 小对话框数据列表
 */
function updateMinorDialogs(minorDialogs) {
    if (!minorDialogs || minorDialogs.length === 0) return;
    
    const avatarPanel = document.querySelector('.new-ui-avatar-panel');
    if (!avatarPanel) return;
    
    // 遍历每个小对话框数据
    minorDialogs.forEach(dialog => {
        const avatarItem = avatarPanel.querySelector(`[data-character-id="${dialog.character_id}"]`);
        if (avatarItem) {
            // 移除旧的小对话框
            const oldDialog = avatarItem.querySelector('.avatar-mini-dialog');
            if (oldDialog) oldDialog.remove();
            
            // 创建新的小对话框
            const miniDialog = document.createElement('div');
            miniDialog.className = 'avatar-mini-dialog';
            miniDialog.textContent = dialog.text;
            miniDialog.title = dialog.full_text || dialog.text;
            avatarItem.appendChild(miniDialog);
        }
    });
}

/**
 * 创建交互类型面板（大类选项卡 + 小类按钮列表）
 * 
 * 数据结构：
 * - types.major_types: 大类列表，每个包含 {id, name, selected, minor_types}
 * - types.minor_types: 当前大类下的小类列表
 * - types.current_major_type: 当前选中的大类ID
 * - types.current_minor_type: 当前选中的小类ID
 */
function createInteractionTypePanel(types) {
    const panel = document.createElement('div');
    panel.className = 'new-ui-interaction-panel';
    
    // Helper for icons - 使用图片图标（2026-02-13更新）
    const getIconHtml = (typeId) => {
        // 交互大类ID到图标文件名的映射
        const iconFiles = {
            'mouth': '嘴部.png',
            'hand': '手部.png',
            'sex': '性爱.png',
            'penis': '阴茎.png',
            'tool': '道具.png',
            'arts': '源石技艺.png',
            'other': '设置.png'
        };
        
        const iconFile = iconFiles[String(typeId)];
        if (iconFile) {
            // 返回图片HTML，图片路径为 /static/assets/ui/
            return `<img src="/static/assets/ui/${encodeURIComponent(iconFile)}" alt="${typeId}" class="interaction-icon-img">`;
        }
        // 如果没有对应图标文件，返回默认圆点
        return '<span class="interaction-icon-default">●</span>';
    };
    
    // 处理旧版数据格式（数组格式）的兼容
    if (Array.isArray(types)) {
        // 旧版格式，保持向后兼容
        types.forEach(type => {
            const btn = document.createElement('button');
            btn.className = 'interaction-type-btn';
            btn.textContent = type.name || type.id;
            btn.dataset.typeId = type.id;
            btn.onclick = () => selectInteractionType(type.id);
            panel.appendChild(btn);
        });
        return panel;
    }
    
    // 新版数据格式（大类/小类嵌套结构）
    const majorTypes = types.major_types || [];
    const currentMajorType = types.current_major_type;
    const currentMinorType = types.current_minor_type;
    
    // 创建列表容器（用于3D透视）
    const list = document.createElement('div');
    list.className = 'interaction-type-list';
    panel.appendChild(list);
    
    // 查找当前激活的大类
    const currentMajor = majorTypes.find(m => {
        const mId = Number(m.id);
        const targetId = Number(currentMajorType);
        // 兼容字符串和数字比较
        return m.selected === true || mId === targetId || String(m.id) === String(currentMajorType);
    });
    
    majorTypes.forEach(majorType => {
        // 1. 创建大类卡片
        const majorCard = document.createElement('div');
        majorCard.className = 'interaction-card major-card';
        majorCard.dataset.id = majorType.id; // Store ID for lookup
        
        // 兼容类型比较
        const isMajorActive = (currentMajor && String(currentMajor.id) === String(majorType.id));
        if (isMajorActive) {
            majorCard.classList.add('active');
        }
        
        majorCard.innerHTML = `
            <span class="icon">${getIconHtml(majorType.id)}</span>
            <div class="label-group">
                <span class="name-cn">${majorType.name}</span>
                <span class="name-en">${String(majorType.id).toUpperCase()}</span>
            </div>
        `;
        
        majorCard.onclick = () => {
             // 显式检查 active 类，不依赖 isMajorActive 变量（闭包可能过期）
             if (majorCard.classList.contains('active')) {
                console.log('重复点击大类按钮，清空选择');
                clearInteractionSelection();
             } else {
                selectMajorType(majorType.id);
             }
        };
        
        list.appendChild(majorCard);
        
        // 2. 如果是大类激活状态，且有小类数据，渲染小类列表（手风琴效果）
        if (isMajorActive) {
            // 优先使用currentMajor中的minor_types，若无则使用types.minor_types (兼容旧逻辑)
            const minorTypes = currentMajor.minor_types || (types.minor_types || []);
            
            if (minorTypes.length > 0) {
                 const minorContainer = document.createElement('div');
                 minorContainer.className = 'interaction-minor-list';
                 
                 minorTypes.forEach(minorType => {
                      const minorCard = document.createElement('div');
                      minorCard.className = 'interaction-card minor-card';
                      minorCard.dataset.id = minorType.id; // 存储小类ID用于响应匹配
                      
                      // 检查是否激活
                      const isMinorActive = minorType.selected || String(minorType.id) === String(currentMinorType);
                      if (isMinorActive) {
                          minorCard.classList.add('active');
                      }
                      
                      // 使用新版HTML结构（防止刷新后名字消失）
                      minorCard.innerHTML = `
                        <span class="name-cn">${minorType.name}</span>
                        <span class="name-en">${String(minorType.id).replace(/_/g, ' ').toUpperCase()}</span>
                      `;
                      
                      minorCard.onclick = (e) => {
                          e.stopPropagation();
                          const wasActive = minorCard.classList.contains('active');
                          
                          if (wasActive) {
                             // 支持反选逻辑
                             console.log('重复点击小类按钮，执行反选');
                             minorCard.classList.remove('active');
                             updateAvailableBodyParts([]);
                          } else {
                              // 清除同级激活状态
                              minorContainer.querySelectorAll('.minor-card').forEach(c => c.classList.remove('active'));
                              minorCard.classList.add('active');
                              selectMinorType(minorType.id);
                          }
                      };
                      minorContainer.appendChild(minorCard);
                 });
                 
                 list.appendChild(minorContainer);
            }
        }
    });
    
    // ========== 恢复交互状态：如果有已选中的小类，触发指令获取和聚焦模式 ==========
    // 这是为了解决主界面刷新后，交互状态显示不完整的问题
    // （例如：选择了大类和小类后，进行指令结算，主界面刷新，此时显示已选中大类和小类，
    //  但没有显示无部位指令，也没有收起其他大类进入聚焦模式）
    if (currentMajor && currentMinorType) {
        // 延迟执行，确保DOM已完全渲染
        setTimeout(() => {
            console.log('[DEBUG] 恢复交互状态：自动触发 selectMinorType，currentMinorType:', currentMinorType);
            selectMinorType(currentMinorType);
        }, 100);
    }
    
    return panel;
}

/**
 * 选择大类型
 * @param {number} majorTypeId - 大类型ID
 */
function selectMajorType(majorTypeId) {
    console.log('[DEBUG] selectMajorType called, majorTypeId:', majorTypeId);
    console.log('[DEBUG] window.socket:', window.socket, 'connected:', window.socket?.connected);
    if (window.socket && window.socket.connected) {
        console.log('[DEBUG] Emitting select_major_type event');
        window.socket.emit('select_major_type', { major_type_id: majorTypeId });
    } else {
        console.warn('[DEBUG] Socket not connected, cannot emit select_major_type');
    }
}

/**
 * 选择小类型
 * @param {number} minorTypeId - 小类型ID
 */
function selectMinorType(minorTypeId) {
    console.log('[DEBUG] selectMinorType called, minorTypeId:', minorTypeId);
    if (window.socket && window.socket.connected) {
        window.socket.emit('select_minor_type', { minor_type_id: minorTypeId });
    }
}

/**
 * 更新小类按钮列表
 * 当用户选择大类时，更新小类按钮区域
 * @param {Array} minorTypes - 小类型列表
 * @param {number} rememberedMinorType - 记忆的小类型ID
 * @param {number|string} majorTypeId - 当前选中的大类型ID
 */
function updateMinorTypeButtons(minorTypes, rememberedMinorType, majorTypeId) {
    // 1. Find the list container
    const list = document.querySelector('.interaction-type-list');
    if (!list) {
        // Fallback or retry? If list is missing, we might be in wrong view, but standard logic applies
        console.warn('未找到交互类型列表容器 .interaction-type-list');
        return; 
    }

    // 2. Remove any existing minor lists (collapse all)
    const existingMinors = list.querySelectorAll('.interaction-minor-list');
    existingMinors.forEach(el => el.remove());

    // 3. Deactivate all major cards
    const allMajorCards = list.querySelectorAll('.interaction-card.major-card');
    let activeCard = null;
    const targetIdStr = String(majorTypeId);

    allMajorCards.forEach(card => {
        card.classList.remove('active');
        if (String(card.dataset.id) === targetIdStr) {
            card.classList.add('active');
            activeCard = card;
        }
    });
    
    // 清空浮现按钮（切换大类时需要重置）
    renderFloatingInstructButtons([]);
    
    // 清空身体部位高亮
    const bodyPartButtons = document.querySelectorAll('.body-part-button');
    bodyPartButtons.forEach(button => {
        button.classList.remove('available');
        button.classList.add('unavailable');
    });

    if (!activeCard) {
        console.warn('未找到对应的大类卡片ID:', majorTypeId);
        // If we can't find the card, we can't insert the list.
        // However, we should still handle rememberedMinorType logic if possible?
        // No, because UI is broken.
        return;
    }

    // 4. Create new minor list if data exists
    if (minorTypes && minorTypes.length > 0) {
         const minorContainer = document.createElement('div');
         minorContainer.className = 'interaction-minor-list';
         
         minorTypes.forEach(minorType => {
              const minorCard = document.createElement('div');
              minorCard.className = 'interaction-card minor-card';
              minorCard.dataset.id = minorType.id; // 存储小类ID用于响应匹配
              
              const isSelected = (minorType.id === rememberedMinorType || minorType.selected);
              if (isSelected) {
                  minorCard.classList.add('active');
              }
              
              minorCard.innerHTML = `
                <span class="name-cn">${minorType.name}</span>
                <span class="name-en">${String(minorType.id).replace(/_/g, ' ').toUpperCase()}</span>
              `;
              
              minorCard.onclick = (e) => {
                  e.stopPropagation();
                  const wasActive = minorCard.classList.contains('active');
                  
                  if (wasActive) {
                      // 重复点击，清空选择 (Requirement 4: Cancel selection)
                      console.log('重复点击小类按钮，执行反选');
                      minorCard.classList.remove('active');
                      // Clear body parts and floating buttons
                      updateAvailableBodyParts([]);
                      // TODO: If server tracks state, we might need to tell it to clear.
                      // For now, client side visual clear is efficient.
                  } else {
                      // 选中当前按钮
                      minorContainer.querySelectorAll('.minor-card').forEach(c => c.classList.remove('active'));
                      minorCard.classList.add('active');
                      selectMinorType(minorType.id);
                  }
              };
              minorContainer.appendChild(minorCard);
         });
         
         // Insert AFTER the active major card
         activeCard.after(minorContainer);
    }
    
    // 如果有记忆的小类型，自动触发选择
    if (rememberedMinorType !== null && rememberedMinorType !== undefined) {
        selectMinorType(rememberedMinorType);
    }
    
    // 切换大类后触发重叠检测（延迟执行确保DOM更新完成）
    setTimeout(() => checkAndAdjustCharacterImage(), 150);
}

/**
 * 更新可交互的身体部位
 * 当用户选择小类时，高亮显示该小类下可交互的部位
 * 同时渲染无部位指令的浮现按钮
 * @param {Array} instructs - 指令列表，每个指令包含body_parts
 */
function updateAvailableBodyParts(instructs) {
    // 检查是否有交互对象
    const hasTarget = window.hasTargetCharacter !== undefined ? window.hasTargetCharacter : true;
    
    // 臀部子部位列表（与后端 HIP_SUB_PARTS 保持一致）
    const HIP_SUB_PARTS = ['vagina', 'womb', 'anus', 'urethra', 'tail', 'crotch'];
    
    // 收集所有可交互的部位（英文部位名）
    const availableParts = new Set();
    // 收集无部位的指令（body_parts为空数组）或当没有交互对象时收集所有指令
    const noBodyPartInstructs = [];
    
    instructs.forEach(instruct => {
        if (instruct.body_parts && Array.isArray(instruct.body_parts) && instruct.body_parts.length > 0) {
            if (hasTarget) {
                // 有交互对象：有部位的指令，添加到可交互部位集合
                instruct.body_parts.forEach(part => availableParts.add(part));
            } else {
                // 没有交互对象：有部位的指令也添加到浮现按钮列表
                noBodyPartInstructs.push(instruct);
            }
        } else {
            // 无部位的指令，添加到浮现按钮列表
            noBodyPartInstructs.push(instruct);
        }
    });
    
    // 检查是否包含臀部子部位，如果有则将臀部也设为可用
    const hasHipSubPart = HIP_SUB_PARTS.some(subPart => availableParts.has(subPart));
    if (hasHipSubPart) {
        availableParts.add('hip');
    }
    
    console.log('可交互部位(英文):', Array.from(availableParts));
    console.log('无部位指令:', noBodyPartInstructs);
    
    // 获取所有身体部位按钮
    const bodyPartButtons = document.querySelectorAll('.body-part-button');
    
    bodyPartButtons.forEach(button => {
        // 使用 basePart（英文部位名）来匹配，因为指令的 body_parts 使用英文
        const basePart = button.dataset.basePart;
        const partName = button.dataset.partName;  // 中文显示名
        
        // 检查 basePart 是否在可交互部位中
        // 注意：basePart 可能是 "hand_left"，需要检查基础名 "hand" 是否匹配
        let isAvailable = availableParts.has(basePart);
        
        // 如果直接匹配失败，尝试匹配基础部位名（去除 _left/_right 后缀）
        if (!isAvailable && basePart) {
            const basePartName = basePart.replace(/_left$|_right$/, '');
            isAvailable = availableParts.has(basePartName);
        }
        
        if (isAvailable) {
            // 该部位可交互，添加高亮样式
            button.classList.add('available');
            button.classList.remove('unavailable');
        } else {
            // 该部位不可交互，添加禁用样式
            button.classList.remove('available');
            button.classList.add('unavailable');
        }
    });
    
    // 渲染无部位指令的浮现按钮
    renderFloatingInstructButtons(noBodyPartInstructs);
    
    // 保存当前可用的指令列表供后续点击使用
    window.currentAvailableInstructs = instructs;
    
    // 注意：重叠检测已在 renderFloatingInstructButtons 内部调用，无需重复
}

/**
 * 渲染无部位指令的浮现按钮
 * 改为显示在交互列表的小类下方
 * 并进入"聚焦模式"（隐藏其他大类）
 * @param {Array} instructs - 无部位指令列表
 */
function renderFloatingInstructButtons(instructs) {
    // 0. Hide old container just in case
    const oldContainer = document.getElementById('floating-instruct-buttons');
    if (oldContainer) oldContainer.style.display = 'none';

    // 1. Focus Mode: Hide other Majors
    const list = document.querySelector('.interaction-type-list');
    if (list) {
         const activeMajor = list.querySelector('.interaction-card.major-card.active');
         if (activeMajor) {
             list.querySelectorAll('.interaction-card.major-card').forEach(c => {
                 if (c !== activeMajor) c.classList.add('hidden-card');
             });
         }
    }

    // 2. Render Floating Buttons in Minor List
    const minorList = document.querySelector('.interaction-minor-list');
    
    // Clear existing floating instructs
    if (minorList) {
        minorList.querySelectorAll('.floating-instruct').forEach(e => e.remove());
    }

    const activeMinor = minorList ? minorList.querySelector('.active') : null;

    if (!instructs || instructs.length === 0 || !activeMinor) {
        // Just trigger standard layout adjustment if needed
        setTimeout(() => checkAndAdjustCharacterImage(), 50);
        return;
    }

    // Insert new buttons
    let referenceNode = activeMinor;
    instructs.forEach(instruct => {
         const card = document.createElement('div');
         card.className = 'interaction-card minor-card floating-instruct';
         // Requirement 3: No English name for floating buttons
         card.innerHTML = `
            <span class="name-cn">${instruct.name}</span>
         `;
         card.onclick = (e) => {
             e.stopPropagation();
             // Highlight this action card briefly?
             // Execute
             executeInstruct(instruct.id);
         };
         
         if (referenceNode.nextSibling) {
             minorList.insertBefore(card, referenceNode.nextSibling);
         } else {
             minorList.appendChild(card);
         }
         referenceNode = card; // Insert next one after this one
    });
    
    // Adjust layout
    setTimeout(() => checkAndAdjustCharacterImage(), 50);
}

/**
 * 检测浮现按钮容器与角色立绘是否重叠，如有重叠则调整立绘位置或大小
 * 注意：变换应用到character-container上，确保图片和部位按钮层同步变化
 * 策略：优先右移，只有当右移会与右侧状态栏冲突时才缩小
 */
function checkAndAdjustCharacterImage() {
    const floatingButtons = document.getElementById('floating-instruct-buttons');
    const characterContainer = document.querySelector('.character-container');
    const characterDisplay = document.querySelector('.new-ui-character-display');
    const targetInfo = document.querySelector('.new-ui-target-info');
    
    if (!floatingButtons || !characterContainer || !characterDisplay) {
        return;
    }
    
    // 如果浮现按钮隐藏，恢复角色容器原始状态
    if (floatingButtons.style.display === 'none' || !floatingButtons.offsetParent) {
        resetCharacterContainerTransform();
        return;
    }
    
    const floatingRect = floatingButtons.getBoundingClientRect();
    const displayRect = characterDisplay.getBoundingClientRect();
    const containerRect = characterContainer.getBoundingClientRect();
    
    // 获取右侧状态栏位置（如果存在）
    const targetInfoRect = targetInfo ? targetInfo.getBoundingClientRect() : null;
    const rightBoundary = targetInfoRect ? targetInfoRect.left - 10 : displayRect.right - 10; // 留10px间距
    
    // 检测是否重叠：浮现按钮的右边界是否超过角色容器的左边界
    const isOverlapping = (
        floatingRect.right > containerRect.left &&
        floatingRect.left < containerRect.right &&
        floatingRect.bottom > containerRect.top &&
        floatingRect.top < containerRect.bottom
    );
    
    if (isOverlapping) {
        // 计算需要右移的距离（避开浮现按钮）
        const overlapWidth = floatingRect.right - containerRect.left + 15; // 额外留15px间距
        
        // 计算右移后角色容器的右边界位置
        const newRightPosition = containerRect.right + overlapWidth;
        
        // 检查右移后是否会与右侧状态栏冲突
        if (newRightPosition <= rightBoundary) {
            // 仅右移，不缩小
            characterContainer.style.transform = `translateX(${overlapWidth}px)`;
            characterContainer.style.transformOrigin = 'center center';
        } else {
            // 右移会冲突，需要在右移的基础上缩小
            // 计算可用空间
            const availableWidth = rightBoundary - floatingRect.right - 20; // 留20px间距
            const currentWidth = containerRect.width;
            
            // 计算缩放比例
            const scaleRatio = Math.max(0.5, Math.min(1, availableWidth / currentWidth));
            
            // 计算右移距离（缩小后需要调整）
            const translateX = overlapWidth - (currentWidth * (1 - scaleRatio) / 2);
            
            characterContainer.style.transform = `translateX(${translateX}px) scale(${scaleRatio})`;
            characterContainer.style.transformOrigin = 'center center';
        }
    } else {
        // 无重叠，恢复原始状态
        resetCharacterContainerTransform();
    }
}

/**
 * 重置角色容器的变换状态
 */
function resetCharacterContainerTransform() {
    const characterContainer = document.querySelector('.character-container');
    if (characterContainer) {
        characterContainer.style.transform = '';
        characterContainer.style.transformOrigin = '';
    }
}

/**
 * 清空交互类型选择
 * 清空当前选择的大类和小类，并恢复角色立绘
 */
function clearInteractionSelection() {
    console.log('[DEBUG] clearInteractionSelection called');
    
    // 1. Reset Major Cards (New UI)
    const majorCards = document.querySelectorAll('.interaction-card.major-card');
    majorCards.forEach(card => {
        card.classList.remove('active');
        card.classList.remove('hidden-card'); // Unhide cards (exit focus mode)
        card.style.display = ''; 
    });

    // 2. Remove Minor Lists (Collapse back to initial state)
    const minorLists = document.querySelectorAll('.interaction-minor-list');
    minorLists.forEach(list => list.remove());

    // 3. Legacy Cleanup
    document.querySelectorAll('.interaction-major-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.interaction-minor-btn').forEach(b => b.classList.remove('active'));
    
    // 4. Reset Body Parts
    const bodyPartButtons = document.querySelectorAll('.body-part-button');
    bodyPartButtons.forEach(button => {
        button.classList.remove('available');
        button.classList.remove('unavailable');
    });
    
    // 5. Clear Floating Buttons (Old Container)
    const floatingButtons = document.getElementById('floating-instruct-buttons');
    if (floatingButtons) {
        floatingButtons.style.display = 'none';
        floatingButtons.innerHTML = '';
    }
    
    // 恢复角色容器变换
    resetCharacterContainerTransform();
    
    // 通知后端清空选择
    if (window.socket && window.socket.connected) {
        window.socket.emit('clear_interaction_selection', {});
    }
}

/**
 * 处理主场景点击事件
 * 点击空白区域时清空交互选择
 * @param {Event} e - 点击事件
 */
function handleMainSceneClick(e) {
    // 检查是否点击的是空白区域
    // 排除交互面板、浮现按钮、状态栏、部位按钮等元素的点击
    // 注意：点击角色图像的非按钮区域也应该触发清空
    const clickedElement = e.target;
    
    // 如果点击的是以下元素或其子元素，不处理
    const excludeSelectors = [
        '.new-ui-interaction-panel',
        '.interaction-floating-buttons',
        '.new-ui-target-info',
        '.body-part-button',
        '.instruct-menu',
        '.hip-sub-menu',
        'button'
    ];
    
    for (const selector of excludeSelectors) {
        if (clickedElement.closest(selector)) {
            return; // 点击的不是空白区域
        }
    }
    
    // 点击的是空白区域（包括角色图像的非按钮区域），清空交互选择
    console.log('[DEBUG] Main scene blank area clicked, clearing interaction selection');
    clearInteractionSelection();
}

/**
 * 执行指令
 * @param {string} instructId - 指令ID
 */
function executeInstruct(instructId) {
    console.log('[DEBUG] executeInstruct called, instructId:', instructId);
    if (window.socket && window.socket.connected) {
        window.socket.emit('execute_instruct', { instruct_id: instructId });
    } else {
        console.warn('[DEBUG] Socket not connected, cannot execute instruct');
    }
}

// 前端图片缓存，避免重复请求相同的裁切图片
const croppedImageCache = new Map();

/**
 * 创建角色立绘显示区
 * @param {Object} targetInfo - 角色信息
 * @param {boolean} showAllBodyParts - 是否始终显示所有身体部位按钮
 */
function createCharacterDisplay(targetInfo, showAllBodyParts = false) {
    const display = document.createElement('div');
    display.className = 'new-ui-character-display';
    
    // 获取立绘图片路径（优先使用全身图，否则使用半身图）
    const imageData = targetInfo.image_data;
    const imagePath = imageData ? (imageData.full_body_image || imageData.half_body_image) : null;
    
    if (imagePath) {
        // 创建角色立绘容器
        const characterContainer = document.createElement('div');
        characterContainer.className = 'character-container';
        
        // 创建立绘图片
        const img = document.createElement('img');
        img.alt = targetInfo.name || 'Character';
        img.className = 'character-image';
        
        // 构建裁切图片API路径
        const normalizedPath = imagePath.replace(/^\/?(image\/)?/, '');
        const croppedImageUrl = `/api/cropped_image/${normalizedPath}`;
        
        // 添加加载错误处理
        img.onerror = function() {
            console.error('加载角色立绘失败:', imagePath);
            display.innerHTML = `<div class="character-placeholder">[${targetInfo.name || '无交互对象'}]</div>`;
        };
        
        // 检查前端缓存，避免重复请求
        const cachedData = croppedImageCache.get(croppedImageUrl);
        if (cachedData) {
            // 使用缓存的 blob URL 和元数据
            img.src = cachedData.blobUrl;
            characterContainer.dataset.cropMetadata = JSON.stringify(cachedData.metadata);
            
            // 图片加载成功后计算并设置高度
            img.onload = function() {
                applyCharacterImageHeight(display, img);
                
                const cropMetadata = cachedData.metadata;
                if (cropMetadata.originalWidth > 0 && cropMetadata.croppedWidth > 0) {
                    requestAnimationFrame(() => {
                        adjustBodyPartsLayerForCrop(characterContainer, cropMetadata);
                    });
                }
            };
        } else {
            // 使用fetch加载裁切图片以获取元数据
            fetch(croppedImageUrl)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    
                    // 从响应头获取裁切元数据
                    const cropMetadata = {
                        originalWidth: parseInt(response.headers.get('X-Original-Width')) || 0,
                        originalHeight: parseInt(response.headers.get('X-Original-Height')) || 0,
                        croppedWidth: parseInt(response.headers.get('X-Cropped-Width')) || 0,
                        croppedHeight: parseInt(response.headers.get('X-Cropped-Height')) || 0,
                        offsetX: parseInt(response.headers.get('X-Offset-X')) || 0,
                        offsetY: parseInt(response.headers.get('X-Offset-Y')) || 0
                    };
                    
                    console.log('[角色立绘] 裁切元数据:', cropMetadata);
                    
                    // 保存裁切元数据到容器
                    characterContainer.dataset.cropMetadata = JSON.stringify(cropMetadata);
                    
                    return response.blob().then(blob => ({ blob, cropMetadata }));
                })
                .then(({ blob, cropMetadata }) => {
                    // 创建blob URL并设置图片源
                    const blobUrl = URL.createObjectURL(blob);
                    img.src = blobUrl;
                    
                    // 缓存到前端
                    croppedImageCache.set(croppedImageUrl, {
                        blobUrl: blobUrl,
                        metadata: cropMetadata
                    });
                    
                    // 图片加载成功后计算并设置高度
                    img.onload = function() {
                        // 计算并应用角色立绘高度
                        applyCharacterImageHeight(display, img);
                        
                        // 获取裁切元数据并调整身体部位按钮层
                        if (cropMetadata.originalWidth > 0 && cropMetadata.croppedWidth > 0) {
                            // 延迟一帧，确保图片渲染尺寸已确定
                            requestAnimationFrame(() => {
                                adjustBodyPartsLayerForCrop(characterContainer, cropMetadata);
                            });
                        }
                    };
                })
                .catch(error => {
                    console.warn('使用裁切图片API失败，回退到原始图片:', error);
                    // 回退到原始图片
                    img.src = imagePath.startsWith('/') ? imagePath : '/' + imagePath;
                    img.onload = function() {
                        applyCharacterImageHeight(display, img);
                    };
                });
        }
        
        characterContainer.appendChild(img);
        
        // 添加身体部位按钮层
        if (imageData.body_parts && imageData.body_parts.body_parts) {
            const bodyPartsLayer = createBodyPartsLayer(imageData.body_parts, targetInfo.name, showAllBodyParts);
            characterContainer.appendChild(bodyPartsLayer);
        }
        
        display.appendChild(characterContainer);
    } else {
        display.innerHTML = `<div class="character-placeholder">[${targetInfo.name || '无交互对象'}]</div>`;
    }
    
    return display;
}

/**
 * 根据裁切元数据调整身体部位按钮层的位置
 * 
 * 裁切后，原本在原图上的身体部位位置需要重新计算：
 * - 将每个按钮的原图坐标转换为裁切后图片坐标
 * - 原始坐标系 (0, 0) 到 (originalWidth, originalHeight)
 * - 裁切后坐标系 (offsetX, offsetY) 到 (offsetX + croppedWidth, offsetY + croppedHeight)
 * 
 * 转换公式：
 * - 新X% = ((原X - offsetX) / croppedWidth) * 100
 * - 新Y% = ((原Y - offsetY) / croppedHeight) * 100
 * - 新大小% = 原大小% * (croppedWidth / originalWidth)
 * 
 * @param {HTMLElement} characterContainer - 角色容器元素
 * @param {Object} cropMetadata - 裁切元数据
 */
function adjustBodyPartsLayerForCrop(characterContainer, cropMetadata) {
    const bodyPartsLayer = characterContainer.querySelector('.body-parts-layer');
    if (!bodyPartsLayer) return;
    
    const { originalWidth, originalHeight, croppedWidth, croppedHeight, offsetX, offsetY } = cropMetadata;
    
    if (originalWidth === 0 || originalHeight === 0 || croppedWidth === 0 || croppedHeight === 0) {
        console.warn('[身体部位] 裁切元数据无效，跳过调整');
        return;
    }
    
    // 获取图片元素及其实际渲染尺寸
    const img = characterContainer.querySelector('.character-image');
    if (!img) {
        console.warn('[身体部位] 未找到图片元素');
        return;
    }
    
    // 获取图片的实际渲染尺寸（显示在屏幕上的像素尺寸）
    const renderedWidth = img.offsetWidth;
    const renderedHeight = img.offsetHeight;
    
    // 获取图片相对于容器的偏移量（如果图片在容器内有居中等布局）
    const imgRect = img.getBoundingClientRect();
    const containerRect = characterContainer.getBoundingClientRect();
    const offsetLeft = imgRect.left - containerRect.left;
    const offsetTop = imgRect.top - containerRect.top;
    
    console.log(`[身体部位] 图片渲染尺寸: ${renderedWidth}x${renderedHeight}px, 偏移: (${offsetLeft}, ${offsetTop})`);
    
    // 设置 layer 的尺寸与图片完全一致（使用像素值而非百分比）
    // 位置也要根据图片在容器内的实际位置来设置
    bodyPartsLayer.style.width = `${renderedWidth}px`;
    bodyPartsLayer.style.height = `${renderedHeight}px`;
    bodyPartsLayer.style.left = `${offsetLeft}px`;
    bodyPartsLayer.style.top = `${offsetTop}px`;
    
    // 获取数据中指定的图片尺寸（身体部位坐标的参考尺寸）
    const dataImageWidth = parseFloat(bodyPartsLayer.dataset.dataImageWidth) || originalWidth;
    const dataImageHeight = parseFloat(bodyPartsLayer.dataset.dataImageHeight) || originalHeight;
    
    // 计算数据坐标系到实际原图坐标系的缩放比例
    const scaleToActual = {
        x: originalWidth / dataImageWidth,
        y: originalHeight / dataImageHeight
    };
    
    console.log(`[身体部位] 坐标系转换: 数据尺寸 ${dataImageWidth}x${dataImageHeight} -> 实际原图 ${originalWidth}x${originalHeight}, 缩放比例: ${scaleToActual.x.toFixed(3)}x${scaleToActual.y.toFixed(3)}`);
    
    // 遍历所有按钮，调整位置和大小
    const buttons = bodyPartsLayer.querySelectorAll('.body-part-button');
    buttons.forEach(button => {
        // 获取保存的数据坐标（相对于数据图片尺寸的像素坐标）
        const dataX = parseFloat(button.dataset.origX) || 0;
        const dataY = parseFloat(button.dataset.origY) || 0;
        const origSizePercent = parseFloat(button.dataset.origSizePercent) || 5;
        
        // 第一步：将数据坐标转换为实际原图坐标
        const actualX = dataX * scaleToActual.x;
        const actualY = dataY * scaleToActual.y;
        
        // 第二步：将实际原图坐标转换为裁切后图片坐标（百分比）
        const newX = ((actualX - offsetX) / croppedWidth) * 100;
        const newY = ((actualY - offsetY) / croppedHeight) * 100;
        
        // 调整按钮大小：origSizePercent 是相对于 dataImageWidth 的百分比
        // 需要转换为相对于裁切后图片宽度的百分比
        // 公式：newSize = origSizePercent * (dataImageWidth / croppedWidth)
        const newSize = origSizePercent * (dataImageWidth / croppedWidth);
        
        // 应用新的位置
        button.style.left = `${newX}%`;
        button.style.top = `${newY}%`;
        button.style.width = `${Math.max(newSize, 3)}%`;
        
        // console.log(`[身体部位] ${button.dataset.partName}: (${origX.toFixed(0)}, ${origY.toFixed(0)}) -> (${newX.toFixed(1)}%, ${newY.toFixed(1)}%), size: ${origSizePercent.toFixed(1)}% -> ${newSize.toFixed(1)}%`);
    });
    
    console.log(`[身体部位] 调整完成, 共 ${buttons.length} 个按钮, 裁切区域: (${offsetX}, ${offsetY}) ${croppedWidth}x${croppedHeight}`);
}

/**
 * 计算并应用角色立绘高度
 * 规则：
 * 1. 首先检查当前窗口大小导致的角色立绘可用高度上限
 * 2. 如果可用高度 > 1024，则将图片高度设为 1024px
 * 3. 如果可用高度 <= 1024，则将图片高度设为可用高度
 * 4. 图片居中显示
 * 
 * 重要：测量可用高度时需要先将图片高度设为最小值，否则图片的 naturalHeight
 * 会通过 flex 布局影响 main-scene 的高度计算。
 * 
 * @param {HTMLElement} display - 角色立绘显示区容器
 * @param {HTMLImageElement} img - 立绘图片元素
 */
function applyCharacterImageHeight(display, img) {
    // 最大高度限制
    const MAX_HEIGHT = 1024;
    
    // 获取主场景区域
    const mainScene = display.closest('.new-ui-main-scene');
    if (!mainScene) {
        console.warn('[角色立绘] 未找到 main-scene 容器');
        return;
    }
    
    // 临时将图片高度设为1px，避免图片 naturalHeight 影响布局计算
    const originalHeight = img.style.height;
    img.style.height = '1px';
    
    // 强制浏览器重新计算布局
    // 通过读取 offsetHeight 触发同步布局
    void mainScene.offsetHeight;
    
    // 现在获取 main-scene 的高度（不受图片内容影响）
    const mainSceneRect = mainScene.getBoundingClientRect();
    const availableHeight = mainSceneRect.height - 20; // 留10px上下边距
    
    // 计算应使用的高度：min(MAX_HEIGHT, 可用高度)
    const targetHeight = Math.min(MAX_HEIGHT, availableHeight);
    
    // 设置图片高度
    if (targetHeight > 0) {
        img.style.height = `${targetHeight}px`;
        img.style.width = 'auto'; // 宽度自动，保持比例
        
        // 保存目标高度到display元素，供重叠检测时使用
        display.dataset.targetHeight = targetHeight;
        display.dataset.maxHeight = MAX_HEIGHT;
        
        console.log(`[角色立绘] main-scene高度: ${mainSceneRect.height}px, 可用高度: ${availableHeight}px, 目标高度: ${targetHeight}px`);
    } else {
        // 如果计算失败，恢复原始高度
        img.style.height = originalHeight;
        console.warn('[角色立绘] 可用高度计算失败，保持原始高度');
    }
    
    // 触发一次重叠检测
    setTimeout(() => checkAndAdjustCharacterImage(), 100);
}

/**
 * 窗口大小改变时重新计算角色立绘高度
 */
function updateCharacterImageHeightOnResize() {
    const display = document.querySelector('.new-ui-character-display');
    const img = display ? display.querySelector('.character-image') : null;
    
    if (display && img && img.complete && img.naturalHeight > 0) {
        applyCharacterImageHeight(display, img);
        
        // 重新调整身体部位按钮层
        const characterContainer = display.querySelector('.character-container');
        if (characterContainer && characterContainer.dataset.cropMetadata) {
            const cropMetadata = JSON.parse(characterContainer.dataset.cropMetadata);
            if (cropMetadata.originalWidth > 0 && cropMetadata.croppedWidth > 0) {
                // 延迟一帧，确保图片尺寸已更新
                requestAnimationFrame(() => {
                    adjustBodyPartsLayerForCrop(characterContainer, cropMetadata);
                });
            }
        }
    }
}

// 监听窗口大小改变，重新计算角色立绘高度
window.addEventListener('resize', debounce(updateCharacterImageHeightOnResize, 200));

/**
 * 辅助函数：防抖
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}


/**
 * 创建身体部位交互按钮层
 * @param {Object} bodyPartsData - 身体部位数据
 * @param {string} characterName - 角色名称
 * @param {boolean} showAllBodyParts - 是否始终显示所有身体部位按钮
 */
function createBodyPartsLayer(bodyPartsData, characterName, showAllBodyParts = false) {
    const layer = document.createElement('div');
    layer.className = 'body-parts-layer';
    
    const parts = bodyPartsData.body_parts || {};
    const imageSize = bodyPartsData.image_size || { width: 1024, height: 1024 };
    
    // 保存数据中的图片尺寸到 layer，供裁切调整时使用
    // 这是身体部位坐标的参考尺寸，可能与实际图片尺寸不同
    layer.dataset.dataImageWidth = imageSize.width;
    layer.dataset.dataImageHeight = imageSize.height;
    
    for (const [partName, partData] of Object.entries(parts)) {
        if (!partData || !partData.center) continue;
        
        const button = document.createElement('div');
        button.className = 'body-part-button';
        
        // 如果全部位显示开启，添加 always-visible 类
        if (showAllBodyParts) {
            button.classList.add('always-visible');
        }
        
        button.dataset.partName = partName;  // 中文显示名
        // base_part 是英文部位名，用于与指令的 body_parts 匹配
        button.dataset.basePart = partData.base_part || partData.part_id || partName;
        
        // 保存原图坐标（像素值），用于裁切调整时重新计算位置
        button.dataset.origX = partData.center.x;
        button.dataset.origY = partData.center.y;
        
        // 计算按钮位置（相对于原图的百分比）
        const centerX = (partData.center.x / imageSize.width) * 100;
        const centerY = (partData.center.y / imageSize.height) * 100;
        
        button.style.left = `${centerX}%`;
        button.style.top = `${centerY}%`;
        
        // 设置按钮大小（基于radius或默认值，相对于原图宽度的百分比）
        const radius = partData.radius || 30;
        const size = (radius * 2 / imageSize.width) * 100;
        
        // 保存原始大小百分比，用于裁切调整时重新计算
        button.dataset.origSizePercent = size;
        
        button.style.width = `${Math.max(size, 5)}%`;
        
        // 添加提示文本
        button.title = partName;
        
        // 点击事件
        button.onclick = function(e) {
            e.stopPropagation();
            // 保存点击的按钮引用，用于定位菜单
            window.lastClickedBodyPartButton = button;
            handleBodyPartClick(partName);
        };
        
        // 悬停效果 - 显示部位名称或指令名（如果只有一个指令）
        const tooltip = document.createElement('span');
        tooltip.className = 'body-part-tooltip';
        tooltip.textContent = partName;  // 默认显示部位名
        button.appendChild(tooltip);
        
        // 保存tooltip引用用于后续更新
        button._tooltip = tooltip;
        
        layer.appendChild(button);
    }
    
    return layer;
}

/**
 * 处理身体部位点击
 * @param {string} partName - 部位名称
 */
function handleBodyPartClick(partName) {
    console.log('点击身体部位:', partName);
    // 先关闭已有的指令菜单
    const existingMenu = document.querySelector('.instruct-menu');
    if (existingMenu) {
        existingMenu.remove();
    }
    
    if (socket && socket.connected) {
        socket.emit('click_body_part', { part_name: partName });
    }
}

/**
 * 显示臀部子菜单
 * @param {Array} subParts - 子部位列表
 */
function showHipSubMenu(subParts) {
    // 移除已有的子菜单
    const existingMenu = document.querySelector('.hip-sub-menu');
    if (existingMenu) {
        existingMenu.remove();
    }
    
    // 找到臀部按钮的位置
    const hipButton = document.querySelector('.body-part-button[data-part-name="臀部"]');
    if (!hipButton) {
        console.warn('未找到臀部按钮');
        return;
    }
    
    // 创建子菜单
    const menu = document.createElement('div');
    menu.className = 'hip-sub-menu';
    
    // 添加标题
    const title = document.createElement('div');
    title.className = 'hip-sub-menu-title';
    title.textContent = '选择部位';
    menu.appendChild(title);
    
    // 添加子部位按钮
    subParts.forEach(subPart => {
        const btn = document.createElement('button');
        btn.className = 'hip-sub-menu-btn';
        btn.textContent = subPart.part_name_cn;
        btn.dataset.partId = subPart.part_id;
        btn.onclick = (e) => {
            e.stopPropagation();
            // 点击子部位时发送事件
            if (socket && socket.connected) {
                socket.emit('click_body_part', { part_name: subPart.part_id });
            }
            menu.remove();
        };
        menu.appendChild(btn);
    });
    
    // 添加关闭按钮
    const closeBtn = document.createElement('button');
    closeBtn.className = 'hip-sub-menu-close';
    closeBtn.textContent = '×';
    closeBtn.onclick = (e) => {
        e.stopPropagation();
        menu.remove();
    };
    menu.appendChild(closeBtn);
    
    // 定位菜单（在臀部按钮旁边）
    const hipRect = hipButton.getBoundingClientRect();
    const container = document.querySelector('.character-container') || document.body;
    const containerRect = container.getBoundingClientRect();
    
    menu.style.position = 'absolute';
    menu.style.left = `${hipRect.right - containerRect.left + 10}px`;
    menu.style.top = `${hipRect.top - containerRect.top}px`;
    
    // 添加到容器
    container.appendChild(menu);
    
    // 点击其他地方关闭菜单
    document.addEventListener('click', function closeMenu(e) {
        if (!menu.contains(e.target)) {
            menu.remove();
            document.removeEventListener('click', closeMenu);
        }
    });
}

/**
 * 显示头部子菜单
 * @param {Array} subParts - 子部位列表
 * @param {boolean} hasBeastEars - 角色是否有兽耳
 * @param {boolean} hasHorn - 角色是否有兽角
 */
function showHeadSubMenu(subParts, hasBeastEars, hasHorn) {
    // 移除已有的子菜单
    const existingMenu = document.querySelector('.head-sub-menu');
    if (existingMenu) {
        existingMenu.remove();
    }
    
    // 找到头部按钮的位置
    const headButton = document.querySelector('.body-part-button[data-part-name="头部"]');
    if (!headButton) {
        console.warn('未找到头部按钮');
        return;
    }
    
    // 创建子菜单
    const menu = document.createElement('div');
    menu.className = 'head-sub-menu';
    
    // 添加标题
    const title = document.createElement('div');
    title.className = 'head-sub-menu-title';
    title.textContent = '选择部位';
    menu.appendChild(title);
    
    // 添加子部位按钮
    subParts.forEach(subPart => {
        const btn = document.createElement('button');
        btn.className = 'head-sub-menu-btn';
        btn.textContent = subPart.part_name_cn;
        btn.dataset.partId = subPart.part_id;
        btn.onclick = (e) => {
            e.stopPropagation();
            // 点击子部位时发送事件
            if (socket && socket.connected) {
                socket.emit('click_body_part', { part_name: subPart.part_id });
            }
            menu.remove();
        };
        menu.appendChild(btn);
    });
    
    // 添加关闭按钮
    const closeBtn = document.createElement('button');
    closeBtn.className = 'head-sub-menu-close';
    closeBtn.textContent = '×';
    closeBtn.onclick = (e) => {
        e.stopPropagation();
        menu.remove();
    };
    menu.appendChild(closeBtn);
    
    // 定位菜单（在头部按钮旁边）
    const headRect = headButton.getBoundingClientRect();
    const container = document.querySelector('.character-container') || document.body;
    const containerRect = container.getBoundingClientRect();
    
    menu.style.position = 'absolute';
    menu.style.left = `${headRect.right - containerRect.left + 10}px`;
    menu.style.top = `${headRect.top - containerRect.top}px`;
    
    // 添加到容器
    container.appendChild(menu);
    
    // 点击其他地方关闭菜单
    document.addEventListener('click', function closeMenu(e) {
        if (!menu.contains(e.target)) {
            menu.remove();
            document.removeEventListener('click', closeMenu);
        }
    });
}

/**
 * 处理身体部位点击结果
 * @param {Object} data - 点击结果数据
 */
function handleBodyPartClickResult(data) {
    console.log('身体部位点击结果:', data);
    
    // 更新该部位的tooltip显示
    if (window.lastClickedBodyPartButton && window.lastClickedBodyPartButton._tooltip) {
        const tooltip = window.lastClickedBodyPartButton._tooltip;
        // 无论单个还是多个指令，都显示部位名
        tooltip.textContent = data.part_name_cn || data.part_name;
    }
    
    // 无论单个还是多个指令，都显示选择菜单
    // 不再自动执行单指令，需要用户点击确认才执行
    if (data.available_instructs.length > 0) {
        showInstructMenu(data.available_instructs, data.part_name_cn);
    } else {
        console.log('该部位没有可执行的指令');
    }
}

/**
 * 显示指令选择菜单
 * 在点击的身体部位位置显示菜单
 * @param {Array} instructs - 指令列表
 * @param {string} partName - 部位名称
 */
function showInstructMenu(instructs, partName) {
    // 移除已有的菜单
    const existingMenu = document.querySelector('.instruct-menu');
    if (existingMenu) {
        existingMenu.remove();
    }
    
    // 创建菜单
    const menu = document.createElement('div');
    menu.className = 'instruct-menu';
    
    // 添加标题
    const title = document.createElement('div');
    title.className = 'instruct-menu-title';
    title.textContent = partName || '选择指令';
    menu.appendChild(title);
    
    // 创建滚动容器
    const container = document.createElement('div');
    container.className = 'instruct-menu-container';
    
    // 添加指令按钮到滚动容器
    instructs.forEach(instruct => {
        const btn = document.createElement('button');
        btn.className = 'instruct-menu-btn';
        btn.textContent = instruct.name;
        btn.onclick = (e) => {
            e.stopPropagation();
            if (socket && socket.connected) {
                socket.emit('execute_instruct', { instruct_id: instruct.id });
            }
            menu.remove();
        };
        container.appendChild(btn);
    });
    
    // 将滚动容器添加到菜单
    menu.appendChild(container);
    
    // 定位菜单：优先在点击的部位位置显示
    menu.style.position = 'fixed';
    
    const clickedButton = window.lastClickedBodyPartButton;
    if (clickedButton) {
        const rect = clickedButton.getBoundingClientRect();
        // 在部位按钮右侧显示菜单
        let left = rect.right + 10;
        let top = rect.top;
        
        // 计算菜单实际高度（标题 + 容器）
        const estimatedHeight = Math.min(instructs.length * 46 + 80, 480);  // 标题约80px，每个按钮约46px
        
        // 确保菜单不超出屏幕右侧
        if (left + 200 > window.innerWidth) {
            left = rect.left - 210;  // 改为在左侧显示
        }
        // 确保菜单不超出屏幕底部
        if (top + estimatedHeight > window.innerHeight) {
            top = window.innerHeight - estimatedHeight - 10;
        }
        // 确保菜单不超出屏幕顶部
        if (top < 10) {
            top = 10;
        }
        
        menu.style.left = `${left}px`;
        menu.style.top = `${top}px`;
    } else {
        // 回退到居中显示
        menu.style.top = '50%';
        menu.style.left = '50%';
        menu.style.transform = 'translate(-50%, -50%)';
    }
    
    document.body.appendChild(menu);
    
    // 点击其他地方关闭菜单（但不包括点击其他身体部位的情况，那个会在handleBodyPartClick中处理）
    setTimeout(() => {
        document.addEventListener('click', function closeMenu(e) {
            // 如果点击的是身体部位按钮，不在这里关闭（handleBodyPartClick会处理）
            if (e.target.closest('.body-part-button')) {
                return;
            }
            if (!menu.contains(e.target)) {
                menu.remove();
                document.removeEventListener('click', closeMenu);
            }
        });
    }, 0);
}

/**
 * 创建交互对象信息面板
 * 包含：名字、好感/信赖、体力/气力、特殊状态、快感状态、其他状态
 * @param {Object} targetInfo - 交互对象信息
 * @returns {HTMLElement} - 信息面板元素
 */
function createTargetInfoPanel(targetInfo) {
    const panel = document.createElement('div');
    panel.className = 'new-ui-target-info';
    
    // ========== 第一行：名字 ==========
    const nameRow = document.createElement('div');
    nameRow.className = 'target-name';
    nameRow.textContent = targetInfo.name || '';
    panel.appendChild(nameRow);
    
    // ========== 第二行：好感度 + 信赖度 ==========
    if (targetInfo.favorability || targetInfo.trust) {
        const relationRow = document.createElement('div');
        relationRow.className = 'target-relation-row';
        
        if (targetInfo.favorability && targetInfo.favorability.level) {
            const favSpan = document.createElement('span');
            favSpan.className = 'target-favorability';
            favSpan.dataset.field = 'favorability';  // 添加字段标识
            favSpan.textContent = `好感:${Math.floor(targetInfo.favorability.value)}(${targetInfo.favorability.level})`;
            favSpan.title = '好感度';
            relationRow.appendChild(favSpan);
        }
        
        if (targetInfo.trust && targetInfo.trust.level) {
            const trustSpan = document.createElement('span');
            trustSpan.className = 'target-trust';
            trustSpan.dataset.field = 'trust';  // 添加字段标识
            trustSpan.textContent = `信赖:${targetInfo.trust.value.toFixed(1)}%(${targetInfo.trust.level})`;
            trustSpan.title = '信赖度';
            relationRow.appendChild(trustSpan);
        }
        
        panel.appendChild(relationRow);
    }
    
    // ========== 第三行：体力槽 + 气力槽 ==========
    const barsContainer = document.createElement('div');
    barsContainer.className = 'target-bars';
    
    if (targetInfo.hp !== undefined) {
        const hpBar = createStatusBar('体力', targetInfo.hp, targetInfo.hp_max, 'hp');
        hpBar.dataset.field = 'hit_point';  // 添加字段标识
        barsContainer.appendChild(hpBar);
    }
    if (targetInfo.mp !== undefined) {
        const mpBar = createStatusBar('气力', targetInfo.mp, targetInfo.mp_max, 'mp');
        mpBar.dataset.field = 'mana_point';  // 添加字段标识
        barsContainer.appendChild(mpBar);
    }
    panel.appendChild(barsContainer);
    
    // ========== 第四行：特殊状态标记 ==========
    if (targetInfo.special_states && targetInfo.special_states.length > 0) {
        const specialRow = document.createElement('div');
        specialRow.className = 'target-special-states';
        
        targetInfo.special_states.forEach(state => {
            const stateSpan = document.createElement('span');
            stateSpan.className = `special-state style-${state.style || 'standard'}`;
            stateSpan.textContent = state.text;
            if (state.tooltip) {
                stateSpan.title = state.tooltip;
            }
            specialRow.appendChild(stateSpan);
        });
        
        panel.appendChild(specialRow);
    }
    
    // ========== 快感状态块 ==========
    if (targetInfo.pleasure_states && targetInfo.pleasure_states.length > 0) {
        const pleasureSection = document.createElement('div');
        pleasureSection.className = 'target-state-section';
        
        const pleasureTitle = document.createElement('div');
        pleasureTitle.className = 'state-section-title';
        pleasureTitle.textContent = '─快感状态─';
        pleasureSection.appendChild(pleasureTitle);
        
        const pleasureGrid = document.createElement('div');
        pleasureGrid.className = 'state-grid';
        
        targetInfo.pleasure_states.forEach(state => {
            pleasureGrid.appendChild(createStateItem(state));
        });
        
        pleasureSection.appendChild(pleasureGrid);
        panel.appendChild(pleasureSection);
    }
    
    // ========== 其他状态块 ==========
    if (targetInfo.other_states && targetInfo.other_states.length > 0) {
        const otherSection = document.createElement('div');
        otherSection.className = 'target-state-section';
        
        const otherTitle = document.createElement('div');
        otherTitle.className = 'state-section-title';
        otherTitle.textContent = '─其他状态─';
        otherSection.appendChild(otherTitle);
        
        const otherGrid = document.createElement('div');
        otherGrid.className = 'state-grid';
        
        targetInfo.other_states.forEach(state => {
            otherGrid.appendChild(createStateItem(state));
        });
        
        otherSection.appendChild(otherGrid);
        panel.appendChild(otherSection);
    }
    
    // ========== 可选部位打印区 ==========
    // 仅在开启全部位显示且有可选部位时显示
    if (targetInfo.show_all_body_parts && targetInfo.available_body_parts && targetInfo.available_body_parts.length > 0) {
        const bodyPartsSection = document.createElement('div');
        bodyPartsSection.className = 'target-body-parts-section';
        
        const bodyPartsTitle = document.createElement('div');
        bodyPartsTitle.className = 'state-section-title';
        bodyPartsTitle.textContent = '─可选部位─';
        bodyPartsSection.appendChild(bodyPartsTitle);
        
        // 使用grid布局，每行显示两个部位
        const bodyPartsGrid = document.createElement('div');
        bodyPartsGrid.className = 'body-parts-display-grid';
        
        targetInfo.available_body_parts.forEach(part => {
            const partItem = document.createElement('div');
            partItem.className = 'body-part-display-item';
            partItem.dataset.partId = part.id;
            partItem.textContent = part.name;
            partItem.title = `点击选择${part.name}`;
            
            // 点击部位时触发部位点击事件
            partItem.onclick = () => handleBodyPartClick(part.name);
            
            bodyPartsGrid.appendChild(partItem);
        });
        
        bodyPartsSection.appendChild(bodyPartsGrid);
        panel.appendChild(bodyPartsSection);
    }
    
    // ========== 数值变化浮动文本 ==========
    if (targetInfo.value_changes && targetInfo.value_changes.length > 0) {
        // 延迟创建浮动文本，确保DOM已渲染
        setTimeout(() => {
            createFloatingValueChanges(panel, targetInfo.value_changes);
        }, 50);
    }
    
    return panel;
}

/**
 * 富文本颜色名称到CSS颜色值的映射
 * 基于 data/csv/FontConfig.csv 中的定义
 */
const RICH_TEXT_COLORS = {
    'hp_point': '#e15a5a',
    'mp_point': '#70C070',
    'sanity': '#7070C0',
    'semen': '#fffacd',
    'light_pink': '#ffb6c1',
    'summer_green': '#96bbab',
    'medium_spring_green': '#00ff7f',
    'persian_pink': '#f77fbe',
    'rose_pink': '#ff66cc',
    'deep_pink': '#ff1493',
    'crimson': '#dc143c',
    'slate_blue': '#6a5acd',
    'pale_cerulean': '#9bc4e2',
    'little_dark_slate_blue': '#5550aa',
    'light_sky_blue': '#87cefa',
    'lavender_pink': '#fbaed2',
    'standard': '#c8c8c8'
};

/**
 * 创建数值变化浮动文本
 * 在每个数值对应的UI元素位置显示浮动文本
 * @param {HTMLElement} panel - 目标信息面板容器
 * @param {Array} valueChanges - 数值变化数组
 */
function createFloatingValueChanges(panel, valueChanges) {
    if (!panel || !valueChanges || valueChanges.length === 0) return;
    
    // 根据字段类型分组变化，同时保留颜色信息
    const fieldGroups = {};
    valueChanges.forEach(change => {
        const field = change.field;
        if (!fieldGroups[field]) {
            fieldGroups[field] = {
                changes: [],
                color: change.color || 'standard',
                field_name: change.field_name || field
            };
        }
        fieldGroups[field].changes.push(change);
    });
    
    // 未匹配到位置的变化，收集到这里最后统一显示
    const unmatchedChanges = [];
    
    // 为每个字段创建浮动文本
    for (const field in fieldGroups) {
        const group = fieldGroups[field];
        const changes = group.changes;
        const totalValue = changes.reduce((sum, c) => sum + c.value, 0);
        if (totalValue === 0) continue;
        
        const displayName = group.field_name;
        const colorName = group.color;
        
        // 查找对应的UI元素，并确定位置类型
        let targetElement = null;
        let positionType = 'inline'; // 默认内联显示
        
        // 根据字段类型查找对应元素
        if (field === 'hit_point') {
            // 体力：显示在数值后面
            targetElement = panel.querySelector('[data-field="hit_point"]');
            positionType = 'end-inline';
        } else if (field === 'mana_point') {
            // 气力：显示在数值后面
            targetElement = panel.querySelector('[data-field="mana_point"]');
            positionType = 'end-inline';
        } else if (field === 'favorability') {
            // 好感：显示在数值后面
            targetElement = panel.querySelector('[data-field="favorability"]');
            positionType = 'end-inline';
        } else if (field === 'trust') {
            // 信赖：显示在数值后面
            targetElement = panel.querySelector('[data-field="trust"]');
            positionType = 'end-inline';
        } else if (field === 'hypnosis_degree') {
            // 催眠度：显示在数值后面
            targetElement = panel.querySelector('[data-field="hypnosis_degree"]');
            if (!targetElement) {
                unmatchedChanges.push({ displayName, totalValue, colorName });
                continue;
            }
            positionType = 'end-inline';
        } else if (field === 'eja_point' || field === 'sanity_point') {
            // 射精欲、理智：下移一行显示
            unmatchedChanges.push({ displayName, totalValue, colorName });
            continue;
        } else if (field.startsWith('status_')) {
            // 状态：在对应状态项位置显示（位置不变）
            const stateId = field.replace('status_', '');
            targetElement = panel.querySelector(`[data-state-id="${stateId}"]`);
            positionType = 'inline';
        } else if (field.startsWith('experience_')) {
            // 经验值：放到底部
            unmatchedChanges.push({ displayName, totalValue, colorName });
            continue;
        } else {
            // 其他未知字段也放到未匹配列表
            unmatchedChanges.push({ displayName, totalValue, colorName });
            continue;
        }
        
        // 如果找到目标元素，在该元素位置显示浮动文本
        if (targetElement) {
            createInlineFloatingText(targetElement, displayName, totalValue, colorName, positionType, panel);
        } else {
            // 未找到元素，放到未匹配列表
            unmatchedChanges.push({ displayName, totalValue, colorName });
        }
    }
    
    // 处理未匹配的变化，在面板底部显示
    if (unmatchedChanges.length > 0) {
        createBottomFloatingTexts(panel, unmatchedChanges);
    }
}

/**
 * 在目标元素旁边创建浮动文本
 * @param {HTMLElement} targetElement - 目标UI元素
 * @param {string} displayName - 显示名称
 * @param {number} totalValue - 数值变化总量
 * @param {string} colorName - 颜色名称
 * @param {string} positionType - 位置类型：'inline'(内联), 'below'(下方), 'hp_middle'(体力气力中间), 'end-inline'(数值后面)
 * @param {HTMLElement} panel - 面板容器（用于hp_middle定位）
 */
function createInlineFloatingText(targetElement, displayName, totalValue, colorName, positionType, panel) {
    // 确保目标元素有相对定位
    const originalPosition = targetElement.style.position;
    if (!originalPosition || originalPosition === 'static') {
        targetElement.style.position = 'relative';
    }
    
    // 创建浮动文本元素
    const floatText = document.createElement('span');
    floatText.className = 'inline-floating-text';
    
    // 设置颜色
    const color = RICH_TEXT_COLORS[colorName] || RICH_TEXT_COLORS['standard'];
    floatText.style.color = color;
    
    // 设置文本内容（带符号和空格）
    const sign = totalValue > 0 ? '+' : '';
    floatText.textContent = ` ${sign}${totalValue}`;
    
    // 根据位置类型设置不同的定位
    if (positionType === 'end-inline') {
        // 显示在数值后面（用于状态条）
        floatText.classList.add('position-end-inline');
    } else if (positionType === 'hp_middle') {
        // 体力：显示在体力和气力的中间位置
        floatText.classList.add('position-hp-middle');
    } else if (positionType === 'below') {
        // 下移一行显示
        floatText.classList.add('position-below');
    } else {
        // 默认内联显示（状态栏）
        floatText.classList.add('position-inline');
    }
    
    targetElement.appendChild(floatText);
    
    // 15秒后移除浮动文本
    setTimeout(() => {
        floatText.classList.add('fade-out');
        setTimeout(() => {
            if (floatText.parentNode) {
                floatText.parentNode.removeChild(floatText);
            }
        }, 500);
    }, 15000);
}

/**
 * 在面板底部创建未匹配变化的浮动文本
 * @param {HTMLElement} panel - 面板容器
 * @param {Array} changes - 未匹配的变化数组
 */
function createBottomFloatingTexts(panel, changes) {
    // 创建底部浮动文本容器
    const container = document.createElement('div');
    container.className = 'bottom-floating-container';
    
    changes.forEach((change, index) => {
        const floatText = document.createElement('span');
        floatText.className = 'bottom-floating-text';
        
        // 设置颜色
        const color = RICH_TEXT_COLORS[change.colorName] || RICH_TEXT_COLORS['standard'];
        floatText.style.color = color;
        
        const sign = change.totalValue > 0 ? '+' : '';
        floatText.textContent = `${change.displayName} ${sign}${change.totalValue}`;
        
        container.appendChild(floatText);
    });
    
    panel.appendChild(container);
    
    // 15秒后移除
    setTimeout(() => {
        container.classList.add('fade-out');
        setTimeout(() => {
            if (container.parentNode) {
                container.parentNode.removeChild(container);
            }
        }, 500);
    }, 15000);
}

/**
 * 创建玩家信息栏的数值变化浮动文本
 * 体力、气力、理智、精液在对应数值槽位置显示
 * 其他变化在特殊状态下方新开一行显示
 * @param {HTMLElement} panel - 玩家信息面板容器
 * @param {Array} valueChanges - 数值变化数组
 */
function createPlayerFloatingValueChanges(panel, valueChanges) {
    if (!panel || !valueChanges || valueChanges.length === 0) return;
    
    // 根据字段类型分组变化
    const fieldGroups = {};
    valueChanges.forEach(change => {
        const field = change.field;
        if (!fieldGroups[field]) {
            fieldGroups[field] = {
                changes: [],
                color: change.color || 'standard',
                field_name: change.field_name || field
            };
        }
        fieldGroups[field].changes.push(change);
    });
    
    // 未匹配到数值槽位置的变化，收集到这里最后统一显示
    const unmatchedChanges = [];
    
    // 定义玩家数值槽字段映射
    const playerBarFields = ['hit_point', 'mana_point', 'sanity_point', 'semen_point'];
    
    // 为每个字段创建浮动文本
    for (const field in fieldGroups) {
        const group = fieldGroups[field];
        const changes = group.changes;
        const totalValue = changes.reduce((sum, c) => sum + c.value, 0);
        if (totalValue === 0) continue;
        
        const displayName = group.field_name;
        const colorName = group.color;
        
        // 检查是否是玩家的数值槽字段
        if (playerBarFields.includes(field)) {
            // 查找对应的UI元素
            const targetElement = panel.querySelector(`[data-field="${field}"]`);
            
            if (targetElement) {
                // 体力、气力、理智、精液在数值后面显示
                let positionType = 'end-inline';
                createInlineFloatingText(targetElement, displayName, totalValue, colorName, positionType, panel);
            } else {
                // 未找到元素，放到未匹配列表
                unmatchedChanges.push({ displayName, totalValue, colorName });
            }
        } else if (field === 'eja_point') {
            // 射精欲单独处理，在其他变化行显示
            unmatchedChanges.push({ displayName, totalValue, colorName });
        } else if (field.startsWith('experience_')) {
            // 经验值在其他变化行显示
            unmatchedChanges.push({ displayName, totalValue, colorName });
        } else {
            // 其他所有变化也放到未匹配列表（将在特殊状态下方显示）
            unmatchedChanges.push({ displayName, totalValue, colorName });
        }
    }
    
    // 处理未匹配的变化，在特殊状态下方新开一行显示
    if (unmatchedChanges.length > 0) {
        createPlayerBottomFloatingTexts(panel, unmatchedChanges);
    }
}

/**
 * 在玩家信息面板底部创建未匹配变化的浮动文本
 * 位于特殊状态下方
 * @param {HTMLElement} panel - 玩家信息面板容器
 * @param {Array} changes - 未匹配的变化数组
 */
function createPlayerBottomFloatingTexts(panel, changes) {
    // 创建底部浮动文本容器
    const container = document.createElement('div');
    container.className = 'player-floating-container';
    
    changes.forEach((change, index) => {
        const floatText = document.createElement('span');
        floatText.className = 'player-floating-text';
        
        // 设置颜色
        const color = RICH_TEXT_COLORS[change.colorName] || RICH_TEXT_COLORS['standard'];
        floatText.style.color = color;
        
        const sign = change.totalValue > 0 ? '+' : '';
        floatText.textContent = `${change.displayName} ${sign}${change.totalValue}`;
        
        container.appendChild(floatText);
    });
    
    panel.appendChild(container);
    
    // 15秒后移除
    setTimeout(() => {
        container.classList.add('fade-out');
        setTimeout(() => {
            if (container.parentNode) {
                container.parentNode.removeChild(container);
            }
        }, 500);
    }, 15000);
}

/**
 * 创建单个状态项
 * @param {Object} state - 状态数据，包含 id, name, value, max_value, level, tooltip
 * @returns {HTMLElement} - 状态项元素
 */
function createStateItem(state) {
    const item = document.createElement('div');
    item.className = 'state-item';
    // 添加状态ID属性，用于匹配浮动文本
    if (state.id !== undefined) {
        item.dataset.stateId = state.id;
    }
    if (state.tooltip) {
        item.title = state.tooltip;
    }
    
    // 第一行：状态名、等级和数值在同一行
    const header = document.createElement('div');
    header.className = 'state-item-header';
    
    // 状态名和等级（左侧）
    const label = document.createElement('span');
    label.className = 'state-label';
    label.textContent = `${state.name}Lv${state.level}`;
    header.appendChild(label);
    
    // 数值显示（右侧）
    const valueSpan = document.createElement('span');
    valueSpan.className = 'state-value';
    valueSpan.textContent = `${state.value}`;
    header.appendChild(valueSpan);
    
    item.appendChild(header);
    
    // 第二行：状态进度条
    const barTrack = document.createElement('div');
    barTrack.className = 'state-bar-track';
    
    const barFill = document.createElement('div');
    barFill.className = 'state-bar-fill';
    const percentage = state.max_value > 0 ? (state.value / state.max_value * 100) : 0;
    barFill.style.width = `${Math.min(percentage, 100)}%`;
    
    barTrack.appendChild(barFill);
    item.appendChild(barTrack);
    
    return item;
}

/**
 * 创建场景信息栏
 * 显示在面板选项卡上方，包含当前场景名（左侧）和游戏时间（居中）
 * 
 * @param {Object} sceneInfoBar - 场景信息栏数据
 *   - scene_name: 场景名称
 *   - game_time: 游戏时间文本
 * @returns {HTMLElement} 场景信息栏元素
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
 *   - type: 类型（"main" 为主面板，"panel" 为其他面板）
 *   - available: 是否可用
 *   - active: 是否为当前激活的选项卡
 * @returns {HTMLElement} 选项卡栏元素
 */
function createPanelTabsBar(tabs) {
    const bar = document.createElement('div');
    bar.className = 'new-ui-panel-tabs';
    
    tabs.forEach(tab => {
        const btn = document.createElement('button');
        btn.className = 'panel-tab-btn';
        
        // 添加主面板特殊样式
        if (tab.type === 'main') {
            btn.classList.add('main-tab');
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
        
        // 主面板选项卡点击不执行操作（已经在主面板）
        // 其他选项卡点击执行对应的面板切换指令
        if (tab.type !== 'main' || !tab.active) {
            btn.onclick = () => clickPanelTab(tab.id);
        }
        
        bar.appendChild(btn);
    });
    
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
 * 使用普通按钮点击API来确保与后端轮询机制兼容
 */
function clickPanelTab(tabId) {
    // 使用普通的按钮点击API，tabId就是指令ID
    handleButtonClick(tabId);
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