/**
 * PDF处理模块 - 加载和渲染PDF
 */

// 配置PDF.js worker
pdfjsLib.GlobalWorkerOptions.workerSrc = '/editor/static/js/pdf.worker.min.js';

// 滚动切换页面的防抖变量
let scrollTimeout = null;
let isScrollSwitching = false;

/**
 * 加载PDF文档
 */
async function loadPDF(data) {
    try {
        console.log('开始加载PDF...');
        
        // 使用PDF.js加载PDF
        const loadingTask = pdfjsLib.getDocument({ data: data });
        AppState.pdfDoc = await loadingTask.promise;
        
        console.log('PDF加载成功，共', AppState.pdfDoc.numPages, '页');
        
        // 初始化页面数组
        AppState.pages = [];
        for (let i = 1; i <= AppState.pdfDoc.numPages; i++) {
            AppState.pages.push({
                pageNumber: i,
                canvas: null,
                thumbnail: null,
                fabricData: null
            });
        }
        
        // 渲染所有页面缩略图
        await renderAllThumbnails();
        
        // 渲染第一页到编辑区
        await renderPageToEditor(0);
        
        // 更新UI
        updateUIState();
        
        // 隐藏加载提示
        showLoading(false);
        
    } catch (error) {
        console.error('加载PDF失败:', error);
        alert('加载PDF失败，请确保文件格式正确！');
        showLoading(false);
    }
}

/**
 * 渲染所有页面的缩略图
 */
async function renderAllThumbnails() {
    const pagesList = document.getElementById('pagesList');
    pagesList.innerHTML = '';
    
    for (let i = 0; i < AppState.pages.length; i++) {
        const page = await AppState.pdfDoc.getPage(i + 1);
        const viewport = page.getViewport({ scale: 0.3 });
        
        // 创建canvas
        const canvas = document.createElement('canvas');
        canvas.width = viewport.width;
        canvas.height = viewport.height;
        const context = canvas.getContext('2d');
        
        // 渲染页面
        await page.render({
            canvasContext: context,
            viewport: viewport
        }).promise;
        
        // 保存缩略图
        AppState.pages[i].thumbnail = canvas.toDataURL();
        
        // 创建页面项元素
        const pageItem = createPageItem(i, canvas.toDataURL());
        pagesList.appendChild(pageItem);
    }
    
    // 初始化拖拽排序
    initSortable();
}

/**
 * 创建页面项元素
 */
function createPageItem(index, thumbnailUrl) {
    const div = document.createElement('div');
    div.className = 'page-item relative';
    div.dataset.pageIndex = index;
    if (index === 0) div.classList.add('active');
    
    // 缩略图
    const img = document.createElement('img');
    img.src = thumbnailUrl;
    img.alt = `第 ${index + 1} 页`;
    
    // 页码标签
    const pageNumber = document.createElement('div');
    pageNumber.className = 'page-number';
    pageNumber.textContent = index + 1;
    
    // 删除按钮
    const deleteBtn = document.createElement('div');
    deleteBtn.className = 'page-delete';
    deleteBtn.innerHTML = '×';
    deleteBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        deletePage(index);
    });
    
    // 点击切换页面
    div.addEventListener('click', () => {
        switchToPage(index);
    });
    
    div.appendChild(img);
    div.appendChild(pageNumber);
    div.appendChild(deleteBtn);
    
    return div;
}

/**
 * 初始化拖拽排序
 */
function initSortable() {
    const pagesList = document.getElementById('pagesList');
    
    new Sortable(pagesList, {
        animation: 150,
        ghostClass: 'sortable-ghost',
        dragClass: 'sortable-drag',
        onEnd: function(evt) {
            // 更新页面顺序
            const oldIndex = evt.oldIndex;
            const newIndex = evt.newIndex;
            
            if (oldIndex !== newIndex) {
                // 移动页面数据
                const movedPage = AppState.pages.splice(oldIndex, 1)[0];
                AppState.pages.splice(newIndex, 0, movedPage);
                
                // 更新当前页面索引
                if (AppState.currentPageIndex === oldIndex) {
                    AppState.currentPageIndex = newIndex;
                } else if (oldIndex < AppState.currentPageIndex && newIndex >= AppState.currentPageIndex) {
                    AppState.currentPageIndex--;
                } else if (oldIndex > AppState.currentPageIndex && newIndex <= AppState.currentPageIndex) {
                    AppState.currentPageIndex++;
                }
                
                // 更新页码显示
                updatePageNumbers();
            }
        }
    });
}

/**
 * 更新页码显示
 */
function updatePageNumbers() {
    const pageItems = document.querySelectorAll('.page-item');
    pageItems.forEach((item, index) => {
        const pageNumber = item.querySelector('.page-number');
        pageNumber.textContent = index + 1;
        item.dataset.pageIndex = index;
    });
}

/**
 * 切换到指定页面
 */
async function switchToPage(index) {
    if (index < 0 || index >= AppState.pages.length) return;
    
    // 保存当前页面的编辑数据
    if (AppState.fabricCanvas && AppState.currentPageIndex >= 0) {
        AppState.pages[AppState.currentPageIndex].fabricData = 
            JSON.stringify(AppState.fabricCanvas.toJSON(['selectable', 'evented']));
    }
    
    // 更新当前页面索引
    AppState.currentPageIndex = index;
    
    // 更新页面项激活状态
    document.querySelectorAll('.page-item').forEach((item, i) => {
        item.classList.toggle('active', i === index);
    });
    
    // 渲染新页面
    await renderPageToEditor(index);
}

/**
 * 渲染页面到编辑区
 */
async function renderPageToEditor(index) {
    if (index < 0 || index >= AppState.pages.length) return;
    
    showLoading(true);
    
    try {
        const page = await AppState.pdfDoc.getPage(AppState.pages[index].pageNumber);
        const scale = 1.5;
        const viewport = page.getViewport({ scale: scale });
        
        // 获取画布元素
        const pdfCanvas = document.getElementById('pdfCanvas');
        const editCanvas = document.getElementById('editCanvas');
        
        // 设置画布尺寸
        pdfCanvas.width = viewport.width;
        pdfCanvas.height = viewport.height;
        editCanvas.width = viewport.width;
        editCanvas.height = viewport.height;
        
        // 渲染PDF页面到底层画布
        const context = pdfCanvas.getContext('2d');
        await page.render({
            canvasContext: context,
            viewport: viewport
        }).promise;
        
        // 初始化或重置Fabric.js画布
        if (AppState.fabricCanvas) {
            AppState.fabricCanvas.clear();
            AppState.fabricCanvas.setDimensions({
                width: viewport.width,
                height: viewport.height
            });
        } else {
            AppState.fabricCanvas = new fabric.Canvas('editCanvas', {
                width: viewport.width,
                height: viewport.height,
                backgroundColor: 'transparent'
            });
            
            // 添加画布事件监听
            initCanvasEvents();
        }
        
        // 恢复该页面的编辑数据
        if (AppState.pages[index].fabricData) {
            AppState.isUndoRedoing = true;  // 设置标志，防止触发保存
            AppState.fabricCanvas.loadFromJSON(AppState.pages[index].fabricData, () => {
                AppState.fabricCanvas.renderAll();
                setTimeout(() => {
                    AppState.isUndoRedoing = false;
                }, 100);
            });
        }
        
        // 初始化标尺
        if (window.initRulers) {
            initRulers(viewport.width, viewport.height);
        }
        
        // 重置历史记录
        AppState.canvasHistory = [JSON.stringify(AppState.fabricCanvas.toJSON())];
        AppState.historyStep = 0;
        
        // 初始化滚动切换页面功能
        initScrollPageSwitch();
        
        console.log('页面渲染完成:', index + 1);
        
    } catch (error) {
        console.error('渲染页面失败:', error);
        alert('渲染页面失败！');
    }
    
    showLoading(false);
}

/**
 * 初始化画布事件
 */
function initCanvasEvents() {
    // 对象修改时保存状态（移动、缩放、旋转等）
    AppState.fabricCanvas.on('object:modified', () => {
        saveCanvasState();
    });
    
    // 注意：不监听object:added事件，因为：
    // 1. 手动添加对象时editor.js已调用saveCanvasState()
    // 2. 撤销/重做时会触发此事件导致历史记录混乱
    // 3. 初始化加载时也会触发，导致重复保存
    
    // 对象移动时显示辅助线
    AppState.fabricCanvas.on('object:moving', (e) => {
        if (window.showGuidelines) {
            showGuidelines(e.target);
        }
    });
    
    // 对象停止移动时隐藏辅助线
    AppState.fabricCanvas.on('mouse:up', () => {
        if (window.hideGuidelines) {
            hideGuidelines();
        }
    });
}

/**
 * 删除页面
 */
function deletePage(index) {
    if (AppState.pages.length <= 1) {
        alert('至少需要保留一页！');
        return;
    }
    
    if (!confirm(`确定要删除第 ${index + 1} 页吗？`)) {
        return;
    }
    
    // 删除页面数据
    AppState.pages.splice(index, 1);
    
    // 更新当前页面索引
    if (AppState.currentPageIndex >= AppState.pages.length) {
        AppState.currentPageIndex = AppState.pages.length - 1;
    } else if (AppState.currentPageIndex > index) {
        AppState.currentPageIndex--;
    }
    
    // 重新渲染页面列表
    renderPagesList();
    
    // 渲染当前页面
    renderPageToEditor(AppState.currentPageIndex);
}

/**
 * 重新渲染页面列表
 */
function renderPagesList() {
    const pagesList = document.getElementById('pagesList');
    pagesList.innerHTML = '';
    
    AppState.pages.forEach((page, index) => {
        const pageItem = createPageItem(index, page.thumbnail);
        pagesList.appendChild(pageItem);
    });
    
    // 重新初始化拖拽
    initSortable();
    
    // 更新激活状态
    document.querySelectorAll('.page-item').forEach((item, i) => {
        item.classList.toggle('active', i === AppState.currentPageIndex);
    });
}

/**
 * 初始化滚动切换页面功能
 */
function initScrollPageSwitch() {
    const canvasContainer = document.getElementById('canvasContainer');
    
    // 移除旧的监听器（如果存在）
    if (canvasContainer._scrollHandler) {
        canvasContainer.removeEventListener('scroll', canvasContainer._scrollHandler);
    }
    
    // 创建新的滚动处理函数
    const scrollHandler = function(e) {
        // 如果正在切换页面，忽略滚动事件
        if (isScrollSwitching) return;
        
        clearTimeout(scrollTimeout);
        
        scrollTimeout = setTimeout(() => {
            // 再次检查标志位，避免延迟期间状态变化
            if (isScrollSwitching) return;
            
            const container = e.target;
            const scrollTop = container.scrollTop;
            const scrollHeight = container.scrollHeight;
            const clientHeight = container.clientHeight;
            
            // 滚动到底部，切换到下一页
            if (scrollTop + clientHeight >= scrollHeight - 5) {
                if (AppState.currentPageIndex < AppState.pages.length - 1) {
                    isScrollSwitching = true;
                    switchToPage(AppState.currentPageIndex + 1).then(() => {
                        // 延迟重置滚动位置和标志位，确保页面渲染完成
                        setTimeout(() => {
                            container.scrollTop = 0;
                            // 再延迟解锁，避免重置滚动触发新事件
                            setTimeout(() => {
                                isScrollSwitching = false;
                            }, 200);
                        }, 150);
                    });
                }
            }
            // 滚动到顶部，切换到上一页
            else if (scrollTop <= 5 && AppState.currentPageIndex > 0) {
                isScrollSwitching = true;
                switchToPage(AppState.currentPageIndex - 1).then(() => {
                    // 延迟重置滚动位置和标志位
                    setTimeout(() => {
                        container.scrollTop = container.scrollHeight - container.clientHeight;
                        // 再延迟解锁
                        setTimeout(() => {
                            isScrollSwitching = false;
                        }, 200);
                    }, 150);
                });
            }
        }, 200); // 增加防抖时间到200ms
    };
    
    // 保存处理函数引用并添加监听器
    canvasContainer._scrollHandler = scrollHandler;
    canvasContainer.addEventListener('scroll', scrollHandler);
}

// 导出函数供其他模块使用
window.loadPDF = loadPDF;
window.switchToPage = switchToPage;
