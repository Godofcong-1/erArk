/**
 * 新UI角色显示模块
 * 包含角色立绘显示、身体部位按钮、交互对象信息面板等
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
