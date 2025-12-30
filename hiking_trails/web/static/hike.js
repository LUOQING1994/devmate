// 页面导航功能
document.addEventListener('DOMContentLoaded', function() {
    // 导航链接点击事件
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.getAttribute('data-page');
            showPage(page);
        });
    });

    // 显示首页（默认）
    showPage('home');

    // 模态框功能
    const modal = document.getElementById('trailModal');
    const span = document.getElementsByClassName('close')[0];
    
    span.onclick = function() {
        modal.style.display = 'none';
    }
    
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }
});

// 显示指定页面
function showPage(pageName) {
    // 隐藏所有页面
    const pages = document.querySelectorAll('.page-content');
    pages.forEach(page => {
        page.classList.remove('active');
    });
    
    // 显示指定页面
    const targetPage = document.getElementById(`${pageName}-page`);
    if (targetPage) {
        targetPage.classList.add('active');
        
        // 如果是地图页面，初始化地图
        if (pageName === 'map') {
            setTimeout(initMap, 100); // 延迟加载地图以确保元素已显示
        }
    }
    
    // 更新浏览器历史记录
    history.pushState({page: pageName}, '', `/${pageName}`);
}

// 显示路线详情
function showTrailDetails(trailId) {
    fetch(`/api/trails/${trailId}`)
        .then(response => response.json())
        .then(trail => {
            const modalBody = document.getElementById('modal-body');
            modalBody.innerHTML = `
                <h2>${trail.name}</h2>
                <div style="display: flex; justify-content: space-between; margin: 1rem 0;">
                    <div><strong>难度:</strong> ${trail.difficulty}</div>
                    <div><strong>距离:</strong> ${trail.distance}</div>
                    <div><strong>时长:</strong> ${trail.duration}</div>
                    <div><strong>爬升:</strong> ${trail.elevation_gain}</div>
                </div>
                <p><strong>描述:</strong> ${trail.description}</p>
                <h3>特色景点:</h3>
                <ul>
                    ${trail.features.map(feature => `<li>• ${feature}</li>`).join('')}
                </ul>
                <p><strong>最佳时间:</strong> ${trail.best_time}</p>
                <p><strong>交通指南:</strong> ${trail.transportation}</p>
            `;
            
            const modal = document.getElementById('trailModal');
            modal.style.display = 'block';
        })
        .catch(error => {
            console.error('获取路线详情失败:', error);
            alert('获取路线详情失败');
        });
}

// 地图功能
let map;
let markers = [];
let circle;

function initMap() {
    // 如果地图已经初始化，则返回
    if (window.mapInitialized) {
        return;
    }
    
    // 初始化地图，定位到东莞
    map = L.map('map').setView([23.02, 113.75], 11); // 东莞中心坐标
    
    // 添加OpenStreetMap图层
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    
    // 添加东莞所有徒步路线的标记
    fetch('/api/trails')
        .then(response => response.json())
        .then(data => {
            data.trails.forEach(trail => {
                const marker = L.marker(trail.coordinates).addTo(map)
                    .bindPopup(`<b>${trail.name}</b><br>难度: ${trail.difficulty}<br>距离: ${trail.distance}`);
                markers.push(marker);
            });
            
            // 更新路线数量显示
            document.getElementById('trailCount').textContent = `路线数量: ${markers.length}`;
        });
    
    // 设置已初始化标志
    window.mapInitialized = true;
    
    // 绑定地图页面按钮事件
    document.getElementById('getLocationBtn').addEventListener('click', showCurrentLocation);
    document.getElementById('showNearbyBtn').addEventListener('click', showNearbyTrails);
    document.getElementById('sortByDistanceBtn').addEventListener('click', sortByDistance);
    document.getElementById('showAllBtn').addEventListener('click', showAllTrails);
}

// 显示当前位置（固定显示“东莞市-香芒东路”）
function showCurrentLocation() {
    // 清除之前的圆形标记
    if (circle) {
        map.removeLayer(circle);
    }
    
    // 东莞市香芒东路坐标
    const location = [23.047508, 113.755880];
    
    // 在地图上标记位置
    circle = L.circle(location, {
        color: 'red',
        fillColor: '#f03',
        fillOpacity: 0.25,
        radius: 500
    }).addTo(map);
    
    // 更新位置信息显示
    document.getElementById('locationInfo').textContent = '位置: 东莞市-香芒东路';
    
    // 移动地图视图到该位置
    map.setView(location, 14);
    
    // 添加标记
    L.marker(location).addTo(map)
        .bindPopup('当前位置: 东莞市-香芒东路')
        .openPopup();
}

// 显示周边路线（距离固定位置最近的3条路线）
function showNearbyTrails() {
    // 清除当前所有标记
    clearAllMarkers();
    
    // 获取周边路线
    fetch('/api/nearby_trails')
        .then(response => response.json())
        .then(data => {
            // 显示最近的3条路线
            data.nearby_trails.forEach(item => {
                const trail = item.trail;
                const marker = L.marker(trail.coordinates).addTo(map)
                    .bindPopup(`<b>${trail.name}</b><br>距离: ${item.distance.toFixed(2)}km<br>难度: ${trail.difficulty}`);
                markers.push(marker);
            });
            
            // 更新路线数量显示
            document.getElementById('trailCount').textContent = `路线数量: ${data.nearby_trails.length}`;
            
            // 更新位置信息
            document.getElementById('locationInfo').textContent = `位置: ${data.reference_location}`;
        })
        .catch(error => {
            console.error('获取周边路线失败:', error);
        });
}

// 按距离排序（计算固定位置与所有路线距离，取top3）
function sortByDistance() {
    // 清除当前所有标记
    clearAllMarkers();
    
    // 获取所有路线并按距离排序
    fetch('/api/nearby_trails')
        .then(response => response.json())
        .then(data => {
            // 只显示前3条最近的路线
            const top3 = data.nearby_trails.slice(0, 3);
            
            top3.forEach(item => {
                const trail = item.trail;
                const marker = L.marker(trail.coordinates).addTo(map)
                    .bindPopup(`<b>${trail.name}</b><br>距离: ${item.distance.toFixed(2)}km<br>难度: ${trail.difficulty}`);
                markers.push(marker);
            });
            
            // 更新路线数量显示
            document.getElementById('trailCount').textContent = `路线数量: ${top3.length}`;
            
            // 更新位置信息
            document.getElementById('locationInfo').textContent = `位置: ${data.reference_location}`;
        })
        .catch(error => {
            console.error('按距离排序失败:', error);
        });
}

// 显示所有路线
function showAllTrails() {
    // 清除当前所有标记
    clearAllMarkers();
    
    // 获取所有路线
    fetch('/api/trails')
        .then(response => response.json())
        .then(data => {
            data.trails.forEach(trail => {
                const marker = L.marker(trail.coordinates).addTo(map)
                    .bindPopup(`<b>${trail.name}</b><br>难度: ${trail.difficulty}<br>距离: ${trail.distance}`);
                markers.push(marker);
            });
            
            // 更新路线数量显示
            document.getElementById('trailCount').textContent = `路线数量: ${data.trails.length}`;
            
            // 更新位置信息
            document.getElementById('locationInfo').textContent = '位置: 东莞市-香芒东路';
        })
        .catch(error => {
            console.error('获取所有路线失败:', error);
        });
}

// 清除所有标记
function clearAllMarkers() {
    if (map) {
        markers.forEach(marker => {
            map.removeLayer(marker);
        });
        markers = [];
    }
}

// 处理浏览器历史记录
window.addEventListener('popstate', function(event) {
    if (event.state && event.state.page) {
        showPage(event.state.page);
    }
});