/**
 * UI管理器模块
 * 包含横屏管理、等待管理和滚动管理功能
 */

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
