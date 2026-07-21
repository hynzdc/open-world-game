#!/usr/bin/env python3
import json
import os
import random
import time
import uuid
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
WORLD_W = 2600
WORLD_H = 1700

players = {}
monsters = {}
tribes = {}
chat = []
stalls = {}
event = {}
_last_monster_tick = 0.0

SPAWNS = [
    (1160, 760), (1210, 820), (1080, 830), (1260, 720), (980, 760),
    (1340, 840), (1120, 690), (1310, 660), (930, 850), (1420, 780)
]

COLORS = {"red", "blue", "green", "yellow", "purple", "pink", "orange", "white", "black", "cyan"}
STYLES = {"warrior", "chef", "mason", "cleaner", "coder", "wanderer", "merchant", "knight"}
REALMS = [(0, "炼气"), (120, "筑基"), (360, "金丹"), (820, "元婴"), (1500, "化神"), (2600, "渡劫")]

ZONES = [
    {"id": "square", "name": "新手广场", "x": 900, "y": 560, "w": 620, "h": 420, "safe": True, "kind": "social"},
    {"id": "work", "name": "打工街", "x": 270, "y": 520, "w": 520, "h": 390, "safe": True, "kind": "work"},
    {"id": "river", "name": "河边", "x": 80, "y": 930, "w": 970, "h": 420, "safe": True, "kind": "fish"},
    {"id": "junk", "name": "垃圾场", "x": 120, "y": 90, "w": 560, "h": 360, "safe": False, "kind": "trash"},
    {"id": "site", "name": "工地", "x": 1540, "y": 940, "w": 480, "h": 430, "safe": False, "kind": "work"},
    {"id": "market", "name": "黑市", "x": 1740, "y": 140, "w": 520, "h": 340, "safe": False, "kind": "shop"},
    {"id": "wild", "name": "野外荒地", "x": 1520, "y": 540, "w": 790, "h": 350, "safe": False, "kind": "pvp"},
    {"id": "cave", "name": "修炼洞府", "x": 2040, "y": 1010, "w": 430, "h": 430, "safe": True, "kind": "train"},
    {"id": "villa", "name": "富婆别墅区", "x": 720, "y": 110, "w": 640, "h": 340, "safe": False, "kind": "villa"},
]

ITEMS = {
    "wood_stick": {"name": "木棍", "type": "weapon", "quality": "普通", "price": 35, "attack": 3},
    "cleaver": {"name": "菜刀", "type": "weapon", "quality": "优秀", "price": 120, "attack": 8, "crit": 2},
    "brick": {"name": "搬砖", "type": "weapon", "quality": "破烂但有故事", "price": 70, "attack": 6, "defense": 1},
    "shovel": {"name": "铁锹", "type": "weapon", "quality": "稀有", "price": 210, "attack": 12},
    "fishing_staff": {"name": "鱼竿", "type": "weapon", "quality": "普通", "price": 80, "attack": 4, "luck": 3},
    "sword": {"name": "长剑", "type": "weapon", "quality": "史诗", "price": 620, "attack": 26, "crit": 7},
    "staff": {"name": "法杖", "type": "weapon", "quality": "传说", "price": 980, "attack": 19, "luck": 10, "speed": 3},
    "vest": {"name": "破背心", "type": "armor", "quality": "普通", "price": 45, "defense": 3, "hp": 10},
    "helmet": {"name": "工地安全帽", "type": "armor", "quality": "优秀", "price": 140, "defense": 8, "hp": 20},
    "cleaner_vest": {"name": "环卫马甲", "type": "armor", "quality": "稀有", "price": 260, "defense": 11, "speed": 3},
    "black_armor": {"name": "黑铁甲", "type": "armor", "quality": "史诗", "price": 700, "defense": 26, "hp": 65, "speed": -2},
    "lucky_ring": {"name": "幸运戒指", "type": "accessory", "quality": "稀有", "price": 420, "luck": 15, "crit": 3},
    "work_necklace": {"name": "打工魂项链", "type": "accessory", "quality": "优秀", "price": 260, "defense": 2, "luck": 4},
    "rich_wallet": {"name": "富婆遗失的钱包", "type": "accessory", "quality": "传说", "price": 900, "luck": 22, "hp": 40},
    "bamboo_rod": {"name": "竹制鱼竿", "type": "tool", "quality": "普通", "price": 90, "luck": 4},
    "alloy_rod": {"name": "合金鱼竿", "type": "tool", "quality": "史诗", "price": 680, "luck": 13},
    "potion": {"name": "药水", "type": "consumable", "quality": "普通", "price": 45},
    "mount": {"name": "共享坐骑月卡", "type": "mount", "quality": "稀有", "price": 520, "speed": 6},
    "small_fish": {"name": "小鱼", "type": "fish", "quality": "普通", "price": 9},
    "big_fish": {"name": "大鱼", "type": "fish", "quality": "优秀", "price": 28},
    "old_shoe": {"name": "破鞋", "type": "trash", "quality": "破烂但有故事", "price": 2},
    "treasure_box": {"name": "宝箱", "type": "box", "quality": "稀有", "price": 120},
    "scroll": {"name": "神秘卷轴", "type": "material", "quality": "史诗", "price": 180},
    "trash_bag": {"name": "垃圾袋", "type": "trash", "quality": "普通", "price": 6},
    "golden_fish": {"name": "黄金鱼", "type": "fish", "quality": "传说", "price": 260},
    "pet_egg": {"name": "宠物蛋", "type": "pet", "quality": "史诗", "price": 320},
    "life_shard": {"name": "人生碎片", "type": "material", "quality": "破烂但有故事", "price": 12},
    "flower": {"name": "鲜花", "type": "quest", "quality": "优秀", "price": 30},
    "coffee": {"name": "冰美式", "type": "quest", "quality": "普通", "price": 22},
    "lipstick": {"name": "廉价口红", "type": "gift", "quality": "优秀", "price": 88},
    "perfume": {"name": "过期香水", "type": "gift", "quality": "稀有", "price": 160},
    "ring_box": {"name": "塑料钻戒", "type": "gift", "quality": "史诗", "price": 520},
    "baby_milk": {"name": "修仙奶粉", "type": "consumable", "quality": "优秀", "price": 66},
    "goblin_ear": {"name": "哥布林耳朵", "type": "material", "quality": "普通", "price": 18},
    "slime_gel": {"name": "史莱姆凝胶", "type": "material", "quality": "优秀", "price": 32},
    "bone_shard": {"name": "骸骨碎片", "type": "material", "quality": "普通", "price": 16},
    "dark_ore": {"name": "暗铁矿", "type": "material", "quality": "稀有", "price": 78},
    "wolf_fang": {"name": "冰霜狼牙", "type": "material", "quality": "稀有", "price": 88},
    "mech_core": {"name": "机械核心", "type": "material", "quality": "史诗", "price": 160},
    "dragon_scale": {"name": "龙鳞碎片", "type": "material", "quality": "传说", "price": 420},
    "demon_blade": {"name": "魔枪残刃", "type": "weapon", "quality": "史诗", "price": 760, "attack": 30, "crit": 8},
    "guardian_plate": {"name": "地下城护甲", "type": "armor", "quality": "史诗", "price": 720, "defense": 28, "hp": 70},
}

SHOP = ["wood_stick", "cleaver", "brick", "shovel", "fishing_staff", "sword", "staff", "vest", "helmet",
        "cleaner_vest", "black_armor", "lucky_ring", "work_necklace", "rich_wallet", "bamboo_rod",
        "alloy_rod", "potion", "mount", "flower", "coffee", "lipstick", "perfume", "ring_box", "baby_milk"]

PETS = [
    {"name": "小狗", "hp": 15, "attack": 2, "luck": 1},
    {"name": "黑猫", "crit": 5, "speed": 2, "luck": 4},
    {"name": "乌龟", "hp": 35, "defense": 6},
    {"name": "河豚", "attack": 5, "crit": 2},
    {"name": "工地老鼠", "speed": 4, "luck": 3},
    {"name": "垃圾桶精灵", "luck": 8, "defense": 2},
]

JOBS = {
    "chef": ("厨师", 42, 6),
    "mason": ("瓦工", 55, 9),
    "cleaner": ("环卫工", 36, 5),
    "runner": ("跑腿", 48, 7),
    "brick": ("搬砖", 60, 10),
}

QUESTS = {
    "hello": {"name": "新手任务", "desc": "和 3 个玩家打招呼", "need": ("chat_count", 3), "gold": 80, "exp": 60},
    "brick": {"name": "打工任务", "desc": "搬 10 块砖", "need": ("work_brick", 10), "gold": 180, "exp": 120},
    "clean": {"name": "环卫任务", "desc": "清理 8 袋垃圾", "need": ("trash_clean", 8), "gold": 130, "exp": 90},
    "fish": {"name": "钓鱼任务", "desc": "钓到 5 条鱼", "need": ("fish_caught", 5), "gold": 150, "exp": 110},
    "pk": {"name": "PK 任务", "desc": "击败 1 名玩家", "need": ("pk_kill", 1), "gold": 220, "exp": 150},
    "hunt": {"name": "猎魔任务", "desc": "击败 8 只怪物", "need": ("monster_kill", 8), "gold": 240, "exp": 180},
    "elite": {"name": "精英讨伐", "desc": "击败 2 只精英怪", "need": ("elite_kill", 2), "gold": 360, "exp": 260},
    "rich": {"name": "富婆任务", "desc": "完成 3 次跑腿", "need": ("villa_task", 3), "gold": 260, "exp": 120},
    "beauty_meet": {"name": "初见佳人", "desc": "和美女 NPC 搭讪 3 次", "need": ("romance_greet", 3), "gold": 120, "exp": 90},
    "beauty_gift": {"name": "送礼达人", "desc": "给美女送礼 4 次", "need": ("romance_gift", 4), "gold": 200, "exp": 140},
    "beauty_date": {"name": "约会专家", "desc": "完成 2 次约会", "need": ("romance_date", 2), "gold": 260, "exp": 180},
    "beauty_love": {"name": "修成正果", "desc": "成功告白成为伴侣", "need": ("romance_partner", 1), "gold": 400, "exp": 260},
    "beauty_baby": {"name": "家族传承", "desc": "生下 1 个孩子", "need": ("baby_born", 1), "gold": 500, "exp": 320},
    "tribe_join": {"name": "部落归属", "desc": "加入或创建 1 个部落", "need": ("tribe_join", 1), "gold": 180, "exp": 120},
    "tribe_donate": {"name": "部落贡献", "desc": "向部落捐献 3 次", "need": ("tribe_donate", 3), "gold": 220, "exp": 150},
    "daily": {"name": "每日任务", "desc": "完成 6 次任意互动", "need": ("daily_actions", 6), "gold": 160, "exp": 100},
}

# 美女 NPC：恋爱 / 送礼 / 约会 / 生孩子
BEAUTIES = {
    "lin": {
        "id": "lin", "name": "林晚晚", "title": "别墅区大小姐", "zone": "villa",
        "x": 980, "y": 240, "color": "#f472b6", "prefer": "flower",
        "line": "有钱可以谈，没钱先去打工。",
    },
    "su": {
        "id": "su", "name": "苏清清", "title": "广场女剑仙", "zone": "square",
        "x": 1180, "y": 700, "color": "#a78bfa", "prefer": "coffee",
        "line": "先打怪升级，再来跟我聊风花雪月。",
    },
    "ye": {
        "id": "ye", "name": "夜未央", "title": "黑市女老板", "zone": "market",
        "x": 1960, "y": 280, "color": "#fb7185", "prefer": "perfume",
        "line": "感情也是买卖，你出价吧。",
    },
    "xia": {
        "id": "xia", "name": "夏浅浅", "title": "河边钓系美女", "zone": "river",
        "x": 420, "y": 1120, "color": "#38bdf8", "prefer": "lipstick",
        "line": "陪我钓到黄金鱼，再考虑心动。",
    },
    "mu": {
        "id": "mu", "name": "沐瑶", "title": "洞府女修", "zone": "cave",
        "x": 2220, "y": 1180, "color": "#c084fc", "prefer": "ring_box",
        "line": "双修是正经修炼，别想歪。",
    },
}

CHILD_TRAITS = [
    {"name": "卷王体质", "attack": 3, "speed": 1},
    {"name": "躺平天赋", "defense": 4, "hp": 12},
    {"name": "暴富命格", "luck": 6, "crit": 2},
    {"name": "社交牛杂", "luck": 3, "speed": 2},
    {"name": "修仙苗子", "attack": 2, "defense": 2, "hp": 8},
    {"name": "嘴强王者", "crit": 4, "luck": 2},
]

CHILD_NAMES_M = ["小卷", "铁蛋", "修修", "狗剩", "元宝", "阿强", "小满"]
CHILD_NAMES_F = ["团子", "糖糖", "灵灵", "小满", "晚晚", "清清", "瑶瑶"]

# 地下城勇士风怪物模板：shape 供前端绘制，zone 指定刷新区
MONSTER_TEMPLATES = {
    "goblin": {
        "name": "哥布林小弟", "shape": "goblin", "color": "#65a30d", "level": 2,
        "hp": 70, "attack": 8, "defense": 2, "speed": 70, "exp": 28, "gold": (8, 22),
        "drops": [("goblin_ear", 55), ("potion", 18), ("wood_stick", 8)], "aggro": 140, "elite": False,
    },
    "slime": {
        "name": "暗黑史莱姆", "shape": "slime", "color": "#7c3aed", "level": 3,
        "hp": 95, "attack": 10, "defense": 4, "speed": 55, "exp": 34, "gold": (10, 28),
        "drops": [("slime_gel", 60), ("potion", 20), ("lucky_ring", 3)], "aggro": 130, "elite": False,
    },
    "skeleton": {
        "name": "骸骨刀兵", "shape": "skeleton", "color": "#e2e8f0", "level": 4,
        "hp": 110, "attack": 14, "defense": 5, "speed": 75, "exp": 42, "gold": (14, 36),
        "drops": [("bone_shard", 58), ("cleaver", 6), ("potion", 16)], "aggro": 160, "elite": False,
    },
    "mushroom": {
        "name": "毒孢蘑菇", "shape": "mushroom", "color": "#f43f5e", "level": 3,
        "hp": 88, "attack": 11, "defense": 3, "speed": 48, "exp": 32, "gold": (9, 26),
        "drops": [("life_shard", 35), ("potion", 25), ("trash_bag", 20)], "aggro": 120, "elite": False,
    },
    "wolf": {
        "name": "冰霜魔狼", "shape": "wolf", "color": "#38bdf8", "level": 6,
        "hp": 150, "attack": 18, "defense": 7, "speed": 110, "exp": 58, "gold": (20, 48),
        "drops": [("wolf_fang", 48), ("potion", 22), ("fishing_staff", 5)], "aggro": 190, "elite": False,
    },
    "troll": {
        "name": "熔岩巨魔", "shape": "troll", "color": "#ea580c", "level": 8,
        "hp": 240, "attack": 22, "defense": 12, "speed": 45, "exp": 80, "gold": (28, 70),
        "drops": [("dark_ore", 40), ("brick", 25), ("helmet", 8)], "aggro": 150, "elite": False,
    },
    "lancer": {
        "name": "魔枪兵", "shape": "lancer", "color": "#a855f7", "level": 7,
        "hp": 170, "attack": 24, "defense": 8, "speed": 85, "exp": 68, "gold": (24, 55),
        "drops": [("dark_ore", 30), ("demon_blade", 4), ("potion", 20)], "aggro": 175, "elite": False,
    },
    "mech": {
        "name": "工地机械兽", "shape": "mech", "color": "#94a3b8", "level": 9,
        "hp": 280, "attack": 20, "defense": 16, "speed": 50, "exp": 90, "gold": (30, 75),
        "drops": [("mech_core", 28), ("shovel", 10), ("helmet", 12)], "aggro": 155, "elite": False,
    },
    "thief": {
        "name": "黑市影贼", "shape": "thief", "color": "#312e81", "level": 7,
        "hp": 140, "attack": 21, "defense": 6, "speed": 100, "exp": 62, "gold": (35, 90),
        "drops": [("rich_wallet", 6), ("lucky_ring", 8), ("scroll", 12)], "aggro": 170, "elite": False,
    },
    "guard": {
        "name": "地下城守卫", "shape": "guard", "color": "#b45309", "level": 10,
        "hp": 320, "attack": 26, "defense": 18, "speed": 60, "exp": 110, "gold": (40, 95),
        "drops": [("guardian_plate", 5), ("dark_ore", 35), ("potion", 25)], "aggro": 180, "elite": False,
    },
    "angel": {
        "name": "堕落天使残影", "shape": "angel", "color": "#f472b6", "level": 12,
        "hp": 260, "attack": 30, "defense": 10, "speed": 95, "exp": 130, "gold": (45, 110),
        "drops": [("scroll", 22), ("staff", 4), ("pet_egg", 6)], "aggro": 200, "elite": True,
    },
    "dragonkin": {
        "name": "金甲龙人", "shape": "dragon", "color": "#fbbf24", "level": 14,
        "hp": 420, "attack": 34, "defense": 20, "speed": 70, "exp": 180, "gold": (70, 160),
        "drops": [("dragon_scale", 18), ("sword", 8), ("demon_blade", 6)], "aggro": 210, "elite": True,
    },
    "overtime": {
        "name": "加班小鬼", "shape": "goblin", "color": "#fb7185", "level": 5,
        "hp": 120, "attack": 15, "defense": 5, "speed": 80, "exp": 48, "gold": (16, 40),
        "drops": [("coffee", 20), ("life_shard", 25), ("potion", 18)], "aggro": 165, "elite": False,
    },
}

# 每个危险区的刷怪配额（模板名列表按权重重复）
MONSTER_SPAWNS = {
    "junk": {"count": 10, "pool": ["mushroom", "mushroom", "slime", "goblin", "goblin", "skeleton"]},
    "site": {"count": 9, "pool": ["mech", "mech", "troll", "goblin", "overtime", "skeleton"]},
    "market": {"count": 8, "pool": ["thief", "thief", "lancer", "slime", "skeleton", "angel"]},
    "wild": {"count": 14, "pool": ["wolf", "wolf", "lancer", "troll", "guard", "overtime", "dragonkin", "skeleton", "goblin"]},
    "villa": {"count": 7, "pool": ["angel", "thief", "wolf", "lancer", "slime", "dragonkin"]},
}


def now():
    return time.time()


def today():
    return time.strftime("%Y-%m-%d", time.localtime())


def clamp(v, a, b):
    try:
        v = float(v)
    except Exception:
        v = a
    return max(a, min(b, v))


def clean_text(s, limit=80):
    if not isinstance(s, str):
        s = ""
    s = s.replace("\r", " ").replace("\n", " ").strip()
    while "  " in s:
        s = s.replace("  ", " ")
    return s[:limit]


def zone_at(x, y):
    for z in ZONES:
        if z["x"] <= x <= z["x"] + z["w"] and z["y"] <= y <= z["y"] + z["h"]:
            return z
    return {"id": "road", "name": "城郊小路", "safe": True, "kind": "road"}


def zone_by_id(zid):
    for z in ZONES:
        if z["id"] == zid:
            return z
    return None


def public_monster(m):
    return {
        "id": m["id"], "type": m["type"], "name": m["name"], "shape": m["shape"],
        "color": m["color"], "x": round(m["x"], 1), "y": round(m["y"], 1),
        "dir": m.get("dir", "down"), "level": m["level"], "hp": max(0, int(m["hp"])),
        "maxHp": m["maxHp"], "elite": bool(m.get("elite")), "zone": m.get("zone", ""),
        "bubble": m.get("bubble", ""), "bubbleAt": m.get("bubbleAt", 0),
        "alive": m["hp"] > 0,
    }


def spawn_point_in_zone(zid):
    z = zone_by_id(zid)
    if not z:
        return WORLD_W / 2, WORLD_H / 2
    pad = 40
    x = random.uniform(z["x"] + pad, z["x"] + z["w"] - pad)
    y = random.uniform(z["y"] + pad, z["y"] + z["h"] - pad)
    return x, y


def create_monster(type_id, zid, mid=None):
    tpl = MONSTER_TEMPLATES[type_id]
    x, y = spawn_point_in_zone(zid)
    elite = bool(tpl.get("elite"))
    # 小概率野外升格精英
    if not elite and zid == "wild" and random.random() < 0.08:
        elite = True
    hp = int(tpl["hp"] * (1.55 if elite and not tpl.get("elite") else 1))
    atk = int(tpl["attack"] * (1.35 if elite and not tpl.get("elite") else 1))
    name = tpl["name"]
    if elite and not tpl.get("elite"):
        name = "精英·" + name
    elif elite and tpl.get("elite"):
        name = "★" + name
    return {
        "id": mid or uuid.uuid4().hex[:10],
        "type": type_id,
        "name": name,
        "shape": tpl["shape"],
        "color": "#fbbf24" if elite and not tpl.get("elite") else tpl["color"],
        "level": tpl["level"] + (2 if elite and not tpl.get("elite") else 0),
        "x": x, "y": y, "homeX": x, "homeY": y,
        "hp": hp, "maxHp": hp,
        "attack": atk, "defense": int(tpl["defense"] * (1.2 if elite else 1)),
        "speed": tpl["speed"],
        "exp": int(tpl["exp"] * (1.6 if elite else 1)),
        "gold": tpl["gold"],
        "drops": list(tpl["drops"]),
        "aggro": tpl["aggro"] + (30 if elite else 0),
        "elite": elite,
        "zone": zid,
        "dir": random.choice(["up", "down", "left", "right"]),
        "targetId": None,
        "lastAttack": 0,
        "nextWander": 0,
        "respawnAt": 0,
        "bubble": "", "bubbleAt": 0,
        "dead": False,
    }


def ensure_monsters():
    """按区域配额补齐怪物（含等待复活的尸体占位，避免超额刷新）。"""
    slots = {zid: 0 for zid in MONSTER_SPAWNS}
    for m in monsters.values():
        zid = m.get("zone")
        if zid in slots:
            slots[zid] += 1
    for zid, conf in MONSTER_SPAWNS.items():
        need = conf["count"] - slots.get(zid, 0)
        for _ in range(max(0, need)):
            type_id = random.choice(conf["pool"])
            m = create_monster(type_id, zid)
            monsters[m["id"]] = m


def nearest_player_for_monster(m, radius):
    best, best_d = None, radius
    for p in players.values():
        if p.get("hp", 0) <= 0:
            continue
        # 安全区玩家不被追
        if zone_at(p["x"], p["y"]).get("safe"):
            continue
        d = ((p["x"] - m["x"]) ** 2 + (p["y"] - m["y"]) ** 2) ** 0.5
        if d <= best_d:
            best, best_d = p, d
    return best, best_d


def tick_monsters():
    """怪物 AI：游荡、追击、反击咬人。由 cleanup 节流调用。"""
    global _last_monster_tick
    t = now()
    dt = min(0.35, max(0.05, t - _last_monster_tick)) if _last_monster_tick else 0.2
    if _last_monster_tick and t - _last_monster_tick < 0.12:
        return
    _last_monster_tick = t
    ensure_monsters()

    for m in list(monsters.values()):
        # 复活
        if m["hp"] <= 0 or m.get("dead"):
            if m.get("respawnAt") and t >= m["respawnAt"]:
                type_id = m["type"] if m["type"] in MONSTER_TEMPLATES else random.choice(list(MONSTER_TEMPLATES))
                zid = m.get("zone") if m.get("zone") in MONSTER_SPAWNS else "wild"
                fresh = create_monster(type_id, zid, mid=m["id"])
                monsters[m["id"]] = fresh
            continue

        # 超出家园太远则回家
        home_d = ((m["x"] - m["homeX"]) ** 2 + (m["y"] - m["homeY"]) ** 2) ** 0.5
        target = players.get(m.get("targetId") or "")
        if target and (target.get("hp", 0) <= 0 or zone_at(target["x"], target["y"]).get("safe")):
            target = None
            m["targetId"] = None
        if not target:
            target, dist = nearest_player_for_monster(m, m["aggro"])
            if target:
                m["targetId"] = target["id"]
        else:
            dist = ((target["x"] - m["x"]) ** 2 + (target["y"] - m["y"]) ** 2) ** 0.5
            if dist > m["aggro"] * 1.35 or home_d > 320:
                m["targetId"] = None
                target = None

        speed = m["speed"] * dt
        if target:
            dx, dy = target["x"] - m["x"], target["y"] - m["y"]
            d = max(0.01, (dx * dx + dy * dy) ** 0.5)
            if d > 42:
                m["x"] += dx / d * speed
                m["y"] += dy / d * speed
                m["dir"] = "right" if abs(dx) > abs(dy) and dx > 0 else "left" if abs(dx) > abs(dy) else ("down" if dy > 0 else "up")
            elif t - m.get("lastAttack", 0) >= 1.35:
                # 近身咬人
                m["lastAttack"] = t
                ps = calc_stats(target)
                dmg = max(1, int(m["attack"] - ps["defense"] * 0.35 + random.randint(0, 5)))
                target["hp"] = max(0, target["hp"] - dmg)
                target["bubble"], target["bubbleAt"] = f"被咬 -{dmg}", t
                m["bubble"], m["bubbleAt"] = "嗷！", t
                if target["hp"] <= 0:
                    target["deadUntil"] = t + 7
                    target["counters"]["deaths"] = target["counters"].get("deaths", 0) + 1
                    epitaph = random.choice(["不该惹地下城的怪", "这波怪太真实了", "被史莱姆教育了", "下把先喝药"])
                    target["bubble"], target["bubbleAt"] = epitaph, t
                    add_chat("墓碑", f"{target['name']} 被 {m['name']} 击败：{epitaph}", sys=True)
                    m["targetId"] = None
        else:
            # 闲逛
            if t >= m.get("nextWander", 0):
                m["nextWander"] = t + random.uniform(1.2, 3.5)
                m["_wdx"] = random.uniform(-1, 1)
                m["_wdy"] = random.uniform(-1, 1)
            wdx, wdy = m.get("_wdx", 0), m.get("_wdy", 0)
            n = max(0.01, (wdx * wdx + wdy * wdy) ** 0.5)
            m["x"] += wdx / n * speed * 0.45
            m["y"] += wdy / n * speed * 0.45
            if home_d > 160:
                m["x"] += (m["homeX"] - m["x"]) * 0.04
                m["y"] += (m["homeY"] - m["y"]) * 0.04

        # 限制在所属区域附近
        z = zone_by_id(m["zone"])
        if z:
            m["x"] = clamp(m["x"], z["x"] + 20, z["x"] + z["w"] - 20)
            m["y"] = clamp(m["y"], z["y"] + 20, z["y"] + z["h"] - 20)
        else:
            m["x"] = clamp(m["x"], 24, WORLD_W - 24)
            m["y"] = clamp(m["y"], 24, WORLD_H - 24)


def kill_monster(m, killer):
    t = now()
    m["hp"] = 0
    m["dead"] = True
    m["respawnAt"] = t + random.uniform(8, 16)
    m["targetId"] = None
    m["bubble"], m["bubbleAt"] = "粉碎…", t

    gold = random.randint(int(m["gold"][0]), int(m["gold"][1]))
    if m.get("elite"):
        gold = int(gold * 1.8)
    killer["gold"] += gold
    add_exp(killer, m["exp"])
    bump(killer, "monster_kill")
    if m.get("elite"):
        bump(killer, "elite_kill")

    drops = []
    for item_id, chance in m.get("drops", []):
        rate = chance + (12 if m.get("elite") else 0) + calc_stats(killer)["luck"] // 4
        if random.randint(1, 100) <= rate:
            add_item(killer, item_id)
            drops.append(ITEMS.get(item_id, {}).get("name", item_id))
    # 精英额外材料
    if m.get("elite") and random.random() < 0.35:
        bonus = random.choice(["dark_ore", "mech_core", "dragon_scale", "demon_blade"])
        add_item(killer, bonus)
        drops.append(ITEMS[bonus]["name"])

    drop_txt = ("，掉落 " + "、".join(drops[:4])) if drops else ""
    if m.get("elite") or m["level"] >= 10:
        add_chat("系统", f"{killer['name']} 击败了 {m['name']}！", sys=True)
    return gold, m["exp"], drop_txt


def realm_name(cultivation):
    name = REALMS[0][1]
    for need, realm in REALMS:
        if cultivation >= need:
            name = realm
    return name


def add_item(p, item_id, qty=1):
    if item_id not in ITEMS or qty <= 0:
        return
    inv = p.setdefault("inventory", {})
    inv[item_id] = int(inv.get(item_id, 0)) + int(qty)


def remove_item(p, item_id, qty=1):
    inv = p.setdefault("inventory", {})
    have = int(inv.get(item_id, 0))
    if have < qty:
        return False
    if have == qty:
        inv.pop(item_id, None)
    else:
        inv[item_id] = have - qty
    return True


def add_exp(p, amount):
    p["exp"] += int(amount)
    leveled = False
    while p["exp"] >= 90 + p["level"] * 55:
        p["exp"] -= 90 + p["level"] * 55
        p["level"] += 1
        p["base"]["hp"] += 8
        p["hp"] = calc_stats(p)["hp"]
        leveled = True
    if leveled:
        add_chat("系统", f"{p['name']} 升到了 {p['level']} 级", sys=True)
    return leveled


def bump(p, key, amount=1):
    if p.get("daily") != today():
        p["daily"] = today()
        p["claimed"].discard("daily")
        p["counters"]["daily_actions"] = 0
    p["counters"][key] = int(p["counters"].get(key, 0)) + amount
    if key != "online":
        p["counters"]["daily_actions"] = int(p["counters"].get("daily_actions", 0)) + 1


def calc_stats(p):
    stats = dict(p.get("base", {}))
    for k in ("hp", "attack", "defense", "speed", "crit", "luck"):
        stats.setdefault(k, 0)
    stats["hp"] += (p.get("level", 1) - 1) * 8
    stats["attack"] += (p.get("level", 1) - 1) * 2
    stats["defense"] += (p.get("level", 1) - 1)
    stats["luck"] += p.get("level", 1) // 2
    for item_id in p.get("equipment", {}).values():
        item = ITEMS.get(item_id, {})
        for k in ("hp", "attack", "defense", "speed", "crit", "luck"):
            stats[k] += item.get(k, 0)
    if p.get("mount"):
        stats["speed"] += ITEMS["mount"]["speed"]
    pet = p.get("pet")
    if pet:
        for k in ("hp", "attack", "defense", "speed", "crit", "luck"):
            stats[k] += pet.get(k, 0) + (pet.get("level", 1) - 1)
    # 孩子提供属性
    for child in p.get("children") or []:
        for k in ("hp", "attack", "defense", "speed", "crit", "luck"):
            stats[k] += int(child.get(k, 0))
    # 伴侣光环
    if p.get("partnerId"):
        stats["luck"] += 3
        stats["hp"] += 10
    # 部落加成
    tribe = tribes.get(p.get("tribeId") or "")
    if tribe:
        lv = int(tribe.get("level", 1))
        stats["attack"] += min(8, lv)
        stats["defense"] += min(6, lv // 2)
        stats["hp"] += min(40, lv * 4)
    status = p.get("status", {})
    if status.get("back_pain_until", 0) > now():
        stats["speed"] = max(2, stats["speed"] - 3)
    if status.get("heartbreak_until", 0) > now():
        stats["luck"] = max(0, stats["luck"] - 4)
        stats["attack"] = max(1, stats["attack"] - 2)
    return stats


def public_beauty(b, p=None):
    aff = 0
    if p:
        aff = int((p.get("affection") or {}).get(b["id"], 0))
    return {
        "id": b["id"], "name": b["name"], "title": b["title"], "zone": b["zone"],
        "x": b["x"], "y": b["y"], "color": b["color"], "prefer": b["prefer"],
        "line": b["line"], "affection": aff,
        "preferName": ITEMS.get(b["prefer"], {}).get("name", b["prefer"]),
    }


def public_tribe(t):
    members = []
    for pid in list(t.get("members") or []):
        pl = players.get(pid)
        if pl:
            members.append({"id": pid, "name": pl["name"], "level": pl["level"], "role": "leader" if pid == t.get("leaderId") else "member"})
    return {
        "id": t["id"], "name": t["name"], "leaderId": t.get("leaderId"), "leaderName": t.get("leaderName", ""),
        "level": t.get("level", 1), "exp": t.get("exp", 0), "notice": t.get("notice", ""),
        "memberCount": len(t.get("members") or []), "members": members[:20],
        "color": t.get("color", "#38bdf8"), "fund": t.get("fund", 0),
    }


def public_player(p):
    stats = calc_stats(p)
    partner = BEAUTIES.get(p.get("partnerId") or "", {})
    tribe = tribes.get(p.get("tribeId") or "")
    return {
        "id": p["id"], "name": p["name"], "color": p["color"], "style": p["style"],
        "x": p["x"], "y": p["y"], "dir": p["dir"], "bubble": p.get("bubble", ""),
        "bubbleAt": p.get("bubbleAt", 0), "level": p["level"], "realm": realm_name(p["cultivation"]),
        "hp": p["hp"], "maxHp": stats["hp"], "title": p.get("title", "修仙废柴"),
        "red": p.get("red", 0), "deadUntil": p.get("deadUntil", 0), "power": power_of(p),
        "pet": p.get("pet", {}).get("name") if p.get("pet") else "",
        "partner": partner.get("name", ""), "childCount": len(p.get("children") or []),
        "tribe": tribe.get("name", "") if tribe else "", "tribeId": p.get("tribeId") or "",
    }


def full_player(p):
    data = public_player(p)
    partner = BEAUTIES.get(p.get("partnerId") or "")
    tribe = tribes.get(p.get("tribeId") or "")
    data.update({
        "exp": p["exp"], "gold": p["gold"], "bank": p["bank"], "cultivation": p["cultivation"],
        "stats": calc_stats(p), "inventory": p["inventory"], "equipment": p["equipment"],
        "titles": sorted(p["titles"]), "counters": p["counters"], "claimed": sorted(p["claimed"]),
        "zone": zone_at(p["x"], p["y"]), "friends": sorted(p["friends"]), "guild": p.get("guild", ""),
        "team": sorted(p["team"]), "petObj": p.get("pet"), "status": p.get("status", {}),
        "daily": p.get("daily", today()), "nextWorkAt": p.get("nextWorkAt", 0), "nextFishAt": p.get("nextFishAt", 0),
        "nextTrashAt": p.get("nextTrashAt", 0), "nextAttackAt": p.get("nextAttackAt", 0),
        "affection": p.get("affection") or {},
        "partnerId": p.get("partnerId") or "",
        "partnerName": partner.get("name", "") if partner else "",
        "children": p.get("children") or [],
        "tribeId": p.get("tribeId") or "",
        "tribeRole": p.get("tribeRole") or "",
        "tribeInfo": public_tribe(tribe) if tribe else None,
        "nextRomanceAt": p.get("nextRomanceAt", 0),
        "nextBabyAt": p.get("nextBabyAt", 0),
        "beauties": [public_beauty(b, p) for b in BEAUTIES.values()],
    })
    return data


def power_of(p):
    s = calc_stats(p)
    return int(s["hp"] * .35 + s["attack"] * 9 + s["defense"] * 6 + s["speed"] * 4 + s["crit"] * 5 + s["luck"] * 2)


def add_chat(name, text, sys=False, **extra):
    chat.append({"sys": sys, "name": name, "text": clean_text(text, 120), "t": now(), **extra})
    if len(chat) > 100:
        del chat[:-100]


def default_player(pid, name, color, style, x, y):
    p = {
        "id": pid, "name": name, "color": color, "style": style, "x": x, "y": y, "dir": "down",
        "bubble": "", "bubbleAt": 0, "last": now(), "joined": now(), "level": 1, "exp": 0,
        "cultivation": 0, "hp": 112, "gold": 180, "bank": 0, "red": 0, "redUntil": 0, "deadUntil": 0,
        "base": {"hp": 112, "attack": 10, "defense": 4, "speed": 5, "crit": 3, "luck": 5},
        "inventory": {"wood_stick": 1, "vest": 1, "potion": 2},
        "equipment": {"weapon": "wood_stick", "armor": "vest"},
        "titles": {"修仙废柴"}, "title": "修仙废柴", "counters": {}, "claimed": set(),
        "friends": set(), "team": set(), "guild": "", "pet": None, "mount": False, "daily": today(),
        "nextWorkAt": 0, "nextFishAt": 0, "nextTrashAt": 0, "nextAttackAt": 0, "lastMoveXp": now(),
        "lastTrainAt": 0, "lastOnlineTick": now(), "status": {},
        "affection": {}, "partnerId": "", "children": [],
        "tribeId": "", "tribeRole": "", "nextRomanceAt": 0, "nextBabyAt": 0,
    }
    p["hp"] = calc_stats(p)["hp"]
    return p


def jsonable_player(p):
    p = dict(p)
    for key in ("titles", "claimed", "friends", "team"):
        p[key] = sorted(p.get(key, []))
    return p


def update_titles(p):
    c = p["counters"]
    if c.get("fish_caught", 0) >= 10:
        p["titles"].add("钓鱼佬")
    if c.get("trash_clean", 0) >= 12 or c.get("life_shard", 0) >= 6:
        p["titles"].add("拾荒王")
    if c.get("work_count", 0) >= 20:
        p["titles"].add("打工皇帝")
    if c.get("pk_kill", 0) >= 3:
        p["titles"].add("街头霸王")
    if c.get("monster_kill", 0) >= 15:
        p["titles"].add("地下城猎人")
    if c.get("elite_kill", 0) >= 5:
        p["titles"].add("精英讨伐者")
    if c.get("monster_kill", 0) >= 50:
        p["titles"].add("怪物图鉴达人")
    if c.get("romance_gift", 0) >= 6:
        p["titles"].add("恋爱脑战士")
    if c.get("romance_partner", 0) >= 1 or p.get("partnerId"):
        p["titles"].add("名草有主")
    if c.get("baby_born", 0) >= 1 or p.get("children"):
        p["titles"].add("奶爸/奶妈预备役")
    if c.get("baby_born", 0) >= 3:
        p["titles"].add("家族族长")
    if p.get("tribeId"):
        p["titles"].add("部落成员")
    if p.get("tribeRole") == "leader":
        p["titles"].add("部落酋长")
    if p["gold"] + p["bank"] <= 3 and p["level"] > 2:
        p["titles"].add("重新做人")
    if c.get("failures", 0) >= 5:
        p["titles"].add("命苦加成")
        p["status"]["luck_until"] = now() + 90
    if c.get("life_shard", 0) >= 8:
        p["titles"].add("人生拼图师")


def ensure_event():
    global event
    t = now()
    if event and event.get("endsAt", 0) > t:
        return
    choices = [
        ("red_packet", "天降红包", "地图随机刷出金币，所有互动金币小幅提高。", 60),
        ("boss_gone", "老板跑路", "打工收益减半，老板说下月一定补。", 55),
        ("rich_pass", "富婆路过", "别墅区附近玩家会收到意外转账。", 45),
        ("patrol", "城管来了", "摆摊玩家会被迫收摊一件商品。", 35),
        ("golden_fish", "黄金鱼潮", "钓鱼稀有率提升。", 65),
        ("world_boss", "世界 Boss 出现", "野外荒地可以围殴加班魔王。", 75),
        ("rain", "地图下雨", "移动变慢，钓鱼概率提升。", 70),
    ]
    typ, name, text, dur = random.choice(choices)
    event = {"type": typ, "name": name, "text": text, "endsAt": t + dur, "startedAt": t}
    if typ == "world_boss":
        event["bossHp"] = 650
    if typ == "patrol":
        owner_ids = list(stalls)
        if owner_ids:
            sid = random.choice(owner_ids)
            stall = stalls.pop(sid, None)
            owner = players.get(stall["sellerId"]) if stall else None
            if owner:
                add_item(owner, stall["itemId"], stall["qty"])
                add_chat("系统", f"城管来了，{owner['name']} 的摊位临时收摊", sys=True)
    add_chat("世界事件", f"{name}：{text}", sys=True)


def cleanup():
    ensure_event()
    tick_monsters()
    t = now()
    for p in list(players.values()):
        if p.get("hp", 0) <= 0 and p.get("deadUntil", 0) and t >= p["deadUntil"]:
            x, y = random.choice(SPAWNS)
            p["x"], p["y"], p["hp"], p["deadUntil"] = x, y, calc_stats(p)["hp"], 0
            p["bubble"], p["bubbleAt"] = "重新做人，马上又输", t
        if p.get("redUntil", 0) and t >= p["redUntil"]:
            p["red"] = max(0, p.get("red", 0) - 1)
            if p["red"] <= 0:
                p["redUntil"] = 0
        if t - p.get("lastOnlineTick", t) >= 10:
            bump(p, "online", int(t - p.get("lastOnlineTick", t)))
            p["lastOnlineTick"] = t
    dead = [pid for pid, p in players.items() if t - p.get("last", 0) > 90]
    for pid in dead:
        p = players.pop(pid, None)
        if p:
            leave_tribe_silent(p)
            add_chat("系统", f"{p['name']} 下线了，世界少了一份工资", sys=True)
    # 清理空部落
    for tid in list(tribes.keys()):
        members = [mid for mid in tribes[tid].get("members", set()) if mid in players]
        tribes[tid]["members"] = set(members)
        if not members:
            tribes.pop(tid, None)
        else:
            if tribes[tid].get("leaderId") not in players:
                new_leader = members[0]
                tribes[tid]["leaderId"] = new_leader
                tribes[tid]["leaderName"] = players[new_leader]["name"]
                players[new_leader]["tribeRole"] = "leader"
    if len(chat) > 100:
        del chat[:-100]


def leave_tribe_silent(p):
    tid = p.get("tribeId")
    if not tid or tid not in tribes:
        p["tribeId"] = ""
        p["tribeRole"] = ""
        return
    t = tribes[tid]
    t["members"].discard(p["id"])
    if t.get("leaderId") == p["id"]:
        remain = [mid for mid in t["members"] if mid in players]
        if remain:
            nid = remain[0]
            t["leaderId"] = nid
            t["leaderName"] = players[nid]["name"]
            players[nid]["tribeRole"] = "leader"
        else:
            tribes.pop(tid, None)
    p["tribeId"] = ""
    p["tribeRole"] = ""
    p["guild"] = ""


def add_affection(p, bid, amount):
    aff = p.setdefault("affection", {})
    aff[bid] = max(0, min(100, int(aff.get(bid, 0)) + int(amount)))
    return aff[bid]


def tribe_add_exp(t, amount):
    t["exp"] = int(t.get("exp", 0)) + int(amount)
    while t["exp"] >= 100 + t.get("level", 1) * 40:
        t["exp"] -= 100 + t.get("level", 1) * 40
        t["level"] = int(t.get("level", 1)) + 1
        add_chat("部落", f"部落「{t['name']}」升到 {t['level']} 级！", sys=True)


def rankings():
    people = list(players.values())
    def row(p, value):
        return {"id": p["id"], "name": p["name"], "title": p.get("title", ""), "value": int(value)}
    boards = {
        "等级榜": [row(p, p["level"]) for p in sorted(people, key=lambda x: x["level"], reverse=True)[:10]],
        "财富榜": [row(p, p["gold"] + p["bank"]) for p in sorted(people, key=lambda x: x["gold"] + x["bank"], reverse=True)[:10]],
        "战力榜": [row(p, power_of(p)) for p in sorted(people, key=power_of, reverse=True)[:10]],
        "钓鱼榜": [row(p, p["counters"].get("fish_caught", 0)) for p in sorted(people, key=lambda x: x["counters"].get("fish_caught", 0), reverse=True)[:10]],
        "击杀榜": [row(p, p["counters"].get("pk_kill", 0)) for p in sorted(people, key=lambda x: x["counters"].get("pk_kill", 0), reverse=True)[:10]],
        "猎魔榜": [row(p, p["counters"].get("monster_kill", 0)) for p in sorted(people, key=lambda x: x["counters"].get("monster_kill", 0), reverse=True)[:10]],
        "恋爱榜": [row(p, sum((p.get("affection") or {}).values()) + (50 if p.get("partnerId") else 0)) for p in sorted(people, key=lambda x: sum((x.get("affection") or {}).values()) + (50 if x.get("partnerId") else 0), reverse=True)[:10]],
        "子嗣榜": [row(p, len(p.get("children") or [])) for p in sorted(people, key=lambda x: len(x.get("children") or []), reverse=True)[:10]],
        "打工榜": [row(p, p["counters"].get("work_count", 0)) for p in sorted(people, key=lambda x: x["counters"].get("work_count", 0), reverse=True)[:10]],
        "修为榜": [row(p, p["cultivation"]) for p in sorted(people, key=lambda x: x["cultivation"], reverse=True)[:10]],
        "在线时长榜": [row(p, p["counters"].get("online", 0)) for p in sorted(people, key=lambda x: x["counters"].get("online", 0), reverse=True)[:10]],
        "死亡次数榜": [row(p, p["counters"].get("deaths", 0)) for p in sorted(people, key=lambda x: x["counters"].get("deaths", 0), reverse=True)[:10]],
        "最惨打工人榜": [row(p, p["counters"].get("work_count", 0) + p["counters"].get("deaths", 0) * 3 + p["counters"].get("failures", 0) * 2) for p in sorted(people, key=lambda x: x["counters"].get("work_count", 0) + x["counters"].get("deaths", 0) * 3 + x["counters"].get("failures", 0) * 2, reverse=True)[:10]],
    }
    return boards


def respond_action(p, message, ok=True, **extra):
    update_titles(p)
    return {"ok": ok, "message": message, "me": full_player(p), **extra}


def handle_action(p, data):
    action = data.get("type")
    payload = data.get("payload") or {}
    z = zone_at(p["x"], p["y"])
    t = now()
    if p.get("hp", 0) <= 0:
        return respond_action(p, "灵魂状态只能飘着等复活", False)

    if action == "fish":
        if z["kind"] != "fish":
            return respond_action(p, "要站在河边才能钓鱼", False)
        if t < p.get("nextFishAt", 0):
            return respond_action(p, "鱼还在开会，稍等一下", False)
        p["nextFishAt"] = t + 3.2
        lvl = 1 + p["counters"].get("fish_caught", 0) // 8
        luck = calc_stats(p)["luck"] + lvl * 2
        rare = min(42, 6 + luck // 3)
        if event.get("type") in ("golden_fish", "rain"):
            rare += 18
        roll = random.randint(1, 100)
        if roll <= 2 + rare // 6:
            item = "golden_fish"
        elif roll <= 4 + rare // 4:
            item = "pet_egg"
        elif roll <= 10 + rare:
            item = random.choice(["treasure_box", "scroll", "big_fish"])
        elif roll <= 78:
            item = random.choice(["small_fish", "small_fish", "big_fish", "trash_bag"])
        else:
            item = random.choice(["old_shoe", "trash_bag", "life_shard"])
        add_item(p, item)
        gain = max(4, ITEMS[item]["price"] // 6)
        p["gold"] += gain
        add_exp(p, 12 + gain)
        bump(p, "fish_caught" if ITEMS[item]["type"] == "fish" else "fishing_loot")
        if item == "life_shard":
            bump(p, "life_shard")
        if item == "golden_fish":
            add_chat("系统", f"{p['name']} 钓到了黄金鱼，河边开始发光", sys=True)
        return respond_action(p, f"钓到 {ITEMS[item]['name']}，获得 {gain} 金币")

    if action == "work":
        if z["kind"] not in {"work", "villa"}:
            return respond_action(p, "这里没有老板，暂时不用上班", False)
        if t < p.get("nextWorkAt", 0):
            return respond_action(p, "刚打完工，先喘口气", False)
        job = payload.get("job")
        if z["kind"] == "villa":
            cost = 0
            if random.random() < .45:
                need = random.choice(["flower", "coffee"])
                if not remove_item(p, need, 1):
                    return respond_action(p, f"富婆任务需要 {ITEMS[need]['name']}，黑市能买", False)
                cost = ITEMS[need]["price"]
            reward = random.randint(110, 260) - cost
            p["gold"] += max(60, reward)
            add_exp(p, 55)
            bump(p, "villa_task")
            p["nextWorkAt"] = t + 7
            return respond_action(p, f"完成富婆跑腿，到账 {max(60, reward)} 金币")
        if job not in JOBS:
            job = "mason" if z["id"] == "site" else random.choice(list(JOBS))
        name, gold, exp = JOBS[job]
        if event.get("type") == "boss_gone":
            gold = max(1, gold // 2)
        if event.get("type") == "red_packet":
            gold += 18
        p["gold"] += gold
        add_exp(p, exp)
        bump(p, "work_count")
        if job == "brick":
            bump(p, "work_brick")
        if job == "cleaner":
            bump(p, "trash_clean")
        p["nextWorkAt"] = t + 5.5
        if p["counters"].get("work_count", 0) and p["counters"]["work_count"] % 12 == 0:
            p["status"]["back_pain_until"] = t + 70
            add_chat("系统", f"{p['name']} 打工太久获得腰肌劳损，移动变慢", sys=True)
        return respond_action(p, f"{name} 完成，获得 {gold} 金币")

    if action == "trash":
        if z["kind"] != "trash":
            return respond_action(p, "垃圾场才有垃圾，广场只有人生建议", False)
        if t < p.get("nextTrashAt", 0):
            return respond_action(p, "刚翻完一堆，下一堆正在刷新", False)
        p["nextTrashAt"] = t + 3
        item = random.choices(
            ["trash_bag", "old_shoe", "life_shard", "potion", "lucky_ring", "rich_wallet"],
            weights=[44, 24, 20, 8, 3, 1],
            k=1,
        )[0]
        add_item(p, item)
        gold = random.randint(3, 24)
        p["gold"] += gold
        add_exp(p, 16)
        bump(p, "trash_clean")
        if item == "life_shard":
            bump(p, "life_shard")
        return respond_action(p, f"捡到 {ITEMS[item]['name']} 和 {gold} 金币")

    if action == "sleep":
        if p["gold"] > 30:
            return respond_action(p, "有钱人暂时不能睡桥洞", False)
        p["hp"] = min(calc_stats(p)["hp"], p["hp"] + 45)
        p["status"]["sleep_until"] = t + 20
        add_exp(p, 6)
        bump(p, "failures")
        return respond_action(p, "桥洞睡醒，体力恢复，尊严稍微掉了一点")

    if action == "buy":
        item_id = payload.get("itemId")
        qty = max(1, min(20, int(payload.get("qty", 1) or 1)))
        item = ITEMS.get(item_id)
        if item_id not in SHOP or not item:
            return respond_action(p, "黑市老板说没这个货", False)
        cost = item["price"] * qty
        if p["gold"] < cost:
            return respond_action(p, "金币不够，老板的笑容消失了", False)
        p["gold"] -= cost
        add_item(p, item_id, qty)
        bump(p, "shopping")
        return respond_action(p, f"购买 {item['name']} x{qty}")

    if action == "sell":
        item_id = payload.get("itemId")
        qty = max(1, min(99, int(payload.get("qty", 1) or 1)))
        item = ITEMS.get(item_id)
        if not item or not remove_item(p, item_id, qty):
            return respond_action(p, "背包里没有这么多", False)
        money = max(1, int(item["price"] * .55)) * qty
        p["gold"] += money
        bump(p, "selling")
        return respond_action(p, f"卖出 {item['name']} x{qty}，获得 {money} 金币")

    if action == "equip":
        item_id = payload.get("itemId")
        item = ITEMS.get(item_id)
        if not item or p["inventory"].get(item_id, 0) <= 0:
            return respond_action(p, "装备不存在", False)
        typ = item["type"]
        if typ in ("weapon", "armor", "accessory"):
            p["equipment"][typ] = item_id
            p["hp"] = min(p["hp"], calc_stats(p)["hp"])
            return respond_action(p, f"已装备 {item['name']}")
        if typ == "mount":
            p["mount"] = True
            remove_item(p, item_id, 1)
            return respond_action(p, "坐骑月卡生效，跑路更像上班了")
        if typ == "pet":
            remove_item(p, item_id, 1)
            pet = dict(random.choice(PETS))
            pet["level"] = 1
            p["pet"] = pet
            return respond_action(p, f"宠物蛋孵化：{pet['name']} 跟随你")
        return respond_action(p, "这个东西不能装备", False)

    if action == "use":
        item_id = payload.get("itemId")
        if item_id != "potion" or not remove_item(p, "potion", 1):
            return respond_action(p, "没有可用药水", False)
        p["hp"] = min(calc_stats(p)["hp"], p["hp"] + 70)
        return respond_action(p, "喝下药水，血量恢复")

    if action == "bank":
        mode = payload.get("mode")
        amount = int(payload.get("amount", 0) or 0)
        amount = max(1, min(999999, amount))
        if mode == "deposit":
            amount = min(amount, p["gold"])
            p["gold"] -= amount
            p["bank"] += amount
            return respond_action(p, f"存入银行 {amount} 金币")
        if mode == "withdraw":
            amount = min(amount, p["bank"])
            p["bank"] -= amount
            p["gold"] += amount
            return respond_action(p, f"取出 {amount} 金币")
        return respond_action(p, "银行业务办不了", False)

    if action == "stall_create":
        item_id = payload.get("itemId")
        qty = max(1, min(99, int(payload.get("qty", 1) or 1)))
        price = max(1, min(99999, int(payload.get("price", 1) or 1)))
        if item_id not in ITEMS or not remove_item(p, item_id, qty):
            return respond_action(p, "摆摊失败，库存不够", False)
        sid = uuid.uuid4().hex[:8]
        stalls[sid] = {"id": sid, "sellerId": p["id"], "seller": p["name"], "itemId": item_id, "qty": qty, "price": price, "createdAt": t}
        bump(p, "stall")
        return respond_action(p, f"已摆摊出售 {ITEMS[item_id]['name']} x{qty}")

    if action == "stall_buy":
        sid = payload.get("stallId")
        stall = stalls.get(sid)
        if not stall:
            return respond_action(p, "摊位已经收了", False)
        if stall["sellerId"] == p["id"]:
            return respond_action(p, "不能买自己的摊，金融闭环失败", False)
        if p["gold"] < stall["price"]:
            return respond_action(p, "金币不够", False)
        seller = players.get(stall["sellerId"])
        p["gold"] -= stall["price"]
        add_item(p, stall["itemId"], stall["qty"])
        if seller:
            seller["gold"] += stall["price"]
            seller["bubble"], seller["bubbleAt"] = "摊位成交", t
        stalls.pop(sid, None)
        return respond_action(p, f"买下 {ITEMS[stall['itemId']]['name']} x{stall['qty']}")

    if action == "stall_cancel":
        sid = payload.get("stallId")
        stall = stalls.get(sid)
        if not stall or stall["sellerId"] != p["id"]:
            return respond_action(p, "这不是你的摊位", False)
        stalls.pop(sid, None)
        add_item(p, stall["itemId"], stall["qty"])
        return respond_action(p, "摊位已收回")

    if action == "attack":
        if z.get("safe"):
            return respond_action(p, "安全区不能攻击，去野外打怪或 PK", False)
        if t < p.get("nextAttackAt", 0):
            return respond_action(p, "攻击冷却中", False)

        monster_id = payload.get("monsterId")
        target_id = payload.get("targetId")
        mon = None
        # 明确指定怪物，或未指定玩家时自动锁最近怪
        if monster_id:
            mon = monsters.get(monster_id)
            if not mon or mon.get("hp", 0) <= 0 or mon.get("dead"):
                return respond_action(p, "怪物已经消失", False)
        elif not target_id:
            best = 110
            for m in monsters.values():
                if m.get("hp", 0) <= 0 or m.get("dead"):
                    continue
                d = ((m["x"] - p["x"]) ** 2 + (m["y"] - p["y"]) ** 2) ** 0.5
                if d < best:
                    best, mon = d, m

        if mon and mon.get("hp", 0) > 0 and not mon.get("dead"):
            if ((mon["x"] - p["x"]) ** 2 + (mon["y"] - p["y"]) ** 2) ** 0.5 > 100:
                return respond_action(p, "离怪物太远，靠近再砍", False)
            p["nextAttackAt"] = t + 0.85
            ps = calc_stats(p)
            crit = random.randint(1, 100) <= ps["crit"]
            dmg = max(1, int(ps["attack"] * (1.85 if crit else 1) - mon["defense"] * 0.4 + random.randint(0, 8)))
            mon["hp"] = max(0, mon["hp"] - dmg)
            mon["bubble"], mon["bubbleAt"] = f"-{dmg}", t
            mon["targetId"] = p["id"]  # 仇恨
            p["bubble"], p["bubbleAt"] = ("暴击!" if crit else "斩!"), t
            msg = f"攻击 {mon['name']} 造成 {dmg} 伤害" + ("，暴击" if crit else "")
            if mon["hp"] <= 0:
                gold, exp_g, drop_txt = kill_monster(mon, p)
                msg = f"击败 {mon['name']}！+{gold} 金币 +{exp_g} 经验{drop_txt}"
            return respond_action(p, msg, monsterId=mon["id"])

        target = players.get(target_id) if target_id else None
        if not target or target_id == p["id"]:
            return respond_action(p, "附近没有怪物或玩家可攻击", False)
        if zone_at(target["x"], target["y"]).get("safe"):
            return respond_action(p, "目标在安全区", False)
        if target.get("hp", 0) <= 0:
            return respond_action(p, "目标已经是灵魂状态", False)
        if ((target["x"] - p["x"]) ** 2 + (target["y"] - p["y"]) ** 2) ** .5 > 95:
            return respond_action(p, "离目标太远", False)
        p["nextAttackAt"] = t + 1.05
        ps, ts = calc_stats(p), calc_stats(target)
        crit = random.randint(1, 100) <= ps["crit"]
        dmg = max(1, int(ps["attack"] * (1.8 if crit else 1) - ts["defense"] * .45 + random.randint(0, 7)))
        target["hp"] = max(0, target["hp"] - dmg)
        target["bubble"], target["bubbleAt"] = f"-{dmg}", t
        add_exp(p, 8)
        msg = f"攻击 {target['name']} 造成 {dmg} 伤害" + ("，暴击" if crit else "")
        if target["hp"] <= 0:
            target["deadUntil"] = t + 7
            target["counters"]["deaths"] = target["counters"].get("deaths", 0) + 1
            bump(p, "pk_kill")
            steal_rate = .22 + min(.38, target.get("red", 0) * .08)
            stolen = min(target["gold"], max(12, int(target["gold"] * steal_rate)))
            target["gold"] -= stolen
            p["gold"] += stolen
            add_exp(p, 75)
            if target.get("red", 0) <= 0:
                p["red"] = p.get("red", 0) + 1
                p["redUntil"] = t + 180
            epitaph = random.choice(["早知道不出安全区", "下辈子少打工", "金币乃身外之物但我没有了", "这把算网卡"])
            target["bubble"], target["bubbleAt"] = epitaph, t
            add_chat("墓碑", f"{target['name']} 的遗言：{epitaph}", sys=True)
            msg += f"，击败目标并获得 {stolen} 金币"
        return respond_action(p, msg)

    if action == "boss":
        if event.get("type") != "world_boss" or z["id"] != "wild":
            return respond_action(p, "现在没有世界 Boss 可打", False)
        dmg = max(5, calc_stats(p)["attack"] + random.randint(0, 25))
        event["bossHp"] = max(0, event.get("bossHp", 0) - dmg)
        p["hp"] = max(1, p["hp"] - random.randint(2, 12))
        add_exp(p, 25)
        reward = 28
        if event["bossHp"] <= 0:
            reward = 260
            event["endsAt"] = 0
            add_chat("系统", f"{p['name']} 终结了加班魔王，全服松了一口气", sys=True)
        p["gold"] += reward
        bump(p, "boss")
        return respond_action(p, f"对 Boss 造成 {dmg} 伤害，获得 {reward} 金币")

    if action == "emote":
        text = payload.get("text") if payload.get("text") in ["挥手", "跳舞", "躺平", "磕头", "装死", "比心"] else "挥手"
        p["bubble"], p["bubbleAt"] = text, t
        bump(p, "emote")
        return respond_action(p, text)

    if action == "social":
        target_id = payload.get("targetId")
        target = players.get(target_id)
        mode = payload.get("mode")
        if not target or target_id == p["id"]:
            return respond_action(p, "没找到这个玩家", False)
        if mode == "friend":
            p["friends"].add(target_id)
            target["friends"].add(p["id"])
            return respond_action(p, f"已和 {target['name']} 成为好友")
        if mode == "team":
            p["team"].add(target_id)
            target["team"].add(p["id"])
            return respond_action(p, f"已和 {target['name']} 组队")
        return respond_action(p, "社交动作失败", False)

    if action == "guild":
        # 兼容旧接口：有部落则改部落名（仅酋长），否则创建同名部落
        name = clean_text(payload.get("name"), 12)
        if not name:
            return respond_action(p, "名字不能为空", False)
        if p.get("tribeId") and p.get("tribeId") in tribes:
            if p.get("tribeRole") != "leader":
                return respond_action(p, "只有酋长能改部落名", False)
            tribes[p["tribeId"]]["name"] = name
            for mid in tribes[p["tribeId"]]["members"]:
                if mid in players:
                    players[mid]["guild"] = name
            return respond_action(p, f"部落更名为 {name}")
        return handle_action(p, {"type": "tribe", "payload": {"mode": "create", "name": name}})

    if action == "romance":
        bid = payload.get("beautyId") or payload.get("id")
        mode = payload.get("mode") or "greet"
        b = BEAUTIES.get(bid)
        if not b:
            return respond_action(p, "这位佳人尚未登场", False)
        # 需靠近美女
        if ((p["x"] - b["x"]) ** 2 + (p["y"] - b["y"]) ** 2) ** 0.5 > 140:
            return respond_action(p, f"离 {b['name']} 太远，先去 {zone_by_id(b['zone'])['name'] if zone_by_id(b['zone']) else b['zone']} 找她", False)
        if mode != "baby" and t < p.get("nextRomanceAt", 0):
            return respond_action(p, "心还在怦怦跳，稍后再互动", False)

        if mode == "greet":
            p["nextRomanceAt"] = t + 2.2
            gain = random.randint(3, 7)
            val = add_affection(p, bid, gain)
            p["bubble"], p["bubbleAt"] = f"搭讪 {b['name']}", t
            bump(p, "romance_greet")
            lines = [b["line"], "嗯？你是谁？", "先证明你不是海王。", "有趣，继续。"]
            return respond_action(p, f"向 {b['name']} 搭讪：{random.choice(lines)} 好感 +{gain}（{val}/100）")

        if mode == "gift":
            item_id = payload.get("itemId") or b["prefer"]
            if item_id not in ITEMS:
                return respond_action(p, "礼物不存在", False)
            # 自动选背包里可用的礼物
            gift_ids = ["flower", "coffee", "lipstick", "perfume", "ring_box"]
            if p["inventory"].get(item_id, 0) <= 0:
                for gid in gift_ids:
                    if p["inventory"].get(gid, 0) > 0:
                        item_id = gid
                        break
            if not remove_item(p, item_id, 1):
                return respond_action(p, f"没有礼物。先去商店买 {ITEMS[b['prefer']]['name']} 等", False)
            p["nextRomanceAt"] = t + 2.8
            prefer_bonus = 12 if item_id == b["prefer"] else 0
            quality = {"普通": 4, "优秀": 7, "稀有": 11, "史诗": 16, "传说": 22, "破烂但有故事": 3}.get(ITEMS[item_id].get("quality"), 5)
            gain = quality + prefer_bonus + random.randint(0, 4)
            val = add_affection(p, bid, gain)
            bump(p, "romance_gift")
            tip = "（她的最爱！）" if prefer_bonus else ""
            p["bubble"], p["bubbleAt"] = f"送礼 {ITEMS[item_id]['name']}", t
            return respond_action(p, f"送给 {b['name']} {ITEMS[item_id]['name']}{tip}，好感 +{gain}（{val}/100）")

        if mode == "date":
            cost = 40
            if p["gold"] < cost:
                return respond_action(p, "约会至少要 40 金币，先去打工", False)
            aff = int((p.get("affection") or {}).get(bid, 0))
            if aff < 25:
                return respond_action(p, f"{b['name']} 还不熟，好感至少 25（当前 {aff}）", False)
            p["gold"] -= cost
            p["nextRomanceAt"] = t + 4.5
            gain = random.randint(10, 18)
            if random.random() < 0.12:
                gain = -random.randint(4, 9)
                p["status"]["heartbreak_until"] = t + 45
                val = add_affection(p, bid, gain)
                bump(p, "failures")
                return respond_action(p, f"约会翻车：被 {b['name']} 放了鸽子，好感 {gain}（{val}/100）", False)
            val = add_affection(p, bid, gain)
            bump(p, "romance_date")
            add_exp(p, 20)
            scenes = ["看夕阳", "黑市逛街", "河边吹风", "别墅喝下午茶", "洞府装深沉"]
            p["bubble"], p["bubbleAt"] = f"约会中·{random.choice(scenes)}", t
            return respond_action(p, f"和 {b['name']} 约会成功，好感 +{gain}（{val}/100），花费 {cost} 金币")

        if mode == "confess":
            aff = int((p.get("affection") or {}).get(bid, 0))
            if aff < 70:
                return respond_action(p, f"告白失败阈值高：好感需 ≥70（当前 {aff}）", False)
            if p.get("partnerId") and p.get("partnerId") != bid:
                old = BEAUTIES.get(p["partnerId"], {}).get("name", "前任")
                return respond_action(p, f"你已有伴侣 {old}，先专一一点（或等她跑了）", False)
            p["nextRomanceAt"] = t + 5
            ring_bonus = 0
            if p["inventory"].get("ring_box", 0) > 0 and remove_item(p, "ring_box", 1):
                ring_bonus = 18
            chance = min(92, 45 + aff // 2 + ring_bonus)
            if random.randint(1, 100) > chance:
                add_affection(p, bid, -8)
                p["status"]["heartbreak_until"] = t + 60
                bump(p, "failures")
                return respond_action(p, f"{b['name']} 拒绝了你：「我们还是做朋友吧。」好感 -8", False)
            p["partnerId"] = bid
            add_affection(p, bid, 10)
            bump(p, "romance_partner")
            p["titles"].add("名草有主")
            p["bubble"], p["bubbleAt"] = f"♥ {b['name']}", t
            add_chat("系统", f"{p['name']} 向 {b['name']} 告白成功，修成正果！", sys=True)
            return respond_action(p, f"告白成功！你与 {b['name']} 成为伴侣（成功率 {chance}%）")

        if mode == "breakup":
            if p.get("partnerId") != bid:
                return respond_action(p, "你们还不是伴侣", False)
            p["partnerId"] = ""
            add_affection(p, bid, -20)
            p["status"]["heartbreak_until"] = t + 90
            bump(p, "failures")
            return respond_action(p, f"你和 {b['name']} 和平分手了（并不和平）")

        if mode == "baby":
            if p.get("partnerId") != bid:
                return respond_action(p, f"只有伴侣才能生孩子。先和 {b['name']} 告白成功", False)
            if len(p.get("children") or []) >= 3:
                return respond_action(p, "最多带 3 个孩子，再多养不起", False)
            if t < p.get("nextBabyAt", 0):
                return respond_action(p, "刚经历人生大事，休息一会儿再考虑", False)
            cost = 120
            if p["gold"] < cost:
                return respond_action(p, f"生孩子仪式费 {cost} 金币，钱包不允许", False)
            # 可选消耗奶粉
            milk_bonus = False
            if p["inventory"].get("baby_milk", 0) > 0 and remove_item(p, "baby_milk", 1):
                milk_bonus = True
            p["gold"] -= cost
            p["nextBabyAt"] = t + 30
            trait = dict(random.choice(CHILD_TRAITS))
            gender = random.choice(["男", "女"])
            cname = random.choice(CHILD_NAMES_F if gender == "女" else CHILD_NAMES_M)
            if milk_bonus:
                for k in ("hp", "attack", "defense", "speed", "crit", "luck"):
                    if k in trait:
                        trait[k] = int(trait[k] * 1.4) + 1
            child = {
                "id": uuid.uuid4().hex[:8],
                "name": cname,
                "gender": gender,
                "mother": b["name"],
                "motherId": bid,
                "trait": trait.get("name", "普通"),
                "level": 1,
                "hp": trait.get("hp", 0),
                "attack": trait.get("attack", 0),
                "defense": trait.get("defense", 0),
                "speed": trait.get("speed", 0),
                "crit": trait.get("crit", 0),
                "luck": trait.get("luck", 0),
                "bornAt": t,
            }
            p.setdefault("children", []).append(child)
            bump(p, "baby_born")
            add_exp(p, 50)
            p["titles"].add("奶爸/奶妈预备役")
            p["bubble"], p["bubbleAt"] = f"喜得爱子 {cname}", t
            add_chat("系统", f"{p['name']} 与 {b['name']} 喜得爱子「{cname}」·{trait.get('name')}！", sys=True)
            return respond_action(p, f"恭喜！{b['name']} 为你生下 {gender}孩「{cname}」·{trait.get('name')}（-{cost} 金币）")

        return respond_action(p, "未知恋爱动作：greet/gift/date/confess/baby", False)

    if action == "tribe":
        mode = payload.get("mode") or "list"
        if mode == "create":
            if p.get("tribeId"):
                return respond_action(p, "你已在部落中，先退出再创建", False)
            name = clean_text(payload.get("name"), 12)
            if not name:
                return respond_action(p, "部落名不能为空", False)
            if any(t.get("name") == name for t in tribes.values()):
                return respond_action(p, "部落名已被占用", False)
            cost = 100
            if p["gold"] < cost:
                return respond_action(p, f"创建部落需要 {cost} 金币", False)
            p["gold"] -= cost
            tid = uuid.uuid4().hex[:8]
            tribes[tid] = {
                "id": tid, "name": name, "leaderId": p["id"], "leaderName": p["name"],
                "members": {p["id"]}, "level": 1, "exp": 0, "notice": "新部落，求抱团发财",
                "createdAt": t, "color": p.get("color", "cyan"), "fund": 0,
            }
            p["tribeId"] = tid
            p["tribeRole"] = "leader"
            p["guild"] = name
            bump(p, "tribe_join")
            add_chat("部落", f"{p['name']} 创建了部落「{name}」", sys=True)
            return respond_action(p, f"部落「{name}」创建成功，你是酋长")

        if mode == "join":
            if p.get("tribeId"):
                return respond_action(p, "你已有部落", False)
            tid = payload.get("tribeId")
            tobj = tribes.get(tid)
            if not tobj:
                # 按名字加入
                name = clean_text(payload.get("name"), 12)
                tobj = next((x for x in tribes.values() if x["name"] == name), None)
            if not tobj:
                return respond_action(p, "部落不存在", False)
            if len(tobj.get("members") or []) >= 20:
                return respond_action(p, "部落人满了（上限 20）", False)
            tobj["members"].add(p["id"])
            p["tribeId"] = tobj["id"]
            p["tribeRole"] = "member"
            p["guild"] = tobj["name"]
            bump(p, "tribe_join")
            tribe_add_exp(tobj, 8)
            return respond_action(p, f"加入部落「{tobj['name']}」成功")

        if mode == "leave":
            if not p.get("tribeId"):
                return respond_action(p, "你不在任何部落", False)
            name = tribes.get(p["tribeId"], {}).get("name", "")
            leave_tribe_silent(p)
            return respond_action(p, f"已离开部落「{name}」")

        if mode == "donate":
            tid = p.get("tribeId")
            tobj = tribes.get(tid)
            if not tobj:
                return respond_action(p, "先加入部落再捐献", False)
            amount = max(10, min(5000, int(payload.get("amount", 50) or 50)))
            if p["gold"] < amount:
                return respond_action(p, "金币不够", False)
            p["gold"] -= amount
            tobj["fund"] = int(tobj.get("fund", 0)) + amount
            tribe_add_exp(tobj, max(1, amount // 20))
            bump(p, "tribe_donate")
            add_exp(p, max(5, amount // 25))
            return respond_action(p, f"向部落捐献 {amount} 金币，当前金库 {tobj['fund']}")

        if mode == "notice":
            tid = p.get("tribeId")
            tobj = tribes.get(tid)
            if not tobj or p.get("tribeRole") != "leader":
                return respond_action(p, "只有酋长能改公告", False)
            notice = clean_text(payload.get("notice"), 60)
            tobj["notice"] = notice
            return respond_action(p, f"部落公告已更新：{notice}")

        if mode == "kick":
            tid = p.get("tribeId")
            tobj = tribes.get(tid)
            if not tobj or p.get("tribeRole") != "leader":
                return respond_action(p, "只有酋长能踢人", False)
            target_id = payload.get("targetId")
            if target_id == p["id"]:
                return respond_action(p, "不能踢自己，请用退出", False)
            if target_id not in tobj.get("members", set()):
                return respond_action(p, "对方不在部落", False)
            tobj["members"].discard(target_id)
            if target_id in players:
                players[target_id]["tribeId"] = ""
                players[target_id]["tribeRole"] = ""
                players[target_id]["guild"] = ""
            return respond_action(p, "已将成员移出部落")

        return respond_action(p, "部落指令：create/join/leave/donate/notice/kick", False)

    if action == "title":
        title = payload.get("title")
        if title in p["titles"]:
            p["title"] = title
            return respond_action(p, f"称号切换为 {title}")
        return respond_action(p, "称号还没解锁", False)

    if action == "claim":
        qid = payload.get("questId")
        q = QUESTS.get(qid)
        if not q:
            return respond_action(p, "任务不存在", False)
        if qid in p["claimed"]:
            return respond_action(p, "任务已经领过奖励", False)
        key, need = q["need"]
        if p["counters"].get(key, 0) < need:
            return respond_action(p, "任务进度还不够", False)
        p["claimed"].add(qid)
        p["gold"] += q["gold"]
        add_exp(p, q["exp"])
        return respond_action(p, f"领取 {q['name']}：{q['gold']} 金币")

    return respond_action(p, "未知互动", False)


class Handler(BaseHTTPRequestHandler):
    server_version = "OpenWorldH5/1.0"

    def log_message(self, fmt, *args):
        return

    def send_json(self, data, code=200):
        raw = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def read_json(self):
        n = int(self.headers.get("Content-Length", "0") or 0)
        if n > 8192:
            n = 8192
        raw = self.rfile.read(n) if n else b"{}"
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return {}

    def do_GET(self):
        cleanup()
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/" or path == "/index.html":
            fp = os.path.join(ROOT, "index.html")
            data = open(fp, "rb").read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        if path == "/state":
            qs = parse_qs(parsed.query)
            pid = (qs.get("id") or [""])[0]
            me = players.get(pid)
            self.send_json({
                "ok": True,
                "time": now(),
                "world": {"w": WORLD_W, "h": WORLD_H, "zones": ZONES},
                "players": [public_player(p) for p in players.values()],
                "monsters": [public_monster(m) for m in monsters.values() if m.get("hp", 0) > 0 and not m.get("dead")],
                "beauties": [public_beauty(b, me) for b in BEAUTIES.values()],
                "tribes": [public_tribe(t) for t in tribes.values()],
                "me": full_player(me) if me else None,
                "chat": chat[-70:],
                "items": ITEMS,
                "shop": SHOP,
                "quests": QUESTS,
                "stalls": list(stalls.values()),
                "rankings": rankings(),
                "event": event,
            })
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        cleanup()
        path = urlparse(self.path).path
        data = self.read_json()
        if path == "/join":
            pid = uuid.uuid4().hex[:10]
            name = clean_text(data.get("name"), 14) or "无名玩家"
            color = data.get("color") if data.get("color") in COLORS else "cyan"
            style = data.get("style") if data.get("style") in STYLES else "wanderer"
            x, y = random.choice(SPAWNS)
            p = default_player(pid, name, color, style, x + random.randint(-45, 45), y + random.randint(-45, 45))
            players[pid] = p
            add_chat("系统", f"{name} 进入游戏人生广场", sys=True)
            self.send_json({"ok": True, "id": pid, "player": full_player(p), "world": {"w": WORLD_W, "h": WORLD_H, "zones": ZONES}})
            return
        if path == "/update":
            pid = data.get("id")
            p = players.get(pid)
            if not p:
                self.send_json({"ok": False, "error": "not_joined"}, 404)
                return
            if p.get("hp", 0) > 0:
                old_x, old_y = p["x"], p["y"]
                p["x"] = clamp(data.get("x", p["x"]), 24, WORLD_W - 24)
                p["y"] = clamp(data.get("y", p["y"]), 24, WORLD_H - 24)
                d = data.get("dir")
                if d in {"up", "down", "left", "right"}:
                    p["dir"] = d
                dist = ((p["x"] - old_x) ** 2 + (p["y"] - old_y) ** 2) ** .5
                if dist > 4 and now() - p.get("lastMoveXp", 0) > 2.2:
                    add_exp(p, 2)
                    bump(p, "move")
                    p["lastMoveXp"] = now()
            z = zone_at(p["x"], p["y"])
            if z["kind"] == "train" and now() - p.get("lastTrainAt", 0) > 1.4 and p.get("hp", 0) > 0:
                gain = 4
                if time.localtime().tm_hour >= 23 or time.localtime().tm_hour <= 5:
                    gain = 7
                    p["hp"] = max(1, p["hp"] - 2)
                p["cultivation"] += gain
                add_exp(p, 2)
                bump(p, "train")
                p["lastTrainAt"] = now()
            if event.get("type") == "rich_pass" and z["id"] == "villa" and random.random() < .04:
                p["gold"] += 30
                p["bubble"], p["bubbleAt"] = "富婆转账 +30", now()
            p["last"] = now()
            update_titles(p)
            self.send_json({"ok": True})
            return
        if path == "/say":
            pid = data.get("id")
            p = players.get(pid)
            if not p:
                self.send_json({"ok": False, "error": "not_joined"}, 404)
                return
            text = clean_text(data.get("text"), 80)
            if text:
                p["bubble"] = text
                p["bubbleAt"] = now()
                p["last"] = now()
                add_exp(p, 5)
                bump(p, "chat_count")
                add_chat(p["name"], text, id=pid, style=p["style"], color=p["color"])
            self.send_json({"ok": True})
            return
        if path == "/action":
            pid = data.get("id")
            p = players.get(pid)
            if not p:
                self.send_json({"ok": False, "error": "not_joined"}, 404)
                return
            p["last"] = now()
            self.send_json(handle_action(p, data))
            return
        if path == "/leave":
            pid = data.get("id")
            p = players.pop(pid, None)
            if p:
                add_chat("系统", f"{p['name']} 离开了广场", sys=True)
            self.send_json({"ok": True})
            return
        self.send_json({"ok": False, "error": "not_found"}, 404)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "80"))
    print(f"OpenWorldH5 listening on 0.0.0.0:{port}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
