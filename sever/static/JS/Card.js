// 获取所有 .card 类
const CardList = document.querySelectorAll('.card');

document.addEventListener('mousemove', (e) => {
    // 遍历每一个元素，全部同步鼠标位置
    CardList.forEach(el => {
        el.style.left = e.clientX + 'px';
        el.style.top = e.clientY + 'px';
    })
})

function GetStrFromForCard(__s){
    /* 获取from是__s的card类的容器列表
    *
    * 用法：
    * GetStrFromForCard('Go-to-Github').forEach(card => {
    *     // 比如：改变样式
    *     card.style.color = `rgba(0,0,0,1)`;
    *     card.style.backgroundColor = `rgba(142, 142, 142, 0.6)`
    *     card.style.height = '20px'
    * });
    * */
    return Array.from(CardList).filter(card => {
        return card.getAttribute('from') === __s;
    });
}





// 实验JS 结果：成功 替换函数：事件布置,提示栏初始化,事件函数
function EverFatherCardTransitionSet(__s){
    let temp = document.getElementById(__s)
    if(!temp) return;

    temp.addEventListener('mouseenter', ()=>Goto(__s))
    temp.addEventListener('mouseleave', ()=>GoOut(__s))

    GoOut(__s)
}

// 正确获取 DOM 元素的 from 属性
const CardFromList = [...new Set(
    Array.from(CardList)
        .map(item => item.getAttribute('from'))
        .filter(from => from && from.trim() !== '')
)];

console.log("CardFromList：", CardFromList);

// 批量绑定事件
function EverFatherCardTransitionSetAPI() {
    CardFromList.forEach(val => {
        EverFatherCardTransitionSet(val);
    });
}

// 页面加载完执行
window.addEventListener('DOMContentLoaded', () => {
    EverFatherCardTransitionSetAPI();
});





// Card事件函数
function Goto(__s){
    console.log(`Mouse Go to ${__s}`);
    GetStrFromForCard(__s).forEach(card => {
        // 比如：改变样式
        card.style.color = `rgba(0,0,0,1)`;
        card.style.backgroundColor = `rgba(142, 142, 142, 0.6)`
        card.style.minHeight = '20px'
    });
}

function GoOut(__s) {
    console.log(`Mouse Go out ${__s}`);
    GetStrFromForCard(__s).forEach(card => {
        // 比如：改变样式
        card.style.color = `rgba(0, 0, 0, 0)`;
        card.style.backgroundColor = `rgba(0, 0, 0, 0)`
        card.style.minHeight = '0'
        card.style.height = '0'
    });
}