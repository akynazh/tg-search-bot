import yaml
import logging

LOG = logging.getLogger(__name__)


class BotConfig:
    def __init__(self, path_config_file: str):
        """初始化

        :param str path_config_file: 配置文件位置
        """
        self.path_config_file = path_config_file
        # config.yaml
        self.tg_chat_id = ""
        self.tg_bot_token = ""
        self.tg_bot_name = ""
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
        try:
            LOG.info(f"load config from {self.path_config_file}")
            with open(self.path_config_file, "r") as f:
                config = yaml.safe_load(f)
            if config["tg_chat_id"]:
                self.tg_chat_id = str(config["tg_chat_id"])
            if config["tg_bot_token"]:
                self.tg_bot_token = str(config["tg_bot_token"])
            if config["tg_bot_name"]:
                self.tg_bot_name = str(config["tg_bot_name"])
            if config["use_proxy"]:
                self.use_proxy = str(config["use_proxy"])
            if config["use_proxy_dmm"]:
                self.use_proxy_dmm = str(config["use_proxy_dmm"])
            if config["proxy_addr"]:
                self.proxy_addr = str(config["proxy_addr"])
            if config["use_pikpak"]:
                self.use_pikpak = str(config["use_pikpak"])
            if config["tg_api_id"]:
                self.tg_api_id = str(config["tg_api_id"])
            if config["tg_api_hash"]:
                self.tg_api_hash = str(config["tg_api_hash"])
            if config["use_cache"]:
                self.use_cache = str(config["use_cache"])
            if config["redis_host"]:
                self.redis_host = str(config["redis_host"])
            if config["redis_port"]:
                self.redis_port = str(config["redis_port"])

            if self.use_proxy == "1":
                self.proxy_json = {"http": self.proxy_addr, "https": self.proxy_addr}
                t1 = self.proxy_addr.find(":")
                t2 = self.proxy_addr.rfind(":")
                self.proxy_json_pikpak = {
                    "scheme": self.proxy_addr[:t1],
                    "hostname": self.proxy_addr[t1 + 3 : t2],
                    "port": int(self.proxy_addr[t2 + 1 :]),
                }
                self.proxy_addr_dmm = self.proxy_addr
                LOG.info(f'set proxy: "{self.proxy_addr}"')
            elif self.use_proxy_dmm == "1":
                self.proxy_addr_dmm = self.proxy_addr
                self.proxy_addr = ""
                LOG.info(f"set proxy for dmm: {self.proxy_addr_dmm}")
            else:
                self.proxy_addr = ""
        except Exception as e:
            LOG.error(f"读取配置文件出错: {e}")
