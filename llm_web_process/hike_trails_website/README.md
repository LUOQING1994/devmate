
# 徒步旅行网站

一个基于FastAPI和Leaflet的徒步旅行网站，展示东莞地区的徒步路线和交互式地图。

## 功能特点

- 🏔️ 展示东莞地区徒步路线详细信息
- 🗺️ 交互式地图功能（使用Leaflet + OpenStreetMap）
- 📍 固定位置标记（东莞市-香芒东路）
- 🔍 路线搜索和筛选功能
- 📱 响应式设计，适配各种设备
- 🎨 现代化UI设计，使用Font Awesome图标

## 技术栈

### 后端

- FastAPI (Python Web框架)
- Uvicorn (ASGI服务器)
- Jinja2 (模板引擎)

### 前端

- HTML5 + CSS3 + JavaScript (原生)
- Leaflet.js (交互式地图)
- Font Awesome 6 (图标库)

### 开发工具

- uv (Python包管理器)
- Python 3.13+

## 项目结构

hiking-website/
├── pyproject.toml # 项目配置和依赖
├── .env # 环境变量配置
├── main.py # FastAPI主应用
├── web/ # 前端文件目录
│ ├── static/ # 静态资源
│ │ ├── hike.js # JavaScript功能
│ │ └── hike.css # 样式文件
│ └── main.html # 主HTML模板
└── README.md # 项目文档
