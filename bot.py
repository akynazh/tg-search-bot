import concurrent.futures
import math
import os
import re
import string
import random
import jvav
import yaml
import asyncio
import threading
import langdetect
import telebot
from pyrogram import Client
from telebot import apihelper, types
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from database import BotFileDb, BotCacheDb
from requests import get
from requests.compat import quote
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
        self.use_proxy = str(config["use_proxy"]) if config["use_proxy"] else "0"
        self.use_proxy_dmm = (
            str(config["use_proxy_dmm"]) if config["use_proxy_dmm"] else "0"
        )
        self.proxy_addr = str(config["proxy_addr"]) if config["proxy_addr"] else ""
        self.use_pikpak = str(config["use_pikpak"]) if config["use_pikpak"] else "0"
        self.tg_api_id = str(config["tg_api_id"]) if config["tg_api_id"] else ""
        self.tg_api_hash = str(config["tg_api_hash"]) if config["tg_api_hash"] else ""
        self.use_cache = str(config["use_cache"]) if config["use_cache"] else "0"
        self.redis_host = str(config["redis_host"]) if config["redis_host"] else ""
        self.redis_port = str(config["redis_port"]) if config["redis_port"] else ""
        self.redis_password = (
            str(config["redis_password"]) if config["redis_password"] else ""
        )
        self.enable_nsfw = str(config["enable_nsfw"]) if config["enable_nsfw"] else "0"
        # set
        self.proxy_addr_dmm = ""
        self.proxy_json = {"http": "", "https": ""}
        self.proxy_json_pikpak = {}
        if self.use_proxy == "1":
            self.proxy_json = {"http": self.proxy_addr, "https": self.proxy_addr}
            self.proxy_addr_dmm = self.proxy_addr
            t1 = self.proxy_addr.find(":")
            t2 = self.proxy_addr.rfind(":")
            self.proxy_json_pikpak = {
                "scheme": self.proxy_addr[:t1],
                "hostname": self.proxy_addr[t1 + 3: t2],
                "port": int(self.proxy_addr[t2 + 1:]),
            }
            LOG.info(f'Set proxy: "{self.proxy_addr}"')
        elif self.use_proxy_dmm == "1":
            self.proxy_addr_dmm = self.proxy_addr
            self.proxy_addr = ""
            LOG.info(f'Set dmm proxy: "{self.proxy_addr_dmm}"')
        else:
            self.proxy_addr = ""
        LOG.info("Successfully read and loaded the configuration file.")


# URL
BASE_URL_TG = "https://t.me"
BASE_URL_MISS_AV = "https://missav.com"
PIKPAK_BOT_NAME = "PikPak6_Bot"
URL_PROJECT_ADDRESS = "https://github.com/akynazh/tg-search-bot"
URL_AUTHOR = f"{BASE_URL_TG}/jackbryant286"
URL_PIKPAK_BOT = f"{BASE_URL_TG}/{PIKPAK_BOT_NAME}"
# PATH
PATH_ROOT = f'{os.path.expanduser("~")}/.tg_search_bot'
PATH_LOG_FILE = f"{PATH_ROOT}/log.txt"
PATH_RECORD_FILE = f"{PATH_ROOT}/record.json"
PATH_SESSION_FILE = f"{PATH_ROOT}/session"
PATH_CONFIG_FILE = f"{PATH_ROOT}/config.yaml"
# BASE
LOG = Logger(path_log_file=PATH_LOG_FILE).logger
BOT_CFG = BotConfig(PATH_CONFIG_FILE)
apihelper.proxy = BOT_CFG.proxy_json
BOT = telebot.TeleBot(BOT_CFG.tg_bot_token)
BOT_DB = BotFileDb(PATH_RECORD_FILE)
BOT_CACHE_DB = BotCacheDb(
    host=BOT_CFG.redis_host,
    port=int(BOT_CFG.redis_port),
    password=BOT_CFG.redis_password,
    use_cache=BOT_CFG.use_cache,
)
BASE_UTIL = jvav.BaseUtil(BOT_CFG.proxy_addr)
DMM_UTIL = jvav.DmmUtil(BOT_CFG.proxy_addr_dmm)
JAVBUS_UTIL = jvav.JavBusUtil(BOT_CFG.proxy_addr)
JAVDB_UTIL = jvav.JavDbUtil(BOT_CFG.proxy_addr)
JAVLIB_UTIL = jvav.JavLibUtil(BOT_CFG.proxy_addr)
SUKEBEI_UTIL = jvav.SukebeiUtil(BOT_CFG.proxy_addr)
TRANS_UTIL = jvav.TransUtil(BOT_CFG.proxy_addr)
WIKI_UTIL = jvav.WikiUtil(BOT_CFG.proxy_addr)
AVGLE_UTIL = jvav.AvgleUtil(BOT_CFG.proxy_addr)
EXECUTOR = concurrent.futures.ThreadPoolExecutor()
ID_PAT = re.compile(r"[a-z0-9]+[-_](?:ppv-)?[a-z0-9]+")
BOT_CMDS = {
    "help": "View command help",
    "stars": "View favorite actors",
    "ids": "View favorite numbers",
    "nice": "Randomly get a high-rated film",
    "new": "Randomly get a latest film",
    "rank": "Get DMM actor rankings",
    "record": "Get saved records file",
    "star": "Followed by the actor's name for searching the actor",
    "id": "Followed by the number for searching the number",
}
MSG_HELP = f"""Just send me the movie title, keywords, or number, and I'll take care of the rest!

"""
for cmd, content in BOT_CMDS.items():
    MSG_HELP += f"""/{cmd}  {content}
"""
MSG_HELP += f"""
[NSFW: {"OPENED" if BOT_CFG.enable_nsfw == "1" else "CLOSED"}]"""


class BotKey:
    KEY_GET_SAMPLE_BY_ID = "k0_0"
    KEY_GET_MORE_MAGNETS_BY_ID = "k0_1"
    KEY_SEARCH_STAR_BY_NAME = "k0_2"
    KEY_GET_TOP_STARS = "k0_3"
    KEY_WATCH_PV_BY_ID = "k1_0"
    KEY_WATCH_FV_BY_ID = "k1_1"
    KEY_GET_AV_BY_ID = "k2_0"
    KEY_RANDOM_GET_AV_BY_STAR_ID = "k2_1"
    KEY_RANDOM_GET_AV_NICE = "k2_2"
    KEY_RANDOM_GET_AV_NEW = "k2_3"
    KEY_GET_NEW_AVS_BY_STAR_NAME_ID = "k2_4"
    KEY_GET_NICE_AVS_BY_STAR_NAME = "k2_5"
    KEY_RECORD_STAR_BY_STAR_NAME_ID = "k3_0"
    KEY_RECORD_AV_BY_ID_STAR_IDS = "k3_1"
    KEY_GET_STARS_RECORD = "k3_2"
    KEY_GET_AVS_RECORD = "k3_3"
    KEY_GET_STAR_DETAIL_RECORD_BY_STAR_NAME_ID = "k3_4"
    KEY_GET_AV_DETAIL_RECORD_BY_ID = "k3_5"
    KEY_UNDO_RECORD_STAR_BY_STAR_NAME_ID = "k3_6"
    KEY_UNDO_RECORD_AV_BY_ID = "k3_7"
    KEY_DEL_AV_CACHE = "k4_1"


class BotUtils:
    av_utils = [JAVDB_UTIL, JAVBUS_UTIL, SUKEBEI_UTIL]

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
            self.send_msg(f"Operation executed: {op}\nExecution result: Success ^_^")
        elif code == 404:
            self.send_msg(
                f"Operation executed: {op}\nExecution result: No results found Q_Q"
            )
        elif code == 500:
            self.send_msg(
                f"Operation executed: {op}\nExecution result: Server error, please retry or check logs Q_Q"
            )
        elif code == 502:
            self.send_msg(
                f"Operation executed: {op}\nExecution result: Network request failed, please retry or check network Q_Q"
            )

    def send_msg_success_op(self, op: str):
        self.send_msg(f"Operation executed: {op}\nExecution result: Success ^_^")

    def send_msg_fail_reason_op(self, reason: str, op: str):
        self.send_msg(
            f"Operation executed: {op}\nExecution result: Failed, {reason} Q_Q"
        )

    def check_success(self, code: int, op: str):
        if code == 200:
            return True
        if code == 404:
            self.send_msg_fail_reason_op(reason="No results found", op=op)
        elif code == 500:
            self.send_msg_fail_reason_op(reason="Server error", op=op)
        elif code == 502:
            self.send_msg_fail_reason_op(reason="Network request failed", op=op)
        return False

    def create_btn_by_key(self, key_type: str, obj):
        if key_type == BotKey.KEY_GET_STAR_DETAIL_RECORD_BY_STAR_NAME_ID:
            return InlineKeyboardButton(
                text=obj["name"], callback_data=f'{obj["name"]}|{obj["id"]}:{key_type}'
            )
        elif key_type == BotKey.KEY_GET_AV_DETAIL_RECORD_BY_ID:
            return InlineKeyboardButton(text=obj, callback_data=f"{obj}:{key_type}")
        elif key_type == BotKey.KEY_SEARCH_STAR_BY_NAME:
            return InlineKeyboardButton(text=obj, callback_data=f"{obj}:{key_type}")
        elif key_type == BotKey.KEY_GET_AV_BY_ID:
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
        objs = objs[start_idx: start_idx + record_count_per_page]
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
        title = f"Total: <b>{record_count_total}</b>, Total Pages: <b>{page_count}</b>"
        return (
            objs,
            [btn_to_first, btn_to_previous, btn_to_current, btn_to_next, btn_to_last],
            title,
        )

    def check_if_enable_nsfw(self):
        if BOT_CFG.enable_nsfw == "0":
            self.send_msg("[NSFW] FORBIDDEN!")
            return False
        return True

    def get_stars_record(self, page=1):
        record, is_star_exists, _ = BOT_DB.check_has_record()
        if not record or not is_star_exists:
            self.send_msg_fail_reason_op(
                reason="No actor favorite records yet", op="Get actor favorite records"
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
            title="<b>Favorite Actors: </b>" + title,
            objs=objs,
            page_btns=page_btns,
        )

    def get_star_detail_record_by_name_id(self, star_name: str, star_id: str):
        record, is_stars_exists, is_avs_exists = BOT_DB.check_has_record()
        if not record:
            self.send_msg_fail_reason_op(
                reason="No favorite records for this actor",
                op=f"Get more information about actor <code>{star_name}</code>",
            )
            return
        avs = []
        star_avs = []
        cur_star_exists = False
        if is_avs_exists:
            avs = record["avs"]
            avs.reverse()
            for av in avs:
                if star_id in av["stars"]:
                    star_avs.append(av["id"])
        if is_stars_exists:
            stars = record["stars"]
            for star in stars:
                if star["id"].lower() == star_id.lower():
                    cur_star_exists = True
        extra_btn1 = InlineKeyboardButton(
            text="Random AV",
            callback_data=f"{star_name}|{star_id}:{BotKey.KEY_RANDOM_GET_AV_BY_STAR_ID}",
        )
        extra_btn2 = InlineKeyboardButton(
            text="Latest AV",
            callback_data=f"{star_name}|{star_id}:{BotKey.KEY_GET_NEW_AVS_BY_STAR_NAME_ID}",
        )
        extra_btn3 = InlineKeyboardButton(
            text="High-rated AV",
            callback_data=f"{star_name}:{BotKey.KEY_GET_NICE_AVS_BY_STAR_NAME}",
        )
        if cur_star_exists:
            extra_btn4 = InlineKeyboardButton(
                text="Remove from Favorites",
                callback_data=f"{star_name}|{star_id}:{BotKey.KEY_UNDO_RECORD_STAR_BY_STAR_NAME_ID}",
            )
        else:
            extra_btn4 = InlineKeyboardButton(
                text="Add to Favorites",
                callback_data=f"{star_name}|{star_id}:{BotKey.KEY_RECORD_STAR_BY_STAR_NAME_ID}",
            )
        title = f'<code>{star_name}</code> | <a href="{WIKI_UTIL.BASE_URL_JAPAN_WIKI}/{star_name}">Wiki</a> | <a href="{JAVBUS_UTIL.base_url_search_by_star_id}/{star_id}">Javbus</a>'
        if len(star_avs) == 0:
            markup = InlineKeyboardMarkup()
            markup.row(extra_btn1, extra_btn2, extra_btn3, extra_btn4)
            self.send_msg(msg=title, markup=markup)
            return
        self.send_msg_btns(
            max_btn_per_row=4,
            max_row_per_msg=10,
            key_type=BotKey.KEY_GET_AV_DETAIL_RECORD_BY_ID,
            title=title,
            objs=star_avs,
            extra_btns=[[extra_btn1, extra_btn2, extra_btn3, extra_btn4]],
        )

    def get_avs_record(self, page=1):
        record, _, is_avs_exists = BOT_DB.check_has_record()
        if not record or not is_avs_exists:
            self.send_msg_fail_reason_op(
                reason="No number favorite records yet",
                op="Get number favorite records",
            )
            return
        avs = [av["id"] for av in record["avs"]]
        avs.reverse()
        extra_btn1 = InlineKeyboardButton(
            text="Random High-rated AV",
            callback_data=f"0:{BotKey.KEY_RANDOM_GET_AV_NICE}",
        )
        extra_btn2 = InlineKeyboardButton(
            text="Random Latest AV", callback_data=f"0:{BotKey.KEY_RANDOM_GET_AV_NEW}"
        )
        col, row = 4, 10
        objs, page_btns, title = self.get_page_elements(
            objs=avs, page=page, col=col, row=row, key_type=BotKey.KEY_GET_AVS_RECORD
        )
        self.send_msg_btns(
            max_btn_per_row=col,
            max_row_per_msg=row,
            key_type=BotKey.KEY_GET_AV_DETAIL_RECORD_BY_ID,
            title="<b>Favorite Numbers: </b>" + title,
            objs=objs,
            extra_btns=[[extra_btn1, extra_btn2]],
            page_btns=page_btns,
        )

    def get_av_detail_record_by_id(self, id: str):
        record, _, is_avs_exists = BOT_DB.check_has_record()
        avs = record["avs"]
        cur_av_exists = False
        for av in avs:
            if id.lower() == av["id"].lower():
                cur_av_exists = True
        markup = InlineKeyboardMarkup()
        btn = InlineKeyboardButton(
            text=f"Get corresponding AV",
            callback_data=f"{id}:{BotKey.KEY_GET_AV_BY_ID}",
        )
        if cur_av_exists:
            markup.row(
                btn,
                InlineKeyboardButton(
                    text=f"Unfavorite",
                    callback_data=f"{id}:{BotKey.KEY_UNDO_RECORD_AV_BY_ID}",
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
            if size >= 1024 ** 2:
                size_str = f"{(size / 1024 ** 2):.2f} mb"
            if size >= 1024 ** 3:
                size_str = f"{(size / 1024 ** 3):.2f} gb"
            return size_str

        def magnet_link(ih, name):
            """Creates the magnet URI"""
            return f"magnet:?xt=urn:btih:{ih}&dn={quote(name)}&tr={append_trackers()}"

        agent = BASE_UTIL.ua()
        url = f"https://apibay.org/q.php?q={quote(q)}"
        results = get(url, headers={"agent": agent})
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

    def get_av_by_id(
            self,
            id: str,
            send_to_pikpak=False,
            is_nice=True,
            is_uncensored=True,
            magnet_max_count=3,
            not_send=False,
    ):
        """
        Get AV based on number

        :param str id: Number
        :param bool send_to_pikpak: Whether to send to pikpak, default is not
        :param bool is_nice: Whether to filter out HD, subtitled magnet links, default is yes
        :param bool is_uncensored: Whether to filter out uncensored magnet links, default is yes
        :param int magnet_max_count: Maximum number of magnet links after filtering, default is 3
        :param not_send: Whether not to send AV results, default is to send
        :return dict: When not sending AV results, return the obtained AV (if any)
        """
        if not self.check_if_enable_nsfw():
            return {}
        op_get_av_by_id = f"Search code: <code>{id}</code>"
        av = BOT_CACHE_DB.get_cache(key=id, type=BotCacheDb.TYPE_AV)
        av_score = None
        is_cache = False
        if not av or not_send:
            for util in self.av_utils:
                code, av = util.get_av_by_id(
                    id=id,
                    is_nice=is_nice,
                    is_uncensored=is_uncensored,
                    magnet_max_count=magnet_max_count,
                )
                if code == 200:
                    av_util = util
                    break
            if not av_util:
                if not not_send:
                    self.send_msg_av_not_found(
                        av_id=id,
                        op=op_get_av_by_id,
                        reason="Can not find result, try again later.",
                    )
                return
            if "score" not in av.keys():
                _, av["score"] = DMM_UTIL.get_score_by_id(id)
            if not not_send:
                if len(av["magnets"]) == 0:
                    BOT_CACHE_DB.set_cache(
                        key=id, value=av, type=BotCacheDb.TYPE_AV, expire=3600 * 24 * 1
                    )
                else:
                    BOT_CACHE_DB.set_cache(key=id, value=av, type=BotCacheDb.TYPE_AV)
        else:
            av_score = av["score"]
            is_cache = True
        if not_send:
            return av
        av_id = id
        av_title = av["title"]
        av_img = av["img"]
        av_date = av["date"]
        av_tags = av["tags"]
        av_stars = av["stars"]
        av_magnets = av["magnets"]
        av_url = av["url"]
        msg = ""
        if av_title != "":
            av_title = av_title.replace("<", "").replace(">", "")
            msg += f"""【Title】<a href="{av_url}">{av_title}</a>
"""
        msg += f"""【Code】<code>{av_id}</code>
"""
        if av_date != "":
            msg += f"""【Date】{av_date}
"""
        if av_score:
            msg += f"""【Score】{av_score}
"""
        if av_stars != []:
            show_star_name = av_stars[0]["name"]
            show_star_id = av_stars[0]["id"]
            stars_msg = ""
            for star in av_stars:
                stars_msg += f"""【Actor】<code>{star["name"]}</code>
"""
            msg += stars_msg
        if av_tags:
            av_tags = " ".join(av_tags).replace("<", "").replace(">", "")
            msg += f"""【Tags】{av_tags}
"""
        msg += f"""【Other】<a href="{URL_PIKPAK_BOT}">Pikpak</a> | <a href="{URL_PROJECT_ADDRESS}">Project</a> | <a href="{URL_AUTHOR}">Author</a>
"""
        magnet_send_to_pikpak = ""
        for i, magnet in enumerate(av_magnets):
            if i == 0:
                magnet_send_to_pikpak = magnet["link"]
            magnet_tags = ""
            if magnet["uc"] == "1":
                magnet_tags += "UC "
            if magnet["hd"] == "1":
                magnet_tags += "HD "
            if magnet["zm"] == "1":
                magnet_tags += "SUB "
            msg_tmp = f"""【{magnet_tags} Magnet-{string.ascii_letters[i].upper()} {magnet["size"]}】<code>{magnet["link"]}</code>
"""
            if len(msg + msg_tmp) >= 2000:
                break
            msg += msg_tmp
        pv_btn = InlineKeyboardButton(
            text="Preview", callback_data=f"{av_id}:{BotKey.KEY_WATCH_PV_BY_ID}"
        )
        fv_btn = InlineKeyboardButton(
            text="Watch", callback_data=f"{av_id}:{BotKey.KEY_WATCH_FV_BY_ID}"
        )
        sample_btn = InlineKeyboardButton(
            text="Screenshot", callback_data=f"{av_id}:{BotKey.KEY_GET_SAMPLE_BY_ID}"
        )
        more_btn = InlineKeyboardButton(
            text="More Magnets",
            callback_data=f"{av_id}:{BotKey.KEY_GET_MORE_MAGNETS_BY_ID}",
        )
        if len(av_magnets) != 0:
            markup = InlineKeyboardMarkup().row(sample_btn, pv_btn, fv_btn, more_btn)
        else:
            markup = InlineKeyboardMarkup().row(sample_btn, pv_btn, fv_btn)
        star_record_btn = None
        if len(av_stars) == 1:
            if BOT_DB.check_star_exists_by_id(star_id=show_star_id):
                star_record_btn = InlineKeyboardButton(
                    text=f"Actor Collection Info",
                    callback_data=f"{show_star_name}|{show_star_id}:{BotKey.KEY_GET_STAR_DETAIL_RECORD_BY_STAR_NAME_ID}",
                )
            else:
                star_record_btn = InlineKeyboardButton(
                    text=f"Collect {show_star_name}",
                    callback_data=f"{show_star_name}|{show_star_id}:{BotKey.KEY_RECORD_STAR_BY_STAR_NAME_ID}",
                )
        star_ids = ""
        for i, star in enumerate(av_stars):
            star_ids += star["id"] + "|"
            if i >= 5:
                star_ids += "...|"
                break
        if star_ids != "":
            star_ids = star_ids[: len(star_ids) - 1]
        av_record_btn = None
        if BOT_DB.check_id_exists(id=av_id):
            av_record_btn = InlineKeyboardButton(
                text=f"Code Collection Info",
                callback_data=f"{av_id}:{BotKey.KEY_GET_AV_DETAIL_RECORD_BY_ID}",
            )
        else:
            av_record_btn = InlineKeyboardButton(
                text=f"Collect {av_id}",
                callback_data=f"{av_id}|{star_ids}:{BotKey.KEY_RECORD_AV_BY_ID_STAR_IDS}",
            )
        renew_btn = None
        if is_cache:
            renew_btn = InlineKeyboardButton(
                text="Retry", callback_data=f"{av_id}:{BotKey.KEY_DEL_AV_CACHE}"
            )
        if star_record_btn and renew_btn:
            markup.row(av_record_btn, star_record_btn, renew_btn)
        elif star_record_btn:
            markup.row(av_record_btn, star_record_btn)
        elif renew_btn:
            markup.row(av_record_btn, renew_btn)
        else:
            markup.row(av_record_btn)
        if av_img == "":
            self.send_msg(msg=msg, markup=markup)
        else:
            try:
                BOT.send_photo(
                    chat_id=BOT_CFG.tg_chat_id,
                    photo=av_img,
                    caption=msg,
                    parse_mode="HTML",
                    reply_markup=markup,
                )
            except Exception:
                self.send_msg(msg=msg, markup=markup)
        if BOT_CFG.use_pikpak == "1" and magnet_send_to_pikpak != "" and send_to_pikpak:
            self.send_magnet_to_pikpak(magnet_send_to_pikpak, av_id)

    def send_magnet_to_pikpak(self, magnet: str, id: str):
        op_send_magnet_to_pikpak = (
            f"Sending the magnet link A for code {id}: <code>{magnet}</code> to Pikpak."
        )
        if self.send_msg_to_pikpak(magnet):
            self.send_msg_success_op(op_send_magnet_to_pikpak)
        else:
            self.send_msg_fail_reason_op(
                reason="Please verify the network or logs yourself.",
                op=op_send_magnet_to_pikpak,
            )

    def get_sample_by_id(self, id: str):
        op_get_sample = f"Get AV screenshots based on the code <code>{id}</code>."
        samples = BOT_CACHE_DB.get_cache(key=id, type=BotCacheDb.TYPE_SAMPLE)
        if not samples:
            code, samples = JAVBUS_UTIL.get_samples_by_id(id)
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
                        reason="The image parsing failed.", op=op_get_sample
                    )
                    break
        if samples_imp != [] and not sample_error:
            try:
                BOT.send_media_group(chat_id=BOT_CFG.tg_chat_id, media=samples_imp)
            except Exception:
                self.send_msg_fail_reason_op(
                    reason="The image parsing failed.", op=op_get_sample
                )

    def watch_av_by_id(self, id: str, type: int):
        id = id.lower()
        if id.find("fc2") != -1 and id.find("ppv") == -1:
            id = id.replace("fc2", "fc2-ppv")
        if type == 0:
            pv = BOT_CACHE_DB.get_cache(key=id, type=BotCacheDb.TYPE_PV)
            if not pv:
                op_watch_av = f"Retrieve preview video for the code <code>{id}</code>."
                futures = {}
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    futures[executor.submit(DMM_UTIL.get_pv_by_id, id)] = 1
                    futures[executor.submit(AVGLE_UTIL.get_pv_by_id, id)] = 2
                    for future in concurrent.futures.as_completed(futures):
                        if futures[future] == 1:
                            code_dmm, pv_dmm = future.result()
                        elif futures[future] == 2:
                            code_avgle, pv_avgle = future.result()
                if code_dmm != 200 and code_avgle != 200:
                    if code_dmm == 502 or code_avgle == 502:
                        self.send_msg_code_op(502, op_watch_av)
                    else:
                        self.send_msg_code_op(404, op_watch_av)
                    return
                from_site = ""
                pv_src = ""
                if code_dmm == 200:
                    from_site = "dmm"
                    pv_src = pv_dmm
                elif code_avgle == 200:
                    from_site = "avgle"
                    pv_src = pv_avgle
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
                        caption=f'Results obtained through DMM search. <a href="{pv_src_nice}">Watch a clearer version here</a>.',
                        parse_mode="HTML",
                    )
                except Exception:
                    self.send_msg(
                        f'Results obtained through DMM search, but video parsing failed: <a href="{pv_src_nice}">Video Link</a> Q_Q.'
                    )
            elif from_site == "avgle":
                try:
                    BOT.send_video(
                        chat_id=BOT_CFG.tg_chat_id,
                        video=pv_src,
                        caption=f'Results obtained through Avgle search: <a href="{pv_src}">Video Link</a>.',
                        parse_mode="HTML",
                    )
                except Exception:
                    self.send_msg(
                        f'Results obtained through Avgle search, but video parsing failed: <a href="{pv_src}">Video Link</a> Q_Q.'
                    )
        elif type == 1:
            video = BOT_CACHE_DB.get_cache(key=id, type=BotCacheDb.TYPE_FV)
            if not video:
                code, video = AVGLE_UTIL.get_fv_by_id(id)
                if code != 200:
                    self.send_msg(f"MissAv video link: {BASE_URL_MISS_AV}/{id}")
                    return
                BOT_CACHE_DB.set_cache(key=id, value=video, type=BotCacheDb.TYPE_FV)
            self.send_msg(
                f"""MissAv video link: {BASE_URL_MISS_AV}/{id}

Avgle video link: {video}
"""
            )

    def search_star_by_name(self, star_name: str):
        if not self.check_if_enable_nsfw():
            return False
        op_search_star = f"Search actor: <code>{star_name}</code>"
        star = BOT_CACHE_DB.get_cache(key=star_name, type=BotCacheDb.TYPE_STAR)
        if not star:
            star_name_origin = star_name
            star_name = self.get_star_ja_name_by_zh_name(star_name)
            code, star = JAVBUS_UTIL.check_star_exists(star_name)
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
                text="Random AV",
                callback_data=f"{star_name}|{star_id}:{BotKey.KEY_RANDOM_GET_AV_BY_STAR_ID}",
            ),
            InlineKeyboardButton(
                text="Latest AV",
                callback_data=f"{star_name}|{star_id}:{BotKey.KEY_GET_NEW_AVS_BY_STAR_NAME_ID}",
            ),
            InlineKeyboardButton(
                text=f"High Rated AV",
                callback_data=f"{star_name}:{BotKey.KEY_GET_NICE_AVS_BY_STAR_NAME}",
            ),
            InlineKeyboardButton(
                text=f"Bookmark {star_name}",
                callback_data=f"{star_name}|{star_id}:{BotKey.KEY_RECORD_STAR_BY_STAR_NAME_ID}",
            ),
        )
        star_wiki = f"{WIKI_UTIL.BASE_URL_CHINA_WIKI}/{star_name}"
        if langdetect.detect(star_name) == "ja":
            star_wiki = f"{WIKI_UTIL.BASE_URL_JAPAN_WIKI}/{star_name}"
        self.send_msg(
            msg=f'<code>{star_name}</code> | <a href="{star_wiki}">Wiki</a> | <a href="{JAVBUS_UTIL.base_url_search_by_star_name}/{star_name}">Javbus</a>',
            markup=markup,
        )
        return True

    def get_top_stars(self, page=1):
        op_get_top_stars = f"Get DMM Actress Ranking"
        stars = BOT_CACHE_DB.get_cache(key=page, type=BotCacheDb.TYPE_RANK)

        if not stars:
            code, stars = DMM_UTIL.get_top_stars(page)
            if not self.check_success(code, op_get_top_stars):
                return
            BOT_CACHE_DB.set_cache(key=page, value=stars, type=BotCacheDb.TYPE_RANK)
        stars_tmp = [None] * 80
        stars = stars_tmp[: ((page - 1) * 20)] + stars + stars_tmp[((page - 1) * 20):]
        col, row = 4, 5
        objs, page_btns, title = self.get_page_elements(
            objs=stars, page=page, col=4, row=5, key_type=BotKey.KEY_GET_TOP_STARS
        )
        self.send_msg_btns(
            max_btn_per_row=col,
            max_row_per_msg=row,
            key_type=BotKey.KEY_SEARCH_STAR_BY_NAME,
            title="<b>DMM Actress Ranking:</b>" + title,
            objs=objs,
            page_btns=page_btns,
        )

    def send_msg_to_pikpak(self, msg):

        async def send():
            try:
                async with Client(
                        name=PATH_SESSION_FILE,
                        api_id=BOT_CFG.tg_api_id,
                        api_hash=BOT_CFG.tg_api_hash,
                        proxy=BOT_CFG.proxy_json_pikpak,
                ) as app:
                    return await app.send_message(PIKPAK_BOT_NAME, msg)
            except Exception as e:
                LOG.error(f"Unable to send message to Pikpak: {e}")
                return None

        return asyncio.run(send())

    def get_more_magnets_by_id(self, id: str):
        magnets = BOT_CACHE_DB.get_cache(key=id, type=BotCacheDb.TYPE_MAGNET)
        if not magnets:
            av = self.get_av_by_id(
                id=id, is_nice=False, is_uncensored=False, not_send=True
            )
            if not av:
                return
            magnets = av["magnets"]
            BOT_CACHE_DB.set_cache(key=id, value=magnets, type=BotCacheDb.TYPE_MAGNET)
        msg = ""
        for magnet in magnets:
            magnet_tags = ""
            if magnet["uc"] == "1":
                magnet_tags += "Uncensored "
            if magnet["hd"] == "1":
                magnet_tags += "HD "
            if magnet["zm"] == "1":
                magnet_tags += "Subtitled "
            star_tag = ""
            if magnet["hd"] == "1" and magnet["zm"] == "1":
                star_tag = "*"
            msg_tmp = f"""【{star_tag}{magnet_tags}Magnet {magnet["size"]}】<code>{magnet["link"]}</code>
        """
            if len(msg + msg_tmp) >= 4000:
                self.send_msg(msg)
                msg = msg_tmp
            else:
                msg += msg_tmp
        if msg != "":
            self.send_msg(msg)

    def get_star_new_avs_by_name_id(self, star_name: str, star_id: str):
        op_get_star_new_avs = f"Get <code>{star_name}</code> Latest AVs"
        ids = BOT_CACHE_DB.get_cache(key=star_id, type=BotCacheDb.TYPE_NEW_AVS_OF_STAR)
        if not ids:
            code, ids = JAVBUS_UTIL.get_new_ids_by_star_id(star_id=star_id)
            if not self.check_success(code, op_get_star_new_avs):
                return
            BOT_CACHE_DB.set_cache(
                key=star_id, value=ids, type=BotCacheDb.TYPE_NEW_AVS_OF_STAR
            )
        title = f"<code>{star_name}</code> Latest AV"
        btns = [
            InlineKeyboardButton(
                text=id, callback_data=f"{id}:{BotKey.KEY_GET_AV_BY_ID}"
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

    def send_bts(self, q, bts):
        res = f"""Query results for {q}:

"""
        for bt in bts:
            if len(res) >= 3000:
                return
            res += f"""Name: {bt['name']}
Size: {bt['size']}
Category: {bt['category']}
Magnet: <code>{bt['magnet']}</code>

"""
        self.send_msg(
            res,
            markup=InlineKeyboardMarkup().row(
                InlineKeyboardButton(
                    "Go to PikPak Cloud Drive", url=URL_PIKPAK_BOT
                )
            ),
        )

    def random_get_new_av(self):
        page = random.randint(1, JAVLIB_UTIL.MAX_RANK_PAGE)
        ids = BOT_CACHE_DB.get_cache(key=page, type=BotCacheDb.TYPE_JLIB_PAGE_NEW_AVS)
        if not ids:
            code, ids = JAVLIB_UTIL.get_random_ids_from_rank_by_page(
                page=page, list_type=1
            )
            if self.check_success(code, "Randomly Fetch Latest AV"):
                BOT_CACHE_DB.set_cache(
                    key=page,
                    value=ids,
                    type=BotCacheDb.TYPE_JLIB_PAGE_NEW_AVS,
                )
            else:
                return
        self.get_av_by_id(id=random.choice(ids))

    def random_get_nice_av(self):
        page = random.randint(1, JAVLIB_UTIL.MAX_RANK_PAGE)
        ids = BOT_CACHE_DB.get_cache(key=page, type=BotCacheDb.TYPE_JLIB_PAGE_NICE_AVS)
        if not ids:
            code, ids = JAVLIB_UTIL.get_random_ids_from_rank_by_page(
                page=page, list_type=0
            )
            if self.check_success(code, "Randomly Fetch High-Rated AV"):
                BOT_CACHE_DB.set_cache(
                    key=page,
                    value=ids,
                    type=BotCacheDb.TYPE_JLIB_PAGE_NICE_AVS,
                )
            else:
                return
        self.get_av_by_id(id=random.choice(ids))

    def random_get_nice_star_avs(self, star_name_ori):
        avs = BOT_CACHE_DB.get_cache(
            key=star_name_ori, type=BotCacheDb.TYPE_NICE_AVS_OF_STAR
        )
        if not avs:
            star_name_ja = self.get_star_ja_name_by_zh_name(star_name_ori)
            code, avs = DMM_UTIL.get_nice_avs_by_star_name(star_name=star_name_ja)
            if self.check_success(
                    code, f"Get High-Rated AVs of Actress {star_name_ori}"
            ):
                avs = avs[:60]
                BOT_CACHE_DB.set_cache(
                    key=star_name_ori,
                    value=avs,
                    type=BotCacheDb.TYPE_NICE_AVS_OF_STAR,
                )
                if star_name_ja != star_name_ori:
                    BOT_CACHE_DB.set_cache(
                        key=star_name_ja,
                        value=avs,
                        type=BotCacheDb.TYPE_NICE_AVS_OF_STAR,
                    )
            else:
                return
        self.send_msg_btns(
            max_btn_per_row=3,
            max_row_per_msg=20,
            key_type=BotKey.KEY_GET_AV_BY_ID,
            title=f"<b>High-Rated AV of Actor {star_name_ori}</b>",
            objs=avs,
        )


def handle_callback(call):
    bot_utils = BotUtils()
    bot_utils.send_action_typing()
    LOG.info(f"Handle callback: {call.data}")
    s = call.data.rfind(":")
    content = call.data[:s]
    key_type = call.data[s + 1:]
    if key_type == BotKey.KEY_WATCH_PV_BY_ID:
        bot_utils.watch_av_by_id(id=content, type=0)
    elif key_type == BotKey.KEY_WATCH_FV_BY_ID:
        bot_utils.watch_av_by_id(id=content, type=1)
    elif key_type == BotKey.KEY_GET_SAMPLE_BY_ID:
        bot_utils.get_sample_by_id(id=content)
    elif key_type == BotKey.KEY_GET_MORE_MAGNETS_BY_ID:
        bot_utils.get_more_magnets_by_id(id=content)
    elif key_type == BotKey.KEY_RANDOM_GET_AV_BY_STAR_ID:
        tmp = content.split("|")
        star_name = tmp[0]
        star_id = tmp[1]
        code, id = JAVBUS_UTIL.get_id_by_star_id(star_id=star_id)
        if bot_utils.check_success(
                code, f"Randomly fetch AV of Actor <code>{star_name}</code>"
        ):
            bot_utils.get_av_by_id(id=id)
    elif key_type == BotKey.KEY_GET_NEW_AVS_BY_STAR_NAME_ID:
        tmp = content.split("|")
        star_name = tmp[0]
        star_id = tmp[1]
        bot_utils.get_star_new_avs_by_name_id(star_name=star_name, star_id=star_id)
    elif key_type == BotKey.KEY_RECORD_STAR_BY_STAR_NAME_ID:
        s = content.find("|")
        star_name = content[:s]
        star_id = content[s + 1:]
        if BOT_DB.record_star_by_name_id(star_name=star_name, star_id=star_id):
            bot_utils.get_star_detail_record_by_name_id(
                star_name=star_name, star_id=star_id
            )
        else:
            bot_utils.send_msg_code_op(500, f"Favorite Actor <code>{star_name}</code>")
    elif key_type == BotKey.KEY_RECORD_AV_BY_ID_STAR_IDS:
        res = content.split("|")
        id = res[0]
        stars = []
        if res[1] != "":
            stars = [s for s in res[1:]]
        if BOT_DB.record_id_by_id_stars(id=id, stars=stars):
            bot_utils.get_av_detail_record_by_id(id=id)
        else:
            bot_utils.send_msg_code_op(500, f"Favorite AV Code <code>{id}</code>")
    elif key_type == BotKey.KEY_GET_STARS_RECORD:
        bot_utils.get_stars_record(page=int(content))
    elif key_type == BotKey.KEY_GET_AVS_RECORD:
        bot_utils.get_avs_record(page=int(content))
    elif key_type == BotKey.KEY_GET_STAR_DETAIL_RECORD_BY_STAR_NAME_ID:
        s = content.find("|")
        bot_utils.get_star_detail_record_by_name_id(
            star_name=content[:s], star_id=content[s + 1:]
        )
    elif key_type == BotKey.KEY_GET_AV_DETAIL_RECORD_BY_ID:
        bot_utils.get_av_detail_record_by_id(id=content)
    elif key_type == BotKey.KEY_GET_AV_BY_ID:
        bot_utils.get_av_by_id(id=content)
    elif key_type == BotKey.KEY_RANDOM_GET_AV_NICE:
        code, id = JAVLIB_UTIL.get_random_id_from_rank(0)
        if bot_utils.check_success(code, "Randomly fetch high-rated AV"):
            bot_utils.get_av_by_id(id=id)
    elif key_type == BotKey.KEY_RANDOM_GET_AV_NEW:
        code, id = JAVLIB_UTIL.get_random_id_from_rank(1)
        if bot_utils.check_success(code, "Randomly fetch newest AV"):
            bot_utils.get_av_by_id(id=id)
    elif key_type == BotKey.KEY_UNDO_RECORD_AV_BY_ID:
        op_undo_record_av = f"Undo favorite AV code <code>{content}</code>"
        if BOT_DB.undo_record_id(id=content):
            bot_utils.send_msg_success_op(op_undo_record_av)
        else:
            bot_utils.send_msg_fail_reason_op(
                reason="File parsing error", op=op_undo_record_av
            )
    elif key_type == BotKey.KEY_UNDO_RECORD_STAR_BY_STAR_NAME_ID:
        s = content.find("|")
        op_undo_record_star = f"Undo favorite actor <code>{content[:s]}</code>"
        if BOT_DB.undo_record_star_by_id(star_id=content[s + 1:]):
            bot_utils.send_msg_success_op(op_undo_record_star)
        else:
            bot_utils.send_msg_fail_reason_op(
                reason="File parsing error", op=op_undo_record_star
            )
    elif key_type == BotKey.KEY_SEARCH_STAR_BY_NAME:
        star_name = content
        star_name_alias = ""
        idx_alias = star_name.find("（")
        if idx_alias != -1:
            star_name_alias = star_name[idx_alias + 1: -1]
            star_name = star_name[:idx_alias]
        if not bot_utils.search_star_by_name(star_name) and star_name_alias != "":
            bot_utils.send_msg(
                f"Attempting to search for actor {star_name}'s alias {star_name_alias}..."
            )
            bot_utils.search_star_by_name(star_name_alias)
    elif key_type == BotKey.KEY_GET_TOP_STARS:
        bot_utils.get_top_stars(page=int(content))
    elif key_type == BotKey.KEY_GET_NICE_AVS_BY_STAR_NAME:
        bot_utils.random_get_nice_star_avs(content)
    elif key_type == BotKey.KEY_DEL_AV_CACHE:
        BOT_CACHE_DB.remove_cache(key=content, type=BotCacheDb.TYPE_AV)
        BOT_CACHE_DB.remove_cache(key=content, type=BotCacheDb.TYPE_STARS_MSG)
        bot_utils.get_av_by_id(id=content)


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
    elif msg_cmd == "/nice":
        if not bot_utils.check_if_enable_nsfw():
            return
        bot_utils.random_get_nice_av()
    elif msg_cmd == "/new":
        if not bot_utils.check_if_enable_nsfw():
            return
        bot_utils.random_get_new_av()
    elif msg_cmd == "/stars":
        bot_utils.get_stars_record()
    elif msg_cmd == "/ids":
        bot_utils.get_avs_record()
    elif msg_cmd == "/record":
        if not os.path.exists(PATH_RECORD_FILE):
            bot_utils.send_msg_fail_reason_op(
                reason="No favorite records yet", op="Retrieve favorite records file"
            )
            return
        BOT.send_document(
            chat_id=BOT_CFG.tg_chat_id, document=types.InputFile(PATH_RECORD_FILE)
        )
    elif msg_cmd == "/rank":
        bot_utils.get_top_stars(1)
    elif msg_cmd == "/star":
        if msg_param:
            bot_utils.send_msg(f"Search actor: <code>{msg_param}</code> ......")
            bot_utils.search_star_by_name(msg_param)
    elif msg_cmd == "/id":
        if msg_param:
            bot_utils.send_msg(f"Search code: <code>{msg_param}</code> ......")
            bot_utils.get_av_by_id(id=msg_param, send_to_pikpak=True)
    else:
        ids = ID_PAT.findall(msg)
        if not ids or len(ids) == 0:
            op = f"Search <code>{msg}</code>"
            bts = BOT_CACHE_DB.get_cache(key=msg, type=BotCacheDb.TYPE_BT)
            if not bts:
                bts = bot_utils.search_bts(msg)
                if not bts:
                    bot_utils.send_msg_fail_reason_op(reason="No result", op=op)
                    return
                if BOT_CFG.enable_nsfw == "0":
                    bts = list(filter(lambda bt: bt["category"] != "nsfw", bts))
                    bts = list(filter(lambda bt: "nsfw" not in bt["name"].lower(), bts))
                bts = bts[:5]
                BOT_CACHE_DB.set_cache(key=msg, value=bts, type=BotCacheDb.TYPE_BT)
            bot_utils.send_bts(msg, bts)
        else:
            ids = [id.lower() for id in ids]
            ids = set(ids)
            ids_msg = ", ".join(ids)
            bot_utils.send_msg(f"Detected AV codes: {ids_msg}, starting search...")
            for i, id in enumerate(ids):
                threading.Thread(target=bot_utils.get_av_by_id, args=(id,)).start()


@BOT.callback_query_handler(func=lambda call: True)
def my_callback_handler(call):
    EXECUTOR.submit(handle_callback, call)


@BOT.message_handler(content_types=["text", "photo", "animation", "video", "document"])
def my_message_handler(message):
    EXECUTOR.submit(handle_message, message)


def pyrogram_auth():
    if BOT_CFG.use_pikpak == "1" and not os.path.exists(f"{PATH_SESSION_FILE}.session"):
        LOG.info("Performing Pyrogram login authentication...")
        try:
            BotUtils().send_msg_to_pikpak("Pyrogram login authentication")
            LOG.info("Pyrogram login authentication successful")
        except BaseException as e:
            LOG.error(f"Pyrogram login authentication failed: {e}")


def main():
    pyrogram_auth()
    try:
        bot_info = BOT.get_me()
        LOG.info(f"Connected to bot: @{bot_info.username} (ID: {bot_info.id})")
    except Exception as e:
        LOG.error(f"Unable to connect to bot: {e}")
        return
    BOT.set_my_commands([types.BotCommand(cmd, BOT_CMDS[cmd]) for cmd in BOT_CMDS])
    BOT.infinity_polling()


if __name__ == "__main__":
    main()
