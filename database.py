import os
import json
import redis
import logging

LOG = logging.getLogger(__name__)


class BotFileDb:
    def __init__(self, path_record_file: str):
        self.path_record_file = path_record_file
        pass

    def check_has_record(self):
        record = {}
        if os.path.exists(self.path_record_file):
            try:
                with open(self.path_record_file, "r", encoding="utf8") as f:
                    record = json.load(f)
            except Exception as e:
                LOG.error(f"Failed to load the saved records file: {e}")
                return None, False, False
        if not record or record == {}:
            return None, False, False
        is_stars_exists = False
        is_vs_exists = False
        if (
                "stars" in record.keys()
                and record["stars"] != []
                and len(record["stars"]) > 0
        ):
            is_stars_exists = True
        if "vs" in record.keys() and record["vs"] != [] and len(record["vs"]) > 0:
            is_vs_exists = True
        return record, is_stars_exists, is_vs_exists

    def check_star_exists_by_id(self, star_id: str):
        record, exists, _ = self.check_has_record()
        if not record or not exists:
            return False
        stars = record["stars"]
        for star in stars:
            if star["id"].lower() == star_id.lower():
                return True

    def check_id_exists(self, id: str):
        record, _, exists = self.check_has_record()
        if not record or not exists:
            return False
        vs = record["vs"]
        for v in vs:
            if v["id"].lower() == id.lower():
                return True

    def renew_record(self, record: dict):
        try:
            with open(self.path_record_file, "w", encoding="utf8") as f:
                json.dump(
                    record, f, separators=(",", ": "), indent=4, ensure_ascii=False
                )
            return True
        except Exception as e:
            LOG.error(f"Failed to update the saved records file: {e}")
            return False

    def record_star_by_name_id(self, star_name: str, star_id: str):
        record, is_stars_exists, _ = self.check_has_record()
        if not record:
            record, stars = {}, []
        else:
            if not is_stars_exists:
                stars = []
            else:
                stars = record["stars"]
        for star in stars:
            if star["id"].lower() == star_id.lower():
                return True
        stars.append({"name": star_name, "id": star_id.lower()})
        record["stars"] = stars
        return self.renew_record(record)

    def record_id_by_id_stars(self, id: str, stars: list):
        record, _, is_vs_exists = self.check_has_record()
        if not record:
            record, vs = {}, []
        else:
            if not is_vs_exists:
                vs = []
            else:
                vs = record["vs"]
        for v in vs:
            if v["id"].lower() == id.lower():
                return True
        vs.append({"id": id.lower(), "stars": stars})
        record["vs"] = vs
        return self.renew_record(record)

    def undo_record_star_by_id(self, star_id: str):
        record, exists, _ = self.check_has_record()
        if not record or not exists:
            return False
        stars = record["stars"]
        exists = False
        for i, star in enumerate(stars):
            if star["id"].lower() == star_id.lower():
                del stars[i]
                exists = True
                break
        if exists:
            record["stars"] = stars
            return self.renew_record(record)
        return True

    def undo_record_id(self, id: str):
        record, _, exists = self.check_has_record()
        if not record or not exists:
            return False
        vs = record["vs"]
        exists = False
        for i, v in enumerate(vs):
            if v["id"].lower() == id.lower():
                del vs[i]
                exists = True
                break
        if exists:
            record["vs"] = vs
            return self.renew_record(record)
        return True


class BotCacheDb:
    CACHE_BT = {
        "prefix": "bt-",
        "expire": 3600 * 24 * 30,
    }
    CACHE_V = {
        "prefix": "v-",
        "expire": 3600 * 24 * 30,
    }
    CACHE_STAR = {
        "prefix": "star-",
        "expire": 0,  # never expire
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
    CACHE_STARS_MSG = {
        "prefix": "stars-msg-",
        "expire": 3600 * 24 * 5,
    }
    CACHE_COMMENT = {"prefix": "comment-", "expire": 3600 * 24 * 30}
    CACHE_NICE_VS_OF_STAR = {
        "prefix": "nice-vs-of-star-",
        "expire": 3600 * 24 * 15,
    }
    CACHE_JLIB_PAGE_NICE_VS = {
        "prefix": "jlib-page-nice-vs-",
        "expire": 3600 * 24 * 7,
    }
    CACHE_JLIB_PAGE_NEW_VS = {
        "prefix": "jlib-page-new-vs-",
        "expire": 3600 * 24 * 2,
    }
    CACHE_STAR_JA_NAME = {"prefix": "star-ja-name-", "expire": 3600 * 24 * 30 * 6}
    CACHE_NEW_VS_OF_STAR = {
        "prefix": "new-vs-of-star-",
        "expire": 3600 * 24 * 12,
    }

    TYPE_V = 1
    TYPE_STAR = 2
    TYPE_RANK = 3
    TYPE_SAMPLE = 4
    TYPE_MAGNET = 5
    TYPE_PV = 6
    TYPE_FV = 7
    TYPE_STARS_MSG = 8
    TYPE_COMMENT = 10
    TYPE_NICE_VS_OF_STAR = 11
    TYPE_JLIB_PAGE_NICE_VS = 12
    TYPE_JLIB_PAGE_NEW_VS = 13
    TYPE_STAR_JA_NAME = 14
    TYPE_NEW_VS_OF_STAR = 16
    TYPE_BT = 17

    TYPE_MAP = {
        TYPE_V: CACHE_V,
        TYPE_STAR: CACHE_STAR,
        TYPE_RANK: CACHE_RANK,
        TYPE_SAMPLE: CACHE_SAMPLE,
        TYPE_MAGNET: CACHE_MAGNET,
        TYPE_PV: CACHE_PV,
        TYPE_FV: CACHE_FV,
        TYPE_STARS_MSG: CACHE_STARS_MSG,
        TYPE_COMMENT: CACHE_COMMENT,
        TYPE_NICE_VS_OF_STAR: CACHE_NICE_VS_OF_STAR,
        TYPE_JLIB_PAGE_NICE_VS: CACHE_JLIB_PAGE_NICE_VS,
        TYPE_JLIB_PAGE_NEW_VS: CACHE_JLIB_PAGE_NEW_VS,
        TYPE_STAR_JA_NAME: CACHE_STAR_JA_NAME,
        TYPE_NEW_VS_OF_STAR: CACHE_NEW_VS_OF_STAR,
        TYPE_BT: CACHE_BT,
    }

    def __init__(self, host: str, port: int, password: str, use_cache: str):
        self.use_cache = use_cache
        self.cache = None
        if self.use_cache == "1":
            try:
                if password:
                    self.cache = redis.Redis(host=host, port=port, password=password)
                else:
                    self.cache = redis.Redis(host=host, port=port)
                self.cache.ping()
                LOG.info(f"Connecting to the Redis service: {host}:{port}")
            except Exception as e:
                self.cache = None
                LOG.error(
                    f"Unable to connect to the Redis service: {host}:{port} : {e}"
                )

    def remove_cache(self, key: str, type: int):
        if self.use_cache == "0" or not self.cache:
            return
        key = str(key).lower()
        cache_key = f"{BotCacheDb.TYPE_MAP[type]['prefix']}{key}"
        try:
            self.cache.delete(cache_key)
        except Exception as e:
            LOG.error(f"Failed to delete cache: {cache_key}: {e}")

    def set_cache(self, key: str, value, type: int, expire=None):
        """
        Set cache.

        :param str key: Key
        :param any value: Value
        :param int type: Cache type
        :param int expire: Cache expiration time (in seconds), defaults to using predefined time
        """
        if self.use_cache == "0" or not self.cache:
            return
        key = str(key).lower()
        if not expire:
            expire = BotCacheDb.TYPE_MAP[type]["expire"]
        prefix = BotCacheDb.TYPE_MAP[type]["prefix"]
        cache_key = f"{prefix}{key}"
        try:
            if expire != 0:
                self.cache.set(
                    name=cache_key,
                    value=json.dumps(value),
                    ex=expire,
                )
            else:
                self.cache.set(name=cache_key, value=json.dumps(value))
        except Exception as e:
            LOG.error(f"Failed to set cache: {cache_key}: {e}")

    def get_cache(self, key, type: int):
        if self.use_cache == "0" or not self.cache:
            return
        key = str(key).lower()
        cache_key = f"{BotCacheDb.TYPE_MAP[type]['prefix']}{key}"
        try:
            value = self.cache.get(cache_key)
            if value:
                return json.loads(value)
        except Exception as e:
            LOG.error(f"Failed to retrieve cache: {cache_key}: {e}")
