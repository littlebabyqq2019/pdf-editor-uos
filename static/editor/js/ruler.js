/**
 * 标尺和辅助线模块
 */

/**
 * 初始化标尺
 */
function initRulers(width, height) {
    console.log('初始化标尺:', width, 'x', height);
    
    // 设置标尺容器尺寸
    const hRuler = document.getElementById('horizontalRuler');
    const vRuler = document.getElementById('verticalRuler');
    
    hRuler.style.width = width + 'px';
    vRuler.style.height = height + 'px';
    
    // 绘制标尺
    drawHorizontalRuler(width);
    drawVerticalRuler(height);
}

/**
 * 绘制水平标尺
 */
function drawHorizontalRuler(width) {
    const canvas = document.getElementById('hRulerCanvas');
    const ctx = canvas.getContext('2d');
    
    // 设置canvas尺寸
    canvas.width = width;
    canvas.height = 32;
    
    // 背景
    ctx.fillStyle = '#d1d5db';
    ctx.fillRect(0, 0, width, 32);
    
    // 绘制刻度
    ctx.strokeStyle = '#6b7280';
    ctx.fillStyle = '#374151';
    ctx.font = '10px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    
    for (let i = 0; i <= width; i += 10) {
        if (i % 50 === 0) {
            // 主刻度（每50px）
            ctx.beginPath();
            ctx.moveTo(i, 16);
            ctx.lineTo(i, 32);
            ctx.stroke();
            
            // 标注数字
            if (i > 0) {
                ctx.fillText(i.toString(), i, 2);
            }
        } else {
            // 次刻度（每10px）
            ctx.beginPath();
            ctx.moveTo(i, 24);
            ctx.lineTo(i, 32);
            ctx.stroke();
        }
    }
}

/**
 * 绘制垂直标尺
 */
function drawVerticalRuler(height) {
    const canvas = document.getElementById('vRulerCanvas');
    const ctx = canvas.getContext('2d');
    
    // 设置canvas尺寸
    canvas.width = 32;
    canvas.height = height;
    
    // 背景
    ctx.fillStyle = '#d1d5db';
    ctx.fillRect(0, 0, 32, height);
    
    // 绘制刻度
    ctx.strokeStyle = '#6b7280';
    ctx.fillStyle = '#374151';
    ctx.font = '10px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    
    for (let i = 0; i <= height; i += 10) {
        if (i % 50 === 0) {
            // 主刻度（每50px）
            ctx.beginPath();
            ctx.moveTo(16, i);
            ctx.lineTo(32, i);
            ctx.stroke();
            
            // 标注数字（旋转）
            if (i > 0) {
                ctx.save();
                ctx.translate(8, i);
                ctx.rotate(-Math.PI / 2);
                ctx.fillText(i.toString(), 0, 0);
                ctx.restore();
            }
        } else {
            // 次刻度（每10px）
            ctx.beginPath();
            ctx.moveTo(24, i);
            ctx.lineTo(32, i);
            ctx.stroke();
        }
    }
}

/**
 * 显示辅助线（拖动对象时）
 */
function showGuidelines(target) {
    if (!target) return;
    
    const guideLine = document.getElementById('guideLine');
    const guideLineH = document.getElementById('guideLineH');
    const guideLineV = document.getElementById('guideLineV');
    
    guideLine.classList.remove('hidden');
    
    // 计算对象中心点
    const centerX = target.left + (target.width * target.scaleX) / 2;
    const centerY = target.top + (target.height * target.scaleY) / 2;
    
    // 设置辅助线位置（相对于canvasArea）
    const canvasArea = document.getElementById('canvasArea');
    const canvasRect = canvasArea.getBoundingClientRect();
    
    // 水平辅助线
    guideLineH.style.top = (centerY + 32) + 'px'; // 32是标尺高度
    guideLineH.style.left = '32px'; // 从标尺右边开始
    guideLineH.style.width = AppState.fabricCanvas.width + 'px';
    
    // 垂直辅助线
    guideLineV.style.left = (centerX + 32) + 'px'; // 32是标尺宽度
    guideLineV.style.top = '32px'; // 从标尺下方开始
    guideLineV.style.height = AppState.fabricCanvas.height + 'px';
}

/**
 * 隐藏辅助线
 */
function hideGuidelines() {
    const guideLine = document.getElementById('guideLine');
    guideLine.classList.add('hidden');
}

/**
 * 更新标尺刻度（当缩放时）
 */
function updateRulerScale(zoom) {
    // 预留功能：支持缩放时更新标尺刻度
    console.log('标尺缩放:', zoom);
}

// 导出函数
window.initRulers = initRulers;
window.showGuidelines = showGuidelines;
window.hideGuidelines = hideGuidelines;
window.updateRulerScale = updateRulerScale;
