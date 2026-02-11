/**
 * UI组件模块
 * 管理所有UI组件的渲染和更新
 */

const UIComponents = {
    /**
     * 初始化所有UI组件
     */
    init: function() {
        this.TabMenu.init();
        this.PlayerInfoPanel.init();
        this.TargetInfoPanel.init();
        this.TargetExtraInfoPanel.init();
        this.AvatarPanel.init();
        this.InteractionTypePanel.init();
        this.DialogBox.init();
    },
    
    /**
     * 选项卡菜单组件
     */
    TabMenu: {
        container: null,
        activeTab: null,
        
        init: function() {
            this.container = document.querySelector('#panel-tabs .tab-container');
        },
        
        update: function(tabs) {
            if (!this.container) return;
            
            this.container.innerHTML = '';
            tabs.forEach(tab => {
                const btn = document.createElement('button');
                btn.className = 'tab-button';
                if (tab.id === this.activeTab) {
                    btn.classList.add('active');
                }
                if (!tab.available) {
                    btn.disabled = true;
                }
                btn.textContent = tab.name;
                btn.dataset.tabId = tab.id;
                btn.addEventListener('click', () => this.handleClick(tab.id));
                this.container.appendChild(btn);
            });
        },
        
        handleClick: function(tabId) {
            this.activeTab = tabId;
            WebSocketHandler.clickPanelTab(tabId);
        },
        
        setActiveTab: function(tabId) {
            this.activeTab = tabId;
            const buttons = this.container.querySelectorAll('.tab-button');
            buttons.forEach(btn => {
                btn.classList.toggle('active', btn.dataset.tabId === tabId);
            });
        }
    },
    
    /**
     * 玩家信息面板组件
     */
    PlayerInfoPanel: {
        container: null,
        
        init: function() {
            this.container = document.getElementById('player-info');
        },
        
        update: function(data) {
            if (!this.container) return;
            
            // 更新名字
            const nameEl = this.container.querySelector('.player-name');
            if (nameEl) nameEl.textContent = data.name || '';
            
            const nickNameEl = this.container.querySelector('.player-nickname');
            if (nickNameEl) nickNameEl.textContent = data.nick_name || '';
            
            // 更新特殊状态
            const statesEl = this.container.querySelector('.player-special-states');
            if (statesEl && data.special_states) {
                statesEl.textContent = data.special_states.join(' ');
            }
            
            // 更新数值槽
            this.updateBar('.hp-bar', data.hp, data.hp_max);
            this.updateBar('.mp-bar', data.mp, data.mp_max);
            this.updateBar('.sanity-bar', data.sanity, data.sanity_max);
            this.updateBar('.semen-bar', data.semen, data.semen_max);
        },
        
        updateBar: function(selector, value, max) {
            const bar = this.container.querySelector(selector);
            if (!bar) return;
            
            const fill = bar.querySelector('.bar-fill');
            const valueEl = bar.querySelector('.bar-value');
            
            const percent = max > 0 ? (value / max * 100) : 0;
            if (fill) fill.style.width = percent + '%';
            if (valueEl) valueEl.textContent = `${value}/${max}`;
        }
    },
    
    /**
     * 交互对象信息面板组件
     */
    TargetInfoPanel: {
        container: null,
        
        init: function() {
            this.container = document.getElementById('target-info-panel');
        },
        
        update: function(data) {
            if (!this.container) return;
            
            // 更新基础信息
            const nameEl = this.container.querySelector('.target-name');
            if (nameEl) nameEl.textContent = data.name || '';
            
            const favorEl = this.container.querySelector('.target-favorability');
            if (favorEl && data.favorability) {
                favorEl.textContent = `好感:${data.favorability.value}(${data.favorability.level})`;
            }
            
            const trustEl = this.container.querySelector('.target-trust');
            if (trustEl && data.trust) {
                trustEl.textContent = `信赖:${data.trust.value}%(${data.trust.level})`;
            }
            
            // 更新数值槽
            this.updateBar('.hp-bar', data.hp, data.hp_max);
            this.updateBar('.mp-bar', data.mp, data.mp_max);
            
            // 更新特殊状态
            const statesEl = this.container.querySelector('.target-special-states');
            if (statesEl && data.special_states) {
                statesEl.textContent = data.special_states.join(' ');
            }
            
            // 更新快感状态
            this.updateStatesGrid('.pleasure-states .states-grid', data.pleasure_states);
            
            // 更新其他状态
            this.updateStatesGrid('.other-states .states-grid', data.other_states);
        },
        
        updateBar: function(selector, value, max) {
            const bar = this.container.querySelector(selector);
            if (!bar) return;
            
            const fill = bar.querySelector('.bar-fill');
            const percent = max > 0 ? (value / max * 100) : 0;
            if (fill) fill.style.width = percent + '%';
        },
        
        updateStatesGrid: function(selector, states) {
            const grid = this.container.querySelector(selector);
            if (!grid || !states) return;
            
            grid.innerHTML = '';
            states.forEach(state => {
                const item = document.createElement('div');
                item.className = 'state-item';
                item.innerHTML = `
                    <div class="state-name">${state.name}</div>
                    <div class="state-value">${state.value}</div>
                `;
                grid.appendChild(item);
            });
        }
    },
    
    /**
     * 交互对象附加信息面板组件
     */
    TargetExtraInfoPanel: {
        container: null,
        currentTab: 'clothing',
        
        init: function() {
            this.container = document.getElementById('target-extra-info');
            this.setupTabEvents();
        },
        
        setupTabEvents: function() {
            if (!this.container) return;
            
            const tabs = this.container.querySelectorAll('.extra-tab');
            tabs.forEach(tab => {
                tab.addEventListener('click', () => {
                    this.switchTab(tab.dataset.tab);
                });
            });
        },
        
        switchTab: function(tabName) {
            this.currentTab = tabName;
            
            // 更新选项卡状态
            const tabs = this.container.querySelectorAll('.extra-tab');
            tabs.forEach(tab => {
                tab.classList.toggle('active', tab.dataset.tab === tabName);
            });
            
            // 更新面板显示
            const panels = this.container.querySelectorAll('.extra-panel');
            panels.forEach(panel => {
                panel.style.display = panel.id === `${tabName}-panel` ? 'block' : 'none';
            });
        },
        
        update: function(data) {
            if (!this.container) return;
            
            // 更新各个面板内容
            this.updatePanel('clothing-panel', data.clothing);
            this.updatePanel('body-panel', data.body);
            this.updatePanel('group-sex-panel', data.group_sex);
            this.updatePanel('hidden-sex-panel', data.hidden_sex);
        },
        
        updatePanel: function(panelId, content) {
            const panel = document.getElementById(panelId);
            if (!panel) return;
            
            if (typeof content === 'string') {
                panel.textContent = content;
            } else if (content && typeof content === 'object') {
                // 如果是对象，格式化显示
                panel.innerHTML = this.formatContent(content);
            }
        },
        
        formatContent: function(obj) {
            if (!obj || Object.keys(obj).length === 0) {
                return '<span style="color: var(--text-secondary);">无信息</span>';
            }
            
            let html = '';
            for (const [key, value] of Object.entries(obj)) {
                html += `<div>${key}: ${value}</div>`;
            }
            return html;
        }
    },
    
    /**
     * 头像区组件
     */
    AvatarPanel: {
        container: null,
        characters: [],
        currentPage: 0,
        maxDisplay: 5,
        
        init: function() {
            this.container = document.getElementById('avatar-area');
        },
        
        update: function(characters) {
            this.characters = characters;
            this.currentPage = 0;
            this.render();
        },
        
        render: function() {
            if (!this.container) return;
            
            const grid = this.container.querySelector('.avatar-grid');
            const pageBtn = this.container.querySelector('.avatar-page-btn');
            
            if (!grid) return;
            
            grid.innerHTML = '';
            
            const startIdx = this.currentPage * this.maxDisplay;
            const endIdx = Math.min(startIdx + this.maxDisplay, this.characters.length);
            const hasMore = this.characters.length > endIdx;
            
            for (let i = startIdx; i < endIdx; i++) {
                const char = this.characters[i];
                const item = document.createElement('div');
                item.className = 'avatar-item';
                item.dataset.charId = char.id;
                
                if (char.avatar) {
                    item.innerHTML = `<img src="/${char.avatar}" alt="${char.name}" title="${char.name}">`;
                } else {
                    item.innerHTML = `<span style="font-size: 10px;">${char.name.substring(0, 2)}</span>`;
                }
                
                item.addEventListener('click', () => this.handleClick(char.id));
                grid.appendChild(item);
            }
            
            // 翻页按钮
            if (pageBtn) {
                pageBtn.style.display = hasMore ? 'block' : 'none';
                pageBtn.onclick = () => this.nextPage();
            }
        },
        
        nextPage: function() {
            const maxPage = Math.ceil(this.characters.length / this.maxDisplay) - 1;
            this.currentPage = (this.currentPage + 1) % (maxPage + 1);
            this.render();
        },
        
        handleClick: function(characterId) {
            WebSocketHandler.switchTarget(characterId);
        }
    },
    
    /**
     * 交互类型面板组件
     */
    InteractionTypePanel: {
        container: null,
        majorTypes: [],
        currentMajor: null,
        
        init: function() {
            this.container = document.getElementById('interaction-type-panel');
        },
        
        update: function(types) {
            if (!this.container) return;
            
            // 保留已加载的小类数据
            const oldMajorTypes = this.majorTypes || [];
            this.majorTypes = types.map(t => {
                const old = oldMajorTypes.find(oldT => oldT.id === t.id);
                return {
                    ...t,
                    minorTypes: old ? old.minorTypes : []
                };
            });
            
            this.render();
        },
        
        updateMinorTypes: function(majorId, minorTypes) {
            const major = this.majorTypes.find(t => t.id === majorId);
            if (major) {
                major.minorTypes = minorTypes;
            }
            this.currentMajor = majorId;
            this.render();
        },
        
        setActiveMinorType: function(minorId) {
             const allMinorBtns = this.container.querySelectorAll('.minor-card');
             allMinorBtns.forEach(btn => {
                 btn.classList.toggle('active', btn.dataset.id === minorId);
             });
        },

        render: function() {
            let list = this.container.querySelector('.interaction-type-list');
            if (!list) {
                list = document.createElement('div');
                list.className = 'interaction-type-list';
                this.container.innerHTML = '';
                this.container.appendChild(list);
            }
            list.innerHTML = '';
            
            this.majorTypes.forEach(major => {
                const majorCard = document.createElement('div');
                majorCard.className = 'interaction-card major-card';
                if (major.id === this.currentMajor) majorCard.classList.add('active');
                
                majorCard.innerHTML = `
                   <span class="icon">${this.getIcon(major.id)}</span>
                   <div class="label-group">
                       <span class="name">${major.name}</span>
                       <span class="desc">INTERACTION</span>
                   </div>
                `;
                majorCard.addEventListener('click', () => {
                     WebSocketHandler.selectMajorType(major.id);
                });
                
                list.appendChild(majorCard);
                
                if (major.id === this.currentMajor && major.minorTypes && major.minorTypes.length > 0) {
                    const minorList = document.createElement('div');
                    minorList.className = 'interaction-minor-list';
                    
                    major.minorTypes.forEach(minor => {
                        const minorCard = document.createElement('div');
                        minorCard.className = 'interaction-card minor-card';
                        minorCard.dataset.id = minor.id;
                        minorCard.innerHTML = `
                            <span class="dot">⬢</span>
                            <span class="name">${minor.name}</span>
                        `;
                        minorCard.addEventListener('click', (e) => {
                             e.stopPropagation();
                             WebSocketHandler.selectMinorType(minor.id);
                        });
                        minorList.appendChild(minorCard);
                    });
                    list.appendChild(minorList);
                }
            });
        },
        
        getIcon: function(typeId) {
            const icons = {
                'talk': '💬',
                'touch': '✋',
                'kiss': '💋',
                'dress': '👔',
                'h': '💕',
                'mouth': '👄',
                'hand': '✋',
                'sex': '❤',
                'penis': '🍆',
                'tool': '💊',
                'arts': '✨',
                'other': '⚙'
            };
            return icons[typeId] || '●';
        },
        
        handleClick: function(typeId) {
             // Backward compatibility or unused
             WebSocketHandler.selectInteractionType(typeId);
        },
        
        clearSelection: function() {
            this.currentMajor = null;
            this.render();
        }
    },
    
    /**
     * 对话框组件
     */
    DialogBox: {
        container: null,
        isVisible: false,
        
        init: function() {
            this.container = document.getElementById('dialog-box');
            this.setupEvents();
        },
        
        setupEvents: function() {
            // 点击推进对话
            document.addEventListener('click', (e) => {
                if (this.isVisible && !e.target.closest('#interaction-type-panel') && 
                    !e.target.closest('#panel-tabs')) {
                    WebSocketHandler.advanceDialog();
                }
            });
            
            // 右键或Ctrl跳过
            document.addEventListener('contextmenu', (e) => {
                if (this.isVisible) {
                    e.preventDefault();
                    WebSocketHandler.skipDialog();
                }
            });
            
            document.addEventListener('keydown', (e) => {
                if (this.isVisible && e.key === 'Control') {
                    WebSocketHandler.skipDialog();
                }
            });
        },
        
        show: function(speaker, text) {
            if (!this.container) return;
            
            const speakerEl = this.container.querySelector('.dialog-speaker');
            const textEl = this.container.querySelector('.dialog-text');
            
            if (speakerEl) speakerEl.textContent = speaker || '';
            if (textEl) textEl.textContent = text || '';
            
            this.container.style.display = 'block';
            this.isVisible = true;
        },
        
        hide: function() {
            if (!this.container) return;
            
            this.container.style.display = 'none';
            this.isVisible = false;
        }
    }
};
