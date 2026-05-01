const title = document.getElementById('title');
// 记录上一次状态
let isScreenSmall = null;
// 阈值
const WIDTH_LIMIT = 630;
// 执行判断逻辑
function checkScreenWidth() {
    console.log('winW Updata')
    const winW = window.innerWidth;
    // 本次状态
    const nowSmall = winW < WIDTH_LIMIT;
    // 状态没变 → 直接返回，不执行
    if (nowSmall === isScreenSmall) return;
    // 状态变更，更新记录 + 执行对应函数
    isScreenSmall = nowSmall;
    if (nowSmall) {
        winWSoSmall();
    } else {
        winWSoLange();
    }
}
// 页面初始化执行一次
checkScreenWidth();

// 窗口缩放监听
window.addEventListener('resize', checkScreenWidth);

// 你自己的两个方法
// 小屏：向下移动 + 淡出
function winWSoSmall() {
    title.style.top = `50px`;     /* 向下偏移 */
    title.style.opacity = `0`;    /* 淡出 */
    title.style.visibility = `hidden`;
}

// 大屏：回到原位置 + 显示
function winWSoLange() {
    title.style.top = `10px`;     /* 复位顶部 */
    title.style.opacity = `1`;    /* 淡入 */
    title.style.visibility = `visible`;
}
