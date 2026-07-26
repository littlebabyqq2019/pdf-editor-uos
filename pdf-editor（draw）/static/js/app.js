/**
 * PDF编辑器 - 主应用逻辑
 */

// 全局状态管理
const AppState = {
    pdfFile: null,
    pdfDoc: null,
    pages: [],
    currentPageIndex: 0,
    currentTool: 'select',
    fabricCanvas: null,
    canvasHistory: [],
    historyStep: -1,
    zoom: 1.0,
    isUndoRedoing: false  // 标志：是否正在执行撤销/重做
};

// 初始化应用
document.addEventListener('DOMContentLoaded', function() {
    console.log('PDF编辑器初始化...');
    
    // 初始化事件监听
    initEventListeners();
    
    // 初始化拖拽上传
    initDragAndDrop();
    
    // 初始化快捷键
    initKeyboardShortcuts();
});

/**
 * 初始化事件监听器
 */
function initEventListeners() {
    // 文件上传（仅保留上传提示区域的按钮）
    document.getElementById('pdfUploadDrop').addEventListener('change', handleFileSelect);
    
    // 工具栏按钮
    document.getElementById('selectTool').addEventListener('click', () => setTool('select'));
    document.getElementById('textTool').addEventListener('click', () => setTool('text'));
    document.getElementById('eraseTool').addEventListener('click', () => setTool('erase'));
    document.getElementById('highlightTool').addEventListener('click', () => setTool('highlight'));
    document.getElementById('underlineTool').addEventListener('click', () => setTool('underline'));
    document.getElementById('shapeTool').addEventListener('click', () => setTool('shape'));
    
    // 编辑操作
    document.getElementById('undoBtn').addEventListener('click', undo);
    document.getElementById('redoBtn').addEventListener('click', redo);
    document.getElementById('deleteBtn').addEventListener('click', deleteSelected);
    
    // 缩放控件
    document.getElementById('zoomInBtn').addEventListener('click', zoomIn);
    document.getElementById('zoomOutBtn').addEventListener('click', zoomOut);
    document.getElementById('zoomResetBtn').addEventListener('click', zoomReset);
    
    // 缩放输入框
    const zoomInput = document.getElementById('zoomInput');
    zoomInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            handleZoomInput();
            zoomInput.blur(); // 失去焦点
        }
    });
    zoomInput.addEventListener('blur', handleZoomInput);
    
    // 输入框获得焦点时选中所有文本
    zoomInput.addEventListener('focus', function() {
        this.select();
    });
    
    // 保存按钮
    document.getElementById('savePdfBtn').addEventListener('click', savePDF);
    
    // 文字工具属性
    document.getElementById('fontFamily').addEventListener('change', updateTextProperties);
    document.getElementById('fontSize').addEventListener('change', updateTextProperties);
    document.getElementById('fontColor').addEventListener('change', updateTextProperties);
    document.getElementById('boldBtn').addEventListener('click', toggleBold);
    document.getElementById('italicBtn').addEventListener('click', toggleItalic);
    
    // 形状工具属性
    document.getElementById('shapeType').addEventListener('change', updateShapeProperties);
    document.getElementById('shapeFill').addEventListener('change', updateShapeProperties);
    document.getElementById('shapeStroke').addEventListener('change', updateShapeProperties);
    document.getElementById('shapeFilled').addEventListener('change', updateShapeProperties);
    
    // 键盘快捷键
    document.addEventListener('keydown', function(e) {
        // Ctrl+Z 撤销
        if (e.ctrlKey && e.key === 'z') {
            e.preventDefault();
            undo();
        }
        // Ctrl+Y 重做
        if (e.ctrlKey && e.key === 'y') {
            e.preventDefault();
            redo();
        }
        // Ctrl+加号 放大
        if (e.ctrlKey && (e.key === '+' || e.key === '=')) {
            e.preventDefault();
            zoomIn();
        }
        // Ctrl+减号 缩小
        if (e.ctrlKey && e.key === '-') {
            e.preventDefault();
            zoomOut();
        }
        // Ctrl+0 重置缩放
        if (e.ctrlKey && e.key === '0') {
            e.preventDefault();
            zoomReset();
        }
    });
}

/**
 * 初始化拖拽上传
 */
function initDragAndDrop() {
    const uploadPrompt = document.getElementById('uploadPrompt');
    
    // 阻止默认拖拽行为
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        document.body.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    // 拖拽进入/离开效果
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadPrompt.addEventListener(eventName, () => {
            uploadPrompt.classList.add('drag-over');
        });
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        uploadPrompt.addEventListener(eventName, () => {
            uploadPrompt.classList.remove('drag-over');
        });
    });
    
    // 处理文件拖放
    uploadPrompt.addEventListener('drop', function(e) {
        const files = e.dataTransfer.files;
        if (files.length > 0 && files[0].type === 'application/pdf') {
            handleFile(files[0]);
        } else {
            alert('请上传PDF文件！');
        }
    });
}

/**
 * 初始化键盘快捷键
 */
function initKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl+Z: 撤销
        if (e.ctrlKey && e.key === 'z') {
            e.preventDefault();
            undo();
        }
        
        // Ctrl+Y: 重做
        if (e.ctrlKey && e.key === 'y') {
            e.preventDefault();
            redo();
        }
        
        // Ctrl+S: 保存
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            savePDF();
        }
        
        // Delete: 删除选中对象
        if (e.key === 'Delete' && AppState.fabricCanvas) {
            deleteSelected();
        }
        
        // ESC: 取消选择
        if (e.key === 'Escape' && AppState.fabricCanvas) {
            AppState.fabricCanvas.discardActiveObject();
            AppState.fabricCanvas.renderAll();
        }
    });
}

/**
 * 处理文件选择
 */
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file && file.type === 'application/pdf') {
        handleFile(file);
    } else {
        alert('请选择PDF文件！');
    }
}

/**
 * 处理PDF文件
 */
function handleFile(file) {
    console.log('处理PDF文件:', file.name);
    AppState.pdfFile = file;
    
    // 显示加载提示
    showLoading(true);
    
    // 读取并加载PDF
    const fileReader = new FileReader();
    fileReader.onload = function() {
        loadPDF(new Uint8Array(this.result));
    };
    fileReader.readAsArrayBuffer(file);
}

/**
 * 设置当前工具
 */
function setTool(toolName) {
    console.log('切换工具:', toolName);
    AppState.currentTool = toolName;
    
    // 更新工具按钮状态
    document.querySelectorAll('.tool-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    const toolBtn = document.getElementById(toolName + 'Tool');
    if (toolBtn) {
        toolBtn.classList.add('active');
    }
    
    // 显示/隐藏工具属性面板
    document.getElementById('textToolbar').classList.toggle('hidden', toolName !== 'text');
    document.getElementById('underlineToolbar').classList.toggle('hidden', toolName !== 'underline');
    document.getElementById('shapeToolbar').classList.toggle('hidden', toolName !== 'shape');
    
    // 更新编辑器模式
    if (window.updateEditorMode) {
        updateEditorMode(toolName);
    }
}

/**
 * 显示/隐藏加载提示
 */
function showLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    overlay.classList.toggle('hidden', !show);
}

/**
 * 更新UI状态
 */
function updateUIState() {
    const hasPDF = AppState.pdfDoc !== null;
    
    // 显示/隐藏工具栏和保存按钮
    document.getElementById('toolBar').classList.toggle('hidden', !hasPDF);
    document.getElementById('savePdfBtn').classList.toggle('hidden', !hasPDF);
    
    // 显示/隐藏页面预览面板
    document.getElementById('pagePreviewPanel').classList.toggle('hidden', !hasPDF);
    
    // 显示/隐藏上传提示和画布
    document.getElementById('uploadPrompt').classList.toggle('hidden', hasPDF);
    document.getElementById('canvasContainer').classList.toggle('hidden', !hasPDF);
}

/**
 * 撤销操作
 */
function undo() {
    if (AppState.historyStep > 0) {
        AppState.isUndoRedoing = true;  // 设置标志
        AppState.historyStep--;
        const state = AppState.canvasHistory[AppState.historyStep];
        if (state && AppState.fabricCanvas) {
            AppState.fabricCanvas.loadFromJSON(state, () => {
                AppState.fabricCanvas.renderAll();
                // 延迟解除标志，确保所有事件处理完成
                setTimeout(() => {
                    AppState.isUndoRedoing = false;
                }, 100);
            });
        } else {
            AppState.isUndoRedoing = false;
        }
    }
}

/**
 * 重做操作
 */
function redo() {
    if (AppState.historyStep < AppState.canvasHistory.length - 1) {
        AppState.isUndoRedoing = true;  // 设置标志
        AppState.historyStep++;
        const state = AppState.canvasHistory[AppState.historyStep];
        if (state && AppState.fabricCanvas) {
            AppState.fabricCanvas.loadFromJSON(state, () => {
                AppState.fabricCanvas.renderAll();
                // 延迟解除标志，确保所有事件处理完成
                setTimeout(() => {
                    AppState.isUndoRedoing = false;
                }, 100);
            });
        } else {
            AppState.isUndoRedoing = false;
        }
    }
}

/**
 * 删除选中对象
 */
function deleteSelected() {
    if (!AppState.fabricCanvas) return;
    
    const activeObjects = AppState.fabricCanvas.getActiveObjects();
    if (activeObjects.length > 0) {
        activeObjects.forEach(obj => {
            AppState.fabricCanvas.remove(obj);
        });
        AppState.fabricCanvas.discardActiveObject();
        AppState.fabricCanvas.renderAll();
        saveCanvasState();
    }
}

/**
 * 保存画布状态（用于撤销/重做）
 */
function saveCanvasState() {
    if (!AppState.fabricCanvas) return;
    
    // 如果正在执行撤销/重做，不保存状态
    if (AppState.isUndoRedoing) return;
    
    const json = JSON.stringify(AppState.fabricCanvas.toJSON());
    
    // 移除当前步骤之后的历史记录（这样重做功能才能正常工作）
    AppState.canvasHistory = AppState.canvasHistory.slice(0, AppState.historyStep + 1);
    
    // 添加新状态
    AppState.canvasHistory.push(json);
    AppState.historyStep++;
    
    // 限制历史记录数量
    if (AppState.canvasHistory.length > 50) {
        AppState.canvasHistory.shift();
        AppState.historyStep--;
    }
}

/**
 * 更新文本属性
 */
function updateTextProperties() {
    if (!AppState.fabricCanvas) return;
    
    const activeObject = AppState.fabricCanvas.getActiveObject();
    if (activeObject && activeObject.type === 'i-text') {
        activeObject.set({
            fontFamily: document.getElementById('fontFamily').value,
            fontSize: parseInt(document.getElementById('fontSize').value),
            fill: document.getElementById('fontColor').value
        });
        AppState.fabricCanvas.renderAll();
        saveCanvasState();
    }
}

/**
 * 切换加粗
 */
function toggleBold() {
    if (!AppState.fabricCanvas) return;
    
    const activeObject = AppState.fabricCanvas.getActiveObject();
    if (activeObject && activeObject.type === 'i-text') {
        const isBold = activeObject.fontWeight === 'bold';
        activeObject.set('fontWeight', isBold ? 'normal' : 'bold');
        AppState.fabricCanvas.renderAll();
        saveCanvasState();
    }
}

/**
 * 切换斜体
 */
function toggleItalic() {
    if (!AppState.fabricCanvas) return;
    
    const activeObject = AppState.fabricCanvas.getActiveObject();
    if (activeObject && activeObject.type === 'i-text') {
        const isItalic = activeObject.fontStyle === 'italic';
        activeObject.set('fontStyle', isItalic ? 'normal' : 'italic');
        AppState.fabricCanvas.renderAll();
        saveCanvasState();
    }
}

/**
 * 更新形状属性
 */
function updateShapeProperties() {
    // 这个函数在绘制新形状时会被调用
    console.log('形状属性已更新');
}

/**
 * 缩放功能
 */
// 缩放级别数组
const zoomLevels = [0.25, 0.5, 0.75, 1, 1.25, 1.5, 2, 3, 4];
let currentZoomIndex = 3; // 默认100% (索引3)

/**
 * 应用缩放
 */
function applyZoom(zoom = null) {
    // 如果没有传入zoom值，使用当前索引的值
    if (zoom === null) {
        zoom = zoomLevels[currentZoomIndex];
    }
    
    AppState.zoom = zoom;
    
    const editorWrapper = document.getElementById('editorWrapper');
    if (editorWrapper) {
        editorWrapper.style.transform = `scale(${zoom})`;
        editorWrapper.style.transformOrigin = 'top center';
    }
    
    // 更新输入框显示
    const zoomInput = document.getElementById('zoomInput');
    if (zoomInput) {
        zoomInput.value = `${Math.round(zoom * 100)}%`;
    }
}

/**
 * 放大
 */
function zoomIn() {
    if (currentZoomIndex < zoomLevels.length - 1) {
        currentZoomIndex++;
        applyZoom();
    }
}

/**
 * 缩小
 */
function zoomOut() {
    if (currentZoomIndex > 0) {
        currentZoomIndex--;
        applyZoom();
    }
}

/**
 * 重置缩放
 */
function zoomReset() {
    currentZoomIndex = 3; // 100%
    applyZoom();
}

/**
 * 处理缩放输入
 */
function handleZoomInput() {
    const zoomInput = document.getElementById('zoomInput');
    if (!zoomInput) return;
    
    // 获取输入值，移除%符号
    let value = zoomInput.value.replace('%', '').trim();
    let percentage = parseInt(value);
    
    // 验证输入
    if (isNaN(percentage)) {
        // 无效输入，恢复当前值
        applyZoom();
        return;
    }
    
    // 限制范围 25-400
    percentage = Math.max(25, Math.min(400, percentage));
    
    // 转换为缩放比例
    const zoom = percentage / 100;
    
    // 找到最接近的预设级别索引
    let closestIndex = 0;
    let minDiff = Math.abs(zoomLevels[0] - zoom);
    for (let i = 1; i < zoomLevels.length; i++) {
        const diff = Math.abs(zoomLevels[i] - zoom);
        if (diff < minDiff) {
            minDiff = diff;
            closestIndex = i;
        }
    }
    
    // 如果输入的值接近预设值，使用预设值
    if (minDiff < 0.01) {
        currentZoomIndex = closestIndex;
        applyZoom();
    } else {
        // 否则使用自定义缩放值
        applyZoom(zoom);
    }
}

// 导出全局对象供其他模块使用
window.AppState = AppState;
window.setTool = setTool;
window.showLoading = showLoading;
window.updateUIState = updateUIState;
window.saveCanvasState = saveCanvasState;
window.zoomIn = zoomIn;
window.zoomOut = zoomOut;
window.zoomReset = zoomReset;
