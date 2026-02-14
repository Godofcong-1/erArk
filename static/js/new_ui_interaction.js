/**
 * 新UI交互模块
 * 包含头像面板、交互类型面板等组件
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
    
    // Clear existing floating instructs (both individual cards and container)
    if (minorList) {
        minorList.querySelectorAll('.floating-instruct').forEach(e => e.remove());
        minorList.querySelectorAll('.floating-instruct-container').forEach(e => e.remove());
    }

    const activeMinor = minorList ? minorList.querySelector('.active') : null;

    if (!instructs || instructs.length === 0 || !activeMinor) {
        // Just trigger standard layout adjustment if needed
        setTimeout(() => checkAndAdjustCharacterImage(), 50);
        return;
    }

    // Create container for floating buttons
    const container = document.createElement('div');
    container.className = 'floating-instruct-container';
    
    // 如果指令数量超过10个，这里不需要特殊处理，CSS会将最大高度限制为约10个的高度 并显示滚动条

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
         container.appendChild(card);
    });
    
    // Insert container after activeMinor
    if (activeMinor.nextSibling) {
        minorList.insertBefore(container, activeMinor.nextSibling);
    } else {
        minorList.appendChild(container);
    }
    
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
