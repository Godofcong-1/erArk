/**
 * 设备检测与缩放管理模块
 * 负责设备类型检测、屏幕方向检测和自动缩放功能
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
