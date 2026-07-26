/**
 * PDF生成和下载模块
 */

/**
 * 保存并下载PDF
 */
async function savePDF() {
    if (!AppState.pdfDoc || AppState.pages.length === 0) {
        alert('没有可保存的PDF！');
        return;
    }
    
    console.log('开始生成PDF...');
    showLoading(true);
    
    try {
        // 保存当前页面的编辑数据
        if (AppState.fabricCanvas && AppState.currentPageIndex >= 0) {
            AppState.pages[AppState.currentPageIndex].fabricData = 
                JSON.stringify(AppState.fabricCanvas.toJSON(['selectable', 'evented']));
        }
        
        // 使用jsPDF创建新PDF
        const { jsPDF } = window.jspdf;
        
        // 获取第一页尺寸来初始化PDF
        const firstPage = await AppState.pdfDoc.getPage(AppState.pages[0].pageNumber);
        const firstViewport = firstPage.getViewport({ scale: 1.5 });
        
        // 计算第一页PDF页面尺寸（转换为mm）
        const firstPageWidth = firstViewport.width * 0.264583; // px to mm
        const firstPageHeight = firstViewport.height * 0.264583;
        
        const pdf = new jsPDF({
            orientation: firstPageWidth > firstPageHeight ? 'landscape' : 'portrait',
            unit: 'mm',
            format: [firstPageWidth, firstPageHeight]
        });
        
        // 处理每一页
        for (let i = 0; i < AppState.pages.length; i++) {
            console.log(`处理第 ${i + 1}/${AppState.pages.length} 页...`);
            
            // 获取当前页面的原始尺寸
            const page = await AppState.pdfDoc.getPage(AppState.pages[i].pageNumber);
            const viewport = page.getViewport({ scale: 1.5 });
            
            // 计算当前页面的尺寸（转换为mm）
            const pageWidth = viewport.width * 0.264583;
            const pageHeight = viewport.height * 0.264583;
            
            // 确定页面方向
            const orientation = pageWidth > pageHeight ? 'landscape' : 'portrait';
            
            // 渲染页面到临时canvas
            const pageImage = await renderPageToImage(i);
            
            // 添加页面（使用当前页面的实际尺寸和方向）
            if (i > 0) {
                pdf.addPage([pageWidth, pageHeight], orientation);
            } else {
                // 第一页：如果方向不匹配，需要调整
                if (orientation !== (firstPageWidth > firstPageHeight ? 'landscape' : 'portrait')) {
                    pdf.deletePage(1);
                    pdf.addPage([pageWidth, pageHeight], orientation);
                }
            }
            
            // 添加图片（使用当前页面的实际尺寸）
            pdf.addImage(pageImage, 'PNG', 0, 0, pageWidth, pageHeight, '', 'FAST');
        }
        
        // 生成文件名
        const fileName = generateFileName();
        
        // 保存PDF
        pdf.save(fileName);
        
        console.log('PDF保存成功！');
        // 移除提示框，保存操作更流畅
        
    } catch (error) {
        console.error('生成PDF失败:', error);
        alert('生成PDF失败，请重试！');
    }
    
    showLoading(false);
}

/**
 * 将页面渲染为图片
 */
async function renderPageToImage(pageIndex) {
    return new Promise(async (resolve, reject) => {
        try {
            // 创建临时canvas
            const tempCanvas = document.createElement('canvas');
            const page = await AppState.pdfDoc.getPage(AppState.pages[pageIndex].pageNumber);
            const scale = 1.5;
            const viewport = page.getViewport({ scale: scale });
            
            tempCanvas.width = viewport.width;
            tempCanvas.height = viewport.height;
            const context = tempCanvas.getContext('2d');
            
            // 渲染PDF页面
            await page.render({
                canvasContext: context,
                viewport: viewport
            }).promise;
            
            // 如果该页面有编辑内容，叠加编辑层
            if (AppState.pages[pageIndex].fabricData) {
                // 创建临时Fabric画布
                const tempFabricCanvas = new fabric.Canvas(document.createElement('canvas'), {
                    width: viewport.width,
                    height: viewport.height
                });
                
                // 加载编辑数据
                await new Promise((resolve) => {
                    tempFabricCanvas.loadFromJSON(AppState.pages[pageIndex].fabricData, () => {
                        resolve();
                    });
                });
                
                // 渲染Fabric画布
                tempFabricCanvas.renderAll();
                
                // 将Fabric画布内容叠加到临时canvas
                context.drawImage(tempFabricCanvas.getElement(), 0, 0);
                
                // 清理临时Fabric画布
                tempFabricCanvas.dispose();
            }
            
            // 转换为Data URL
            const imageData = tempCanvas.toDataURL('image/png', 1.0);
            resolve(imageData);
            
        } catch (error) {
            reject(error);
        }
    });
}

/**
 * 生成文件名
 */
function generateFileName() {
    // 获取原始文件名
    let originalName = 'document.pdf';
    if (AppState.pdfFile && AppState.pdfFile.name) {
        originalName = AppState.pdfFile.name;
    }
    
    // 在原文件名前添加"去红头-"前缀
    const newFileName = '去红头-' + originalName;
    
    return newFileName;
}

/**
 * 导出单页为图片（额外功能）
 */
async function exportPageAsImage(pageIndex) {
    try {
        showLoading(true);
        
        const imageData = await renderPageToImage(pageIndex);
        
        // 创建下载链接
        const link = document.createElement('a');
        link.download = `page_${pageIndex + 1}.png`;
        link.href = imageData;
        link.click();
        
        console.log(`第 ${pageIndex + 1} 页已导出为图片`);
        
    } catch (error) {
        console.error('导出图片失败:', error);
        alert('导出图片失败！');
    }
    
    showLoading(false);
}

/**
 * 批量导出所有页面为图片（额外功能）
 */
async function exportAllPagesAsImages() {
    if (!confirm('确定要将所有页面导出为图片吗？')) {
        return;
    }
    
    try {
        showLoading(true);
        
        for (let i = 0; i < AppState.pages.length; i++) {
            const imageData = await renderPageToImage(i);
            
            const link = document.createElement('a');
            link.download = `page_${i + 1}.png`;
            link.href = imageData;
            link.click();
            
            // 延迟以避免浏览器阻止多个下载
            await new Promise(resolve => setTimeout(resolve, 500));
        }
        
        alert('所有页面已导出为图片！');
        
    } catch (error) {
        console.error('批量导出失败:', error);
        alert('批量导出失败！');
    }
    
    showLoading(false);
}

// 导出函数
window.savePDF = savePDF;
window.exportPageAsImage = exportPageAsImage;
window.exportAllPagesAsImages = exportAllPagesAsImages;
