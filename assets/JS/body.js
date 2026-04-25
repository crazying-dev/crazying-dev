// 获取所有 .follow 类
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