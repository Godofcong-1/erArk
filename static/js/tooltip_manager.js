/**
 * 工具提示管理器模块
 * 管理按钮悬停时的提示文本展示
 */

/**
 * 工具提示管理器
 * 功能：负责在 Web 端按钮悬停、聚焦或触摸时显示说明文本
 * 输入：外部通过 attach 传入 DOM 元素与文本
 * 输出：在页面上渲染/隐藏提示浮层，无返回值
 */
const TooltipManager = (() => {
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
