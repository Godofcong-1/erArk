/**
 * 交互管理器模块
 * 负责处理用户交互逻辑和结算流程
 */

const InteractionManager = {
    isSettling: false,
    currentPhase: 'idle',
    
    /**
     * 初始化交互管理器
     */
    init: function() {
        this.setupGlobalEvents();
    },
    
    /**
     * 设置全局事件监听
     */
    setupGlobalEvents: function() {
        // 快捷键处理
        document.addEventListener('keydown', (e) => {
            this.handleKeyDown(e);
        });
        
        // 点击空白区域关闭菜单
        document.addEventListener('click', (e) => {
            if (!e.target.closest('#instruct-menu') && 
                !e.target.closest('.body-part-btn')) {
                GameRenderer.hideInstructMenu();
            }
        });
    },
    
    /**
     * 处理键盘按键
     * @param {KeyboardEvent} e - 键盘事件
     */
    handleKeyDown: function(e) {
        // ESC键关闭菜单
        if (e.key === 'Escape') {
            GameRenderer.hideInstructMenu();
            UIComponents.InteractionTypePanel.clearSelection();
            GameRenderer.clearBodyPartButtons();
        }
        
        // 空格键推进对话
        if (e.key === ' ' && UIComponents.DialogBox.isVisible) {
            e.preventDefault();
            WebSocketHandler.advanceDialog();
        }
    },
    
    /**
     * 处理结算阶段
     * @param {object} data - 结算数据
     */
    handleSettlement: function(data) {
        switch (data.phase) {
            case 'start':
                this.startSettlement();
                break;
            case 'dialog':
                this.handleSettlementDialog(data);
                break;
            case 'value_change':
                this.handleSettlementValueChange(data);
                break;
            case 'end':
                this.endSettlement();
                break;
        }
    },
    
    /**
     * 开始结算阶段
     */
    startSettlement: function() {
        this.isSettling = true;
        this.currentPhase = 'settling';
        
        // 隐藏交互UI
        this.disableInteraction();
    },
    
    /**
     * 处理结算对话
     * @param {object} data - 对话数据
     */
    handleSettlementDialog: function(data) {
        if (data.dialog_type === 'full') {
            // 完整对话框显示（玩家和交互对象）
            UIComponents.DialogBox.show(data.speaker, data.text);
        } else if (data.dialog_type === 'mini') {
            // 小型对话框显示（其他角色）
            this.showMiniDialog(data.character_id, data.text);
        }
    },
    
    /**
     * 显示小型对话框（头像上方）
     * @param {number} characterId - 角色ID
     * @param {string} text - 对话文本
     */
    showMiniDialog: function(characterId, text) {
        const avatarGrid = document.querySelector('.avatar-grid');
        if (!avatarGrid) return;
        
        const avatarItem = avatarGrid.querySelector(`[data-char-id="${characterId}"]`);
        if (!avatarItem) return;
        
        // 创建小对话框
        let miniDialog = avatarItem.querySelector('.mini-dialog');
        if (!miniDialog) {
            miniDialog = document.createElement('div');
            miniDialog.className = 'mini-dialog';
            miniDialog.style.cssText = `
                position: absolute;
                bottom: 100%;
                left: 50%;
                transform: translateX(-50%);
                background: rgba(0, 0, 0, 0.8);
                color: #fff;
                padding: 5px 10px;
                border-radius: 5px;
                font-size: 11px;
                white-space: nowrap;
                max-width: 150px;
                overflow: hidden;
                text-overflow: ellipsis;
            `;
            avatarItem.style.position = 'relative';
            avatarItem.appendChild(miniDialog);
        }
        
        // 截取前N个字符
        const maxLength = 15;
        const displayText = text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
        miniDialog.textContent = displayText;
        miniDialog.style.display = 'block';
        
        // 一段时间后自动隐藏
        setTimeout(() => {
            miniDialog.style.display = 'none';
        }, 3000);
    },
    
    /**
     * 处理结算数值变化
     * @param {object} data - 数值变化数据
     */
    handleSettlementValueChange: function(data) {
        data.changes.forEach((change, index) => {
            // 延迟显示，形成依次出现的效果
            setTimeout(() => {
                GameRenderer.showValueChange({
                    x: change.x || 100,
                    y: (change.y || 100) + index * 25,
                    value: change.value,
                    isPositive: change.value > 0
                });
            }, index * 200);
        });
    },
    
    /**
     * 结束结算阶段
     */
    endSettlement: function() {
        this.isSettling = false;
        this.currentPhase = 'idle';
        
        // 恢复交互UI
        this.enableInteraction();
        
        // 隐藏对话框
        UIComponents.DialogBox.hide();
    },
    
    /**
     * 禁用交互
     */
    disableInteraction: function() {
        // 隐藏选项卡
        const tabs = document.getElementById('panel-tabs');
        if (tabs) tabs.style.pointerEvents = 'none';
        
        // 隐藏交互类型栏
        const interactionPanel = document.getElementById('interaction-type-panel');
        if (interactionPanel) interactionPanel.style.pointerEvents = 'none';
        
        // 清除身体部位按钮
        GameRenderer.clearBodyPartButtons();
    },
    
    /**
     * 启用交互
     */
    enableInteraction: function() {
        // 恢复选项卡
        const tabs = document.getElementById('panel-tabs');
        if (tabs) tabs.style.pointerEvents = 'auto';
        
        // 恢复交互类型栏
        const interactionPanel = document.getElementById('interaction-type-panel');
        if (interactionPanel) interactionPanel.style.pointerEvents = 'auto';
    },
    
    /**
     * 处理指令执行结果
     * @param {object} data - 执行结果
     */
    handleInstructResult: function(data) {
        if (data.success) {
            // 隐藏指令菜单
            GameRenderer.hideInstructMenu();
            
            // 清除交互类型选择
            UIComponents.InteractionTypePanel.clearSelection();
            
            // 清除身体部位按钮
            GameRenderer.clearBodyPartButtons();
        } else {
            // 显示错误信息
            console.error('指令执行失败:', data.error);
            // TODO: 显示错误提示
        }
    },
    
    /**
     * 处理身体部位点击响应
     * @param {object} data - 部位点击响应数据
     */
    handleBodyPartResponse: function(data) {
        if (data.auto_execute && data.instructs.length === 1) {
            // 只有一个指令，直接执行
            WebSocketHandler.executeInstruct(data.instructs[0].id);
        } else if (data.instructs.length > 1) {
            // 多个指令，显示选择菜单
            // 获取点击的部位按钮位置
            const btn = document.querySelector(`[data-part="${data.body_part}"]`);
            if (btn) {
                const rect = btn.getBoundingClientRect();
                GameRenderer.showInstructMenu(
                    rect.left + rect.width / 2,
                    rect.top,
                    data.instructs
                );
            }
        }
    },
    
    /**
     * 检查当前是否可以进行交互
     * @returns {boolean} 是否可以交互
     */
    canInteract: function() {
        return !this.isSettling && this.currentPhase === 'idle';
    }
};
