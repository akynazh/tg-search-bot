# -*- coding: UTF-8 -*-
import asyncio
import concurrent.futures
import json
import logging
import math
import os
import re
import string
import typing

import jvav
import langdetect
import lxml
import redis
import telebot
import yaml
from pyrogram import Client
from telebot import apihelper, types
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto

# 定义回调按键值
KEY_GET_SAMPLE_BY_ID = "k0_0"
KEY_GET_MORE_MAGNETS_BY_ID = "k0_1"
KEY_SEARCH_STAR_BY_NAME = "k0_2"
KEY_GET_TOP_STARS = "k0_3"
KEY_WATCH_PV_BY_ID = "k1_0"
KEY_WATCH_FV_BY_ID = "k1_1"
KEY_GET_AV_BY_ID = "k2_0"
kEY_RANDOM_GET_AV_BY_STAR_ID = "k2_1"
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
# 项目地址
PROJECT_ADDRESS = "https://github.com/akynazh/tg-jav-bot"
# 默认使用官方机器人: https://t.me/PikPak6_Bot
PIKPAK_BOT_NAME = "PikPak6_Bot"
# 联系作者
CONTACT_AUTHOR = "https://t.me/jackbryant286"
# 文件存储目录位置
PATH_ROOT = f'{os.path.expanduser("~")}/.tg_jav_bot'
# 日志文件位置
PATH_LOG_FILE = f"{PATH_ROOT}/log.txt"
# 记录文件位置
PATH_RECORD_FILE = f"{PATH_ROOT}/record.json"
# my_account.session 文件位置
PATH_SESSION_FILE = f"{PATH_ROOT}/my_account"
# 配置文件位置
PATH_CONFIG_FILE = f"{PATH_ROOT}/config.yaml"

if not os.path.exists(PATH_ROOT):
    os.makedirs(PATH_ROOT)


class Logger:
    """日志记录器"""

    def __init__(self, log_level):
        """初始化日志记录器

        :param _type_ log_level: 记录级别
        """
        self.logger = logging.getLogger()
        self.logger.addHandler(self.get_file_handler(PATH_LOG_FILE))
        self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(log_level)

    def get_file_handler(self, file):
        file_handler = logging.FileHandler(file)
        file_handler.setFormatter(
            logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
        )
        return file_handler


LOG = Logger(log_level=logging.INFO).logger


class BotConfig:
    def __init__(self):
        # config.yaml
        self.tg_chat_id = ""
        self.tg_bot_token = ""
        self.use_proxy = "0"
        self.use_proxy_dmm = "0"
        self.proxy_addr = ""
        self.use_pikpak = "0"
        self.tg_api_id = ""
        self.tg_api_hash = ""
        self.redis_host = ""
        self.redis_port = ""
        # extend
        self.proxy_json = {"http": "", "https": ""}
        self.proxy_json_pikpak = {}
        self.proxy_addr_dmm = ""

    def load_config(self):
        with open(PATH_CONFIG_FILE, "r") as f:
            config = yaml.safe_load(f)
        self.tg_chat_id = str(config["tg_chat_id"])
        self.tg_bot_token = str(config["tg_bot_token"])
        self.use_proxy = str(config["use_proxy"])
        self.use_proxy_dmm = config["use_proxy_dmm"]
        self.proxy_addr = str(config["proxy_addr"])
        self.use_pikpak = str(config["use_pikpak"])
        self.tg_api_id = str(config["tg_api_id"])
        self.tg_api_hash = str(config["tg_api_hash"])
        self.use_cache = str(config["use_cache"])
        self.redis_host = str(config["redis_host"])
        self.redis_port = str(config["redis_port"])

        if self.use_proxy == "1":
            self.proxy_json = {"http": self.proxy_addr, "https": self.proxy_addr}
            t1 = self.proxy_addr.find(":")
            t2 = self.proxy_addr.rfind(":")
            self.proxy_json_pikpak = {
                "scheme": self.proxy_addr[:t1],
                "hostname": self.proxy_addr[t1 + 3 : t2 - 1],
                "port": int(self.proxy_addr[t2 + 1 :]),
            }
            self.proxy_addr_dmm = self.proxy_addr
        elif self.use_proxy_dmm == "1":
            self.proxy_addr_dmm = self.proxy_addr


BOT_CFG = BotConfig()
BOT_CFG.load_config()
apihelper.proxy = BOT_CFG.proxy_json
BOT = telebot.TeleBot(BOT_CFG.tg_bot_token)


class BotCache:
    CACHE_AV = {
        "prefix": "av-",
        "expire": 3600 * 24 * 30,
    }
    CACHE_STAR = {
        "prefix": "star-",
        "expire": 0,
    }
    CACHE_RANK = {
        "prefix": "rank-",
        "expire": 3600 * 24 * 7,
    }
    CACHE_SAMPLE = {
        "prefix": "sample-",
        "expire": 3600 * 24 * 30,
    }
    CACHE_MAGNET = {
        "prefix": "magnet-",
        "expire": 3600 * 24 * 5,
    }
    CACHE_PV = {
        "prefix": "pv-",
        "expire": 3600 * 24 * 15,
    }
    CACHE_FV = {
        "prefix": "fv-",
        "expire": 3600 * 24 * 15,
    }

    TYPE_AV = 1
    TYPE_STAR = 2
    TYPE_RANK = 3
    TYPE_SAMPLE = 4
    TYPE_MAGNET = 5
    TYPE_PV = 6
    TYPE_FV = 7

    TYPE_MAP = {
        TYPE_AV: CACHE_AV,
        TYPE_STAR: CACHE_STAR,
        TYPE_RANK: CACHE_RANK,
        TYPE_SAMPLE: CACHE_SAMPLE,
        TYPE_MAGNET: CACHE_MAGNET,
        TYPE_PV: CACHE_PV,
        TYPE_FV: CACHE_FV,
    }

    def __init__(self, host, port):
        if BOT_CFG.use_cache == "1":
            self.cache = redis.Redis(host=host, port=port)

    def clear_cache(self):
        LOG.warning("清空缓存")
        for k in self.cache.scan_iter("prefix:*"):
            self.cache.delete(k)

    def remove_cache(self, key, type: int):
        if BOT_CFG.use_cache == "0":
            return
        LOG.info(f"清除缓存: {key}")
        key = str(key)
        key = key.lower()
        self.cache.delete(f"{BOT_CACHE.TYPE_MAP[type]['prefix']}{key}")

    def set_cache(self, key: str, value, type: int):
        """设置缓存

        :param str key: 键
        :param any value: 值
        :param int type: 缓存类型
        """
        if BOT_CFG.use_cache == "0":
            return
        LOG.info(f"设置缓存: {key}")
        key = str(key)
        key = key.lower()
        cache_info = BOT_CACHE.TYPE_MAP[type]
        expire = cache_info["expire"]
        prefix = cache_info["prefix"]
        if expire != 0:
            self.cache.set(
                name=f"{prefix}{key}",
                value=json.dumps({"data": value}),
                ex=expire,
            )
        else:
            self.cache.set(name=f"{prefix}{key}", value=json.dumps({"data": value}))

    def get_cache(self, key, type: int) -> any:
        """获取缓存

        :param str key: 键
        :param int type: 缓存类型
        :return any: 缓存对象
        """
        if BOT_CFG.use_cache == "0":
            return
        key = str(key)
        key = key.lower()
        cache_info = BOT_CACHE.TYPE_MAP[type]
        prefix = cache_info["prefix"]
        json_str = self.cache.get(f"{prefix}{key}")
        if json_str:
            LOG.info(f"从缓存中找到结果: {key}")
            return json.loads(json_str)["data"]


BOT_CACHE = BotCache(host=BOT_CFG.redis_host, port=BOT_CFG.redis_port)


class BotUtils:
    def __init__(self):
        self.util_dmm = jvav.DmmUtil(BOT_CFG.proxy_addr_dmm)
        self.util_javbus = jvav.JavBusUtil(BOT_CFG.proxy_addr)
        self.util_javlib = jvav.JavLibUtil(BOT_CFG.proxy_addr)
        self.util_sukebei = jvav.SukebeiUtil(BOT_CFG.proxy_addr)
        self.util_trans = jvav.TransUtil(BOT_CFG.proxy_addr)
        self.util_wiki = jvav.WikiUtil(BOT_CFG.proxy_addr)
        self.util_avgle = jvav.AvgleUtil(BOT_CFG.proxy_addr)

    def send_action_typing(self):
        """显示机器人正在处理消息"""
        BOT.send_chat_action(chat_id=BOT_CFG.tg_chat_id, action="typing")

    def send_msg(self, msg: str, pv=False, markup=None):
        """发送消息

        :param str msg: 消息文本内容
        :param bool pv: 是否展现预览, 默认不展示
        :param InlineKeyboardMarkup markup: 标记, 默认没有
        """
        BOT.send_message(
            chat_id=BOT_CFG.tg_chat_id,
            text=msg,
            disable_web_page_preview=not pv,
            parse_mode="HTML",
            reply_markup=markup,
        )

    def send_msg_code_op(self, code: int, op: str):
        """根据状态码和操作描述发送消息

        :param int code: 状态码
        :param str op: 执行的操作描述
        """
        if code == 200:
            self.send_msg(
                f"""执行操作: {op}
执行结果: 成功 ^_^"""
            )
        elif code == 404:
            self.send_msg(
                f"""执行操作: {op}
执行结果: 未查找到结果 Q_Q"""
            )
        elif code == 500:
            self.send_msg(
                f"""执行操作: {op}
执行结果: 服务器出错, 请重试或检查日志 Q_Q"""
            )
        elif code == 502:
            self.send_msg(
                f"""执行操作: {op}
执行结果: 网络请求失败, 请重试或检查网络 Q_Q"""
            )

    def send_msg_success_op(self, op: str):
        """根据操作描述发送执行成功的消息

        :param str op: 执行的操作描述
        """
        self.send_msg(
            f"""执行操作: {op}
执行结果: 成功 ^_^"""
        )

    def send_msg_fail_reason_op(self, reason: str, op: str):
        """根据失败原因和操作描述发送执行失败的消息

        :param str reason: 失败原因
        :param str op: 执行的操作描述
        """
        self.send_msg(
            f"""执行操作: {op}
执行结果: 失败, {reason} Q_Q"""
        )

    def check_success(self, code: int, op: str) -> bool:
        """检查状态码, 确认请求是否成功

        :param int code: 状态码
        :param str op: 执行的操作描述
        :return bool: 请求成功与否
        """
        if code == 200:
            return True
        if code == 404:
            self.send_msg_code_op(code=404, op=op)
        elif code == 500:
            self.send_msg_code_op(code=500, op=op)
        elif code == 502:
            self.send_msg_code_op(code=502, op=op)
        return False

    def create_btn_by_key(self, key_type: str, obj: dict) -> InlineKeyboardButton:
        """根据按钮种类创建按钮

        :param str key_type: 按钮种类
        :param dict obj: 数据对象
        :return InlineKeyboardButton: 按钮对象
        """
        if key_type == KEY_GET_STAR_DETAIL_RECORD_BY_STAR_NAME_ID:
            return InlineKeyboardButton(
                text=obj["name"], callback_data=f'{obj["name"]}|{obj["id"]}:{key_type}'
            )
        elif key_type == KEY_GET_AV_DETAIL_RECORD_BY_ID:
            return InlineKeyboardButton(text=obj, callback_data=f"{obj}:{key_type}")
        elif key_type == KEY_SEARCH_STAR_BY_NAME:
            return InlineKeyboardButton(text=obj, callback_data=f"{obj}:{key_type}")
        elif key_type == KEY_GET_AV_BY_ID:
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
        extra_btns_br=True,
        page_btns=[],
    ):
        """发送按钮消息

        :param int max_btn_per_row: 每行最大按钮数量
        :param int max_row_per_msg: 每条消息最多行数
        :param str key_type: 按钮种类
        :param str title: 消息标题
        :param dict objs: 数据对象数组
        :param list extra_btns: 附加按钮列表, 每行一个按钮, 附加在每条消息尾部, 默认为空
        :param bool extra_btns_br: 附加按钮列表是否换行, 默认换行
        :param list page_btns: 分页块
        """
        # 初始化数据
        markup = InlineKeyboardMarkup()
        row_count = 0
        btns = []
        # 开始生成按钮和发送消息
        for obj in objs:
            btns.append(self.create_btn_by_key(key_type, obj))
            # 若一行按钮的数量达到 max_btn_per_row, 则加入行
            if len(btns) == max_btn_per_row:
                markup.row(*btns)
                row_count += 1
                btns = []
            # 若消息中行数达到 max_row_per_msg, 则发送消息
            if row_count == max_row_per_msg:
                if extra_btns_br:
                    for extra_btn in extra_btns:
                        markup.row(extra_btn)
                else:
                    markup.row(*extra_btns)
                if page_btns != []:
                    markup.row(*page_btns)
                self.send_msg(msg=title, markup=markup)
                row_count = 0
                markup = InlineKeyboardMarkup()
        # 若当前行按钮数量不为 0, 则加入行
        if btns != []:
            markup.row(*btns)
            row_count += 1
        # 若当前行数不为 0, 则发送消息
        if row_count != 0:
            if extra_btns_br:
                for extra_btn in extra_btns:
                    markup.row(extra_btn)
            else:
                markup.row(*extra_btns)
            if page_btns != []:
                markup.row(*page_btns)
            self.send_msg(msg=title, markup=markup)

    def get_page_elements(
        self, objs: dict, page: int, col: int, row: int, key_type: str
    ) -> typing.Tuple[dict, list, str]:
        """获取当前页对象字典, 分页按钮列表, 数量标题

        :param dict objs: 对象字典
        :param int page: 当前页
        :param int col: 当前页列数
        :param int row: 当前页行数
        :param str key_type: 按键类型
        :return tuple[dict, list, str]: 当前页对象字典, 分页按钮列表, 数量标题
        """
        # 记录总数
        record_count_total = len(objs)
        # 每页记录数
        record_count_per_page = col * row
        # 页数
        if record_count_per_page > record_count_total:
            page_count = 1
        else:
            page_count = math.ceil(record_count_total / record_count_per_page)
        # 如果要获取的页大于总页数, 那么获取的页设为最后一页
        if page > page_count:
            page = page_count
        # 获取当前页对象字典
        start_idx = (page - 1) * record_count_per_page
        objs = objs[start_idx : start_idx + record_count_per_page]
        # 获取按键列表
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
        # 获取数量标题
        title = f"总数: <b>{record_count_total}</b>, 总页数: <b>{page_count}</b>"
        return (
            objs,
            [btn_to_first, btn_to_previous, btn_to_current, btn_to_next, btn_to_last],
            title,
        )

    def check_has_record(self) -> typing.Tuple[dict, bool, bool]:
        """检查是否有收藏记录, 如果有则返回记录

        :return tuple[dict, bool, bool]: 收藏记录, 演员记录是否存在, 番号记录是否存在
        """
        # 初始化数据
        record = {}
        # 加载记录
        if os.path.exists(PATH_RECORD_FILE):
            try:
                with open(PATH_RECORD_FILE, "r") as f:
                    record = json.load(f)
            except Exception as e:
                LOG.error(e)
                return None, False, False
        # 尚无记录
        if not record or record == {}:
            return None, False, False
        # 检查并返回记录
        is_stars_exists = False
        is_avs_exists = False
        if (
            "stars" in record.keys()
            and record["stars"] != []
            and len(record["stars"]) > 0
        ):
            is_stars_exists = True
        if "avs" in record.keys() and record["avs"] != [] and len(record["avs"]) > 0:
            is_avs_exists = True
        return record, is_stars_exists, is_avs_exists

    def check_star_exists_by_id(self, star_id: str) -> bool:
        """根据演员 id 确认收藏记录中演员是否存在

        :param str star_id: 演员 id
        :return bool: 是否存在
        """
        record, exists, _ = self.check_has_record()
        if not record or not exists:
            return False
        stars = record["stars"]
        for star in stars:
            if star["id"].lower() == star_id.lower():
                return True

    def check_id_exists(self, id: str) -> bool:
        """根据番号确认收藏记录中番号是否存在

        :param str id: 番号
        :return bool: 是否存在
        """
        record, _, exists = self.check_has_record()
        if not record or not exists:
            return False
        avs = record["avs"]
        for av in avs:
            if av["id"].lower() == id.lower():
                return True

    def renew_record(self, record: dict) -> bool:
        """更新记录

        :param dict record: 新的记录
        :return bool: 是否更新成功
        """
        try:
            with open(PATH_RECORD_FILE, "w") as f:
                json.dump(
                    record, f, separators=(",", ": "), indent=4, ensure_ascii=False
                )
            return True
        except Exception as e:
            LOG.error(e)
            return False

    def record_star_by_name_id(self, star_name: str, star_id: str) -> bool:
        """记录演员

        :param str star_name: 演员名称
        :param str star_id: 演员编号
        :return bool: 是否收藏成功
        """
        # 加载记录
        record, is_stars_exists, _ = self.check_has_record()
        if not record:
            record, stars = {}, []
        else:
            if not is_stars_exists:
                stars = []
            else:
                stars = record["stars"]
        # 检查记录是否存在
        for star in stars:
            if star["id"].lower() == star_id.lower():
                return True
        # 如果记录需要更新则写回记录
        stars.append({"name": star_name, "id": star_id.lower()})
        record["stars"] = stars
        return self.renew_record(record)

    def record_id_by_id_stars(self, id: str, stars: list) -> bool:
        """记录番号

        :param str id: 番号
        :param list stars: 演员编号列表
        :return bool: 是否收藏成功
        """
        # 加载记录
        record, _, is_avs_exists = self.check_has_record()
        if not record:
            record, avs = {}, []
        else:
            if not is_avs_exists:
                avs = []
            else:
                avs = record["avs"]
        # 检查记录是否存在
        for av in avs:
            if av["id"].lower() == id.lower():
                return True
        # 如果记录需要更新则写回记录
        avs.append({"id": id.lower(), "stars": stars})
        record["avs"] = avs
        return self.renew_record(record)

    def undo_record_star_by_id(self, star_id: str) -> bool:
        """取消收藏演员

        :param str star_id: 演员id
        :return bool: 是否取消收藏成功
        """
        # 加载记录
        record, exists, _ = self.check_has_record()
        if not record or not exists:
            return False
        stars = record["stars"]
        exists = False
        # 删除记录
        for i, star in enumerate(stars):
            if star["id"].lower() == star_id.lower():
                del stars[i]
                exists = True
                break
        # 更新记录
        if exists:
            record["stars"] = stars
            return self.renew_record(record)
        return True

    def undo_record_id(self, id: str) -> bool:
        """取消收藏番号

        :param str id: 番号
        :return bool: 是否取消收藏成功
        """
        # 加载记录
        record, _, exists = self.check_has_record()
        if not record or not exists:
            return False
        avs = record["avs"]
        exists = False
        # 删除记录
        for i, av in enumerate(avs):
            if av["id"].lower() == id.lower():
                del avs[i]
                exists = True
                break
        # 更新记录
        if exists:
            record["avs"] = avs
            return self.renew_record(record)
        return True

    def get_stars_record(self, page=1):
        """获取演员收藏记录

        :param int page: 第几页, 默认第一页
        """
        # 初始化数据
        record, is_star_exists, _ = self.check_has_record()
        if not record or not is_star_exists:
            self.send_msg_fail_reason_op(reason="尚无演员收藏记录", op="获取演员收藏记录")
            return
        stars = record["stars"]
        stars.reverse()
        col, row = 4, 5
        objs, page_btns, title = self.get_page_elements(
            objs=stars, page=page, col=col, row=row, key_type=KEY_GET_STARS_RECORD
        )
        # 发送按钮消息
        self.send_msg_btns(
            max_btn_per_row=col,
            max_row_per_msg=row,
            key_type=KEY_GET_STAR_DETAIL_RECORD_BY_STAR_NAME_ID,
            title="<b>收藏的演员: </b>" + title,
            objs=objs,
            page_btns=page_btns,
        )

    def get_star_detail_record_by_name_id(self, star_name: str, star_id: str):
        """根据演员名称和编号获取该演员更多信息

        :param str star_name: 演员名称
        :param str star_id: 演员编号
        """
        # 初始化数据
        record, is_stars_exists, is_avs_exists = self.check_has_record()
        if not record:
            self.send_msg(reason="尚无该演员收藏记录", op=f"获取演员 <code>{star_name}</code> 的更多信息")
            return
        avs = []
        star_avs = []
        cur_star_exists = False
        if is_avs_exists:
            avs = record["avs"]
            avs.reverse()
            for av in avs:
                # 如果演员编号在该 av 的演员编号列表中
                if star_id in av["stars"]:
                    star_avs.append(av["id"])
        if is_stars_exists:
            stars = record["stars"]
            for star in stars:
                if star["id"].lower() == star_id.lower():
                    cur_star_exists = True
        # 发送按钮消息
        extra_btn1 = InlineKeyboardButton(
            text=f"随机 av",
            callback_data=f"{star_name}|{star_id}:{kEY_RANDOM_GET_AV_BY_STAR_ID}",
        )
        extra_btn2 = InlineKeyboardButton(
            text=f"最新 av",
            callback_data=f"{star_name}|{star_id}:{KEY_GET_NEW_AVS_BY_STAR_NAME_ID}",
        )
        extra_btn3 = InlineKeyboardButton(
            text=f"高分 av", callback_data=f"{star_name}:{KEY_GET_NICE_AVS_BY_STAR_NAME}"
        )
        if cur_star_exists:
            extra_btn4 = InlineKeyboardButton(
                text=f"取消收藏",
                callback_data=f"{star_name}|{star_id}:{KEY_UNDO_RECORD_STAR_BY_STAR_NAME_ID}",
            )
        else:
            extra_btn4 = InlineKeyboardButton(
                text=f"收藏演员",
                callback_data=f"{star_name}|{star_id}:{KEY_RECORD_STAR_BY_STAR_NAME_ID}",
            )
        title = f'<code>{star_name}</code> | <a href="{self.util_wiki.BASE_URL_JAPAN_WIKI}/{star_name}">Wiki</a> | <a href="{self.util_javbus.BASE_URL_SEARCH_BY_STAR_ID}/{star_id}">Javbus</a>'
        if len(star_avs) == 0:  # 没有该演员对应 av 收藏记录
            markup = InlineKeyboardMarkup()
            markup.row(extra_btn1, extra_btn2, extra_btn3, extra_btn4)
            self.send_msg(msg=title, markup=markup)
            return
        self.send_msg_btns(
            max_btn_per_row=4,
            max_row_per_msg=10,
            key_type=KEY_GET_AV_DETAIL_RECORD_BY_ID,
            title=title,
            objs=star_avs,
            extra_btns_br=False,
            extra_btns=[extra_btn1, extra_btn2, extra_btn3, extra_btn4],
        )

    def get_avs_record(self, page=1):
        """获取番号收藏记录

        :param int page: 第几页, 默认第一页
        """
        # 初始化数据
        record, _, is_avs_exists = self.check_has_record()
        if not record or not is_avs_exists:
            self.send_msg_fail_reason_op(reason="尚无番号收藏记录", op="获取番号收藏记录")
            return
        avs = [av["id"] for av in record["avs"]]
        avs.reverse()
        # 发送按钮消息
        extra_btn1 = InlineKeyboardButton(
            text="随机高分 av", callback_data=f"0:{KEY_RANDOM_GET_AV_NICE}"
        )
        extra_btn2 = InlineKeyboardButton(
            text="随机最新 av", callback_data=f"0:{KEY_RANDOM_GET_AV_NEW}"
        )
        col, row = 4, 10
        objs, page_btns, title = self.get_page_elements(
            objs=avs, page=page, col=col, row=row, key_type=KEY_GET_AVS_RECORD
        )
        self.send_msg_btns(
            max_btn_per_row=col,
            max_row_per_msg=row,
            key_type=KEY_GET_AV_DETAIL_RECORD_BY_ID,
            title="<b>收藏的番号: </b>" + title,
            objs=objs,
            extra_btns=[extra_btn1, extra_btn2],
            extra_btns_br=False,
            page_btns=page_btns,
        )

    def get_av_detail_record_by_id(self, id: str):
        """根据番号获取该番号更多信息

        :param str id: 番号
        """
        record, _, is_avs_exists = self.check_has_record()
        avs = record["avs"]
        cur_av_exists = False
        for av in avs:
            if id.lower() == av["id"].lower():
                cur_av_exists = True
        markup = InlineKeyboardMarkup()
        btn = InlineKeyboardButton(
            text=f"获取对应 av", callback_data=f"{id}:{KEY_GET_AV_BY_ID}"
        )
        if cur_av_exists:
            markup.row(
                btn,
                InlineKeyboardButton(
                    text=f"取消收藏", callback_data=f"{id}:{KEY_UNDO_RECORD_AV_BY_ID}"
                ),
            )
        else:
            markup.row(btn)
        self.send_msg(msg=f"<code>{id}</code>", markup=markup)

    def get_av_by_id(
        self,
        id: str,
        send_to_pikpak=False,
        is_nice=True,
        is_uncensored=True,
        magnet_max_count=3,
        not_send=False,
    ) -> dict:
        """根据番号获取 av

        :param str id: 番号
        :param bool send_to_pikpak: 是否发给 pikpak, 默认不发送
        :param bool is_nice: 是否过滤出高清, 有字幕磁链, 默认是
        :param bool is_uncensored: 是否过滤出无码磁链, 默认是
        :param int magnet_max_count: 过滤后磁链的最大数目, 默认为 3
        :param not_send: 是否不发送 av 结果, 默认发送
        :return dict: 当不发送 av 结果时, 返回得到的 av(如果有)
        """
        # 获取 av
        op_get_av_by_id = f"搜索番号 <code>{id}</code>"
        av = BOT_CACHE.get_cache(key=id, type=BOT_CACHE.TYPE_AV)
        av_score = None
        is_cache = False
        futures = {}
        if not av:
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                if not not_send:
                    futures[
                        executor.submit(self.util_dmm.get_score_by_id, id)
                    ] = 0  # 获取 av 评分
                futures[
                    executor.submit(
                        self.util_javbus.get_av_by_id,
                        id,
                        is_nice,
                        is_uncensored,
                        magnet_max_count,
                    )
                ] = 1  # 通过 javbus 获取 av
                futures[
                    executor.submit(
                        self.util_sukebei.get_av_by_id,
                        id,
                        is_nice,
                        is_uncensored,
                        magnet_max_count,
                    )
                ] = 2  # 通过 sukebei 获取 av
                for future in concurrent.futures.as_completed(futures):
                    future_type = futures[future]
                    if future_type == 0:
                        _, av_score = future.result()
                    elif future_type == 1:
                        code_javbus, av_javbus = future.result()
                    elif future_type == 2:
                        code_sukebei, av_sukebei = future.result()
            if code_javbus != 200 and code_sukebei != 200:
                if code_javbus == 502 or code_sukebei == 502:
                    self.send_msg_code_op(502, op_get_av_by_id)
                else:
                    self.send_msg_code_op(404, op_get_av_by_id)
                return
            if code_javbus == 200:  # 优先选择 javbus
                av = av_javbus
            elif code_sukebei == 200:
                av = av_sukebei
            av["score"] = av_score
            BOT_CACHE.set_cache(key=id, value=av, type=BOT_CACHE.TYPE_AV)
        else:
            av_score = av["score"]
            is_cache = True
        if not_send:
            return av
        # 提取数据
        av_id = id
        av_title = av["title"]
        av_img = av["img"]
        av_date = av["date"]
        av_tags = av["tags"]
        av_stars = av["stars"]
        av_magnets = av["magnets"]
        av_url = av["url"]
        # 拼接消息
        msg = ""
        # 标题
        if av_title != "":
            av_title_ch = self.util_trans.trans(
                text=av_title, from_lang="ja", to_lang="zh-CN"
            )
            if av_title_ch:
                av_title = av_title_ch
            av_title = av_title.replace("<", "").replace(">", "")
            msg += f"""【标题】<a href="{av_url}">{av_title}</a>
"""
        # 番号
        msg += f"""【番号】<code>{av_id}</code>
"""
        # 日期
        if av_date != "":
            msg += f"""【日期】{av_date}
"""
        # 评分
        if av_score:
            msg += f"""【评分】{av_score}
"""
        # 演员
        if av_stars != []:
            futures = {}
            more_star_msg = ""
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                for i, star in enumerate(av_stars):
                    # 如果个数大于 5 则退出
                    if i >= 5:
                        more_star_msg = f"""【演员】<a href="{av_url}">查看更多......</a>
"""
                        break
                    # 获取搜索名
                    name = star["name"]
                    other_name_start = name.find("(")  # 删除别名
                    if other_name_start != -1:
                        name = name[:other_name_start]
                        star["name"] = name
                    # 如果 i == 0, 则为收藏对象
                    if i == 0:
                        show_star_name = star["name"]
                        show_star_id = star["id"]
                    # 从日文维基获取中文维基
                    futures[
                        executor.submit(
                            self.util_wiki.get_wiki_page_by_lang, name, "ja", "zh"
                        )
                    ] = i
                for future in concurrent.futures.as_completed(futures):
                    future_type = futures[future]
                    wiki_json = future.result()
                    wiki = f"{self.util_wiki.BASE_URL_JAPAN_WIKI}/{name}"
                    name = av_stars[future_type]["name"]
                    link = f'{self.util_javbus.BASE_URL_SEARCH_BY_STAR_ID}/{av_stars[future_type]["id"]}'
                    if wiki_json and wiki_json["lang"] == "zh":
                        name_zh = wiki_json["title"]
                        wiki_zh = wiki_json["url"]
                        msg += f"""【演员】<code>{name_zh}</code> | <a href="{wiki_zh}">Wiki</a> | <a href="{link}">Javbus</a>
"""
                    else:
                        msg += f"""【演员】<code>{name}</code> | <a href="{wiki}">Wiki</a> | <a href="{link}">Javbus</a>
"""
            if more_star_msg != "":
                msg += more_star_msg
        # 标签
        if av_tags != "":
            av_tags = av_tags.replace("<", "").replace(">", "")
            msg += f"""【标签】{av_tags}
"""
        # 其它
        msg += f"""【其它】<a href="https://t.me/{PIKPAK_BOT_NAME}">Pikpak</a> | <a href="{PROJECT_ADDRESS}">项目</a> | <a href="{CONTACT_AUTHOR}">作者</a>
"""
        # 磁链
        magnet_send_to_pikpak = ""
        for i, magnet in enumerate(av_magnets):
            if i == 0:
                magnet_send_to_pikpak = magnet["link"]
            magnet_tags = ""
            if magnet["uc"] == "1":
                magnet_tags += "无码"
            if magnet["hd"] == "1":
                magnet_tags += "高清"
            if magnet["zm"] == "1":
                magnet_tags += "含字幕"
            msg_tmp = f"""【{magnet_tags}磁链-{string.ascii_letters[i].upper()} {magnet["size"]}】<code>{magnet["link"]}</code>
"""
            if len(msg + msg_tmp) >= 2000:
                break
            msg += msg_tmp
        # 生成回调按钮
        # 第一排按钮
        pv_btn = InlineKeyboardButton(
            text="预览", callback_data=f"{av_id}:{KEY_WATCH_PV_BY_ID}"
        )
        fv_btn = InlineKeyboardButton(
            text="观看", callback_data=f"{av_id}:{KEY_WATCH_FV_BY_ID}"
        )
        sample_btn = InlineKeyboardButton(
            text="截图", callback_data=f"{av_id}:{KEY_GET_SAMPLE_BY_ID}"
        )
        more_btn = InlineKeyboardButton(
            text="更多磁链", callback_data=f"{av_id}:{KEY_GET_MORE_MAGNETS_BY_ID}"
        )
        markup = InlineKeyboardMarkup().row(sample_btn, pv_btn, fv_btn, more_btn)
        # 第二排按钮
        # 收藏演员按钮
        star_record_btn = None
        if len(av_stars) == 1:
            if self.check_star_exists_by_id(star_id=show_star_id):
                star_record_btn = InlineKeyboardButton(
                    text=f"演员收藏信息",
                    callback_data=f"{show_star_name}|{show_star_id}:{KEY_GET_STAR_DETAIL_RECORD_BY_STAR_NAME_ID}",
                )
            else:
                star_record_btn = InlineKeyboardButton(
                    text=f"收藏{show_star_name}",
                    callback_data=f"{show_star_name}|{show_star_id}:{KEY_RECORD_STAR_BY_STAR_NAME_ID}",
                )
        star_ids = ""
        for i, star in enumerate(av_stars):
            star_ids += star["id"] + "|"
            if i >= 5:
                star_ids += "...|"
                break
        if star_ids != "":
            star_ids = star_ids[: len(star_ids) - 1]
        # 收藏番号按钮
        av_record_btn = None
        if self.check_id_exists(id=av_id):
            av_record_btn = InlineKeyboardButton(
                text=f"番号收藏信息",
                callback_data=f"{av_id}:{KEY_GET_AV_DETAIL_RECORD_BY_ID}",
            )
        else:
            av_record_btn = InlineKeyboardButton(
                text=f"收藏 {av_id}",
                callback_data=f"{av_id}|{star_ids}:{KEY_RECORD_AV_BY_ID_STAR_IDS}",
            )
        # 重新获取按钮
        renew_btn = None
        if is_cache:
            renew_btn = InlineKeyboardButton(
                text="重新获取", callback_data=f"{av_id}:{KEY_DEL_AV_CACHE}"
            )
        markup.row(av_record_btn, star_record_btn, renew_btn)
        # 发送消息
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
            except Exception:  # 少数图片可能没法发送
                self.send_msg(msg=msg, markup=markup)
        # 发给pikpak
        if BOT_CFG.use_pikpak == 1 and magnet_send_to_pikpak != "" and send_to_pikpak:
            self.send_magnet_to_pikpak(magnet_send_to_pikpak, av_id)

    def send_magnet_to_pikpak(self, magnet: str, id: str):
        """发送磁链到pikpak

        :param str magnet: 磁链
        :param str id: 磁链对应的番号
        """
        name = PIKPAK_BOT_NAME
        op_send_magnet_to_pikpak = f"发送番号 {id} 的磁链 A 到 pikpak: <code>{magnet}</code>"
        if self.send_msg_to_pikpak(magnet):
            self.send_msg_success_op(op_send_magnet_to_pikpak)
        else:
            self.send_msg_fail_reason_op(
                reason="请自行检查网络或日志", op=op_send_magnet_to_pikpak
            )

    def get_sample_by_id(self, id: str):
        """根据番号获取 av 截图

        :param str id: 番号
        """
        op_get_sample = f"根据番号 <code>{id}</code> 获取 av 截图"
        # 获取截图
        samples = BOT_CACHE.get_cache(key=id, type=BOT_CACHE.TYPE_SAMPLE)
        if not samples:
            code, samples = self.util_javbus.get_samples_by_id(id)
            if not self.check_success(code, op_get_sample):
                return
            BOT_CACHE.set_cache(key=id, value=samples, type=BOT_CACHE.TYPE_SAMPLE)
        # 发送图片列表
        samples_imp = []
        sample_error = False
        for sample in samples:
            samples_imp.append(InputMediaPhoto(sample))
            if len(samples_imp) == 10:  # 图片数目达到 10 张则发送一次
                try:
                    BOT.send_media_group(chat_id=BOT_CFG.tg_chat_id, media=samples_imp)
                    samples_imp = []
                except Exception:
                    sample_error = True
                    self.send_msg_fail_reason_op(reason="图片解析失败", op=op_get_sample)
                    break
        if samples_imp != [] and not sample_error:
            try:
                BOT.send_media_group(chat_id=BOT_CFG.tg_chat_id, media=samples_imp)
            except Exception:
                self.send_msg_fail_reason_op(reason="图片解析失败", op=op_get_sample)

    def watch_av_by_id(self, id: str, type: str):
        """获取番号对应视频

        :param str id: 番号
        :param str type: 0 预览视频 | 1 完整视频
        """
        if type == 0:
            pv = BOT_CACHE.get_cache(key=id, type=BOT_CACHE.TYPE_PV)
            if not pv:
                op_watch_av = f"获取番号 <code>{id}</code> 对应 av 预览视频"
                futures = {}
                with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                    futures[executor.submit(self.util_dmm.get_pv_by_id, id)] = 1
                    futures[executor.submit(self.util_avgle.get_pv_by_id, id)] = 2
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
                BOT_CACHE.set_cache(key=id, value=pv_cache, type=BOT_CACHE.TYPE_PV)
            else:
                from_site = pv["from_site"]
                pv_src = pv["src"]
            if from_site == "dmm":  # 优先 dmm
                try:
                    # 获取更清晰的视频地址
                    pv_src_nice = self.util_dmm.get_nice_pv_by_src(pv_src)
                    # 发送普通视频, 附带更清晰的视频链接
                    BOT.send_video(
                        chat_id=BOT_CFG.tg_chat_id,
                        video=pv_src,
                        caption=f'通过 DMM 搜索得到结果, <a href="{pv_src_nice}">在这里观看更清晰的版本</a>',
                        parse_mode="HTML",
                    )
                except Exception:
                    self.send_msg(
                        f'通过 DMM 搜索得到结果, 但视频解析失败: <a href="{pv_src_nice}">视频地址</a> Q_Q'
                    )
            elif from_site == "avgle":
                try:
                    BOT.send_video(
                        chat_id=BOT_CFG.tg_chat_id,
                        video=pv_src,
                        caption=f'通过 Avgle 搜索得到结果: <a href="{pv_src}">视频地址</a>',
                        parse_mode="HTML",
                    )
                except Exception:
                    self.send_msg(
                        f'通过 Avgle 搜索得到结果, 但视频解析失败: <a href="{pv_src}">视频地址</a> Q_Q'
                    )
        elif type == 1:
            op_watch_av = f"获取番号 <code>{id}</code> 对应 av 完整视频"
            video = BOT_CACHE.get_cache(key=id, type=BOT_CACHE.TYPE_FV)
            if not video:
                code, video = self.util_avgle.get_fv_by_id(id)
                if not self.check_success(code, op_watch_av):
                    return
                BOT_CACHE.set_cache(key=id, value=video, type=BOT_CACHE.TYPE_FV)
            self.send_msg(f"Avgle 视频地址: {video}")

    def search_star_by_name(self, star_name: str):
        """根据演员名称搜索演员

        :param str star_name: 演员名称
        """
        op_search_star = f"搜索演员 <code>{star_name}</code>"
        star_id = BOT_CACHE.get_cache(key=star_name, type=BOT_CACHE.TYPE_STAR)

        if not star_id:
            if langdetect.detect(star_name) != "ja":  # zh
                # 通过 wiki 获取日文名
                wiki_json = self.util_wiki.get_wiki_page_by_lang(
                    topic=star_name, from_lang="zh", to_lang="ja"
                )
                if wiki_json and wiki_json["lang"] == "ja":
                    star_name = wiki_json["title"]
            code, star_id = self.util_javbus.check_star_exists(star_name)
            if not self.check_success(code, op_search_star):
                return
            BOT_CACHE.set_cache(key=star_name, value=star_id, type=BOT_CACHE.TYPE_STAR)
        if self.check_star_exists_by_id(star_id):
            self.get_star_detail_record_by_name_id(star_name=star_name, star_id=star_id)
            return
        markup = InlineKeyboardMarkup()

        markup.row(
            InlineKeyboardButton(
                text="随机 av",
                callback_data=f"{star_name}|{star_id}:{kEY_RANDOM_GET_AV_BY_STAR_ID}",
            ),
            InlineKeyboardButton(
                text="最新 av",
                callback_data=f"{star_name}|{star_id}:{KEY_GET_NEW_AVS_BY_STAR_NAME_ID}",
            ),
            InlineKeyboardButton(
                text=f"高分 av",
                callback_data=f"{star_name}:{KEY_GET_NICE_AVS_BY_STAR_NAME}",
            ),
            InlineKeyboardButton(
                text=f"收藏 {star_name}",
                callback_data=f"{star_name}|{star_id}:{KEY_RECORD_STAR_BY_STAR_NAME_ID}",
            ),
        )
        self.send_msg(
            msg=f'<code>{star_name}</code> | <a href="{self.util_wiki.BASE_URL_JAPAN_WIKI}/{star_name}">Wiki</a> | <a href="{self.util_javbus.BASE_URL_SEARCH_BY_STAR_NAME}/{star_name}">Javbus</a>',
            markup=markup,
        )

    def get_top_stars(self, page=1):
        """根据页数获取 DMM 女优排行榜, 每页 20 位女优

        :param int page: 第几页, 默认第一页
        """
        op_get_top_stars = f"获取 DMM 女优排行榜"
        stars = BOT_CACHE.get_cache(key=page, type=BOT_CACHE.TYPE_RANK)

        if not stars:
            code, stars = self.util_dmm.get_top_stars(page)
            if not self.check_success(code, op_get_top_stars):
                return
            BOT_CACHE.set_cache(key=page, value=stars, type=BOT_CACHE.TYPE_RANK)
        stars_tmp = [None] * 80
        stars = stars_tmp[: ((page - 1) * 20)] + stars + stars_tmp[((page - 1) * 20) :]
        col, row = 4, 5
        objs, page_btns, title = self.get_page_elements(
            objs=stars, page=page, col=4, row=5, key_type=KEY_GET_TOP_STARS
        )
        self.send_msg_btns(
            max_btn_per_row=col,
            max_row_per_msg=row,
            key_type=KEY_SEARCH_STAR_BY_NAME,
            title="<b>DMM 女优排行榜: </b>" + title,
            objs=objs,
            page_btns=page_btns,
        )

    def send_msg_to_pikpak(self, msg):
        """发送消息到Pikpak机器人

        :param _type_ msg: 消息
        :return any: 如果失败则为 None
        """

        async def main():
            async with Client(
                name=PATH_SESSION_FILE,
                api_id=BOT_CFG.tg_api_id,
                api_hash=BOT_CFG.tg_api_hash,
                proxy=BOT_CFG.proxy_json_pikpak,
            ) as app:
                return await app.send_message(PIKPAK_BOT_NAME, msg)

        try:
            return asyncio.run(main())
        except Exception as e:
            LOG.error(e)
            return None

    def get_more_magnets_by_id(self, id: str):
        """根据番号获取更多磁链

        :param id: 番号
        """
        magnets = BOT_CACHE.get_cache(key=id, type=BOT_CACHE.TYPE_MAGNET)
        if not magnets:
            av = self.get_av_by_id(
                id=id, is_nice=False, is_uncensored=False, not_send=True
            )
            if not av:
                return
            magnets = av["magnets"]
            BOT_CACHE.set_cache(key=id, value=magnets, type=BOT_CACHE.TYPE_MAGNET)
        msg = ""
        for magnet in magnets:
            magnet_tags = ""
            if magnet["uc"] == "1":
                magnet_tags += "无码"
            if magnet["hd"] == "1":
                magnet_tags += "高清"
            if magnet["zm"] == "1":
                magnet_tags += "含字幕"
            msg_tmp = f"""【{magnet_tags}磁链 {magnet["size"]}】<code>{magnet["link"]}</code>
"""
            if len(msg + msg_tmp) >= 4000:
                self.send_msg(msg)
                msg = msg_tmp
            else:
                msg += msg_tmp
        if msg != "":
            self.send_msg(msg)

    def get_star_new_avs_by_name_id(self, star_name: str, star_id: str):
        """获取演员最新 av

        :param str star_name: 演员名称
        :param str star_id: 演员 id
        """
        op_get_star_new_avs = f"获取 <code>{star_name}</code> 最新 av"
        code, ids = self.util_javbus.get_new_ids_by_star_id(star_id=star_id)
        title = f"<code>{star_name}</code> 最新 av"
        if self.check_success(code, op_get_star_new_avs):
            btns = [
                InlineKeyboardButton(text=id, callback_data=f"{id}:{KEY_GET_AV_BY_ID}")
                for id in ids
            ]
            if len(btns) <= 4:
                self.send_msg(msg=title, markup=InlineKeyboardMarkup().row(*btns))
            else:
                markup = InlineKeyboardMarkup()
                markup.row(*btns[:4])
                markup.row(*btns[4:])
                self.send_msg(msg=title, markup=markup)

    def get_msg_param(self, msg: str) -> str:
        """获取消息参数

        :param str msg: 消息文本, 已经通过 strip() 函数将两旁空白清除
        :return str: 消息参数(保证只有一个)
        """
        msgs = msg.split(" ", 1)  # 划分为两部分
        if len(msgs) > 1:  # 有参数
            param = "".join(msgs[1].split())  # 去除参数所有空白
            if param != "":
                return param

    def intercept(self, chat_id: str) -> bool:
        """拦截消息

        :param str chat_id: 对话 id
        :return bool: 是否通过
        """
        if chat_id.lower() == BOT_CFG.tg_chat_id.lower():
            return True
        LOG.info(f"拦截到非目标用户请求, id: {chat_id}")
        BOT.send_message(
            chat_id=chat_id,
            text=f'该机器人仅供私人使用, 如需使用请自行部署: <a href="{PROJECT_ADDRESS}">项目地址</a>',
            parse_mode="HTML",
        )
        return False

    def help(self):
        """发送指令帮助消息"""
        msg = """发送给机器人一条含有番号的消息, 机器人会匹配并搜索消息中所有符合<b>“字母-数字”</b>格式的番号, 其它格式的番号可通过<code>/av</code>命令查找。

/help  查看指令帮助

/stars  查看收藏的演员

/avs  查看收藏的番号

/nice  随机获取一部高分 av

/new  随机获取一部最新 av

/rank  获取 DMM 女优排行榜

/record  获取收藏记录文件

/clear  清空缓存

<code>/star</code>  后接演员名称可搜索该演员

<code>/av</code>  后接番号可搜索该番号
"""
        self.send_msg(msg)

    def set_command(self):
        """设置机器人命令"""
        tg_cmd_dict = {
            "help": "查看指令帮助",
            "stars": "查看收藏的演员",
            "avs": "查看收藏的番号",
            "nice": "随机获取一部高分 av",
            "new": "随机获取一部最新 av",
            "rank": "获取 DMM 女优排行榜",
            "record": "获取收藏记录文件",
        }
        cmds = []
        for cmd in tg_cmd_dict:
            cmds.append(types.BotCommand(cmd, tg_cmd_dict[cmd]))
        BOT.set_my_commands(cmds)

    def test(self):
        """用于测试"""
        return


BOT_UTILS = BotUtils()


@BOT.callback_query_handler(func=lambda call: True)
def listen_callback(call):
    """消息回调处理器

    :param _type_ call: 触发回调的消息内容
    """
    # 回显 typing...
    BOT_UTILS.send_action_typing()
    # 提取回调内容
    s = call.data.rfind(":")
    content = call.data[:s]
    key_type = call.data[s + 1 :]
    # 检查按键类型并处理
    if key_type == KEY_WATCH_PV_BY_ID:
        BOT_UTILS.watch_av_by_id(id=content, type=0)
    elif key_type == KEY_WATCH_FV_BY_ID:
        BOT_UTILS.watch_av_by_id(id=content, type=1)
    elif key_type == KEY_GET_SAMPLE_BY_ID:
        BOT_UTILS.get_sample_by_id(id=content)
    elif key_type == KEY_GET_MORE_MAGNETS_BY_ID:
        BOT_UTILS.get_more_magnets_by_id(id=content)
    elif key_type == kEY_RANDOM_GET_AV_BY_STAR_ID:
        tmp = content.split("|")
        star_name = tmp[0]
        star_id = tmp[1]
        code, id = BOT_UTILS.util_javbus.get_id_by_star_id(star_id=star_id)
        if BOT_UTILS.check_success(code, f"随机获取演员 <code>{star_name}</code> 的 av"):
            BOT_UTILS.get_av_by_id(id=id)
    elif key_type == KEY_GET_NEW_AVS_BY_STAR_NAME_ID:
        tmp = content.split("|")
        star_name = tmp[0]
        star_id = tmp[1]
        BOT_UTILS.get_star_new_avs_by_name_id(star_name=star_name, star_id=star_id)
    elif key_type == KEY_RECORD_STAR_BY_STAR_NAME_ID:
        s = content.find("|")
        star_name = content[:s]
        star_id = content[s + 1 :]
        if BOT_UTILS.record_star_by_name_id(star_name=star_name, star_id=star_id):
            BOT_UTILS.get_star_detail_record_by_name_id(
                star_name=star_name, star_id=star_id
            )
        else:
            BOT_UTILS.send_msg_code_op(500, f"收藏演员 <code>{star_name}</code>")
    elif key_type == KEY_RECORD_AV_BY_ID_STAR_IDS:
        res = content.split("|")
        id = res[0]
        stars = [s for s in res[1:]]
        if BOT_UTILS.record_id_by_id_stars(id=id, stars=stars):
            BOT_UTILS.get_av_detail_record_by_id(id=id)
        else:
            BOT_UTILS.send_msg_code_op(500, f"收藏番号 <code>{id}</code>")
    elif key_type == KEY_GET_STARS_RECORD:
        BOT_UTILS.get_stars_record(page=int(content))
    elif key_type == KEY_GET_AVS_RECORD:
        BOT_UTILS.get_avs_record(page=int(content))
    elif key_type == KEY_GET_STAR_DETAIL_RECORD_BY_STAR_NAME_ID:
        s = content.find("|")
        BOT_UTILS.get_star_detail_record_by_name_id(
            star_name=content[:s], star_id=content[s + 1 :]
        )
    elif key_type == KEY_GET_AV_DETAIL_RECORD_BY_ID:
        BOT_UTILS.get_av_detail_record_by_id(id=content)
    elif key_type == KEY_GET_AV_BY_ID:
        BOT_UTILS.get_av_by_id(id=content)
    elif key_type == KEY_RANDOM_GET_AV_NICE:
        code, id = BOT_UTILS.util_javlib.get_random_id_from_rank(0)
        if BOT_UTILS.check_success(code, "随机获取高分 av"):
            BOT_UTILS.get_av_by_id(id=id)
    elif key_type == KEY_RANDOM_GET_AV_NEW:
        code, id = BOT_UTILS.util_javlib.get_random_id_from_rank(1)
        if BOT_UTILS.check_success(code, "随机获取最新 av"):
            BOT_UTILS.get_av_by_id(id=id)
    elif key_type == KEY_UNDO_RECORD_AV_BY_ID:
        op_undo_record_av = f"取消收藏番号 <code>{content}</code>"
        if BOT_UTILS.undo_record_id(id=content):
            BOT_UTILS.send_msg_success_op(op_undo_record_av)
        else:
            BOT_UTILS.send_msg_fail_reason_op(reason="文件解析出错", op=op_undo_record_av)
    elif key_type == KEY_UNDO_RECORD_STAR_BY_STAR_NAME_ID:
        s = content.find("|")
        op_undo_record_star = f"取消收藏演员 <code>{content[:s]}</code>"
        if BOT_UTILS.undo_record_star_by_id(star_id=content[s + 1 :]):
            BOT_UTILS.send_msg_success_op(op_undo_record_star)
        else:
            BOT_UTILS.send_msg_fail_reason_op(reason="文件解析出错", op=op_undo_record_star)
    elif key_type == KEY_SEARCH_STAR_BY_NAME:
        BOT_UTILS.search_star_by_name(content)
    elif key_type == KEY_GET_TOP_STARS:
        BOT_UTILS.get_top_stars(page=int(content))
    elif key_type == KEY_GET_NICE_AVS_BY_STAR_NAME:
        code, avs = BOT_UTILS.util_dmm.get_nice_avs_by_star_name(star_name=content)
        avs = avs[:60]
        if BOT_UTILS.check_success(code, f"获取演员 {content} 的高分 av"):
            BOT_UTILS.send_msg_btns(
                max_btn_per_row=3,
                max_row_per_msg=20,
                key_type=KEY_GET_AV_BY_ID,
                title=f"<b>演员 {content} 的高分 av</b>",
                objs=avs,
            )
    elif key_type == KEY_DEL_AV_CACHE:
        BOT_CACHE.remove_cache(key=content, type=BOT_CACHE.TYPE_AV)
        BOT_UTILS.get_av_by_id(id=content)


@BOT.message_handler(content_types=["text", "photo", "animation", "video"])
def handle_message(message):
    """消息处理器

    :param _type_ message: 消息
    """
    # 拦截请求
    if not BOT_UTILS.intercept(str(message.chat.id)):
        return
    # 回显 typing...
    BOT_UTILS.send_action_typing()
    # 获取消息文本内容
    if message.content_type != "text":
        msg_origin = message.caption
    else:
        msg_origin = message.text
    if not msg_origin:
        return
    LOG.info(f'收到消息: "{msg_origin}"')
    # 如果是 inline 形式的消息, 则提取 @ 前的字符串
    inline_idx = msg_origin.find("@")
    if inline_idx != -1:
        msg = msg_origin[:inline_idx]
    else:
        msg = msg_origin
    # 处理消息
    if msg == "/test":
        BOT_UTILS.test()
    elif msg == "/help" or msg.find("/start") != -1:
        BOT_UTILS.help()
    elif msg == "/nice":
        code, id = BOT_UTILS.util_javlib.get_random_id_from_rank(0)
        if BOT_UTILS.check_success(code, "随机获取高分 av"):
            BOT_UTILS.get_av_by_id(id=id)
    elif msg == "/new":
        code, id = BOT_UTILS.util_javlib.get_random_id_from_rank(1)
        if BOT_UTILS.check_success(code, "随机获取最新 av"):
            BOT_UTILS.get_av_by_id(id=id)
    elif msg == "/stars":
        BOT_UTILS.get_stars_record()
    elif msg == "/avs":
        BOT_UTILS.get_avs_record()
    elif msg == "/record":
        if os.path.exists(PATH_RECORD_FILE):
            BOT.send_document(
                chat_id=BOT_CFG.tg_chat_id, document=types.InputFile(PATH_RECORD_FILE)
            )
        else:
            BOT_UTILS.send_msg_fail_reason_op(reason="尚无收藏记录", op="获取收藏记录文件")
    elif msg == "/rank":
        BOT_UTILS.get_top_stars(1)
    elif msg == "/clear":
        BOT_CACHE.clear_cache()
        BOT_UTILS.send_msg_success_op(op="清空缓存")
    elif msg_origin.find("/star") != -1:
        param = BOT_UTILS.get_msg_param(msg_origin)
        if param:
            BOT_UTILS.send_msg(f"搜索演员: <code>{param}</code> ......")
            BOT_UTILS.search_star_by_name(param)
    elif msg_origin.find("/av") != -1:
        param = BOT_UTILS.get_msg_param(msg_origin)
        if param:
            BOT_UTILS.send_msg(f"搜索番号: <code>{param}</code> ......")
            BOT_UTILS.get_av_by_id(id=param, send_to_pikpak=True)
    else:
        # ids = re.compile(r'^[A-Za-z]+[-][0-9]+$').findall(msg)
        ids = re.compile(r"[A-Za-z]+[-][0-9]+").findall(msg_origin)
        if not ids:
            BOT_UTILS.send_msg(
                "消息似乎不存在符合<b>“字母-数字”</b>格式的番号, 请重试或使用“<code>/av</code> 番号”进行查找 =_="
            )
        else:
            ids = [id.lower() for id in ids]
            ids = set(ids)
            ids_msg = ", ".join(ids)
            BOT_UTILS.send_msg(f"检测到番号: {ids_msg}, 开始搜索......")
            for id in ids:
                BOT_UTILS.get_av_by_id(id=id, send_to_pikpak=True)


if __name__ == "__main__":
    if BOT_CFG.use_pikpak and not os.path.exists(PATH_SESSION_FILE):
        BOT_UTILS.send_msg_to_pikpak("登录认证")
    BOT_UTILS.set_command()
    BOT.infinity_polling()
