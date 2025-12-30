// 全局变量
let map;
let markers = [];
let currentTrails = [];
const fixedLocation = {
    name: "东莞市-香芒东路",
    lat: 22.9907,
    lng: 113.7378
};

// 初始化地图
function initMap() {
    // 创建地图实例
    map = L.map('map').setView([fixedLocation.lat, fixedLocation.lng], 12);

    // 添加OpenStreetMap图层
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // 添加固定位置标记
    addFixedLocationMarker();

    // 初始加载所有路线
    loadAllTrails();
}

// 添加固定位置标记
function addFixedLocationMarker() {
    const fixedMarker = L.marker([fixedLocation.lat, fixedLocation.lng])
        .addTo(map)
        .bindPopup(`
            <div style="text-align: center;">
                <strong><i class="fas fa-location-dot"></i> ${fixedLocation.name}</strong><br>
                <small>纬度: ${fixedLocation.lat.toFixed(4)}</small><br>
                <small>经度: ${fixedLocation.lng.toFixed(4)}</small>
            </div>
        `)
        .openPopup();

    markers.push(fixedMarker);
}

// 加载所有路线
async function loadAllTrails() {
    try {
        const response = await fetch('/api/trails');
        const data = await response.json();
        currentTrails = data.trails;
        displayTrails(currentTrails);
        updateRouteCount(currentTrails.length);
    } catch (error) {
        console.error('加载路线失败:', error);
    }
}

// 显示路线在地图上
function displayTrails(trails) {
    // 清除现有标记
    markers.forEach(marker => {
        if (marker !== markers[0]) { // 保留固定位置标记
            map.removeLayer(marker);
        }
    });
    markers = markers.slice(0, 1); // 只保留固定位置标记

    // 添加新标记
    trails.forEach(trail => {
        const marker = L.marker([trail.lat, trail.lng])
            .addTo(map)
            .bindPopup(`
                <div style="min-width: 200px;">
                    <h4 style="margin: 0 0 10px; color: #4CAF50;">
                        <i class="fas fa-route"></i> ${trail.title}
                    </h4>
                    <p style="margin: 5px 0;"><strong>难度：</strong>${trail.difficulty}</p>
                    <p style="margin: 5px 0;"><strong>特色：</strong>${trail.features}</p>
                    <p style="margin: 5px 0;"><strong>距离：</strong>${trail.distance ? trail.distance.toFixed(2) + '公里' : '计算中...'}</p>
                    <button onclick="centerOnTrail(${trail.lat}, ${trail.lng})" 
                            style="background: #4CAF50; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer; margin-top: 5px;">
                        <i class="fas fa-crosshairs"></i> 定位
                    </button>
                </div>
            `);

        markers.push(marker);
    });

    // 调整地图视图以显示所有标记
    if (trails.length > 0) {
        const bounds = L.latLngBounds(
            trails.map(trail => [trail.lat, trail.lng])
        );
        bounds.extend([fixedLocation.lat, fixedLocation.lng]); // 包含固定位置
        map.fitBounds(bounds, { padding: [50, 50] });
    }
}

// 在路线列表中显示路线
function displayTrailsInList(trails) {
    const container = document.getElementById('trailsContainer');
    container.innerHTML = '';

    if (trails.length === 0) {
        container.innerHTML = '<p class="no-trails">暂无路线数据</p>';
        return;
    }

    trails.forEach(trail => {
        const trailElement = document.createElement('div');
        trailElement.className = 'trail-item';
        trailElement.innerHTML = `
            <h4>${trail.title}</h4>
            <p><strong>难度：</strong>${trail.difficulty}</p>
            <p><strong>特色：</strong>${trail.features}</p>
            <div class="trail-info">
                <span><i class="fas fa-map-marker-alt"></i> ${trail.coordinates}</span>
                <span class="trail-distance">${trail.distance ? trail.distance.toFixed(2) + '公里' : '计算中...'}</span>
            </div>
        `;

        trailElement.addEventListener('click', () => {
            centerOnTrail(trail.lat, trail.lng);
        });

        container.appendChild(trailElement);
    });
}

// 显示所有路线
async function showAllRoutes() {
    await loadAllTrails();
}

// 显示周边路线
async function showNearbyTrails() {
    try {
        const response = await fetch('/api/nearby-trails');
        const trails = await response.json();
        currentTrails = trails;
        displayTrails(trails);
        displayTrailsInList(trails);
        updateRouteCount(trails.length);
    } catch (error) {
        console.error('加载周边路线失败:', error);
    }
}

// 按距离排序显示路线
async function showDistanceSortedTrails() {
    try {
        const response = await fetch('/api/distance-sorted-trails');
        const trails = await response.json();
        currentTrails = trails;
        displayTrails(trails);
        displayTrailsInList(trails);
        updateRouteCount(trails.length);
    } catch (error) {
        console.error('加载排序路线失败:', error);
    }
}

// 获取位置（固定位置）
function getMyLocation() {
    // 使用固定位置
    const locationInfo = document.getElementById('locationInfo');
    locationInfo.textContent = fixedLocation.name;

    // 居中显示固定位置
    map.setView([fixedLocation.lat, fixedLocation.lng], 14);

    // 显示提示
    showNotification('已定位到固定位置：' + fixedLocation.name);
}

// 居中显示特定路线
function centerOnTrail(lat, lng) {
    map.setView([lat, lng], 14);

    // 打开对应标记的弹窗
    markers.forEach(marker => {
        const markerLatLng = marker.getLatLng();
        if (markerLatLng.lat === lat && markerLatLng.lng === lng) {
            marker.openPopup();
        }
    });
}

// 更新路线数量显示
function updateRouteCount(count) {
    document.getElementById('routeCount').textContent = count;
}

// 显示通知
function showNotification(message) {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #4CAF50;
        color: white;
        padding: 15px 20px;
        border-radius: 5px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        z-index: 1000;
        animation: slideIn 0.3s ease;
        max-width: 300px;
    `;

    notification.innerHTML = `
        <i class="fas fa-info-circle"></i> ${message}
    `;

    document.body.appendChild(notification);

    // 3秒后移除通知
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// 添加CSS动画
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .no-trails {
        text-align: center;
        padding: 2rem;
        color: #666;
    }
`;
document.head.appendChild(style);

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function () {
    // 初始化移动端菜单切换
    const menuToggle = document.getElementById('menuToggle');
    const navMenu = document.querySelector('.nav-menu');

    if (menuToggle && navMenu) {
        menuToggle.addEventListener('click', function () {
            navMenu.classList.toggle('active');
        });
    }

    // 如果是地图页面，初始化地图
    if (document.getElementById('map')) {
        initMap();

        // 绑定按钮事件
        document.getElementById('getLocation').addEventListener('click', getMyLocation);
        document.getElementById('showNearby').addEventListener('click', showNearbyTrails);
        document.getElementById('sortByDistance').addEventListener('click', showDistanceSortedTrails);
        document.getElementById('showAllRoutes').addEventListener('click', showAllRoutes);

        // 初始化位置信息显示
        document.getElementById('locationInfo').textContent = fixedLocation.name;
    }
});