
## 徒步旅行网站项目代码规范和约束
## 项目要求
### 技术栈
1. 后端：FastAPI + uvicorn
2. 前端：HTML5 + CSS3 + JavaScript (纯原生，不使用框架)
3. 地图：Leaflet (使用OpenStreetMap，避免API密钥需求)
4. 图标：Font Awesome 6
5. 包管理：uv (Python 3.13+)

### 网站功能要求
#### 1. 整体布局

- 网站宽度为当前页面的80%，居中显示
- 响应式设计，适配各种屏幕尺寸
- 顶部有Logo和导航菜单

#### 2. 页面结构

- 首页：等宽风景大图 + 100字关于风景的文字描述
- 路线页面：展示徒步路线详细信息
- 地图页面：交互式地图功能
- 关于我们：网站介绍 + 图片

#### 3. 地图页面具体功能

- 四个功能按钮（带图标）：
  1. 获取我的位置 - 显示固定位置"东莞市-香芒东路"
  2. 显示周边路线 - 显示距离固定位置最近的3条路线
  3. 按距离排序 - 计算固定位置与所有路线距离，取top3
  4. 显示所有线路 - 在地图上显示所有路线
- 信息显示区域：
  1. 位置信息：固定显示"东莞市-香芒东路"
  2. 线路数量：统计当前地图显示的路线数量
- 地图区域：使用Leaflet，默认定位到东莞市

#### 4. 项目结构要求
hiking_trails/
├── pyproject.toml            # uv项目配置，包含[project.scripts]
├── .env                      # 环境变量配置文件
├── main.py                   # FastAPI主应用，包含main()函数 启动端口必须为3000 host必须为localhost
├── web/                      # 前端文件目录
│   ├── static/              # 静态资源目录
│   │   ├── hike.js          # JavaScript文件
│   │   └── hike.css         # CSS样式文件
│   └── main.html            # 主HTML模板文件
└── README.md                # Markdown格式的项目说明文档

#### 5. 特殊要求
位置信息固定为"东莞市-香芒东路"，不自动获取用户真实位置
地图页面加载时自动标记固定位置
所有距离计算基于固定位置(22.9907, 113.7378)
pyproject.toml必须包含[project.scripts]部分
main.py必须包含main()函数作为入口点
使用模板引擎(Jinja2)渲染HTML页面
静态文件挂载在/static路径

#### 6. 输出格式要求
请按照以下结构输出完整代码：
1) pyproject.toml
[提供完整的toml配置文件]

2) .env
[提供环境变量配置文件]

3) main.py
[提供完整的Python代码]

4) web/main.html
[提供完整的HTML代码]

5) web/static/hike.css
[提供完整的CSS代码]

6) web/static/hike.js
[提供完整的JavaScript代码]

7) README.md
[提供完整的项目说明文档]

### 网站需要的示例数据
1) 首页图片
雪山图片URL: https://cube.elemecdn.com/6/94/4d3ea53c084bad6931a56d5158a48jpeg.jpeg
关于我们图片URL: https://fuss10.elemecdn.com/a/3f/3302e58f9a181d2509f3dc0fa68b0jpeg.jpeg

2) 固定位置
名称：东莞市-香芒东路
坐标：纬度22.9907，经度113.7378
