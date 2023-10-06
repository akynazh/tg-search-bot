import yaml
import logging

LOG = logging.getLogger(__name__)


class BotConfig:
    def __init__(self, path_config_file: str):
        """初始化

        :param str path_config_file: 配置文件位置
        """
        # load
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
        self.tg_api_hash = (
            str(config["tg_api_hash"]) if config["tg_api_hash"] else ""
        )
        self.use_cache = str(config["use_cache"]) if config["use_cache"] else "0"
        self.redis_host = str(config["redis_host"]) if config["redis_host"] else ""
        self.redis_port = str(config["redis_port"]) if config["redis_port"] else ""
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
                "hostname": self.proxy_addr[t1 + 3 : t2],
                "port": int(self.proxy_addr[t2 + 1 :]),
            }
            LOG.info(f'设置代理: "{self.proxy_addr}"')
        elif self.use_proxy_dmm == "1":
            self.proxy_addr_dmm = self.proxy_addr
            self.proxy_addr = ""
            LOG.info(f'设置 DMM 代理: "{self.proxy_addr_dmm}"')
        else:
            self.proxy_addr = ""
