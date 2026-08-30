import concurrent.futures
import math
import os
import re
import string
import random
import jvav as jv
import yaml
import threading
import langdetect
import html
import telebot
from telebot import apihelper, types
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from database import BotFileDb, BotCacheDb
from ai import AiClient
from pikpak import PikPakClient
from requests import get
from requests.compat import quote
from bs4 import BeautifulSoup
import logging
from logging.handlers import RotatingFileHandler


class Logger:

    def __init__(self, path_log_file: str, log_level=logging.INFO):
        self.logger = logging.getLogger()
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        r_file_handler = RotatingFileHandler(
            path_log_file, maxBytes=1024 * 1024 * 16, backupCount=1
        )
        r_file_handler.setFormatter(formatter)
        self.logger.addHandler(r_file_handler)
        self.logger.addHandler(stream_handler)
        self.logger.setLevel(log_level)


class BotConfig:
    def __init__(self, path_config_file: str):
        with open(path_config_file, "r", encoding="utf8") as f:
            config = yaml.safe_load(f)
        self.tg_chat_id = str(config["tg_chat_id"]) if config["tg_chat_id"] else ""
        self.tg_bot_token = (
            str(config["tg_bot_token"]) if config["tg_bot_token"] else ""
        )
        self.enable_nsfw = str(config["enable_nsfw"]) if config["enable_nsfw"] else "0"
        self.use_proxy = str(config["use_proxy"]) if config["use_proxy"] else "0"
        self.proxy_addr = str(config["proxy_addr"]) if config["proxy_addr"] else ""
        self.pikpak_username = (
            str(config["pikpak_username"]) if config.get("pikpak_username") else ""
        )
        self.pikpak_password = (
            str(config["pikpak_password"]) if config.get("pikpak_password") else ""
        )
        self.ai_base_url = (
            str(config["ai_base_url"]) if config.get("ai_base_url") else ""
        )
        self.ai_api_key = str(config["ai_api_key"]) if config.get("ai_api_key") else ""
        self.ai_model = (
            str(config["ai_model"]) if config.get("ai_model") else "gpt-4o-mini"
        )
        # set
        self.proxy_json = {"http": "", "https": ""}
        if self.use_proxy == "1":
            self.proxy_json = {"http": self.proxy_addr, "https": self.proxy_addr}
            LOG.info(f'Set proxy: "{self.proxy_addr}"')
        else:
            self.proxy_addr = ""
        LOG.info("Successfully read and loaded the configuration file.")


# URL
BASE_URL_TG = "https://t.me"
PIKPAK_BOT_NAME = "PikPak6_Bot"
URL_PROJECT_ADDRESS = "https://github.com/akynazh/tg-search-bot"
URL_PIKPAK_BOT = f"{BASE_URL_TG}/{PIKPAK_BOT_NAME}"
# PATH
PATH_ROOT = f'{os.path.expanduser("~")}/.tg_search_bot'
PATH_LOG_FILE = f"{PATH_ROOT}/log.txt"
PATH_RECORD_FILE = f"{PATH_ROOT}/record.json"
PATH_PIKPAK_TOKEN_FILE = f"{PATH_ROOT}/pikpak_token.json"
PATH_CACHE_FILE = f"{PATH_ROOT}/cache.db"
PATH_CONFIG_FILE = f"{PATH_ROOT}/config.yaml"
# BASE
LOG = Logger(path_log_file=PATH_LOG_FILE).logger
BOT_CFG = BotConfig(PATH_CONFIG_FILE)
apihelper.proxy = BOT_CFG.proxy_json
BOT = telebot.TeleBot(BOT_CFG.tg_bot_token)
BOT_DB = BotFileDb(PATH_RECORD_FILE)
BOT_CACHE_DB = BotCacheDb(
    path_cache_file=PATH_CACHE_FILE,
    use_cache="1",
)
BASE_UTIL = jv.BaseUtil(BOT_CFG.proxy_addr)
DMM_UTIL = jv.DmmUtil(BOT_CFG.proxy_addr)
JBUS_UTIL = jv.JavBusUtil(BOT_CFG.proxy_addr)
JDB_UTIL = jv.JavDbUtil(BOT_CFG.proxy_addr)
JLIB_UTIL = jv.JavLibUtil(BOT_CFG.proxy_addr)
SUKEBEI_UTIL = jv.SukebeiUtil(BOT_CFG.proxy_addr)
TRANS_UTIL = jv.TransUtil(BOT_CFG.proxy_addr)
WIKI_UTIL = jv.WikiUtil(BOT_CFG.proxy_addr)
VGLE_UTIL = jv.AvgleUtil(BOT_CFG.proxy_addr)
EXECUTOR = concurrent.futures.ThreadPoolExecutor()
PIKPAK = PikPakClient(
    username=BOT_CFG.pikpak_username,
    password=BOT_CFG.pikpak_password,
    proxy=BOT_CFG.proxy_addr,
    token_path=PATH_PIKPAK_TOKEN_FILE,
)
AI = AiClient(
    base_url=BOT_CFG.ai_base_url,
    api_key=BOT_CFG.ai_api_key,
    model=BOT_CFG.ai_model,
    proxy=BOT_CFG.proxy_addr,
)
# BT 搜索结果分页会话：token -> {"q": ..., "bts": [...], "page": n}
BT_SESSIONS = {}
CHAT_BT_SESSION = {}
ID_PAT = re.compile(r"[a-z0-9]+[-_](?:ppv-)?[a-z0-9]+")
BOT_CMDS = {
    "help": "查看帮助",
    "stars": "查看已收藏的演职人员",
    "ids": "查看已收藏的编号",
    "record": "导出收藏记录文件",
}
MSG_HELP = f"""直接发送片名、关键词或编号，剩下的交给我！

"""
for cmd, content in BOT_CMDS.items():
    MSG_HELP += f"""/{cmd}  {content}
"""
MSG_HELP += f"""
[NSFW: {"已开启" if BOT_CFG.enable_nsfw == "1" else "已关闭"}]"""


class BotKey:
    KEY_GET_SAMPLE_BY_ID = "k0_0"
    KEY_GET_MORE_MAGNETS_BY_ID = "k0_1"
    KEY_SEARCH_STAR_BY_NAME = "k0_2"
    KEY_WATCH_PV_BY_ID = "k1_0"
    KEY_WATCH_FV_BY_ID = "k1_1"
    KEY_GET_V_BY_ID = "k2_0"
    KEY_RANDOM_GET_V_BY_STAR_ID = "k2_1"
    KEY_RANDOM_GET_V_NICE = "k2_2"
    KEY_RANDOM_GET_V_NEW = "k2_3"
    KEY_GET_NEW_VS_BY_STAR_NAME_ID = "k2_4"
    KEY_GET_NICE_VS_BY_STAR_NAME = "k2_5"
    KEY_RECORD_STAR_BY_STAR_NAME_ID = "k3_0"
    KEY_RECORD_V_BY_ID_STAR_IDS = "k3_1"
    KEY_GET_STARS_RECORD = "k3_2"
    KEY_GET_VS_RECORD = "k3_3"
    KEY_GET_STAR_DETAIL_RECORD_BY_STAR_NAME_ID = "k3_4"
    KEY_GET_V_DETAIL_RECORD_BY_ID = "k3_5"
    KEY_UNDO_RECORD_STAR_BY_STAR_NAME_ID = "k3_6"
    KEY_UNDO_RECORD_V_BY_ID = "k3_7"
    KEY_DEL_V_CACHE = "k4_1"
    KEY_BT_PAGE = "k5_0"


class BotUtils:
    v_utils = [JDB_UTIL, JBUS_UTIL, SUKEBEI_UTIL]

    def send_action_typing(self):
        BOT.send_chat_action(chat_id=BOT_CFG.tg_chat_id, action="typing")

    def send_msg(self, msg: str, pv=False, markup=None):
        BOT.send_message(
            chat_id=BOT_CFG.tg_chat_id,
            text=msg,
            disable_web_page_preview=not pv,
            parse_mode="HTML",
            reply_markup=markup,
        )

    def send_msg_code_op(self, code: int, op: str):
        if code == 200:
            self.send_msg(f"✅ 操作成功：{op}")
        elif code == 404:
            self.send_msg(f"没有找到相关结果，{op} 未完成 Q_Q")
        elif code == 500:
            self.send_msg(f"服务器出错，{op} 未完成，请稍后重试或查看日志 Q_Q")
        elif code == 502:
            self.send_msg(f"网络请求失败，{op} 未完成，请检查网络后重试 Q_Q")

    def send_msg_success_op(self, op: str):
        self.send_msg(f"✅ 操作成功：{op}")

    def send_msg_fail_reason_op(self, reason: str, op: str):
        self.send_msg(f"{op} 失败：{reason} Q_Q")

    def send_msg_v_not_found(self, v_id: str):
        self.send_msg(
            f"没有找到 <code>{html.escape(v_id)}</code> 的相关结果，请稍后重试或检查编号是否正确。"
        )

    def check_success(self, code: int, op: str):
        if code == 200:
            return True
        if code == 404:
            self.send_msg_fail_reason_op(reason="未找到相关结果", op=op)
        elif code == 500:
            self.send_msg_fail_reason_op(reason="服务器错误", op=op)
        elif code == 502:
            self.send_msg_fail_reason_op(reason="网络请求失败", op=op)
        return False

    def create_btn_by_key(self, key_type: str, obj):
        if key_type == BotKey.KEY_GET_STAR_DETAIL_RECORD_BY_STAR_NAME_ID:
            return InlineKeyboardButton(
                text=obj["name"], callback_data=f'{obj["name"]}|{obj["id"]}:{key_type}'
            )
        elif key_type == BotKey.KEY_GET_V_DETAIL_RECORD_BY_ID:
            return InlineKeyboardButton(text=obj, callback_data=f"{obj}:{key_type}")
        elif key_type == BotKey.KEY_SEARCH_STAR_BY_NAME:
            return InlineKeyboardButton(text=obj, callback_data=f"{obj}:{key_type}")
        elif key_type == BotKey.KEY_GET_V_BY_ID:
            return InlineKeyboardButton(
                text=f'{obj["id"]} | {obj["rate"]}',
                callback_data=f'{obj["id"]}:{key_type}',
            )

    def send_msg_btns(
        self,
        max_btn_per_row: int,
        max_row_per_msg: int,
        key_type: str,
        title: str,
        objs: list,
        extra_btns=[],
        page_btns=[],
    ):
        markup = InlineKeyboardMarkup()
        row_count = 0
        btns = []
        for obj in objs:
            btns.append(self.create_btn_by_key(key_type, obj))
            if len(btns) == max_btn_per_row:
                markup.row(*btns)
                row_count += 1
                btns = []
            if row_count == max_row_per_msg:
                for extra_btn in extra_btns:
                    markup.row(*extra_btn)
                if page_btns != []:
                    markup.row(*page_btns)
                self.send_msg(msg=title, markup=markup)
                row_count = 0
                markup = InlineKeyboardMarkup()
        if btns != []:
            markup.row(*btns)
            row_count += 1
        if row_count != 0:
            for extra_btn in extra_btns:
                markup.row(*extra_btn)
            if page_btns != []:
                markup.row(*page_btns)
            self.send_msg(msg=title, markup=markup)

    def get_page_elements(
        self, objs: list, page: int, col: int, row: int, key_type: str
    ):
        """
        Get the list of objects on the current page, list of pagination buttons, and the title of quantity.

        :param list objs: All objects
        :param int page: Current page
        :param int col: Number of columns on the current page
        :param int row: Number of rows on the current page
        :param str key_type: Key type
        :return tuple[list, list, str]: List of objects on the current page, list of pagination buttons, title of quantity
        """
        record_count_total = len(objs)
        record_count_per_page = col * row
        if record_count_per_page > record_count_total:
            page_count = 1
        else:
            page_count = math.ceil(record_count_total / record_count_per_page)
        if page > page_count:
            page = page_count
        start_idx = (page - 1) * record_count_per_page
        objs = objs[start_idx : start_idx + record_count_per_page]
        if page == 1:
            to_previous = 1
        else:
            to_previous = page - 1
        if page == page_count:
            to_next = page_count
        else:
            to_next = page + 1
        btn_to_first = InlineKeyboardButton(text="<<", callback_data=f"1:{key_type}")
        btn_to_previous = InlineKeyboardButton(
            text="<", callback_data=f"{to_previous}:{key_type}"
        )
        btn_to_current = InlineKeyboardButton(
            text=f"-{page}-", callback_data=f"{page}:{key_type}"
        )
        btn_to_next = InlineKeyboardButton(
            text=">", callback_data=f"{to_next}:{key_type}"
        )
        btn_to_last = InlineKeyboardButton(
            text=">>", callback_data=f"{page_count}:{key_type}"
        )
        # Get the title of quantity
        title = f"共 <b>{record_count_total}</b> 条，共 <b>{page_count}</b> 页"
        return (
            objs,
            [btn_to_first, btn_to_previous, btn_to_current, btn_to_next, btn_to_last],
            title,
        )

    def check_if_enable_nsfw(self):
        if BOT_CFG.enable_nsfw == "0":
            self.send_msg("[NSFW] 已关闭，无法访问该内容。")
            return False
        return True

    def get_stars_record(self, page=1):
        record, is_star_exists, _ = BOT_DB.check_has_record()
        if not record or not is_star_exists:
            self.send_msg_fail_reason_op(
                reason="还没有收藏任何演职人员", op="查看收藏的演职人员"
            )
            return
        stars = record["stars"]
        stars.reverse()
        col, row = 4, 5
        objs, page_btns, title = self.get_page_elements(
            objs=stars,
            page=page,
            col=col,
            row=row,
            key_type=BotKey.KEY_GET_STARS_RECORD,
        )
        self.send_msg_btns(
            max_btn_per_row=col,
            max_row_per_msg=row,
            key_type=BotKey.KEY_GET_STAR_DETAIL_RECORD_BY_STAR_NAME_ID,
            title="<b>已收藏的演职人员：</b>" + title,
            objs=objs,
            page_btns=page_btns,
        )

    def get_star_detail_record_by_name_id(self, star_name: str, star_id: str):
        record, is_stars_exists, is_vs_exists = BOT_DB.check_has_record()
        if not record:
            self.send_msg_fail_reason_op(
                reason="还没有收藏该演职人员",
                op=f"查看演职人员 <code>{star_name}</code> 的详情",
            )
            return
        star_vs = []
        cur_star_exists = False
        if is_vs_exists:
            vs = record["vs"]
            vs.reverse()
            for v in vs:
                if star_id in v["stars"]:
                    star_vs.append(v["id"])
        if is_stars_exists:
            stars = record["stars"]
            for star in stars:
                if star["id"].lower() == star_id.lower():
                    cur_star_exists = True
        extra_btn1 = InlineKeyboardButton(
            text="随机一部",
            callback_data=f"{star_name}|{star_id}:{BotKey.KEY_RANDOM_GET_V_BY_STAR_ID}",
        )
        extra_btn2 = InlineKeyboardButton(
            text="最新作品",
            callback_data=f"{star_name}|{star_id}:{BotKey.KEY_GET_NEW_VS_BY_STAR_NAME_ID}",
        )
        extra_btn3 = InlineKeyboardButton(
            text="高分作品",
            callback_data=f"{star_name}:{BotKey.KEY_GET_NICE_VS_BY_STAR_NAME}",
        )
        if cur_star_exists:
            extra_btn4 = InlineKeyboardButton(
                text="取消收藏",
                callback_data=f"{star_name}|{star_id}:{BotKey.KEY_UNDO_RECORD_STAR_BY_STAR_NAME_ID}",
            )
        else:
            extra_btn4 = InlineKeyboardButton(
                text="收藏",
                callback_data=f"{star_name}|{star_id}:{BotKey.KEY_RECORD_STAR_BY_STAR_NAME_ID}",
            )
        title = f'<code>{star_name}</code> | <a href="{WIKI_UTIL.BASE_URL_JAPAN_WIKI}/{star_name}">Wiki</a> | <a href="{JBUS_UTIL.base_url_search_by_star_id}/{star_id}">Javbus</a>'
        if len(star_vs) == 0:
            markup = InlineKeyboardMarkup()
            markup.row(extra_btn1, extra_btn2, extra_btn3, extra_btn4)
            self.send_msg(msg=title, markup=markup)
            return
        self.send_msg_btns(
            max_btn_per_row=4,
            max_row_per_msg=10,
            key_type=BotKey.KEY_GET_V_DETAIL_RECORD_BY_ID,
            title=title,
            objs=star_vs,
            extra_btns=[[extra_btn1, extra_btn2, extra_btn3, extra_btn4]],
        )

    def get_vs_record(self, page=1):
        record, _, is_vs_exists = BOT_DB.check_has_record()
        if not record or not is_vs_exists:
            self.send_msg_fail_reason_op(
                reason="还没有收藏任何编号",
                op="查看收藏的编号",
            )
            return
        vs = [v["id"] for v in record["vs"]]
        vs.reverse()
        extra_btn1 = InlineKeyboardButton(
            text="随机高分",
            callback_data=f"0:{BotKey.KEY_RANDOM_GET_V_NICE}",
        )
        extra_btn2 = InlineKeyboardButton(
            text="随机最新", callback_data=f"0:{BotKey.KEY_RANDOM_GET_V_NEW}"
        )
        col, row = 4, 10
        objs, page_btns, title = self.get_page_elements(
            objs=vs, page=page, col=col, row=row, key_type=BotKey.KEY_GET_VS_RECORD
        )
        self.send_msg_btns(
            max_btn_per_row=col,
            max_row_per_msg=row,
            key_type=BotKey.KEY_GET_V_DETAIL_RECORD_BY_ID,
            title="<b>已收藏的编号：</b>" + title,
            objs=objs,
            extra_btns=[[extra_btn1, extra_btn2]],
            page_btns=page_btns,
        )

    def get_v_detail_record_by_id(self, id: str):
        record, _, is_vs_exists = BOT_DB.check_has_record()
        vs = record["vs"]
        cur_v_exists = False
        for v in vs:
            if id.lower() == v["id"].lower():
                cur_v_exists = True
        markup = InlineKeyboardMarkup()
        btn = InlineKeyboardButton(
            text=f"查看",
            callback_data=f"{id}:{BotKey.KEY_GET_V_BY_ID}",
        )
        if cur_v_exists:
            markup.row(
                btn,
                InlineKeyboardButton(
                    text=f"取消收藏",
                    callback_data=f"{id}:{BotKey.KEY_UNDO_RECORD_V_BY_ID}",
                ),
            )
        else:
            markup.row(btn)
        self.send_msg(msg=f"<code>{id}</code>", markup=markup)

    def search_bts(self, q):
        def append_trackers():
            """Returns the base tracker list"""
            trackers = [
                "udp://tracker.coppersurfer.tk:6969/announce",
                "udp://tracker.openbittorrent.com:6969/announce",
                "udp://9.rarbg.to:2710/announce",
                "udp://9.rarbg.me:2780/announce",
                "udp://9.rarbg.to:2730/announce",
                "udp://tracker.opentrackr.org:1337",
                "http://p4p.arenabg.com:1337/announce",
                "udp://tracker.torrent.eu.org:451/announce",
                "udp://tracker.tiny-vps.com:6969/announce",
                "udp://open.stealth.si:80/announce",
            ]
            trackers = [quote(tr) for tr in trackers]
            return "&tr=".join(trackers)

        def category_name(category):
            """Translates the category code to a name"""
            names = ["", "audio", "video", "apps", "games", "nsfw", "other"]
            category = int(category[0])
            category = category if category < len(names) - 1 else -1
            return names[category]

        def size_as_str(size):
            """Formats the file size in bytes to kb, mb or gb accordingly"""
            size = int(size)
            size_str = f"{size} b"
            if size >= 1024:
                size_str = f"{(size / 1024):.2f} kb"
            if size >= 1024**2:
                size_str = f"{(size / 1024 ** 2):.2f} mb"
            if size >= 1024**3:
                size_str = f"{(size / 1024 ** 3):.2f} gb"
            return size_str

        def magnet_link(ih, name):
            """Creates the magnet URI"""
            return f"magnet:?xt=urn:btih:{ih}&dn={quote(name)}&tr={append_trackers()}"

        agent = BASE_UTIL.ua()
        url = f"https://apibay.org/q.php?q={quote(q)}"
        try:
            results = get(url, headers={"agent": agent}, timeout=10)
        except Exception as e:
            LOG.error(f"apibay search request failed: {e}")
            return None
        if not results.status_code == 200:
            return None
        matches = []
        data = results.json()
        if data and "no results" in data[0]["name"].lower():
            return matches
        for d in data:
            matches.append(
                {
                    "seeders": d["seeders"],
                    "leechers": d["leechers"],
                    "name": d["name"],
                    "category": category_name(d["category"]),
                    "size": size_as_str(d["size"]),
                    "magnet": magnet_link(d["info_hash"], d["name"]),
                }
            )
        return matches

    def search_bts_torrentkitty(self, q):
        """通过 TorrentKitty 搜索中文 BT 资源，返回与 search_bts 相同格式的列表或 None。

        TorrentKitty 聚合国内多家 BT 站，中文关键词命中率远高于 apibay。
        """
        url = f"https://www.torrentkitty.tv/search/{quote(q)}"
        try:
            resp = get(
                url,
                headers={"user-agent": BASE_UTIL.ua()},
                timeout=10,
            )
        except Exception as e:
            LOG.error(f"TorrentKitty search request failed: {e}")
            return None
        if resp.status_code != 200:
            return None
        try:
            soup = BeautifulSoup(resp.text, "html.parser")
            matches = []
            for tr in soup.find_all("tr"):
                name_td = tr.find("td", class_="name")
                size_td = tr.find("td", class_="size")
                magnet_a = tr.find("a", rel="magnet")
                if not name_td or not magnet_a:
                    continue
                matches.append(
                    {
                        "seeders": 0,
                        "leechers": 0,
                        "name": name_td.get_text(strip=True),
                        "category": "general",
                        "size": size_td.get_text(strip=True) if size_td else "",
                        "magnet": magnet_a.get("href"),
                    }
                )
            return matches if matches else None
        except Exception as e:
            LOG.error(f"TorrentKitty search parse failed: {e}")
            return None

    def get_v_by_id(
        self,
        id: str,
        send_to_pikpak=True,
        is_nice=True,
        is_uncensored=True,
        magnet_max_count=3,
        not_send=False,
    ):
        """
        Get based on id

        :param str id: Number
        :param bool send_to_pikpak: Whether to send to pikpak, default is yes
        :param bool is_nice: Whether to filter out HD, subtitled magnet links, default is yes
        :param bool is_uncensored: Whether to filter out uncensored magnet links, default is yes
        :param int magnet_max_count: Maximum id of magnet links after filtering, default is 3
        :param not_send: Whether not to send results, default is to send
        :return dict: When not sending results, return the obtained results (if any)
        """
        if not self.check_if_enable_nsfw():
            return {}
        op_get_v_by_id = f"搜索编号 <code>{id}</code>"
        v = BOT_CACHE_DB.get_cache(key=id, type=BotCacheDb.TYPE_V)
        v_score = None
        is_cache = False
        if not v or not_send:
            v_util = None
            for util in self.v_utils:
                code, v = util.get_av_by_id(
                    id=id,
                    is_nice=is_nice,
                    is_uncensored=is_uncensored,
                    magnet_max_count=magnet_max_count,
                )
                if code == 200:
                    v_util = util
                    break
            if not v_util:
                if not not_send:
                    self.send_msg_v_not_found(v_id=id)
                return
            if "score" not in v.keys():
                _, v["score"] = DMM_UTIL.get_score_by_id(id)
            if not not_send:
                if len(v["magnets"]) == 0:
                    BOT_CACHE_DB.set_cache(
                        key=id, value=v, type=BotCacheDb.TYPE_V, expire=3600 * 24 * 1
                    )
                else:
                    BOT_CACHE_DB.set_cache(key=id, value=v, type=BotCacheDb.TYPE_V)
        else:
            v_score = v["score"]
            is_cache = True
        if not_send:
            return v
        v_id = id
        v_title = v["title"]
        v_img = v["img"]
        v_date = v["date"]
        v_tags = v["tags"]
        v_stars = v["stars"]
        v_magnets = v["magnets"]
        v_url = v["url"]
        LOG.info(f"AV 搜索结果: {v_id} | {v_title}")
        for _m in v_magnets:
            LOG.info(f"  磁力: {_m['link']}")
        msg = ""
        if v_title != "":
            v_title = v_title.replace("<", "").replace(">", "")
            msg += f"""【标题】<a href="{v_url}">{v_title}</a>
"""
        msg += f"""【编号】<code>{v_id}</code>
"""
        if v_date != "":
            msg += f"""【日期】{v_date}
"""
        if v_score:
            msg += f"""【评分】{v_score}
"""
        if v_stars != []:
            show_star_name = v_stars[0]["name"]
            show_star_id = v_stars[0]["id"]
            stars_msg = ""
            for star in v_stars:
                stars_msg += f"""【演职人员】<code>{star["name"]}</code>
"""
            msg += stars_msg
        if v_tags:
            v_tags = " ".join(v_tags).replace("<", "").replace(">", "")
            msg += f"""【标签】{v_tags}
"""
        msg += f"""【其他】<a href="{URL_PIKPAK_BOT}">Pikpak</a> | <a href="{URL_PROJECT_ADDRESS}">项目主页</a>
"""
        magnet_send_to_pikpak = ""
        for i, magnet in enumerate(v_magnets):
            if i == 0:
                magnet_send_to_pikpak = magnet["link"]
            magnet_tags = ""
            if magnet["uc"] == "1":
                magnet_tags += "无码 "
            if magnet["hd"] == "1":
                magnet_tags += "HD "
            if magnet["zm"] == "1":
                magnet_tags += "中字 "
            msg_tmp = f"""【{magnet_tags}磁力-{string.ascii_letters[i].upper()} {magnet["size"]}】<code>{magnet["link"]}</code>
"""
            if len(msg + msg_tmp) >= 2000:
                break
            msg += msg_tmp
        pv_btn = InlineKeyboardButton(
            text="预览", callback_data=f"{v_id}:{BotKey.KEY_WATCH_PV_BY_ID}"
        )
        fv_btn = InlineKeyboardButton(
            text="在线观看", callback_data=f"{v_id}:{BotKey.KEY_WATCH_FV_BY_ID}"
        )
        sample_btn = InlineKeyboardButton(
            text="截图", callback_data=f"{v_id}:{BotKey.KEY_GET_SAMPLE_BY_ID}"
        )
        more_btn = InlineKeyboardButton(
            text="更多磁力",
            callback_data=f"{v_id}:{BotKey.KEY_GET_MORE_MAGNETS_BY_ID}",
        )
        if len(v_magnets) != 0:
            markup = InlineKeyboardMarkup().row(sample_btn, pv_btn, fv_btn, more_btn)
        else:
            markup = InlineKeyboardMarkup().row(sample_btn, pv_btn, fv_btn)
        star_record_btn = None
        if len(v_stars) == 1:
            if BOT_DB.check_star_exists_by_id(star_id=show_star_id):
                star_record_btn = InlineKeyboardButton(
                    text="详情",
                    callback_data=f"{show_star_name}|{show_star_id}:{BotKey.KEY_GET_STAR_DETAIL_RECORD_BY_STAR_NAME_ID}",
                )
            else:
                star_record_btn = InlineKeyboardButton(
                    text="收藏演职人员",
                    callback_data=f"{show_star_name}|{show_star_id}:{BotKey.KEY_RECORD_STAR_BY_STAR_NAME_ID}",
                )
        star_ids = ""
        for i, star in enumerate(v_stars):
            star_ids += star["id"] + "|"
            if i >= 5:
                star_ids += "...|"
                break
        if star_ids != "":
            star_ids = star_ids[: len(star_ids) - 1]
        v_record_btn = None
        if BOT_DB.check_id_exists(id=v_id):
            v_record_btn = InlineKeyboardButton(
                text="详情",
                callback_data=f"{v_id}:{BotKey.KEY_GET_V_DETAIL_RECORD_BY_ID}",
            )
        else:
            v_record_btn = InlineKeyboardButton(
                text="收藏",
                callback_data=f"{v_id}|{star_ids}:{BotKey.KEY_RECORD_V_BY_ID_STAR_IDS}",
            )
        renew_btn = None
        if is_cache:
            renew_btn = InlineKeyboardButton(
                text="刷新", callback_data=f"{v_id}:{BotKey.KEY_DEL_V_CACHE}"
            )
        if star_record_btn and renew_btn:
            markup.row(v_record_btn, star_record_btn, renew_btn)
        elif star_record_btn:
            markup.row(v_record_btn, star_record_btn)
        elif renew_btn:
            markup.row(v_record_btn, renew_btn)
        else:
            markup.row(v_record_btn)
        if v_img == "":
            self.send_msg(msg=msg, markup=markup)
        else:
            try:
                BOT.send_photo(
                    chat_id=BOT_CFG.tg_chat_id,
                    photo=v_img,
                    caption=msg,
                    parse_mode="HTML",
                    reply_markup=markup,
                )
            except Exception:
                self.send_msg(msg=msg, markup=markup)
        if magnet_send_to_pikpak != "" and send_to_pikpak:
            self.send_magnet_to_pikpak(magnet_send_to_pikpak, v_id)

    def send_magnet_to_pikpak(self, magnet: str, id: str):
        if not PIKPAK.enabled:
            self.send_msg_fail_reason_op(
                reason="请在 config.yaml 中配置 PikPak 账号 (pikpak_username / pikpak_password)",
                op=f"保存编号 {id} 的磁力链接到 PikPak",
            )
            return
        self.send_msg("💾 正在保存到 PikPak 网盘 ...")
        ok, msg = PIKPAK.offline_download(magnet)
        if ok:
            self.send_msg(f"✅ 保存结果：{msg}")
        else:
            self.send_msg_fail_reason_op(
                reason=msg, op=f"保存编号 {id} 的磁力链接到 PikPak"
            )

    def get_bts_by_keyword(self, q):
        """按关键词搜索 BT 资源（带缓存），返回资源列表或 None。

        并行搜索 TorrentKitty（中文）与 apibay（英文）两个来源的结果，按磁力 info_hash 去重。
        """
        bts = BOT_CACHE_DB.get_cache(key=q, type=BotCacheDb.TYPE_BT)
        if bts:
            return bts
        merged = []
        seen = set()
        # 并行搜索两个来源，但每个来源最多等待短时间，避免长时间无响应。
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            tk_future = executor.submit(self.search_bts_torrentkitty, q)
            ab_future = executor.submit(self.search_bts, q)
            srcs = []
            for name, future in (("torrentkitty", tk_future), ("apibay", ab_future)):
                try:
                    srcs.append(future.result(timeout=8))
                except concurrent.futures.TimeoutError:
                    LOG.warning(f"BT source {name} timed out for query: {q}")
                    srcs.append([])
            for src in srcs:
                for bt in src or []:
                    if not bt.get("magnet"):
                        continue
                    m = re.search(r"urn:btih:([A-Za-z0-9]+)", bt["magnet"])
                    key = m.group(1).lower() if m else bt["magnet"]
                    if key in seen:
                        continue
                    seen.add(key)
                    merged.append(bt)
        if not merged:
            return None
        if BOT_CFG.enable_nsfw == "0":
            merged = list(filter(lambda bt: bt["category"] != "nsfw", merged))
            merged = list(filter(lambda bt: "nsfw" not in bt["name"].lower(), merged))
        merged = merged[:30]
        BOT_CACHE_DB.set_cache(key=q, value=merged, type=BotCacheDb.TYPE_BT)
        LOG.info(f"BT 搜索结果 {len(merged)} 条: {q}")
        for _bt in merged:
            LOG.info(f"  {_bt['name']} | {_bt['size']} | {_bt['magnet']}")
        return merged

    def search_bts_and_save(self, q):
        try:
            bts = self.get_bts_by_keyword(q)
        except Exception as e:
            LOG.error(f"BT 搜索异常: {e}")
            self.send_msg_fail_reason_op(
                reason=f"搜索超时或网络错误：{str(e)[:50]}",
                op=f"搜索 <code>{html.escape(q)}</code>",
            )
            return False
        if not bts:
            self.send_msg_fail_reason_op(
                reason="没有找到相关资源", op=f"搜索 <code>{html.escape(q)}</code>"
            )
            return False
        self.show_bt_results(q, bts, save_first=True)
        return True

    def search_av_keyword(self, q):
        """按关键词搜索 AV（JavDB 标签搜索），找到则返回 True。"""
        code, ids = JDB_UTIL.get_ids_by_tag(q)
        if code == 200 and ids:
            self.get_v_by_id(id=ids[0])
            return True
        return False

    def handle_nlp_search(self, msg):
        """AI 自然语言理解搜索流程。返回 True 表示已处理。"""
        if not AI.enabled:
            return False
        LOG.info(f'AI 搜索字符: "{msg}"')
        intent = AI.understand(msg)
        LOG.info(f"AI 返回结果: {intent}")
        if not intent:
            return False
        target = (intent.get("target") or msg).strip()
        kind = (intent.get("intent") or "general").strip().lower()
        explain = (intent.get("explain") or target).strip()
        source = (intent.get("source") or "auto").strip().lower()

        # AV 相关意图需先检查 NSFW 开关
        if kind in ("av_id", "actor") and not self.check_if_enable_nsfw():
            return True

        self.send_msg(f"🔍 搜索：<b>{html.escape(explain)}</b>")
        self.send_msg("⏳ 搜索中 ...")

        if kind == "av_id":
            self.get_v_by_id(id=target)
            return True
        if kind == "actor":
            # 仅在 AI 明确判定为日本 AV 演员时，才走演员搜索；其他“演员/明星”类请求继续走一般搜索
            self.search_star_by_name(target)
            return True

        # 类型 / 关键词 / 剧情 / 其他：优先 AV 关键词搜索，失败则 BT 搜索
        if (
            source in ("javdb", "javbus", "sukebei", "dmm")
            and BOT_CFG.enable_nsfw == "1"
        ):
            if self.search_av_keyword(target):
                return True
        # BT 搜索（总是返回 True，表示已处理；搜索结果由 search_bts_and_save 内部反馈给用户）
        self.search_bts_and_save(target)
        return True

    def get_sample_by_id(self, id: str):
        op_get_sample = f"获取编号 <code>{id}</code> 的截图"
        samples = BOT_CACHE_DB.get_cache(key=id, type=BotCacheDb.TYPE_SAMPLE)
        if not samples:
            code, samples = JBUS_UTIL.get_samples_by_id(id)
            if not self.check_success(code, op_get_sample):
                return
            BOT_CACHE_DB.set_cache(key=id, value=samples, type=BotCacheDb.TYPE_SAMPLE)
        samples_imp = []
        sample_error = False
        for sample in samples:
            samples_imp.append(InputMediaPhoto(sample))
            if len(samples_imp) == 10:
                try:
                    BOT.send_media_group(chat_id=BOT_CFG.tg_chat_id, media=samples_imp)
                    samples_imp = []
                except Exception:
                    sample_error = True
                    self.send_msg_fail_reason_op(
                        reason="图片解析失败", op=op_get_sample
                    )
                    break
        if samples_imp != [] and not sample_error:
            try:
                BOT.send_media_group(chat_id=BOT_CFG.tg_chat_id, media=samples_imp)
            except Exception:
                self.send_msg_fail_reason_op(reason="图片解析失败", op=op_get_sample)

    def watch_v_by_id(self, id: str, type: int):
        id = id.lower()
        if id.find("fc2") != -1 and id.find("ppv") == -1:
            id = id.replace("fc2", "fc2-ppv")
        if type == 0:
            pv = BOT_CACHE_DB.get_cache(key=id, type=BotCacheDb.TYPE_PV)
            if not pv:
                op_watch_v = f"获取编号 <code>{id}</code> 的预览视频"
                futures = {}
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    futures[executor.submit(DMM_UTIL.get_pv_by_id, id)] = 1
                    futures[executor.submit(VGLE_UTIL.get_pv_by_id, id)] = 2
                    for future in concurrent.futures.as_completed(futures):
                        if futures[future] == 1:
                            code_dmm, pv_dmm = future.result()
                        elif futures[future] == 2:
                            code_vgle, pv_vgle = future.result()
                if code_dmm != 200 and code_vgle != 200:
                    if code_dmm == 502 or code_vgle == 502:
                        self.send_msg_code_op(502, op_watch_v)
                    else:
                        self.send_msg_code_op(404, op_watch_v)
                    return
                from_site = ""
                pv_src = ""
                if code_dmm == 200:
                    from_site = "dmm"
                    pv_src = pv_dmm
                elif code_vgle == 200:
                    from_site = "avgle"
                    pv_src = pv_vgle
                pv_cache = {"from_site": from_site, "src": pv_src}
                BOT_CACHE_DB.set_cache(key=id, value=pv_cache, type=BotCacheDb.TYPE_PV)
            else:
                from_site = pv["from_site"]
                pv_src = pv["src"]
            if from_site == "dmm":
                try:
                    pv_src_nice = DMM_UTIL.get_nice_pv_by_src(pv_src)
                    BOT.send_video(
                        chat_id=BOT_CFG.tg_chat_id,
                        video=pv_src,
                        caption=f'来自 DMM 的搜索结果。<a href="{pv_src_nice}">点此观看更清晰的版本</a>。',
                        parse_mode="HTML",
                    )
                except Exception:
                    self.send_msg(
                        f'来自 DMM 的搜索结果，但视频解析失败：<a href="{pv_src_nice}">视频链接</a> Q_Q。'
                    )
            elif from_site == "avgle":
                try:
                    BOT.send_video(
                        chat_id=BOT_CFG.tg_chat_id,
                        video=pv_src,
                        caption=f'来自 Avgle 的搜索结果：<a href="{pv_src}">视频链接</a>。',
                        parse_mode="HTML",
                    )
                except Exception:
                    self.send_msg(
                        f'来自 Avgle 的搜索结果，但视频解析失败：<a href="{pv_src}">视频链接</a> Q_Q。'
                    )
        elif type == 1:
            video = BOT_CACHE_DB.get_cache(key=id, type=BotCacheDb.TYPE_FV)
            if not video:
                code, video = VGLE_UTIL.get_fv_by_id(id)
                if code != 200:
                    self.send_msg("没有找到相关结果。")
                    return
                BOT_CACHE_DB.set_cache(key=id, value=video, type=BotCacheDb.TYPE_FV)
            self.send_msg(video)

    def search_star_by_name(self, star_name: str):
        if not self.check_if_enable_nsfw():
            return False
        op_search_star = f"搜索演职人员 <code>{star_name}</code>"
        star = BOT_CACHE_DB.get_cache(key=star_name, type=BotCacheDb.TYPE_STAR)
        if not star:
            star_name_origin = star_name
            star_name = self.get_star_ja_name_by_zh_name(star_name)
            code, star = JBUS_UTIL.check_star_exists(star_name)
            if not self.check_success(code, op_search_star):
                return
            BOT_CACHE_DB.set_cache(key=star_name, value=star, type=BotCacheDb.TYPE_STAR)
            if star_name_origin != star_name:
                BOT_CACHE_DB.set_cache(
                    key=star_name_origin,
                    value=star,
                    type=BotCacheDb.TYPE_STAR,
                )
        star_id = star["star_id"]
        star_name = star["star_name"]
        if BOT_DB.check_star_exists_by_id(star_id=star_id):
            self.get_star_detail_record_by_name_id(star_name=star_name, star_id=star_id)
            return True
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton(
                text="随机一部",
                callback_data=f"{star_name}|{star_id}:{BotKey.KEY_RANDOM_GET_V_BY_STAR_ID}",
            ),
            InlineKeyboardButton(
                text="最新作品",
                callback_data=f"{star_name}|{star_id}:{BotKey.KEY_GET_NEW_VS_BY_STAR_NAME_ID}",
            ),
            InlineKeyboardButton(
                text="高分作品",
                callback_data=f"{star_name}:{BotKey.KEY_GET_NICE_VS_BY_STAR_NAME}",
            ),
            InlineKeyboardButton(
                text=f"收藏 {star_name}",
                callback_data=f"{star_name}|{star_id}:{BotKey.KEY_RECORD_STAR_BY_STAR_NAME_ID}",
            ),
        )
        star_wiki = f"{WIKI_UTIL.BASE_URL_CHINA_WIKI}/{star_name}"
        if langdetect.detect(star_name) == "ja":
            star_wiki = f"{WIKI_UTIL.BASE_URL_JAPAN_WIKI}/{star_name}"
        self.send_msg(
            msg=f'<code>{star_name}</code> | <a href="{star_wiki}">Wiki</a> | <a href="{JBUS_UTIL.base_url_search_by_star_name}/{star_name}">Javbus</a>',
            markup=markup,
        )
        return True

    def get_more_magnets_by_id(self, id: str):
        magnets = BOT_CACHE_DB.get_cache(key=id, type=BotCacheDb.TYPE_MAGNET)
        if not magnets:
            v = self.get_v_by_id(
                id=id, is_nice=False, is_uncensored=False, not_send=True
            )
            if not v:
                return
            magnets = v["magnets"]
            BOT_CACHE_DB.set_cache(key=id, value=magnets, type=BotCacheDb.TYPE_MAGNET)
        msg = ""
        for magnet in magnets:
            magnet_tags = ""
            if magnet["uc"] == "1":
                magnet_tags += "无码 "
            if magnet["hd"] == "1":
                magnet_tags += "HD "
            if magnet["zm"] == "1":
                magnet_tags += "中字 "
            star_tag = ""
            if magnet["hd"] == "1" and magnet["zm"] == "1":
                star_tag = "*"
            msg_tmp = f"""【{star_tag}{magnet_tags}磁力 {magnet["size"]}】<code>{magnet["link"]}</code>
        """
            if len(msg + msg_tmp) >= 4000:
                self.send_msg(msg)
                msg = msg_tmp
            else:
                msg += msg_tmp
        if msg != "":
            self.send_msg(msg)

    def get_star_new_vs_by_name_id(self, star_name: str, star_id: str):
        op_get_star_new_vs = f"获取 <code>{star_name}</code> 的最新作品"
        ids = BOT_CACHE_DB.get_cache(key=star_id, type=BotCacheDb.TYPE_NEW_VS_OF_STAR)
        if not ids:
            code, ids = JBUS_UTIL.get_new_ids_by_star_id(star_id=star_id)
            if not self.check_success(code, op_get_star_new_vs):
                return
            BOT_CACHE_DB.set_cache(
                key=star_id, value=ids, type=BotCacheDb.TYPE_NEW_VS_OF_STAR
            )
        title = f"<code>{star_name}</code> 的最新作品"
        btns = [
            InlineKeyboardButton(
                text=id, callback_data=f"{id}:{BotKey.KEY_GET_V_BY_ID}"
            )
            for id in ids
        ]
        if len(btns) <= 4:
            self.send_msg(msg=title, markup=InlineKeyboardMarkup().row(*btns))
        else:
            markup = InlineKeyboardMarkup()
            markup.row(*btns[:4])
            markup.row(*btns[4:])
            self.send_msg(msg=title, markup=markup)

    def get_star_ja_name_by_zh_name(self, star_name: str):
        if langdetect.detect(star_name) == "ja":
            return star_name
        star_ja_name = BOT_CACHE_DB.get_cache(
            key=star_name, type=BotCacheDb.TYPE_STAR_JA_NAME
        )
        if star_ja_name:
            return star_ja_name
        wiki_json = WIKI_UTIL.get_wiki_page_by_lang(
            topic=star_name, from_lang="zh", to_lang="ja"
        )
        if wiki_json and wiki_json["lang"] == "ja":
            BOT_CACHE_DB.set_cache(
                key=star_name,
                value=wiki_json["title"],
                type=BotCacheDb.TYPE_STAR_JA_NAME,
            )
            return wiki_json["title"]
        return star_name

    def register_bt_session(self, q, bts):
        token = "".join(random.choices(string.ascii_letters + string.digits, k=8))
        BT_SESSIONS[token] = {"q": q, "bts": bts, "page": 1}
        CHAT_BT_SESSION[BOT_CFG.tg_chat_id] = token
        return token

    def show_bt_results(self, q, bts, save_first=False):
        token = self.register_bt_session(q, bts)
        self.show_bt_page(token, 1)
        if save_first and bts:
            self.send_magnet_to_pikpak(bts[0]["magnet"], q)
        return token

    def show_bt_page(self, token, page):
        sess = BT_SESSIONS.get(token)
        if not sess:
            self.send_msg("结果会话已过期，请重新搜索。")
            return
        bts = sess["bts"]
        page_size = 5
        page_count = math.ceil(len(bts) / page_size) if bts else 1
        if page < 1:
            page = 1
        if page > page_count:
            page = 1  # 换一批：最后一页回到第一页
        sess["page"] = page
        start = (page - 1) * page_size
        items = bts[start : start + page_size]
        res = (
            f"「<b>{html.escape(sess['q'])}</b>」的搜索结果"
            f"（第 {page}/{page_count} 页）：\n\n"
        )
        for i, bt in enumerate(items):
            idx = start + i + 1
            name = bt.get("name") or ""
            if len(name) > 80:
                name = name[:77] + "..."
            magnet = bt.get("magnet") or ""
            magnet_preview = magnet
            if len(magnet_preview) > 80:
                magnet_preview = magnet_preview[:77] + "..."
            res += (
                f"{idx}. {html.escape(name)}\n"
                f"   大小: {bt.get('size', '')} | 分类: {bt.get('category', 'general')}\n"
                f"   磁力: <code>{html.escape(magnet_preview)}</code>\n\n"
            )
        res = res[:3500] + "\n\n..." if len(res) > 3500 else res
        markup = InlineKeyboardMarkup()
        btns = []
        if page > 1:
            btns.append(
                InlineKeyboardButton(
                    "◀ 上一页",
                    callback_data=f"{token}|{page - 1}:{BotKey.KEY_BT_PAGE}",
                )
            )
        btns.append(
            InlineKeyboardButton(
                "🔄 换一批",
                callback_data=f"{token}|{page + 1}:{BotKey.KEY_BT_PAGE}",
            )
        )
        markup.row(*btns)
        markup.row(InlineKeyboardButton("保存到 PikPak 网盘", url=URL_PIKPAK_BOT))
        self.send_msg(res, markup=markup)

    def handle_bt_followup(self, msg):
        """处理 BT 搜索结果的多轮追问：换一批 / 上一页 / 保存第 N 个。"""
        token = CHAT_BT_SESSION.get(BOT_CFG.tg_chat_id)
        if not token or token not in BT_SESSIONS:
            return False
        sess = BT_SESSIONS[token]
        m = msg.strip()
        save_match = re.match(r"^(?:保存|save)\s*第?\s*(\d+)\s*个?$", m)
        if save_match:
            n = int(save_match.group(1))
            bts = sess["bts"]
            if 1 <= n <= len(bts):
                self.send_magnet_to_pikpak(bts[n - 1]["magnet"], sess["q"])
            else:
                self.send_msg_fail_reason_op(
                    reason=f"没有第 {n} 个结果", op="保存到 PikPak"
                )
            return True
        if m in ("下一页", "下一批", "next"):
            self.show_bt_page(token, sess["page"] + 1)
            return True
        if m in ("上一页", "prev"):
            self.show_bt_page(token, sess["page"] - 1)
            return True
        if m in ("换一批", "换一页", "还有吗", "再来", "more"):
            self.show_bt_page(token, sess["page"] + 1)
            return True
        return False

    def random_get_new_v(self):
        page = random.randint(1, JLIB_UTIL.MAX_RANK_PAGE)
        ids = BOT_CACHE_DB.get_cache(key=page, type=BotCacheDb.TYPE_JLIB_PAGE_NEW_VS)
        if not ids:
            code, ids = JLIB_UTIL.get_random_ids_from_rank_by_page(
                page=page, list_type=1
            )
            if self.check_success(code, "随机获取最新影片"):
                BOT_CACHE_DB.set_cache(
                    key=page,
                    value=ids,
                    type=BotCacheDb.TYPE_JLIB_PAGE_NEW_VS,
                )
            else:
                return
        self.get_v_by_id(id=random.choice(ids))

    def random_get_nice_v(self):
        page = random.randint(1, JLIB_UTIL.MAX_RANK_PAGE)
        ids = BOT_CACHE_DB.get_cache(key=page, type=BotCacheDb.TYPE_JLIB_PAGE_NICE_VS)
        if not ids:
            code, ids = JLIB_UTIL.get_random_ids_from_rank_by_page(
                page=page, list_type=0
            )
            if self.check_success(code, "随机获取高分影片"):
                BOT_CACHE_DB.set_cache(
                    key=page,
                    value=ids,
                    type=BotCacheDb.TYPE_JLIB_PAGE_NICE_VS,
                )
            else:
                return
        self.get_v_by_id(id=random.choice(ids))

    def random_get_nice_star_vs(self, star_name_ori):
        vs = BOT_CACHE_DB.get_cache(
            key=star_name_ori, type=BotCacheDb.TYPE_NICE_VS_OF_STAR
        )
        if not vs:
            star_name_ja = self.get_star_ja_name_by_zh_name(star_name_ori)
            code, vs = DMM_UTIL.get_nice_vs_by_star_name(star_name=star_name_ja)
            if self.check_success(code, f"获取演职人员 {star_name_ori} 的高分作品"):
                vs = vs[:60]
                BOT_CACHE_DB.set_cache(
                    key=star_name_ori,
                    value=vs,
                    type=BotCacheDb.TYPE_NICE_VS_OF_STAR,
                )
                if star_name_ja != star_name_ori:
                    BOT_CACHE_DB.set_cache(
                        key=star_name_ja,
                        value=vs,
                        type=BotCacheDb.TYPE_NICE_VS_OF_STAR,
                    )
            else:
                return
        self.send_msg_btns(
            max_btn_per_row=3,
            max_row_per_msg=20,
            key_type=BotKey.KEY_GET_V_BY_ID,
            title=f"<b>{star_name_ori} 的高分作品</b>",
            objs=vs,
        )


def handle_callback(call):
    bot_utils = BotUtils()
    bot_utils.send_action_typing()
    LOG.info(f"Handle callback: {call.data}")
    s = call.data.rfind(":")
    content = call.data[:s]
    key_type = call.data[s + 1 :]
    if key_type == BotKey.KEY_WATCH_PV_BY_ID:
        bot_utils.watch_v_by_id(id=content, type=0)
    elif key_type == BotKey.KEY_WATCH_FV_BY_ID:
        bot_utils.watch_v_by_id(id=content, type=1)
    elif key_type == BotKey.KEY_GET_SAMPLE_BY_ID:
        bot_utils.get_sample_by_id(id=content)
    elif key_type == BotKey.KEY_GET_MORE_MAGNETS_BY_ID:
        bot_utils.get_more_magnets_by_id(id=content)
    elif key_type == BotKey.KEY_RANDOM_GET_V_BY_STAR_ID:
        tmp = content.split("|")
        star_name = tmp[0]
        star_id = tmp[1]
        code, id = JBUS_UTIL.get_id_by_star_id(star_id=star_id)
        if bot_utils.check_success(
            code, f"从演职人员 <code>{star_name}</code> 随机选取作品"
        ):
            bot_utils.get_v_by_id(id=id)
    elif key_type == BotKey.KEY_GET_NEW_VS_BY_STAR_NAME_ID:
        tmp = content.split("|")
        star_name = tmp[0]
        star_id = tmp[1]
        bot_utils.get_star_new_vs_by_name_id(star_name=star_name, star_id=star_id)
    elif key_type == BotKey.KEY_RECORD_STAR_BY_STAR_NAME_ID:
        s = content.find("|")
        star_name = content[:s]
        star_id = content[s + 1 :]
        if BOT_DB.record_star_by_name_id(star_name=star_name, star_id=star_id):
            bot_utils.get_star_detail_record_by_name_id(
                star_name=star_name, star_id=star_id
            )
        else:
            bot_utils.send_msg_code_op(500, f"收藏演职人员 <code>{star_name}</code>")
    elif key_type == BotKey.KEY_RECORD_V_BY_ID_STAR_IDS:
        res = content.split("|")
        id = res[0]
        stars = []
        if res[1] != "":
            stars = [s for s in res[1:]]
        if BOT_DB.record_id_by_id_stars(id=id, stars=stars):
            bot_utils.get_v_detail_record_by_id(id=id)
        else:
            bot_utils.send_msg_code_op(500, f"收藏编号 <code>{id}</code>")
    elif key_type == BotKey.KEY_GET_STARS_RECORD:
        bot_utils.get_stars_record(page=int(content))
    elif key_type == BotKey.KEY_GET_VS_RECORD:
        bot_utils.get_vs_record(page=int(content))
    elif key_type == BotKey.KEY_GET_STAR_DETAIL_RECORD_BY_STAR_NAME_ID:
        s = content.find("|")
        bot_utils.get_star_detail_record_by_name_id(
            star_name=content[:s], star_id=content[s + 1 :]
        )
    elif key_type == BotKey.KEY_GET_V_DETAIL_RECORD_BY_ID:
        bot_utils.get_v_detail_record_by_id(id=content)
    elif key_type == BotKey.KEY_GET_V_BY_ID:
        bot_utils.get_v_by_id(id=content)
    elif key_type == BotKey.KEY_RANDOM_GET_V_NICE:
        code, id = JLIB_UTIL.get_random_id_from_rank(0)
        if bot_utils.check_success(code, "随机获取高分影片"):
            bot_utils.get_v_by_id(id=id)
    elif key_type == BotKey.KEY_RANDOM_GET_V_NEW:
        code, id = JLIB_UTIL.get_random_id_from_rank(1)
        if bot_utils.check_success(code, "随机获取最新影片"):
            bot_utils.get_v_by_id(id=id)
    elif key_type == BotKey.KEY_UNDO_RECORD_V_BY_ID:
        op_undo_record_v = f"取消收藏编号 <code>{content}</code>"
        if BOT_DB.undo_record_id(id=content):
            bot_utils.send_msg_success_op(op_undo_record_v)
        else:
            bot_utils.send_msg_fail_reason_op(
                reason="文件解析错误", op=op_undo_record_v
            )
    elif key_type == BotKey.KEY_UNDO_RECORD_STAR_BY_STAR_NAME_ID:
        s = content.find("|")
        op_undo_record_star = f"取消收藏演职人员 <code>{content[:s]}</code>"
        if BOT_DB.undo_record_star_by_id(star_id=content[s + 1 :]):
            bot_utils.send_msg_success_op(op_undo_record_star)
        else:
            bot_utils.send_msg_fail_reason_op(
                reason="文件解析错误", op=op_undo_record_star
            )
    elif key_type == BotKey.KEY_SEARCH_STAR_BY_NAME:
        star_name = content
        star_name_alias = ""
        idx_alias = star_name.find("（")
        if idx_alias != -1:
            star_name_alias = star_name[idx_alias + 1 : -1]
            star_name = star_name[:idx_alias]
        if not bot_utils.search_star_by_name(star_name) and star_name_alias != "":
            bot_utils.send_msg(
                f"尝试搜索演职人员 {star_name} 的别名 {star_name_alias}..."
            )
            bot_utils.search_star_by_name(star_name_alias)
    elif key_type == BotKey.KEY_GET_NICE_VS_BY_STAR_NAME:
        bot_utils.random_get_nice_star_vs(content)
    elif key_type == BotKey.KEY_DEL_V_CACHE:
        BOT_CACHE_DB.remove_cache(key=content, type=BotCacheDb.TYPE_V)
        BOT_CACHE_DB.remove_cache(key=content, type=BotCacheDb.TYPE_STARS_MSG)
        bot_utils.get_v_by_id(id=content)
    elif key_type == BotKey.KEY_BT_PAGE:
        tmp = content.split("|")
        bot_utils.show_bt_page(token=tmp[0], page=int(tmp[1]))


def handle_message(message):
    bot_utils = BotUtils()
    bot_utils.send_action_typing()
    chat_id = str(message.chat.id)
    if chat_id.lower() != BOT_CFG.tg_chat_id.lower():
        return
    bot_utils = BotUtils()
    if message.content_type != "text":
        msg = message.caption
    else:
        msg = message.text
    if not msg:
        return
    LOG.info(f'Get message: "{msg}"')
    msg = msg.lower().strip()
    msgs = msg.split(" ", 1)
    msg_cmd = msgs[0]
    msg_param = ""
    if len(msgs) > 1:
        msg_param = msgs[1].strip()
    if msg_cmd == "/help" or msg_cmd == "/start":
        bot_utils.send_msg(MSG_HELP)
    elif msg_cmd == "/stars":
        bot_utils.get_stars_record()
    elif msg_cmd == "/ids":
        bot_utils.get_vs_record()
    elif msg_cmd == "/record":
        if not os.path.exists(PATH_RECORD_FILE):
            bot_utils.send_msg_fail_reason_op(
                reason="还没有任何收藏记录", op="导出收藏记录"
            )
            return
        BOT.send_document(
            chat_id=BOT_CFG.tg_chat_id, document=types.InputFile(PATH_RECORD_FILE)
        )
    else:
        # 多轮会话：换一批 / 上一页 / 保存第 N 个
        if bot_utils.handle_bt_followup(msg):
            return
        ids = ID_PAT.findall(msg)
        if not ids or len(ids) == 0:
            # 优先走 AI 自然语言理解搜索，失败则退回 BT 关键词搜索
            if bot_utils.handle_nlp_search(msg):
                return
            bts = bot_utils.get_bts_by_keyword(msg)
            if not bts:
                bot_utils.send_msg_fail_reason_op(
                    reason="没有找到相关资源",
                    op=f"搜索 <code>{html.escape(msg)}</code>",
                )
                return
            bot_utils.show_bt_results(msg, bts)
        else:
            ids = [id.lower() for id in ids]
            ids = set(ids)
            ids_msg = ", ".join(ids)
            bot_utils.send_msg(f"已识别到编号：{ids_msg}，开始搜索...")
            for i, id in enumerate(ids):
                threading.Thread(target=bot_utils.get_v_by_id, args=(id,)).start()


@BOT.callback_query_handler(func=lambda call: True)
def my_callback_handler(call):
    EXECUTOR.submit(handle_callback, call)


@BOT.message_handler(content_types=["text", "photo", "animation", "video", "document"])
def my_message_handler(message):
    EXECUTOR.submit(handle_message, message)


def main():
    try:
        bot_info = BOT.get_me()
        LOG.info(f"Connected to bot: @{bot_info.username} (ID: {bot_info.id})")
        if PIKPAK.enabled:
            ok, msg = PIKPAK.ensure_login()
            if ok:
                LOG.info(f"PikPak: {msg}")
            else:
                LOG.error(f"PikPak login failed: {msg}")
        LOG.info("Connected to api")
    except Exception as e:
        LOG.error(f"Unable to connect to bot or api: {e}")
        return
    BOT.set_my_commands([types.BotCommand(cmd, BOT_CMDS[cmd]) for cmd in BOT_CMDS])
    BOT.infinity_polling()


if __name__ == "__main__":
    main()
