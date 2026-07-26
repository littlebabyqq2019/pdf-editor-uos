/**
 * 编辑器模块 - 各种编辑工具的实现
 */

let isDrawing = false;
let drawingObject = null;
let startX, startY;

/**
 * 更新编辑器模式
 */
function updateEditorMode(tool) {
    if (!AppState.fabricCanvas) return;
    
    console.log('更新编辑器模式:', tool);
    
    // 重置所有对象的可选择性
    AppState.fabricCanvas.forEachObject(obj => {
        obj.selectable = (tool === 'select');
        obj.evented = (tool === 'select');
    });
    
    // 移除所有鼠标事件监听
    AppState.fabricCanvas.off('mouse:down');
    AppState.fabricCanvas.off('mouse:move');
    AppState.fabricCanvas.off('mouse:up');
    
    // 取消选择
    AppState.fabricCanvas.discardActiveObject();
    AppState.fabricCanvas.selection = (tool === 'select');
    
    // 根据工具类型设置事件
    switch (tool) {
        case 'select':
            setupSelectMode();
            break;
        case 'text':
            setupTextMode();
            break;
        case 'erase':
            setupEraseMode();
            break;
        case 'highlight':
            setupHighlightMode();
            break;
        case 'underline':
            setupUnderlineMode();
            break;
        case 'shape':
            setupShapeMode();
            break;
    }
    
    AppState.fabricCanvas.renderAll();
}

/**
 * 选择模式
 */
function setupSelectMode() {
    AppState.fabricCanvas.defaultCursor = 'default';
    AppState.fabricCanvas.hoverCursor = 'move';
}

// 文字工具状态：标记是否已插入文本框
let textInserted = false;

/**
 * 文字模式
 */
function setupTextMode() {
    AppState.fabricCanvas.defaultCursor = 'text';
    textInserted = false; // 重置标记
    
    AppState.fabricCanvas.on('mouse:down', function(options) {
        // 如果已经插入过文本框，不再插入新的
        if (textInserted) return;
        // 如果点击在已有对象上，不创建新文本
        if (options.target) return;
        
        const pointer = AppState.fabricCanvas.getPointer(options.e);
        
        // 创建空白文本框
        const text = new fabric.IText('', {
            left: pointer.x,
            top: pointer.y,
            fontFamily: document.getElementById('fontFamily').value,
            fontSize: parseInt(document.getElementById('fontSize').value),
            fill: document.getElementById('fontColor').value,
            fontWeight: 'normal',
            fontStyle: 'normal'
        });
        
        AppState.fabricCanvas.add(text);
        AppState.fabricCanvas.setActiveObject(text);
        text.enterEditing();
        
        // 标记已插入
        textInserted = true;
        
        saveCanvasState();
    });
}

/**
 * 擦除模式
 */
function setupEraseMode() {
    AppState.fabricCanvas.defaultCursor = 'crosshair';
    
    AppState.fabricCanvas.on('mouse:down', function(options) {
        isDrawing = true;
        const pointer = AppState.fabricCanvas.getPointer(options.e);
        startX = pointer.x;
        startY = pointer.y;
        
        // 创建白色矩形覆盖（绘制时显示边框）
        drawingObject = new fabric.Rect({
            left: startX,
            top: startY,
            width: 0,
            height: 0,
            fill: '#ffffff',
            stroke: '#3b82f6',  // 蓝色边框，绘制时可见
            strokeWidth: 2,
            strokeDashArray: [5, 5],  // 虚线边框，更明显
            selectable: false,
            evented: false
        });
        
        AppState.fabricCanvas.add(drawingObject);
    });
    
    AppState.fabricCanvas.on('mouse:move', function(options) {
        if (!isDrawing) return;
        
        const pointer = AppState.fabricCanvas.getPointer(options.e);
        const width = pointer.x - startX;
        const height = pointer.y - startY;
        
        drawingObject.set({
            width: Math.abs(width),
            height: Math.abs(height),
            left: width > 0 ? startX : pointer.x,
            top: height > 0 ? startY : pointer.y
        });
        
        AppState.fabricCanvas.renderAll();
    });
    
    AppState.fabricCanvas.on('mouse:up', function() {
        if (isDrawing && drawingObject) {
            isDrawing = false;
            // 松开鼠标后移除边框，保留纯白色填充
            drawingObject.set({
                stroke: null,  // 移除边框
                strokeWidth: 0,
                strokeDashArray: null,
                selectable: true,
                evented: true
            });
            AppState.fabricCanvas.renderAll();
            saveCanvasState();
            drawingObject = null;
        }
    });
}

/**
 * 高亮模式
 */
function setupHighlightMode() {
    AppState.fabricCanvas.defaultCursor = 'crosshair';
    
    AppState.fabricCanvas.on('mouse:down', function(options) {
        isDrawing = true;
        const pointer = AppState.fabricCanvas.getPointer(options.e);
        startX = pointer.x;
        startY = pointer.y;
        
        // 创建半透明黄色矩形
        drawingObject = new fabric.Rect({
            left: startX,
            top: startY,
            width: 0,
            height: 0,
            fill: 'rgba(255, 255, 0, 0.3)',
            stroke: 'rgba(255, 200, 0, 0.5)',
            strokeWidth: 1,
            selectable: false,
            evented: false
        });
        
        AppState.fabricCanvas.add(drawingObject);
    });
    
    AppState.fabricCanvas.on('mouse:move', function(options) {
        if (!isDrawing) return;
        
        const pointer = AppState.fabricCanvas.getPointer(options.e);
        const width = pointer.x - startX;
        const height = pointer.y - startY;
        
        drawingObject.set({
            width: Math.abs(width),
            height: Math.abs(height),
            left: width > 0 ? startX : pointer.x,
            top: height > 0 ? startY : pointer.y
        });
        
        AppState.fabricCanvas.renderAll();
    });
    
    AppState.fabricCanvas.on('mouse:up', function() {
        if (isDrawing && drawingObject) {
            isDrawing = false;
            drawingObject.set({
                selectable: true,
                evented: true
            });
            saveCanvasState();
            drawingObject = null;
        }
    });
}

/**
 * 下划线模式
 */
function setupUnderlineMode() {
    AppState.fabricCanvas.defaultCursor = 'crosshair';
    
    AppState.fabricCanvas.on('mouse:down', function(options) {
        isDrawing = true;
        const pointer = AppState.fabricCanvas.getPointer(options.e);
        startX = pointer.x;
        startY = pointer.y;
        
        // 创建线条
        drawingObject = new fabric.Line([startX, startY, startX, startY], {
            stroke: document.getElementById('underlineColor').value,
            strokeWidth: parseInt(document.getElementById('underlineWidth').value),
            selectable: false,
            evented: false
        });
        
        AppState.fabricCanvas.add(drawingObject);
    });
    
    AppState.fabricCanvas.on('mouse:move', function(options) {
        if (!isDrawing) return;
        
        const pointer = AppState.fabricCanvas.getPointer(options.e);
        
        // 限制下划线只能水平，y2固定为startY
        drawingObject.set({
            x2: pointer.x,
            y2: startY  // 保持y坐标不变
        });
        
        AppState.fabricCanvas.renderAll();
    });
    
    AppState.fabricCanvas.on('mouse:up', function() {
        if (isDrawing && drawingObject) {
            isDrawing = false;
            drawingObject.set({
                selectable: true,
                evented: true
            });
            saveCanvasState();
            drawingObject = null;
        }
    });
}

/**
 * 形状模式
 */
function setupShapeMode() {
    AppState.fabricCanvas.defaultCursor = 'crosshair';
    
    AppState.fabricCanvas.on('mouse:down', function(options) {
        isDrawing = true;
        const pointer = AppState.fabricCanvas.getPointer(options.e);
        startX = pointer.x;
        startY = pointer.y;
        
        const shapeType = document.getElementById('shapeType').value;
        const fill = document.getElementById('shapeFilled').checked ? 
                     document.getElementById('shapeFill').value : 'transparent';
        const stroke = document.getElementById('shapeStroke').value;
        
        if (shapeType === 'rect') {
            drawingObject = new fabric.Rect({
                left: startX,
                top: startY,
                width: 0,
                height: 0,
                fill: fill,
                stroke: stroke,
                strokeWidth: 2,
                selectable: false,
                evented: false
            });
        } else if (shapeType === 'circle') {
            drawingObject = new fabric.Circle({
                left: startX,
                top: startY,
                radius: 0,
                fill: fill,
                stroke: stroke,
                strokeWidth: 2,
                selectable: false,
                evented: false
            });
        } else if (shapeType === 'line') {
            drawingObject = new fabric.Line([startX, startY, startX, startY], {
                stroke: stroke,
                strokeWidth: 3,
                selectable: false,
                evented: false
            });
        }
        
        AppState.fabricCanvas.add(drawingObject);
    });
    
    AppState.fabricCanvas.on('mouse:move', function(options) {
        if (!isDrawing) return;
        
        const pointer = AppState.fabricCanvas.getPointer(options.e);
        const shapeType = document.getElementById('shapeType').value;
        
        if (shapeType === 'rect') {
            const width = pointer.x - startX;
            const height = pointer.y - startY;
            
            drawingObject.set({
                width: Math.abs(width),
                height: Math.abs(height),
                left: width > 0 ? startX : pointer.x,
                top: height > 0 ? startY : pointer.y
            });
        } else if (shapeType === 'circle') {
            const radius = Math.sqrt(
                Math.pow(pointer.x - startX, 2) + 
                Math.pow(pointer.y - startY, 2)
            ) / 2;
            
            drawingObject.set({
                radius: radius,
                left: startX,
                top: startY
            });
        } else if (shapeType === 'line') {
            drawingObject.set({
                x2: pointer.x,
                y2: pointer.y
            });
        }
        
        AppState.fabricCanvas.renderAll();
    });
    
    AppState.fabricCanvas.on('mouse:up', function() {
        if (isDrawing && drawingObject) {
            isDrawing = false;
            drawingObject.set({
                selectable: true,
                evented: true
            });
            saveCanvasState();
            drawingObject = null;
        }
    });
}

// 导出函数
window.updateEditorMode = updateEditorMode;
