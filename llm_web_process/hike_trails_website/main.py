import os
from typing import List, Dict
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
from dotenv import load_dotenv
import math

# 加载环境变量
load_dotenv()

app = FastAPI(title="Hike Trails Website")

# 挂载静态文件
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# 设置模板
templates = Jinja2Templates(directory="web")

# 固定位置坐标
FIXED_LOCATION = {
    "name": "东莞市-香芒东路",
    "lat": 22.9907,
    "lng": 113.7378
}

# 路线数据
HIKING_TRAILS = [
    {
        "id": 1,
        "title": "路线一：银瓶山森林公园线",
        "difficulty": "★★★☆☆ 中级",
        "features": "东莞第一高峰，瀑布群壮观",
        "data": {
            "主峰海拔": "898米",
            "公园面积": "123.5平方公里",
            "门票": "免费"
        },
        "route": "公园入口 → 碧水叠潭 → 飞瀑流泉 → 银瓶嘴 → 返回",
        "choices": [
            "东线步道：原始山路，3小时登顶",
            "西线步道：石阶平缓，4小时登顶"
        ],
        "highlights": "东莞第一峰、瀑布群、原始森林",
        "coordinates": "(113.82, 22.95)",
        "lat": 22.95,
        "lng": 113.82,
        "distance": 0  # 将在运行时计算
    },
    {
        "id": 2,
        "title": "路线二：大岭山森林公园线",
        "difficulty": "★★☆☆☆ 初级",
        "features": "城市绿肺，湖光山色优美",
        "data": {
            "主峰海拔": "530米",
            "公园面积": "74平方公里",
            "门票": "免费"
        },
        "route": "入口广场 → 茶山顶 → 碧幽谷 → 观音寺 → 返回",
        "choices": [
            "环湖路线：轻松平缓，2小时",
            "登山路线：陡峭挑战，1.5小时登顶"
        ],
        "highlights": "茶山云雾、湖景、古寺",
        "coordinates": "(113.78, 22.93)",
        "lat": 22.93,
        "lng": 113.78,
        "distance": 0
    },
    {
        "id": 3,
        "title": "路线三：同沙生态公园线",
        "difficulty": "★☆☆☆☆ 入门",
        "features": "湿地生态，骑行徒步俱佳",
        "data": {
            "环湖周长": "15公里",
            "公园面积": "40.2平方公里",
            "门票": "免费"
        },
        "route": "北门入口 → 映翠湖 → 荷花塘 → 湿地观鸟区 → 返回",
        "choices": [
            "步行路线：全程5公里，1.5小时",
            "骑行路线：环湖15公里，1小时"
        ],
        "highlights": "湿地生态、骑行道、观鸟",
        "coordinates": "(113.75, 22.96)",
        "lat": 22.96,
        "lng": 113.75,
        "distance": 0
    },
    {
        "id": 4,
        "title": "路线四：水濂山森林公园线",
        "difficulty": "★★☆☆☆ 初级",
        "features": "城市森林公园，文化古迹丰富",
        "data": {
            "主峰海拔": "378米",
            "公园面积": "6000亩",
            "门票": "免费"
        },
        "route": "公园入口 → 西山古寺 → 水濂洞天 → 天池 → 金峰顶 → 返回",
        "choices": [
            "左路大路：上坡较累，1小时登顶",
            "寺庙路线：缓坡轻松，2小时登顶"
        ],
        "highlights": "免费开放、文化古迹、交通便利",
        "coordinates": "(113.70, 22.98)",
        "lat": 22.98,
        "lng": 113.70,
        "distance": 0
    },
    {
        "id": 5,
        "title": "路线五：大屏障森林公园线",
        "difficulty": "★★★☆☆ 中级",
        "features": "天然氧吧，竹林茂密",
        "data": {
            "主峰海拔": "348米",
            "公园面积": "26.7平方公里",
            "门票": "免费"
        },
        "route": "入口 → 竹径探幽 → 清风台 → 揽胜台 → 返回",
        "choices": [
            "登山步道：台阶较多，2小时",
            "环山公路：平缓舒适，3小时"
        ],
        "highlights": "竹海景观、观景平台、空气清新",
        "coordinates": "(114.15, 22.73)",
        "lat": 22.73,
        "lng": 114.15,
        "distance": 0
    },
    {
        "id": 6,
        "title": "路线六：黄旗山城市公园线",
        "difficulty": "★☆☆☆☆ 入门",
        "features": "城市中心，夜景迷人",
        "data": {
            "主峰海拔": "185米",
            "公园面积": "5.2平方公里",
            "门票": "免费"
        },
        "route": "正门 → 古庙 → 山顶灯笼 → 观景台 → 返回",
        "choices": [
            "台阶路线：直接登顶，30分钟",
            "盘山公路：缓慢上行，45分钟"
        ],
        "highlights": "城市地标、夜景、交通便利",
        "coordinates": "(113.76, 23.02)",
        "lat": 23.02,
        "lng": 113.76,
        "distance": 0
    }
]

def calculate_distance(lat1, lon1, lat2, lon2):
    """计算两个坐标点之间的距离（公里）"""
    # 将角度转换为弧度
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # 使用Haversine公式计算距离
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # 地球半径（公里）
    
    return c * r

def calculate_all_distances():
    """计算所有路线到固定位置的距离"""
    for trail in HIKING_TRAILS:
        trail['distance'] = calculate_distance(
            FIXED_LOCATION['lat'], FIXED_LOCATION['lng'],
            trail['lat'], trail['lng']
        )

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """首页"""
    return templates.TemplateResponse("main.html", {
        "request": request,
        "page": "home",
        "title": "首页 - 徒步旅行网站"
    })

@app.get("/routes", response_class=HTMLResponse)
async def routes(request: Request):
    """路线页面"""
    return templates.TemplateResponse("main.html", {
        "request": request,
        "page": "routes",
        "title": "徒步路线 - 徒步旅行网站",
        "trails": HIKING_TRAILS
    })

@app.get("/map", response_class=HTMLResponse)
async def map_page(request: Request):
    """地图页面"""
    calculate_all_distances()
    return templates.TemplateResponse("main.html", {
        "request": request,
        "page": "map",
        "title": "互动地图 - 徒步旅行网站",
        "trails": HIKING_TRAILS,
        "fixed_location": FIXED_LOCATION
    })

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    """关于我们页面"""
    return templates.TemplateResponse("main.html", {
        "request": request,
        "page": "about",
        "title": "关于我们 - 徒步旅行网站"
    })

@app.get("/api/trails")
async def get_trails():
    """获取所有路线数据API"""
    calculate_all_distances()
    return {
        "fixed_location": FIXED_LOCATION,
        "trails": HIKING_TRAILS
    }

@app.get("/api/nearby-trails")
async def get_nearby_trails():
    """获取附近路线API（距离最近的3条）"""
    calculate_all_distances()
    sorted_trails = sorted(HIKING_TRAILS, key=lambda x: x['distance'])
    return sorted_trails[:3]

@app.get("/api/distance-sorted-trails")
async def get_distance_sorted_trails():
    """按距离排序的路线API"""
    calculate_all_distances()
    return sorted(HIKING_TRAILS, key=lambda x: x['distance'])

def main():
    """应用入口点"""
    port = int(os.getenv("APP_PORT", 3000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

if __name__ == "__main__":
    main()