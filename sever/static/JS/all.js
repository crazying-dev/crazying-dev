function log(...msg) {
    console.log(...msg);
    fetch("/log",{
        method:"POST",
        headers:{
            "Content-Type":"application/json",
            "from": "Website"
        },
        body:JSON.stringify(msg)
    }).catch(null)
}
    // 忽略回复

/**
 * Load HTML fragment into specified container
 * @param {string} url - HTML file path
 * @param {string} targetId - Container ID
 */
async function loadHTML(url, targetId) {
    try {
        const res = await fetch(url);
        if (!res.ok) throw new Error(`Failed to load: ${res.status}`);
        const html = await res.text();

        const container = document.getElementById(targetId);
        if (!container) throw new Error(`Container not found: #${targetId}`);

        // 创建临时容器解析HTML
        const temp = document.createElement('div');
        temp.innerHTML = html;

        // 分离外部脚本和内联脚本
        const externalScripts = [];
        const inlineScripts = [];
        
        temp.querySelectorAll('script').forEach(script => {
            if (script.src) {
                externalScripts.push(script);
            } else if (script.textContent.trim()) {
                inlineScripts.push(script);
            }
        });

        // 1. 先加载所有外部脚本
        for (const script of externalScripts) {
            await new Promise((resolve) => {
                const newScript = document.createElement('script');
                Array.from(script.attributes).forEach(attr => {
                    newScript.setAttribute(attr.name, attr.value);
                });
                newScript.onload = resolve;
                newScript.onerror = () => {
                    console.warn(`Script load failed: ${script.src}`);
                    resolve();
                };
                document.body.appendChild(newScript);
            });
        }

        // 2. 设置HTML内容（不含script标签）
        temp.querySelectorAll('script').forEach(s => s.remove());
        container.innerHTML = temp.innerHTML;

        // 3. 最后执行内联脚本
        for (const script of inlineScripts) {
            try {
                eval(script.textContent);
            } catch (err) {
                console.error('Inline script error:', err);
            }
        }

        console.log(`Successfully loaded: ${url} → #${targetId}`);
    } catch (err) {
        console.error('loadHTML error:', err);
    }
}

function load(__r, ...arge) {
    __r(...arge);
}

async function loadPage(url, targetId, __r=()=>{}, ...args) {
    await loadHTML(url, targetId);
    load(__r, ...args);
}