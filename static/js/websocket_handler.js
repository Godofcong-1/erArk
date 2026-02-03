/**
 * WebSocket处理模块
 * 负责与后端的实时通信
 */

const WebSocketHandler = {
    socket: null,
    connected: false,
    reconnectAttempts: 0,
    maxReconnectAttempts: 5,
    
    /**
     * 初始化WebSocket连接
     */
    init: function() {
        this.connect();
        this.setupEventListeners();
    },
    
    /**
     * 建立WebSocket连接
     */
    connect: function() {
        // 使用Socket.IO连接
        this.socket = io({
            reconnection: true,
            reconnectionDelay: 1000,
            reconnectionDelayMax: 5000,
            reconnectionAttempts: this.maxReconnectAttempts
        });
        
        this.socket.on('connect', () => {
            console.log('WebSocket已连接');
            this.connected = true;
            this.reconnectAttempts = 0;
            // 请求初始游戏状态
            this.requestGameState();
        });
        
        this.socket.on('disconnect', () => {
            console.log('WebSocket已断开');
            this.connected = false;
        });
        
        this.socket.on('connect_error', (error) => {
            console.error('WebSocket连接错误:', error);
            this.reconnectAttempts++;
        });
    },
    
    /**
     * 设置事件监听器
     */
    setupEventListeners: function() {
        // 监听游戏状态更新
        this.socket.on('game_state_update', (data) => {
            this.handleGameStateUpdate(data);
        });
        
        // 监听对话框更新
        this.socket.on('dialog_update', (data) => {
            this.handleDialogUpdate(data);
        });
        
        // 监听结算阶段更新
        this.socket.on('settlement_update', (data) => {
            this.handleSettlementUpdate(data);
        });
        
        // 监听数值变化
        this.socket.on('value_change', (data) => {
            this.handleValueChange(data);
        });
        
        // 监听指令执行结果
        this.socket.on('instruct_result', (data) => {
            this.handleInstructResult(data);
        });
    },
    
    /**
     * 请求当前游戏状态
     */
    requestGameState: function() {
        this.emit('request_game_state', {});
    },
    
    /**
     * 发送消息到服务器
     * @param {string} event - 事件名称
     * @param {object} data - 数据
     */
    emit: function(event, data) {
        if (this.connected && this.socket) {
            this.socket.emit(event, data);
        } else {
            console.warn('WebSocket未连接，无法发送消息:', event);
        }
    },
    
    /**
     * 处理游戏状态更新
     * @param {object} data - 游戏状态数据
     */
    handleGameStateUpdate: function(data) {
        console.log('收到游戏状态更新:', data);
        
        // 更新场景背景
        if (data.scene) {
            GameRenderer.updateSceneBackground(data.scene);
        }
        
        // 更新玩家信息
        if (data.player_info) {
            UIComponents.PlayerInfoPanel.update(data.player_info);
        }
        
        // 更新交互对象信息
        if (data.target_info) {
            UIComponents.TargetInfoPanel.update(data.target_info);
            GameRenderer.updateCharacterImage(data.target_info);
        }
        
        // 更新交互对象附加信息
        if (data.target_extra_info) {
            UIComponents.TargetExtraInfoPanel.update(data.target_extra_info);
        }
        
        // 更新场景角色头像
        if (data.scene_characters) {
            UIComponents.AvatarPanel.update(data.scene_characters);
        }
        
        // 更新交互类型
        if (data.interaction_types) {
            UIComponents.InteractionTypePanel.update(data.interaction_types);
        }
        
        // 更新面板选项卡
        if (data.panel_tabs) {
            UIComponents.TabMenu.update(data.panel_tabs);
        }
        
        // 更新可用部位
        if (data.available_body_parts !== undefined) {
            GameRenderer.updateBodyPartButtons(data.available_body_parts);
        }
    },
    
    /**
     * 处理对话框更新
     * @param {object} data - 对话框数据
     */
    handleDialogUpdate: function(data) {
        if (data.visible) {
            UIComponents.DialogBox.show(data.speaker, data.text);
        } else {
            UIComponents.DialogBox.hide();
        }
    },
    
    /**
     * 处理结算阶段更新
     * @param {object} data - 结算数据
     */
    handleSettlementUpdate: function(data) {
        InteractionManager.handleSettlement(data);
    },
    
    /**
     * 处理数值变化
     * @param {object} data - 数值变化数据
     */
    handleValueChange: function(data) {
        GameRenderer.showValueChange(data);
    },
    
    /**
     * 处理指令执行结果
     * @param {object} data - 执行结果数据
     */
    handleInstructResult: function(data) {
        InteractionManager.handleInstructResult(data);
    },
    
    /**
     * 选择交互类型
     * @param {string} typeId - 交互类型ID
     */
    selectInteractionType: function(typeId) {
        this.emit('select_interaction_type', { type_id: typeId });
    },
    
    /**
     * 点击身体部位
     * @param {string} partName - 部位名称
     */
    clickBodyPart: function(partName) {
        this.emit('click_body_part', { part_name: partName });
    },
    
    /**
     * 执行指令
     * @param {number} instructId - 指令ID
     */
    executeInstruct: function(instructId) {
        this.emit('execute_instruct', { instruct_id: instructId });
    },
    
    /**
     * 切换交互对象
     * @param {number} characterId - 角色ID
     */
    switchTarget: function(characterId) {
        this.emit('switch_target', { character_id: characterId });
    },
    
    /**
     * 点击面板选项卡
     * @param {string} tabId - 选项卡ID
     */
    clickPanelTab: function(tabId) {
        this.emit('click_panel_tab', { tab_id: tabId });
    },
    
    /**
     * 推进对话
     */
    advanceDialog: function() {
        this.emit('advance_dialog', {});
    },
    
    /**
     * 跳过对话
     */
    skipDialog: function() {
        this.emit('skip_dialog', {});
    }
};
