/**
 * 持久输入框历史管理
 * 为Web游戏界面提供命令历史记录功能
 */

// 持久输入框历史管理全局变量
const PERSISTENT_INPUT_HISTORY_MAX_LENGTH = 21;
const PERSISTENT_INPUT_HISTORY_STORAGE_KEY = 'erark_persistent_input_history_v1';
let persistentInputHistory = [];
let persistentInputHistoryIndex = -1;
let persistentInputHistoryDraft = '';
let persistentInputHistoryBrowsing = false;

/**
 * 从本地存储加载历史记录
 */
function loadPersistentInputHistoryFromStorage() {
    try {
        const rawValue = localStorage.getItem(PERSISTENT_INPUT_HISTORY_STORAGE_KEY);
        if (!rawValue) return;

        const parsed = JSON.parse(rawValue);
        if (!Array.isArray(parsed)) return;

        // 仅保留有效字符串，限制最大长度
        persistentInputHistory = parsed
            .filter(item => typeof item === 'string' && item.trim() !== '')
            .slice(-PERSISTENT_INPUT_HISTORY_MAX_LENGTH);
    } catch (error) {
        console.warn('[PersistentInputHistory] 读取本地历史失败:', error);
        persistentInputHistory = [];
    }
}

/**
 * 将历史记录写入本地存储
 */
function savePersistentInputHistoryToStorage() {
    try {
        localStorage.setItem(PERSISTENT_INPUT_HISTORY_STORAGE_KEY, JSON.stringify(persistentInputHistory));
    } catch (error) {
        console.warn('[PersistentInputHistory] 保存本地历史失败:', error);
    }
}

/**
 * 添加命令到历史记录
 * 仅在输入非空时添加，避免重复的空输入
 */
function addPersistentInputHistory(command) {
    if (!command || command.trim() === '') return;
    if (persistentInputHistory.length === 0 || persistentInputHistory[persistentInputHistory.length - 1] !== command) {
        persistentInputHistory.push(command);
        if (persistentInputHistory.length > PERSISTENT_INPUT_HISTORY_MAX_LENGTH) {
            persistentInputHistory.shift();
        }
        savePersistentInputHistoryToStorage();
    }
}

/**
 * 重置历史浏览状态
 */
function resetPersistentInputHistoryState() {
    persistentInputHistoryBrowsing = false;
    persistentInputHistoryIndex = -1;
    persistentInputHistoryDraft = '';
}

/**
 * 规范化命令文本，压缩多余空白
 */
function normalizePersistentInputCommand(command) {
    return String(command || '').replace(/\s+/g, ' ').trim();
}

/**
 * 判断两个命令文本是否等价
 */
function matchesPersistentInputCommand(leftCommand, rightCommand) {
    const normalizedLeft = normalizePersistentInputCommand(leftCommand);
    const normalizedRight = normalizePersistentInputCommand(rightCommand);
    if (!normalizedLeft || !normalizedRight) {
        return false;
    }

    return normalizedLeft === normalizedRight || normalizedLeft.replace(/\s+/g, '') === normalizedRight.replace(/\s+/g, '');
}

/**
 * 记录一条命令并重置历史浏览状态
 */
function recordPersistentInputCommand(command) {
    addPersistentInputHistory(command);
    resetPersistentInputHistoryState();
}

/**
 * 获取上一个不同的历史命令索引
 */
function getPreviousDistinctPersistentInputIndex() {
    if (persistentInputHistory.length === 0) return -1;
    const currentCommand = persistentInputHistoryIndex >= 0 ? persistentInputHistory[persistentInputHistoryIndex] : '';
    let searchIndex = persistentInputHistoryIndex - 1;
    
    while (searchIndex >= 0) {
        if (persistentInputHistory[searchIndex] !== currentCommand) {
            return searchIndex;
        }
        searchIndex--;
    }
    return -1;
}

/**
 * 获取下一个不同的历史命令索引
 */
function getNextDistinctPersistentInputIndex() {
    if (persistentInputHistory.length === 0) return -1;
    const currentCommand = persistentInputHistoryIndex >= 0 ? persistentInputHistory[persistentInputHistoryIndex] : '';
    let searchIndex = persistentInputHistoryIndex + 1;
    
    while (searchIndex < persistentInputHistory.length) {
        if (persistentInputHistory[searchIndex] !== currentCommand) {
            return searchIndex;
        }
        searchIndex++;
    }
    return -1;
}

/**
 * 显示上一条历史命令
 */
function showPreviousPersistentInput() {
    const persistentInput = document.getElementById('persistent-input');
    if (!persistentInput || persistentInputHistory.length === 0) return;
    
    if (!persistentInputHistoryBrowsing) {
        persistentInputHistoryDraft = persistentInput.value;
        persistentInputHistoryBrowsing = true;
        persistentInputHistoryIndex = persistentInputHistory.length - 1;
        persistentInput.value = persistentInputHistory[persistentInputHistoryIndex];
        return;
    }
    
    const nextIndex = getPreviousDistinctPersistentInputIndex();
    if (nextIndex !== -1) {
        persistentInputHistoryIndex = nextIndex;
        persistentInput.value = persistentInputHistory[nextIndex];
    }
}

/**
 * 显示下一条历史命令
 */
function showNextPersistentInput() {
    const persistentInput = document.getElementById('persistent-input');
    if (!persistentInput || persistentInputHistory.length === 0) return;
    if (!persistentInputHistoryBrowsing) return;
    
    const nextIndex = getNextDistinctPersistentInputIndex();
    if (nextIndex !== -1) {
        persistentInputHistoryIndex = nextIndex;
        persistentInput.value = persistentInputHistory[nextIndex];
    } else {
        persistentInput.value = persistentInputHistoryDraft;
        resetPersistentInputHistoryState();
    }
}

/**
 * 初始化持久输入框的历史功能
 */
function initPersistentInputHistory() {
    const persistentInput = document.getElementById('persistent-input');
    if (!persistentInput) return;

    // 初始化时恢复上次会话的历史记录
    loadPersistentInputHistoryFromStorage();
    
    // 扩展现有的 keydown 监听器
    persistentInput.addEventListener('keydown', (event) => {
        if (event.key === 'ArrowUp') {
            event.preventDefault();
            event.stopPropagation();
            showPreviousPersistentInput();
            return;
        }
        if (event.key === 'ArrowDown') {
            event.preventDefault();
            event.stopPropagation();
            showNextPersistentInput();
            return;
        }
    });
    
    // 添加input事件监听，用户编辑时重置浏览状态
    persistentInput.addEventListener('input', () => {
        if (persistentInputHistoryBrowsing) {
            resetPersistentInputHistoryState();
        }
    });
}

// 当 DOM 准备好时初始化历史功能
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPersistentInputHistory);
} else {
    // DOM 已经加载，直接初始化
    setTimeout(initPersistentInputHistory, 0);
}
