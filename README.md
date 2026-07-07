# 游戏人生 Online - 开放世界聊天室

一个零依赖 Python + H5 小游戏：选择昵称/外貌/身份，开放世界移动，多人在线，头顶气泡发言，右侧聊天区。

现在已经扩展成“修仙打工开放世界”玩法：

- 角色成长：等级、经验、修为、境界、属性、称号。
- 经济系统：金币、商店、背包、装备、摆摊、银行、打工。
- 地图玩法：新手广场、打工街、河边、垃圾场、工地、黑市、野外荒地、修炼洞府、富婆别墅区。
- 互动玩法：钓鱼、捡垃圾、PK、死亡灵魂状态、红名、任务、好友、组队、帮派、表情气泡。
- 扩展系统：随机世界事件、排行榜、宠物、黑色幽默状态和奖励。

## 运行环境

- Python 3.8+
- 不需要安装第三方依赖

## 本地运行

```bash
cd open-world-game
python3 server.py
```

默认监听 `0.0.0.0:80`。

如果不是 root 用户或 80 端口不可用：

```bash
PORT=8080 python3 server.py
```

然后访问：

```text
http://服务器IP:8080/
```

## 后台运行

```bash
cd open-world-game
nohup python3 server.py > game.log 2>&1 &
echo $! > game.pid
```

8080 端口示例：

```bash
cd open-world-game
nohup env PORT=8080 python3 server.py > game.log 2>&1 &
echo $! > game.pid
```

## 停止服务

```bash
kill $(cat game.pid)
```

## 文件说明

- `index.html`：前端页面和游戏逻辑
- `server.py`：Python 标准库 HTTP 服务，提供页面、玩家状态、聊天接口
- `README.md`：部署说明

## 主要接口

- `GET /` 页面
- `GET /state` 获取世界状态
- `POST /join` 加入游戏
- `POST /update` 更新坐标
- `POST /say` 发言
- `POST /action` 执行钓鱼、打工、交易、战斗等互动
- `POST /leave` 离开
