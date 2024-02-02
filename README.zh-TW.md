# tg 搜索機器人

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->

[![All Contributors](https://img.shields.io/badge/all_contributors-4-orange.svg?style=flat-square)](#contributors-)

<!-- ALL-CONTRIBUTORS-BADGE:END -->

**一個可用於搜尋各種影片磁鏈的電報機器人, 支援收藏, 匯出記錄, 自動儲存磁鍊等操作, 可手動設定以屏蔽 NSFW 內容和代理程式上網。**

機器人基於 Python3 建置, 支援 Docker 一鍵部署, 並透過 Redis 實現了快取功能。

## 功能簡介

以下功能依開發完成時間排序，後續有新功能將持續補充。

-   支援獲取影片基本資訊和磁鏈 - 2022/11/25
-   支援配置代理 - 2022/11/26
-   支援過濾磁鏈 (uncensored => hd => subtitle)- 2022/11/26
-   支援讓機器人自動將最優磁鏈保存到 Pikpak - 2022/12/29
-   支援取得預覽影片和完整影片 - 2022/12/31
-   支援取得影片截圖 - 2023/01/01
-   支持收藏演員和影片 - 2023/01/04
-   支援透過 docker 部署 - 2023/01/08
-   支援取得演員排行榜，影片評分 - 2023/01/20
-   支援隨機獲取高分影片和最新影片 - 2023/01/25
-   支持透過維基百科取得演員中文名 - 2023/02/18
-   支援翻譯日文標題 - 2023/02/18
-   支援搜尋演員 - 2023/02/18
-   支援透過 redis 進行快取 - 2023/03/17

## 使用教程

首先需要下載本專案代碼到本地，然後配置機器人，編輯`~/.tg_search_bot/config.yaml`：

```yaml
# TG 对话 ID
tg_chat_id:
# TG 机器人 Token
tg_bot_token:
# 全局是否使用代理 1 是 | 0 否
use_proxy:
# 访问 dmm 时是否使用代理，如果全局使用代理，则忽略该字段 1 是 | 0 否
use_proxy_dmm:
# 代理服务器地址，如果不使用代理，则忽略该字段
proxy_addr:
# 是否使用 Pikpak 自动发送功能 1 是 | 0 否
use_pikpak:
# 配置 TG API，如果不使用 Pikpak 自动发送功能，则忽略以下两个字段，可在这里申请 API: https://my.telegram.org/apps
tg_api_id:
tg_api_hash:
# 是否使用缓存 1 是 | 0 否
use_cache:
# redis 地址，如果不使用缓存，则忽略以下两个字段
redis_host:
redis_port:
# nsfw 1 是 | 0 否
enable_nsfw: 0
```

PS: 如需使用 Pikpak 自動傳送功能，需先手動授權[Pikpak 官方機器人](https://t.me/PikPak6_Bot)，然後在初次運行機器人時進行登入操作。 (我的 Pikpak 邀請碼: 99492001, 輸入可得會員)

最後運行機器人即可：(記錄和日誌等文件位於`~/.tg_search_bot`目錄下)

```sh
# 方法一: 通过 docker 运行：(推荐)
docker-compose up -d
# 方法二: 通过普通方法运行:（Python >=3.10, 如果使用缓存的话需先开启 redis 服务）
pip install -r requirements.txt && python3 bot.py
```

## 開發步驟

我使用 python-3.10.9 進行開發，請使用 python &lt;= 3.10 進行開發，另外，建議使用 python 虛擬環境開發以避免一些不必要的問題。以下是一個我的開發步驟，僅供參考：

```shell
# python=3.10.9
git clone https://github.com/akynazh/tg-search-bot.git
cd tg-search-bot
python3 -m venv venv
source ./venv/bin/activate
pip3 install -r requirements.txt
```

接著就可以開始寫程式碼了，完成後記得寫或執行測試實例(在`tests/test.py`中)。請確保測試沒問題再提交代碼喲～

## 全部

-   英文版本
-   影片搜尋支援更多磁力網站(目前只支援了海盜灣)
-   其他你希望出現的功能...

## 鳴謝

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->

<!-- prettier-ignore-start -->

<!-- markdownlint-disable -->

<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://akynazh.site"><img src="https://avatars.githubusercontent.com/u/78672905?v=4?s=100" width="100px;" alt="Jack Bryant"/><br /><sub><b>Jack Bryant</b></sub></a><br /><a href="#maintenance-akynazh" title="Maintenance">🚧</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/z-hhh"><img src="https://avatars.githubusercontent.com/u/8455958?v=4?s=100" width="100px;" alt="zhhh"/><br /><sub><b>zhhh</b></sub></a><br /><a href="https://github.com/akynazh/tg-search-bot/commits?author=z-hhh" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://allcontributors.org"><img src="https://avatars.githubusercontent.com/u/46410174?v=4?s=100" width="100px;" alt="All Contributors"/><br /><sub><b>All Contributors</b></sub></a><br /><a href="https://github.com/akynazh/tg-search-bot/commits?author=all-contributors" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/JackBryant286"><img src="https://avatars.githubusercontent.com/u/113345781?v=4?s=100" width="100px;" alt="Jack Bryant"/><br /><sub><b>Julia</b></sub></a><br /><a href="https://github.com/akynazh/tg-search-bot/commits?author=JackBryant286" title="Code">💻</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->

<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

如果你也想為社區貢獻自己的一份力量, 請查看[全部](https://github.com/akynazh/tg-search-bot#todo), 並根據[開發步驟](https://github.com/akynazh/tg-search-bot#开发步骤)進行開發, 歡迎 issue 和 pr。
