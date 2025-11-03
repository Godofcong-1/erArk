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

        groupLines.forEach(line => {
            line.style.width = '';
            line.style.marginLeft = '';
            line.style.marginRight = '';
        });

        if (wrapper) {
            wrapper.style.width = '100%';
        }

        if (inner) {
            inner.style.width = '';
        }

        requestAnimationFrame(() => {
            const widths = groupLines.map(line => line.scrollWidth || line.offsetWidth || 0);
            const maxWidth = Math.max(...widths);
            groupLines.forEach(line => {
                line.style.width = `${maxWidth}px`;
                line.style.marginLeft = '0';
                line.style.marginRight = '0';
                line.style.justifyContent = 'flex-start';
            });

            if (inner) {
                inner.style.width = `${maxWidth}px`;
            }
        });

        currentGroup = [];
    };

    children.forEach(child => {
        if (child.classList && child.classList.contains('map-line')) {
            currentGroup.push(child);
        } else {
            flushGroup();
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