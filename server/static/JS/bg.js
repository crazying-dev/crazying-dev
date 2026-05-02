// 双背景图 自动备用图源
const bgList = {
    pc: [
        "/bg?type=pc",                             // 来自服务器
        "https://img.hk256.top/random?t=webp&o=h",
        "https://api.rls.icu/horizontal",
        "https://random.moejue.cn/randbg?type=pc"
    ],
    mobile: [
        "/bg?type=mobile",                        // 来自服务器
        "https://img.hk256.top/random?t=webp&o=v",
        "https://api.rls.icu/vertical",
        "https://api.sretna.cn/mobile"
    ]
};

// 加载图片并失败自动重试
function loadImage(urls, element) {
    let index = 0;
    function tryLoad() {
        if (index >= urls.length) return;
        const img = new Image();
        img.src = urls[index];
        img.onload = () => {
            element.style.backgroundImage = `url(${urls[index]})`;
        };
        img.onerror = () => {
            index++;
            tryLoad();
        };
    }
    tryLoad();
}
