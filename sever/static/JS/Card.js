// 封装初始化逻辑，方便外部调用
function initCards() {
    // 1. 每次都重新获取所有 .card 元素（关键！）
    const CardList = document.querySelectorAll('.card');

    // 给所有card加过渡动画（让高度、透明度有渐变）
    CardList.forEach(el => {
        el.style.transition = "all 0.4s ease";
        // 关键：用max-height做动画，代替height:auto
        el.style.maxHeight = "0px";
        el.style.overflow = "hidden";
    });

    // 2. 绑定鼠标跟随效果（给所有卡片）
    document.addEventListener('mousemove', (e) => {
        CardList.forEach(el => {
            el.style.left = e.clientX + 'px';
            el.style.top = e.clientY + 'px';
        });
    });

    // 存放每个元素的定时器
    const hoverTimer = {};
    // 延时触发秒数 2秒
    const DELAY_TIME = 100;

    // 3. 辅助函数：根据 from 属性筛选卡片
    function GetStrFromForCard(__s){
        return Array.from(CardList).filter(card => {
            return card.getAttribute('from') === __s;
        });
    }

    // 4. 单卡片事件绑定
    function EverFatherCardTransitionSet(__s){
        let temp = document.getElementById(__s)
        if(!temp) return;

        // 鼠标进入：延迟2秒再展开
        temp.addEventListener('mouseenter', ()=>{
            // 先清除旧定时器
            if (hoverTimer[__s]) clearTimeout(hoverTimer[__s]);
            // 2秒后执行展开
            hoverTimer[__s] = setTimeout(() => {
                Goto(__s);
            }, DELAY_TIME);
        });

        // 鼠标离开：立刻清除计时 + 立刻收起
        temp.addEventListener('mouseleave', ()=>{
            if (hoverTimer[__s]) {
                clearTimeout(hoverTimer[__s]);
                delete hoverTimer[__s];
            }
            GoOut(__s);
        });

        GoOut(__s)
    }

    // 5. 获取所有唯一的 from 属性值
    const CardFromList = [...new Set(
        Array.from(CardList)
            .map(item => item.getAttribute('from'))
            .filter(from => from && from.trim() !== '')
    )];

    console.log("CardFromList：", CardFromList);

    // 6. 批量绑定事件
    function EverFatherCardTransitionSetAPI() {
        CardFromList.forEach(val => {
            EverFatherCardTransitionSet(val);
        });
    }

    // 7. 卡片事件函数
    function Goto(__s){
        console.log(`Mouse Go to ${__s}`);
        GetStrFromForCard(__s).forEach(card => {
            card.style.color = `rgba(0,0,0,1)`;
            card.style.backgroundColor = `rgba(142, 142, 142, 0.6)`;
            if (card.tagName.toLowerCase() === 'img'){
                card.style.minHeight = '120px';
            }else{
                // 关键：给一个足够大的max-height实现自适应动画
                card.style.minHeight = '20px';
            }
        });
    }

    function GoOut(__s) {
        console.log(`Mouse Go out ${__s}`);
        GetStrFromForCard(__s).forEach(card => {
            card.style.color = `rgba(0, 0, 0, 0)`;
            card.style.backgroundColor = `rgba(0, 0, 0, 0)`;
            card.style.minHeight = '0';
            // 收起 max-height 实现动画收缩
            card.style.maxHeight = '0px';
        });
    }

    // 8. 执行批量绑定
    EverFatherCardTransitionSetAPI();
}

// 页面 DOM 加载完成时，执行一次初始化
window.addEventListener('DOMContentLoaded', () => {
    initCards();
});

// 关键：把 initCards 暴露到全局，让 HTML 可以调用
window.initCards = initCards;