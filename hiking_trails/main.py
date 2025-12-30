from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import math

app = FastAPI(title="东莞徒步路线网站")

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# 设置模板目录
templates = Jinja2Templates(directory="web")

# 东莞徒步路线数据
hiking_trails = [
    {
        "id": 1,
        "name": "黄旗山城市公园",
        "difficulty": "初级",
        "distance": "8.4公里",
        "duration": "2-3小时",
        "elevation_gain": "约200米",
        "description": "黄旗山是东莞的标志性景点，有“黄旗山顶挂灯笼”的美誉。公园内有黄旗古庙、黄岭道观等古迹，还有8.4公里的环山绿道。登顶后可360°饱览东莞城市中心区全景。",
        "features": ["黄旗山顶灯笼", "黄旗古庙", "环山绿道", "城市全景"],
        "coordinates": [23.0222, 113.7574],  # 黄旗山坐标
        "best_time": "四季皆宜，清晨或傍晚最佳",
        "transportation": "位于东莞大道和东城中路交汇处，交通便利"
    },
    {
        "id": 2,
        "name": "银瓶山森林公园",
        "difficulty": "中级",
        "distance": "5公里（主峰路线）",
        "duration": "3-4小时",
        "elevation_gain": "约698米",
        "description": "银瓶山是东莞最高峰，海拔898米，远望如银瓶，山尖如嘴。公园内森林茂密，有清澈的溪流和壮观的瀑布，四季景色各异，是自然爱好者的天堂。",
        "features": ["东莞最高峰", "森林溪流", "瀑布景观", "生物多样性"],
        "coordinates": [22.9333, 114.1333],  # 银瓶山坐标
        "best_time": "春秋季节最佳，春季可赏野花，秋季观红叶",
        "transportation": "导航至东莞市银瓶山自然保护区界碑，有停车场"
    },
    {
        "id": 3,
        "name": "水濂山森林公园",
        "difficulty": "初级",
        "distance": "约6公里",
        "duration": "2-3小时",
        "elevation_gain": "约150米",
        "description": "以水濂阁为标志，位于水濂山顶，有五层高。登上水濂阁视野开阔，有“一览众山小”的感觉，可远眺市中心区以及虎门、厚街、大岭山等镇。",
        "features": ["水濂阁", "五层观景", "远眺美景", "森林氧吧"],
        "coordinates": [23.0000, 113.7833],  # 水濂山坐标
        "best_time": "全年适宜，清晨或傍晚光线最佳",
        "transportation": "位于南城，交通便利"
    },
    {
        "id": 4,
        "name": "同沙生态公园",
        "difficulty": "初级",
        "distance": "环湖路线约8公里",
        "duration": "3-4小时",
        "elevation_gain": "约50米",
        "description": "以映翠湖景区为核心，有滟潋亭、入翠亭、览翠亭、洛书亭等景点。体现了小巧玲珑、秀丽典雅的岭南园林建筑风格。",
        "features": ["映翠湖景区", "岭南园林", "桥梁水榭", "亭台楼阁"],
        "coordinates": [23.0500, 113.8500],  # 同沙生态公园坐标
        "best_time": "全年适宜，春秋季节景色更佳",
        "transportation": "设有正门和北门，可骑自行车游览"
    },
    {
        "id": 5,
        "name": "大岭山森林公园",
        "difficulty": "中级",
        "distance": "约10公里",
        "duration": "4-5小时",
        "elevation_gain": "约300米",
        "description": "位于东莞南部，跨大岭山、厚街、虎门、长安四镇，占地74平方公里。主要景点有茶趣轩，登顶可览虎门、长安、大岭山、厚街等镇美景。",
        "features": ["跨四镇公园", "茶趣轩观景", "广域景观", "森林覆盖"],
        "coordinates": [22.9833, 113.7833],  # 大岭山森林公园坐标
        "best_time": "春秋季节，天气晴朗时视野最佳",
        "transportation": "位于大岭山镇，多条公交线路可达"
    },
    {
        "id": 6,
        "name": "松山湖风景区",
        "difficulty": "初级",
        "distance": "绿道总长122公里",
        "duration": "1-5小时（可选段）",
        "elevation_gain": "约30米",
        "description": "以湖泊湿地风光、植物季相和色花系列观赏为特色，是东莞最为成熟和经典的游览线路。松山湖绿道总长达122公里，是东莞里程最长的绿道。",
        "features": ["湖泊湿地", "绿道系统", "四季花卉", "休闲骑行"],
        "coordinates": [23.0167, 113.8833],  # 松山湖坐标
        "best_time": "全年适宜，春秋季节花卉盛开",
        "transportation": "位于东莞松山湖高新区，交通便利"
    },
    {
        "id": 7,
        "name": "榴花公园",
        "difficulty": "初级",
        "distance": "约3公里",
        "duration": "1-2小时",
        "elevation_gain": "约80米",
        "description": "位于东莞市东城街道，以榴花塔为标志性建筑，是东莞著名的历史文化景点。公园环境清幽，适合休闲徒步。",
        "features": ["榴花塔", "历史文化", "休闲徒步", "古塔景观"],
        "coordinates": [23.0667, 113.8000],  # 榴花公园坐标
        "best_time": "春秋季节，气候宜人",
        "transportation": "位于东城街道，多条公交线路可达"
    },
    {
        "id": 8,
        "name": "观音山森林公园",
        "difficulty": "中级",
        "distance": "约7公里",
        "duration": "3-4小时",
        "elevation_gain": "约250米",
        "description": "国家4A级景区，以观音圣像和古建筑群为特色。山中林木葱茏，空气清新，是著名的佛教文化旅游胜地和自然生态保护区。",
        "features": ["观音圣像", "古建筑群", "佛教文化", "生态保护区"],
        "coordinates": [23.0333, 114.0500],  # 观音山坐标
        "best_time": "全年适宜，避开雨季",
        "transportation": "位于樟木头镇，有专车直达"
    },
    {
        "id": 9,
        "name": "大屏嶂森林公园",
        "difficulty": "中级",
        "distance": "约8公里",
        "duration": "4-5小时",
        "elevation_gain": "约350米",
        "description": "位于东莞市东南部，拥有丰富的森林资源和独特的自然景观。公园内有多个登山步道，适合有一定经验的徒步爱好者。",
        "features": ["森林资源", "多条步道", "自然景观", "生态教育"],
        "coordinates": [22.9500, 114.0333],  # 大屏嶂坐标
        "best_time": "春秋季节，气候凉爽",
        "transportation": "位于塘厦镇，可自驾或乘公交到达"
    },
    {
        "id": 10,
        "name": "凤山公园",
        "difficulty": "初级",
        "distance": "约2公里",
        "duration": "1小时",
        "elevation_gain": "约60米",
        "description": "位于东莞市中心区域，是市民休闲健身的好去处。公园内绿树成荫，环境优美，适合家庭休闲徒步。",
        "features": ["市中心公园", "休闲健身", "家庭友好", "绿树成荫"],
        "coordinates": [23.0333, 113.7667],  # 凤山公园坐标
        "best_time": "全年适宜，清晨或傍晚最佳",
        "transportation": "位于市中心，交通便利"
    }
]

# 计算两点间距离（使用Haversine公式）
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # 地球半径（公里）
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2)**2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dlon/2)**2)
    c = 2 * math.asin(math.sqrt(a))
    return R * c

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("main.html", {"request": request, "page": "home", "trails": hiking_trails})

@app.get("/trails", response_class=HTMLResponse)
async def read_trails(request: Request):
    return templates.TemplateResponse("main.html", {"request": request, "page": "trails", "trails": hiking_trails})

@app.get("/map", response_class=HTMLResponse)
async def read_map(request: Request):
    return templates.TemplateResponse("main.html", {"request": request, "page": "map", "trails": hiking_trails})

@app.get("/about", response_class=HTMLResponse)
async def read_about(request: Request):
    return templates.TemplateResponse("main.html", {"request": request, "page": "about", "trails": hiking_trails})

@app.get("/api/trails")
async def get_trails():
    return {"trails": hiking_trails}

@app.get("/api/trails/{trail_id}")
async def get_trail(trail_id: int):
    for trail in hiking_trails:
        if trail["id"] == trail_id:
            return trail
    return {"error": "Trail not found"}

@app.get("/api/nearby_trails")
async def get_nearby_trails():
    # 固定位置：东莞市-香芒东路
    reference_lat, reference_lon = 23.047508, 113.755880  # 东莞市香芒东路坐标
    
    # 计算每条路线与参考位置的距离
    trails_with_distance = []
    for trail in hiking_trails:
        distance = calculate_distance(
            reference_lat, reference_lon,
            trail["coordinates"][0], trail["coordinates"][1]
        )
        trails_with_distance.append({
            "trail": trail,
            "distance": distance
        })
    
    # 按距离排序并取前3条
    trails_with_distance.sort(key=lambda x: x["distance"])
    nearby_trails = trails_with_distance[:3]
    
    return {
        "reference_location": "东莞市-香芒东路",
        "nearby_trails": nearby_trails
    }

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)

if __name__ == "__main__":
    main()