# tg-jav-bot

**一个万能 Telegram 番号查询机器人。基于 Javbus，Sukebei，Avgle，Dmm，Javlibrary，维基百科，谷歌翻译等进行构建，集成了 Pikpak 作为磁链保存网盘。**

该项目持续更新，如果发现代码有问题（特别是爬虫失效了）或者功能需要完善、需要其它新的功能等，欢迎提 issue 或者参与到本项目中~ 如果有其它问题，可以通过邮箱 [akynazh@qq.com](mailto://akynazh@qq.com) 或电报 [@jackbryant286](https://t.me/jackbryant286) 联系我。

## 功能简介

**主要功能：**

发送给机器人一条含有番号的消息，机器人会匹配并通过 Javbus 和 Sukebei 搜索消息中所有符合“字母-数字”格式的番号（其它格式的番号可通过 /av 命令查找）。如果搜索到结果，将返回番号对应 AV 的封面，标题，日期，演员，磁链等。

**附加功能：**

- 支持收藏演员和番号
- 支持过滤磁链（过滤顺序：无码，高清，有字幕）
- 支持配置代理
- 支持通过 Javbus 获取影片截图
- 支持通过 Javbus 获取演员最新 AV，随机获取演员 AV
- 支持让机器人自动将最优磁链发送到 Pikpak（随机获取时不会自动发送）
- 支持通过 Dmm 获取预览视频，女优排行榜，AV 评分 （由于 DMM 限制，只支持日本 IP）
- 支持通过 Avgle 获取预览视频和完整视频
- 支持通过 Javlibrary 各种排行榜随机获取番号
- 支持通过维基百科获取演员中文名
- 支持通过谷歌翻译日文标题
- 支持通过 Javbus 和维基百科以日文或中文搜索演员（演员名称需要和维基对应词条一致）

注：记录和日志等文件生成位置在 `~/.tg_jav_bot` 目录下。

**机器人指令：**

- /help  查看指令帮助
- /star  后接演员名称可搜索该演员
- /av  后接番号可搜索该番号
- /stars  查看收藏的演员
- /avs  查看收藏的番号
- /nice  随机获取一部高分 AV
- /new  随机获取一部最新 AV
- /rank  获取 DMM 女优排行榜
- /record  获取收藏记录文件

**部分结果展示：**

![部分结果展示](res.png)

## 使用教程

### 配置机器人

将 `cfg.pub.py` 重命名为 `cfg.py` 并根据文件中的提示编辑即可。

如需使用 Pikpak 自动发送功能，需要先手动授权 [Pikpak 官方机器人](https://t.me/PikPak6_Bot)，然后通过命令 `python3 utils/util_pikpak.py` 完成登录操作即可（Python >= 3.7）。

### 运行机器人

**通过 docker 运行：**

```
docker-compose up -d
```

**或通过普通方法运行：**

```
# Python >=3.7
pip install -r requirements.txt
python3 bot.py
```