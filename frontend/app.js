const API_BASE = 'http://localhost:15001/_manage';
let currentApiKey = 'mock-server-admin';

// 保存API密钥
function saveApiKey() {
    currentApiKey = document.getElementById('apiKey').value;
    localStorage.setItem('mock_server_api_key', currentApiKey);
    showAlert('API密钥已保存', 'success');
}

// 加载保存的API密钥
function loadApiKey() {
    const savedKey = localStorage.getItem('mock_server_api_key');
    if (savedKey) {
        document.getElementById('apiKey').value = savedKey;
        currentApiKey = savedKey;
    }
}

// 显示提示信息
function showAlert(message, type = 'success') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;

    document.body.appendChild(alert);

    setTimeout(() => {
        alert.remove();
    }, 3000);
}

// API请求函数
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${url}`, {
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': currentApiKey,
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API请求失败:', error);
        showAlert(`请求失败: ${error.message}`, 'error');
        throw error;
    }
}

// 加载路由列表
async function loadRoutes() {
    const activeOnly = document.getElementById('activeOnly').checked;
    const routesList = document.getElementById('routes-list');

    routesList.innerHTML = '<div class="loading">加载中...</div>';

    try {
        const url = activeOnly ? '/routes?active_only=true' : '/routes';
        const data = await apiRequest(url);

        routesList.innerHTML = '';

        if (data.routes.length === 0) {
            routesList.innerHTML = '<div class="loading">暂无路由</div>';
            return;
        }

        data.routes.forEach(route => {
            const routeCard = createRouteCard(route);
            routesList.appendChild(routeCard);
        });
    } catch (error) {
        routesList.innerHTML = '<div class="loading">加载失败</div>';
    }
}

// 创建路由卡片
function createRouteCard(route) {
    const card = document.createElement('div');
    card.className = 'route-card';

    const methods = route.methods.map(method =>
        `<span class="method-badge method-${method.toLowerCase()}">${method}</span>`
    ).join('');

    card.innerHTML = `
        <div class="route-header">
            <div class="route-methods">${methods}</div>
            <span class="route-status">${route.is_active ? '✅ 激活' : '❌ 停用'}</span>
        </div>
        <div class="route-path">${route.path}</div>
        ${route.description ? `<div class="route-description">${route.description}</div>` : ''}
        <div class="route-actions">
            <button class="btn btn-edit" onclick="editRoute(${route.id})">编辑</button>
            <button class="btn btn-toggle ${route.is_active ? '' : 'btn-inactive'}"
                    onclick="toggleRoute(${route.id}, ${!route.is_active})">
                ${route.is_active ? '停用' : '激活'}
            </button>
            <button class="btn btn-delete" onclick="deleteRoute(${route.id})">删除</button>
        </div>
    `;

    return card;
}

// 创建路由
async function createRoute(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const data = {
        path: formData.get('path'),
        methods: Array.from(formData.getAll('methods')),
        status_code: parseInt(formData.get('status_code')),
        delay: parseFloat(formData.get('delay')) || 0,
        description: formData.get('description'),
        headers: formData.get('headers') ? JSON.parse(formData.get('headers')) : {},
        response: JSON.parse(formData.get('response')),
        is_active: true
    };

    try {
        await apiRequest('/routes', {
            method: 'POST',
            body: JSON.stringify(data)
        });

        showAlert('路由创建成功', 'success');
        event.target.reset();
        loadRoutes();
        openTab('routes-tab');
    } catch (error) {
        showAlert('创建路由失败', 'error');
    }
}

// 编辑路由
async function editRoute(routeId) {
    try {
        const route = await apiRequest(`/routes/${routeId}`);
        openEditModal(route);
    } catch (error) {
        showAlert('获取路由详情失败', 'error');
    }
}

// 打开编辑模态框
function openEditModal(route) {
    const modal = document.getElementById('edit-modal');
    const form = document.getElementById('edit-form');

    form.innerHTML = `
        <input type="hidden" name="id" value="${route.id}">
        <div class="form-group">
            <label>路径:</label>
            <input type="text" name="path" value="${route.path}" required>
        </div>
        <div class="form-group">
            <label>HTTP方法:</label>
            <select name="methods" multiple required>
                ${['GET', 'POST', 'PUT', 'DELETE', 'PATCH'].map(method =>
                    `<option value="${method}" ${route.methods.includes(method) ? 'selected' : ''}>${method}</option>`
                ).join('')}
            </select>
        </div>
        <div class="form-group">
            <label>状态码:</label>
            <input type="number" name="status_code" value="${route.status_code}" required>
        </div>
        <div class="form-group">
            <label>响应延迟(秒):</label>
            <input type="number" name="delay" value="${route.delay}" step="0.1">
        </div>
        <div class="form-group">
            <label>描述:</label>
            <input type="text" name="description" value="${route.description || ''}">
        </div>
        <div class="form-group">
            <label>响应头(JSON):</label>
            <textarea name="headers" rows="3">${JSON.stringify(route.headers, null, 2)}</textarea>
        </div>
        <div class="form-group">
            <label>响应体(JSON):</label>
            <textarea name="response" rows="6" required>${JSON.stringify(route.response, null, 2)}</textarea>
        </div>
        <div class="form-group">
            <label>激活状态:</label>
            <input type="checkbox" name="is_active" ${route.is_active ? 'checked' : ''}>
        </div>
        <button type="submit">更新路由</button>
    `;

    form.onsubmit = async (e) => {
        e.preventDefault();
        await updateRoute(e);
    };

    modal.style.display = 'block';
}

// 关闭模态框
function closeModal() {
    document.getElementById('edit-modal').style.display = 'none';
}

// 更新路由
async function updateRoute(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const routeId = formData.get('id');
    const data = {
        path: formData.get('path'),
        methods: Array.from(formData.getAll('methods')),
        status_code: parseInt(formData.get('status_code')),
        delay: parseFloat(formData.get('delay')) || 0,
        description: formData.get('description'),
        headers: formData.get('headers') ? JSON.parse(formData.get('headers')) : {},
        response: JSON.parse(formData.get('response')),
        is_active: formData.get('is_active') === 'on'
    };

    try {
        await apiRequest(`/routes/${routeId}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });

        showAlert('路由更新成功', 'success');
        closeModal();
        loadRoutes();
    } catch (error) {
        showAlert('更新路由失败', 'error');
    }
}

// 切换路由状态
async function toggleRoute(routeId, isActive) {
    try {
        await apiRequest(`/routes/${routeId}`, {
            method: 'PUT',
            body: JSON.stringify({ is_active: isActive })
        });

        showAlert(`路由已${isActive ? '激活' : '停用'}`, 'success');
        loadRoutes();
    } catch (error) {
        showAlert('操作失败', 'error');
    }
}

// 删除路由
async function deleteRoute(routeId) {
    if (!confirm('确定要删除这个路由吗？')) return;

    try {
        await apiRequest(`/routes/delete1/${routeId}`, {
            method: 'POST'
        });

        showAlert('路由删除成功', 'success');
        loadRoutes();
    } catch (error) {
        showAlert('删除路由失败', 'error');
    }
}

// 加载健康状态
async function loadHealth() {
    try {
        const health = await apiRequest('/health');
        const healthInfo = document.getElementById('health-info');

        healthInfo.innerHTML = `
            <p><strong>状态:</strong> ${health.status}</p>
            <p><strong>数据库:</strong> ${health.database}</p>
            <p><strong>总路由数:</strong> ${health.total_routes}</p>
            <p><strong>激活路由:</strong> ${health.active_routes}</p>
            <p><strong>停用路由:</strong> ${health.inactive_routes}</p>
            <p><strong>最后检查:</strong> ${new Date(health.timestamp * 1000).toLocaleString()}</p>
        `;
    } catch (error) {
        document.getElementById('health-info').innerHTML = '<p>获取健康状态失败</p>';
    }
}

// 切换标签页
function openTab(tabName) {
    // 隐藏所有标签页
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    // 移除所有按钮的激活状态
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // 显示选中的标签页
    document.getElementById(tabName).classList.add('active');

    // 激活对应的按钮
    event.currentTarget.classList.add('active');

    // 如果是健康标签页，加载健康状态
    if (tabName === 'health-tab') {
        loadHealth();
    }
}

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    loadApiKey();
    loadRoutes();

    // 绑定表单提交事件
    document.getElementById('create-form').onsubmit = createRoute;

    // 点击模态框外部关闭
    window.onclick = function(event) {
        const modal = document.getElementById('edit-modal');
        if (event.target === modal) {
            closeModal();
        }
    };
});