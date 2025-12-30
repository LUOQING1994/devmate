# 东莞徒步路线网站

一个展示东莞十大经典徒步路线的网站项目，使用FastAPI作为后端，HTML/CSS/JavaScript作为前端，Leaflet作为地图组件。

## 项目特性

- 展示东莞十大经典徒步路线的详细信息
- 交互式地图功能，显示各路线位置
- 响应式设计，支持移动设备访问
- 路线搜索和筛选功能
- 实时位置和周边路线显示

## 技术栈

- **后端**: FastAPI + uvicorn
- **前端**: HTML5 + CSS3 + JavaScript (纯原生，不使用框架)
- **地图**: Leaflet (使用OpenStreetMap)
- **图标**: Font Awesome 6
- **包管理**: uv (Python 3.13+)

## 功能模块

1. **首页**: 展示风景大图和简介
2. **路线页面**: 详细展示各徒步路线信息
3. **地图页面**: 交互式地图功能
   - 获取我的位置（固定显示“东莞市-香芒东路”）
   - 显示周边路线（距离固定位置最近的3条路线）
   - 按距离排序（计算固定位置与所有路线距离，取top3）
   - 显示所有线路
4. **关于我们**: 网站介绍

## 项目结构

```
hiking_trails/
├── pyproject.toml            # uv项目配置，包含[project.scripts]
├── main.py                   # FastAPI主应用，包含main()函数
├── web/                      # 前端文件目录
│   ├── static/              # 静态资源目录
│   │   ├── hike.js          # JavaScript文件
│   │   └── hike.css         # CSS样式文件
│   └── main.html            # 主HTML模板文件
└── README.md                # 项目说明文档
```

## 东莞十大徒步路线

1. 黄旗山城市公园
2. 银瓶山森林公园
3. 水濂山森林公园
4. 同沙生态公园
5. 大岭山森林公园
6. 松山湖风景区
7. 榴花公园
8. 观音山森林公园
9. 大屏嶂森林公园
10. 凤山公园

## 安装和运行

1. 确保已安装 Python 3.13+ 和 uv

2. 克隆项目并进入目录:
   ```bash
   git clone <repository-url>
   cd hiking_trails
   ```

3. 创建虚拟环境并安装依赖:
   ```bash
   uv venv
   source .venv/bin/activate  # Linux/Mac
   # 或
   .venv\Scripts\activate     # Windows
   uv pip install -e .
   ```

4. 启动服务器:
   ```bash
   uv run start
   # 或
   python main.py
   ```

5. 访问网站:
   打开浏览器访问 `http://localhost:8000`

## API 接口

- `GET /` - 首页
- `GET /trails` - 路线页面
- `GET /map` - 地图页面
- `GET /about` - 关于我们页面
- `GET /api/trails` - 获取所有路线数据
- `GET /api/trails/{id}` - 获取特定路线数据
- `GET /api/nearby_trails` - 获取周边路线数据

## 数据来源

- 路线信息来源于东莞主要公园和自然景区的公开信息
- 地图使用 OpenStreetMap 数据
- 图片素材来源于 Unsplash

## 许可证

本项目仅供学习和参考使用。