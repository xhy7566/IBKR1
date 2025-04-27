// 前端核心逻辑：提交任务、更新任务列表
async function addTask() {
    const symbol = document.getElementById('symbol').value.trim();
    const triggerPrice = document.getElementById('triggerPrice').value;
    const action = document.getElementById('action').value;
    const startTime = document.getElementById('startTime').value;
    const endTime = document.getElementById('endTime').value;
    const quantity = document.getElementById('quantity').value;

    if (!symbol || !triggerPrice || !action || !startTime || !endTime || !quantity) {
        alert('请填写所有必填字段');
        return;
    }

    // 发送 POST 请求添加任务
    const response = await fetch('/add_task', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            symbol,
            trigger_price: triggerPrice,
            action,
            start_time: startTime + ":00",
            end_time: endTime + ":00",
            quantity,
        }),
    });

    try {
        const data = await response.json();
        if (response.ok) {
            if (data.status === 'success') {
                alert('任务添加成功');
                loadTasks();
            } else {
                alert(`添加失败：${data.message}`);
            }
        } else {
            alert(`请求失败：${data.message}`);
        }
    } catch (error) {
        console.error('解析响应数据出错:', error);
        alert('解析响应数据出错，请稍后重试');
    }
}

// 加载任务列表（含实时状态更新）
async function loadTasks() {
    const response = await fetch('/get_tasks');
    const { tasks } = await response.json();
    const taskList = document.getElementById('taskList');
    taskList.innerHTML = '';

    tasks.forEach((task, index) => {
        const item = document.createElement('div');
        item.className = 'task-item';
        // 根据状态显示不同颜色
        let statusColor = '';
        if (task.order_status === '未提交') {
            statusColor = 'color: gray;';
        } else if (task.order_status === '已提交') {
            statusColor = 'color: orange;';
        }
        item.innerHTML = `
            <div>
                <strong>${task.symbol}</strong> -
                ${task.action === 'BUY' ? '买入' : '卖出'}
                触发价：${task.trigger_price}
                数量：${task.quantity}
                状态：<span style="${statusColor}">${task.order_status}</span>
            </div>
            <div class="task-actions">
                <button onclick="pauseTask(${index})">
                    ${task.active ? '暂停' : '恢复'}
                </button>
                <button onclick="cancelTask(${index})">取消</button>
            </div>
        `;
        taskList.appendChild(item);
    });
}

// 暂停/恢复任务
async function pauseTask(index) {
    const tasks = await getTasks();
    const task = tasks[index];
    task.active = !task.active;
    const response = await fetch('/update_task', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            index,
            active: task.active
        })
    });
    const data = await response.json();
    if (data.status === 'success') {
        loadTasks();
    } else {
        alert(`操作失败：${data.message}`);
    }
}

// 取消任务
async function cancelTask(index) {
    const tasks = await getTasks();
    const task = tasks[index];
    if (task.order_id) {
        const response = await fetch('/cancel_order', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                order_id: task.order_id
            })
        });
        const data = await response.json();
        if (data.status === 'success') {
            alert('委托单取消成功');
            loadTasks();
        } else {
            alert(`委托单取消失败：${data.message}`);
        }
    } else {
        const response = await fetch('/remove_task', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                index
            })
        });
        const data = await response.json();
        if (data.status === 'success') {
            alert('任务移除成功');
            loadTasks();
        } else {
            alert(`任务移除失败：${data.message}`);
        }
    }
}

// 获取任务列表
async function getTasks() {
    const response = await fetch('/get_tasks');
    const { tasks } = await response.json();
    return tasks;
}

// 查询股票价格
async function queryPrice() {
    const symbol = document.getElementById('symbol').value.trim();
    if (!symbol) {
        return;
    }
    try {
        const response = await fetch(`/query_price?symbol=${symbol}`);
        const data = await response.json();
        if (data.status === 'success') {
            const priceDisplay = document.getElementById('price-display');
            priceDisplay.textContent = `当前价格: ${data.price.toFixed(2)}`;
        } else {
            alert(`查询失败：${data.message}`);
        }
    } catch (error) {
        alert(`查询出错：${error.message}`);
    }
}

// 更新美国东部时间
function updateUSTime() {
    const usTimeElement = document.getElementById('usTime');
    const eastern = new Intl.DateTimeFormat('en-US', {
        timeZone: 'America/New_York',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    });
    const usTime = eastern.format(new Date());
    const formattedTime = usTime.replace(/(\d+)\/(\d+)\/(\d+), (\d+):(\d+):(\d+)/, '$3-$1-$2 $4:$5:$6');
    usTimeElement.textContent = formattedTime;
}

// 页面加载时自动查询一次委托单，并启动定时查询
async function loadIBOrders() {
    try {
        const response = await fetch('/get_all_ib_orders');
        const { orders } = await response.json();
        // 这里可以根据需要对 orders 做进一步处理
        loadTasks();
    } catch (error) {
        console.error('获取IB委托单出错:', error);
    }
}

window.onload = () => {
    loadIBOrders();
    setInterval(loadIBOrders, 40000);
    setInterval(loadTasks, 30000);
    setInterval(updateUSTime, 1000);
    updateUSTime();
    const symbol = document.getElementById('symbol').value.trim();
    if (symbol) {
        queryPrice();
    }
    setInterval(() => {
        const symbol = document.getElementById('symbol').value.trim();
        if (symbol) {
            queryPrice();
        }
    }, 45000);
};