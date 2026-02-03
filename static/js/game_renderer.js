/**
 * 游戏渲染器模块
 * 负责场景背景、角色立绘和身体部位按钮的渲染
 */

const GameRenderer = {
    canvas: null,
    ctx: null,
    currentBackground: null,
    currentCharacterImage: null,
    characterImageScale: 1,
    characterImageOffset: { x: 0, y: 0 },
    bodyPartButtons: [],
    
    /**
     * 初始化渲染器
     */
    init: function() {
        this.canvas = document.getElementById('character-canvas');
        if (this.canvas) {
            this.ctx = this.canvas.getContext('2d');
            this.resizeCanvas();
            window.addEventListener('resize', () => this.resizeCanvas());
        }
        
        this.setupBodyPartEvents();
    },
    
    /**
     * 调整Canvas尺寸
     */
    resizeCanvas: function() {
        if (!this.canvas) return;
        
        const container = document.getElementById('character-display');
        if (container) {
            this.canvas.width = container.clientWidth;
            this.canvas.height = container.clientHeight;
            this.redraw();
        }
    },
    
    /**
     * 重新绘制
     */
    redraw: function() {
        if (!this.ctx) return;
        
        // 清除画布
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // 绘制角色立绘
        if (this.currentCharacterImage) {
            this.drawCharacterImage();
        }
    },
    
    /**
     * 更新场景背景
     * @param {object} sceneData - 场景数据
     */
    updateSceneBackground: function(sceneData) {
        const bgElement = document.getElementById('scene-background');
        if (!bgElement) return;
        
        if (sceneData.background_image) {
            bgElement.style.backgroundImage = `url('/${sceneData.background_image}')`;
        } else {
            bgElement.style.backgroundImage = 'none';
        }
    },
    
    /**
     * 更新角色图像
     * @param {object} targetInfo - 交互对象信息
     */
    updateCharacterImage: function(targetInfo) {
        if (!targetInfo || !targetInfo.image_data) {
            this.currentCharacterImage = null;
            this.redraw();
            return;
        }
        
        const imageData = targetInfo.image_data;
        const imagePath = imageData.full_body_image || imageData.half_body_image;
        
        if (imagePath) {
            const img = new Image();
            img.onload = () => {
                this.currentCharacterImage = img;
                this.calculateImageTransform(img);
                this.redraw();
                
                // 如果有身体部位数据，保存它
                if (imageData.body_parts) {
                    this.bodyPartsData = imageData.body_parts;
                }
            };
            img.onerror = () => {
                console.error('加载角色图像失败:', imagePath);
                this.currentCharacterImage = null;
                this.redraw();
            };
            img.src = '/' + imagePath;
        } else {
            this.currentCharacterImage = null;
            this.redraw();
        }
    },
    
    /**
     * 计算图像变换参数（缩放和偏移）
     * @param {HTMLImageElement} img - 图像对象
     */
    calculateImageTransform: function(img) {
        if (!this.canvas) return;
        
        const canvasWidth = this.canvas.width;
        const canvasHeight = this.canvas.height;
        const imgWidth = img.width;
        const imgHeight = img.height;
        
        // 计算缩放比例，保持宽高比，使图像适应画布高度
        const scale = canvasHeight / imgHeight;
        
        // 计算居中偏移
        const scaledWidth = imgWidth * scale;
        const offsetX = (canvasWidth - scaledWidth) / 2;
        
        this.characterImageScale = scale;
        this.characterImageOffset = { x: offsetX, y: 0 };
    },
    
    /**
     * 绘制角色图像
     */
    drawCharacterImage: function() {
        if (!this.ctx || !this.currentCharacterImage) return;
        
        const img = this.currentCharacterImage;
        const scale = this.characterImageScale;
        const offset = this.characterImageOffset;
        
        this.ctx.drawImage(
            img,
            offset.x,
            offset.y,
            img.width * scale,
            img.height * scale
        );
    },
    
    /**
     * 设置身体部位事件监听
     */
    setupBodyPartEvents: function() {
        const buttonsContainer = document.getElementById('body-part-buttons');
        const tooltip = document.getElementById('body-part-tooltip');
        
        if (!buttonsContainer) return;
        
        // 鼠标移动事件，用于显示提示框
        buttonsContainer.addEventListener('mousemove', (e) => {
            if (tooltip) {
                tooltip.style.left = (e.clientX + 10) + 'px';
                tooltip.style.top = (e.clientY + 10) + 'px';
            }
        });
    },
    
    /**
     * 更新身体部位按钮
     * @param {Array} parts - 可用部位列表
     */
    updateBodyPartButtons: function(parts) {
        const container = document.getElementById('body-part-buttons');
        if (!container) return;
        
        container.innerHTML = '';
        this.bodyPartButtons = [];
        
        if (!parts || parts.length === 0 || !this.bodyPartsData) {
            return;
        }
        
        const bodyParts = this.bodyPartsData.body_parts || {};
        
        parts.forEach(partName => {
            const partData = bodyParts[partName];
            if (!partData) return;
            
            // 计算实际位置
            const center = partData.center || [0, 0];
            const radius = partData.radius || 30;
            
            const actualX = center[0] * this.characterImageScale + this.characterImageOffset.x;
            const actualY = center[1] * this.characterImageScale + this.characterImageOffset.y;
            const actualRadius = radius * this.characterImageScale;
            
            // 创建按钮
            const btn = document.createElement('button');
            btn.className = 'body-part-btn';
            btn.style.left = (actualX - actualRadius) + 'px';
            btn.style.top = (actualY - actualRadius) + 'px';
            btn.style.width = (actualRadius * 2) + 'px';
            btn.style.height = (actualRadius * 2) + 'px';
            btn.dataset.part = partName;
            
            // 悬停显示提示
            btn.addEventListener('mouseenter', () => {
                this.showPartTooltip(partName);
            });
            
            btn.addEventListener('mouseleave', () => {
                this.hidePartTooltip();
            });
            
            // 点击事件
            btn.addEventListener('click', () => {
                this.handleBodyPartClick(partName);
            });
            
            container.appendChild(btn);
            this.bodyPartButtons.push(btn);
        });
    },
    
    /**
     * 显示部位提示框
     * @param {string} partName - 部位名称
     */
    showPartTooltip: function(partName) {
        const tooltip = document.getElementById('body-part-tooltip');
        if (!tooltip) return;
        
        const displayName = this.getPartDisplayName(partName);
        tooltip.textContent = displayName;
        tooltip.style.display = 'block';
    },
    
    /**
     * 隐藏部位提示框
     */
    hidePartTooltip: function() {
        const tooltip = document.getElementById('body-part-tooltip');
        if (tooltip) {
            tooltip.style.display = 'none';
        }
    },
    
    /**
     * 获取部位显示名称
     * @param {string} partName - 部位英文名称
     * @returns {string} 部位中文名称
     */
    getPartDisplayName: function(partName) {
        const names = {
            'head': '头部',
            'mouth': '嘴巴',
            'forehead': '额头',
            'cheek': '脸颊',
            'neck': '脖子',
            'L_hand': '左手',
            'R_hand': '右手',
            'chest': '胸部',
            'waist': '腰部',
            'L_leg': '左腿',
            'R_leg': '右腿',
            'L_foot': '左脚',
            'R_foot': '右脚',
            'back': '背部',
            'hip': '臀部'
        };
        return names[partName] || partName;
    },
    
    /**
     * 处理身体部位点击
     * @param {string} partName - 部位名称
     */
    handleBodyPartClick: function(partName) {
        WebSocketHandler.clickBodyPart(partName);
    },
    
    /**
     * 显示指令选择菜单
     * @param {number} x - X坐标
     * @param {number} y - Y坐标
     * @param {Array} instructs - 指令列表
     */
    showInstructMenu: function(x, y, instructs) {
        const menu = document.getElementById('instruct-menu');
        if (!menu) return;
        
        const list = menu.querySelector('.instruct-menu-list');
        list.innerHTML = '';
        
        instructs.forEach(instruct => {
            const item = document.createElement('div');
            item.className = 'instruct-menu-item';
            item.textContent = instruct.name;
            item.addEventListener('click', () => {
                WebSocketHandler.executeInstruct(instruct.id);
                this.hideInstructMenu();
            });
            list.appendChild(item);
        });
        
        menu.style.left = x + 'px';
        menu.style.top = y + 'px';
        menu.style.display = 'block';
        
        // 点击其他地方关闭菜单
        document.addEventListener('click', this.hideInstructMenuHandler, { once: true });
    },
    
    hideInstructMenuHandler: function(e) {
        const menu = document.getElementById('instruct-menu');
        if (menu && !menu.contains(e.target)) {
            menu.style.display = 'none';
        }
    },
    
    /**
     * 隐藏指令选择菜单
     */
    hideInstructMenu: function() {
        const menu = document.getElementById('instruct-menu');
        if (menu) {
            menu.style.display = 'none';
        }
    },
    
    /**
     * 显示数值变化
     * @param {object} data - 数值变化数据
     */
    showValueChange: function(data) {
        const layer = document.getElementById('value-change-layer');
        if (!layer) return;
        
        const { x, y, value, isPositive } = data;
        
        const elem = document.createElement('div');
        elem.className = 'value-change ' + (isPositive ? 'positive' : 'negative');
        elem.textContent = (isPositive ? '+' : '') + value;
        elem.style.left = x + 'px';
        elem.style.top = y + 'px';
        
        layer.appendChild(elem);
        
        // 动画结束后移除
        setTimeout(() => {
            elem.remove();
        }, 2000);
    },
    
    /**
     * 清除所有身体部位按钮
     */
    clearBodyPartButtons: function() {
        const container = document.getElementById('body-part-buttons');
        if (container) {
            container.innerHTML = '';
        }
        this.bodyPartButtons = [];
    }
};
