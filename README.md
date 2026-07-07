# 游戏人生 Online - 开放世界聊天室

一个零依赖 Python + H5 小游戏：选择昵称/外貌/身份，开放世界移动，多人在线，头顶气泡发言，右侧聊天区。

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
- `POST /leave` 离开
