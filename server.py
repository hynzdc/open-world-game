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
chat = []
stalls = {}
event = {}

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
}

SHOP = ["wood_stick", "cleaver", "brick", "shovel", "fishing_staff", "sword", "staff", "vest", "helmet",
        "cleaner_vest", "black_armor", "lucky_ring", "work_necklace", "rich_wallet", "bamboo_rod",
        "alloy_rod", "potion", "mount", "flower", "coffee"]

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
    "rich": {"name": "富婆任务", "desc": "完成 3 次跑腿", "need": ("villa_task", 3), "gold": 260, "exp": 120},
    "daily": {"name": "每日任务", "desc": "完成 6 次任意互动", "need": ("daily_actions", 6), "gold": 160, "exp": 100},
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
    status = p.get("status", {})
    if status.get("back_pain_until", 0) > now():
        stats["speed"] = max(2, stats["speed"] - 3)
    return stats


def public_player(p):
    stats = calc_stats(p)
    return {
        "id": p["id"], "name": p["name"], "color": p["color"], "style": p["style"],
        "x": p["x"], "y": p["y"], "dir": p["dir"], "bubble": p.get("bubble", ""),
        "bubbleAt": p.get("bubbleAt", 0), "level": p["level"], "realm": realm_name(p["cultivation"]),
        "hp": p["hp"], "maxHp": stats["hp"], "title": p.get("title", "修仙废柴"),
        "red": p.get("red", 0), "deadUntil": p.get("deadUntil", 0), "power": power_of(p),
        "pet": p.get("pet", {}).get("name") if p.get("pet") else "",
    }


def full_player(p):
    data = public_player(p)
    data.update({
        "exp": p["exp"], "gold": p["gold"], "bank": p["bank"], "cultivation": p["cultivation"],
        "stats": calc_stats(p), "inventory": p["inventory"], "equipment": p["equipment"],
        "titles": sorted(p["titles"]), "counters": p["counters"], "claimed": sorted(p["claimed"]),
        "zone": zone_at(p["x"], p["y"]), "friends": sorted(p["friends"]), "guild": p.get("guild", ""),
        "team": sorted(p["team"]), "petObj": p.get("pet"), "status": p.get("status", {}),
        "daily": p.get("daily", today()), "nextWorkAt": p.get("nextWorkAt", 0), "nextFishAt": p.get("nextFishAt", 0),
        "nextTrashAt": p.get("nextTrashAt", 0), "nextAttackAt": p.get("nextAttackAt", 0),
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
            add_chat("系统", f"{p['name']} 下线了，世界少了一份工资", sys=True)
    if len(chat) > 100:
        del chat[:-100]


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
            return respond_action(p, "安全区不能攻击", False)
        target_id = payload.get("targetId")
        target = players.get(target_id)
        if not target or target_id == p["id"]:
            return respond_action(p, "没有可攻击目标", False)
        if zone_at(target["x"], target["y"]).get("safe"):
            return respond_action(p, "目标在安全区", False)
        if target.get("hp", 0) <= 0:
            return respond_action(p, "目标已经是灵魂状态", False)
        if ((target["x"] - p["x"]) ** 2 + (target["y"] - p["y"]) ** 2) ** .5 > 95:
            return respond_action(p, "离目标太远", False)
        if t < p.get("nextAttackAt", 0):
            return respond_action(p, "攻击冷却中", False)
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
        name = clean_text(payload.get("name"), 12)
        p["guild"] = name
        return respond_action(p, f"帮派设置为 {name or '无'}")

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
