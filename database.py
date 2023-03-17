import os
import json
import redis
import typing
import logging

LOG = logging.getLogger(__name__)


class BotRelDb:
    pass


class BotFileDb:
    def __init__(self, path_record_file: str):
        """初始化

        :param str path_record_file: 记录文件位置
        """
        self.path_record_file = path_record_file
        pass

    def check_has_record(self) -> typing.Tuple[dict, bool, bool]:
        """检查是否有收藏记录, 如果有则返回记录

        :return tuple[dict, bool, bool]: 收藏记录, 演员记录是否存在, 番号记录是否存在
        """
        # 初始化数据
        record = {}
        # 加载记录
        if os.path.exists(self.path_record_file):
            try:
                with open(self.path_record_file, "r") as f:
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
            with open(self.path_record_file, "w") as f:
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


class BotCacheDb:
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

    def __init__(self, host: str, port: int, use_cache: str):
        """初始化

        :param str host: ip 地址
        :param int port: 端口
        :param str use_cache: 是否使用缓存
        """
        self.use_cache = use_cache
        if self.use_cache == "1":
            try:
                self.cache = redis.Redis(host=host, port=port)
                LOG.info(f"connect to redis server: {host}:{port}")
            except Exception as e:
                LOG.error(f"fail to connect to redis server: {host}:{port}")

    def clear_cache(self):
        LOG.warning("清空缓存")
        self.cache.flushdb()

    def remove_cache(self, key, type: int):
        if self.use_cache == "0" or not self.cache:
            return
        LOG.info(f"清除缓存: {key}")
        key = str(key)
        key = key.lower()
        self.cache.delete(f"{BotCacheDb.TYPE_MAP[type]['prefix']}{key}")

    def set_cache(self, key: str, value, type: int):
        """设置缓存

        :param str key: 键
        :param any value: 值
        :param int type: 缓存类型
        """
        if self.use_cache == "0" or not self.cache:
            return
        LOG.info(f"设置缓存: {key}")
        key = str(key)
        key = key.lower()
        cache_info = BotCacheDb.TYPE_MAP[type]
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
        if self.use_cache == "0" or not self.cache:
            return
        key = str(key)
        key = key.lower()
        cache_info = BotCacheDb.TYPE_MAP[type]
        prefix = cache_info["prefix"]
        json_str = self.cache.get(f"{prefix}{key}")
        if json_str:
            LOG.info(f"从缓存中找到结果: {key}")
            return json.loads(json_str)["data"]
