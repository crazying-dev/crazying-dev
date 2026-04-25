/*
 *name            GitHub Static Resource Acceleration
 *version         2.3
 *description     GitHub raw static resource acceleration, automatically switch to domestic mirror when loading timeout or failure
 *author          crazying-dev, cary-ing, crazying
 *collaboratorAI
 *    豆包           日志内容
 *    deepseek      内容纠错
 *    iflow(已下架)  提供思路
 *    Qoder         逻辑测试,内容纠错
 */

const CONFIG = {
    timeout: 3000,
    originalDomain: 'raw.githubusercontent.com',
    mirrorDomain: 'raw.fgit.cf'
};

function toMirrorUrl(url) {
    return url.replace(CONFIG.originalDomain, CONFIG.mirrorDomain);
}

function loadImageWithFallback(imgEl, originalUrl) {
    console.log('[Image Acceleration] Starting to load the original address:', originalUrl);

    let isTimeout = false;
    let timer = setTimeout(() => {
        isTimeout = true;
        const mirrorUrl = toMirrorUrl(originalUrl);
        // 日志：超时切换镜像
        console.log('[Image Acceleration] Loading timeout, automatically switching to mirror address:', mirrorUrl);
        imgEl.src = mirrorUrl;
    }, CONFIG.timeout);

    const img = new Image();
    img.onload = () => {
        clearTimeout(timer);
        if (!isTimeout) {
            // 日志：加载成功
            console.log('[Image Acceleration] Original address loaded successfully:', originalUrl);
            imgEl.src = originalUrl;
        }
    };
    img.onerror = () => {
        clearTimeout(timer);
        const mirrorUrl = toMirrorUrl(originalUrl);
        // 日志：加载失败切换镜像
        console.log('[Image Acceleration] Original address loading failed, automatically switching to mirror address:', mirrorUrl);
        imgEl.src = mirrorUrl;
    };
    img.src = originalUrl;
}

document.addEventListener('DOMContentLoaded', () => {
    const img = document.getElementById('githubImg');
    const src = img.dataset.src;
    if (src) loadImageWithFallback(img, src);
});