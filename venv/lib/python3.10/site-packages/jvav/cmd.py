# -*- coding: UTF-8 -*-
import os
import sys
import json
import logging
import argparse
import langdetect
import jvav

PATH_ROOT = os.path.expanduser("~") + "/.jvav"
if not os.path.exists(PATH_ROOT):
    os.makedirs(PATH_ROOT)


class Logger:
    def __init__(self, log_level: int, path_log_file: str):
        """初始化日志记录器

        :param int log_level: 记录级别
        :param str path_log_file: 日志文件位置
        """
        self.logger = logging.getLogger()
        self.logger.addHandler(self.get_file_handler(path_log_file))
        self.logger.addHandler(logging.StreamHandler(sys.stdout))
        self.logger.setLevel(log_level)

    def get_file_handler(self, file):
        file_handler = logging.FileHandler(file)
        file_handler.setFormatter(
            logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
        )
        return file_handler


LOG = Logger(logging.INFO, f"{PATH_ROOT}/log.txt").logger


class JvavArgsParser:
    def __init__(self):
        parser = argparse.ArgumentParser()
        # Check version
        parser.add_argument(
            "-v", "--version", action="store_true", help="Check version"
        )
        # Search number
        parser.add_argument(
            "-av1",
            type=str,
            default="",
            help="Followed by a code, search this code on JavBus",
        )
        parser.add_argument(
            "-av2",
            type=str,
            default="",
            help="Followed by a code, search this code on Sukebei",
        )
        parser.add_argument(
            "-nc",
            action="store_true",
            help="Filter out high-definition subtitles magnet links",
        )
        parser.add_argument(
            "-uc", action="store_true", help="Filter out uncoded magnet links"
        )
        # Search actor
        parser.add_argument(
            "-sr",
            type=str,
            default="",
            help="Followed by an actress name, get a list of high-rated codes based on the actress name",
        )
        parser.add_argument(
            "-srn",
            type=str,
            default="",
            help="Followed by an actress name, get a list of the most recent codes based on the actress name",
        )
        # Search number by keyword
        parser.add_argument(
            "-tg",
            type=str,
            default="",
            help="Followed by a keyword, search for codes based on the keyword",
        )
        # Get preview video
        parser.add_argument(
            "-pv1",
            type=str,
            default="",
            help="Followed by a code, get the corresponding preview video of the code on DMM",
        )
        parser.add_argument(
            "-pv2",
            type=str,
            default="",
            help="Follow a code, get the corresponding preview video of the code on Avgle",
        )
        # Get leaderboard
        parser.add_argument(
            "-tp", action="store_true", help="Get the top 25 ranking of DMM actresses"
        )
        # Configure proxy
        parser.add_argument(
            "-p",
            "--proxy",
            type=str,
            default="",
            help="Followed by a proxy server address (by default reads the value of the environment variable http_proxy)",
        )
        self.parser = parser
        self.args = None

    def handle_code(self, code: int, res):
        """处理结果

        :param int code: 状态码
        :param any res: 结果
        """
        if code != 200:
            LOG.error(code)
            return
        LOG.info(json.dumps(res, indent=4, ensure_ascii=False))

    def parse(self):
        """解析命令行参数"""
        parser = self.parser
        self.args = parser.parse_args()

    def exec(self):
        """根据参数表自行相应操作"""
        if not self.args:
            self.parser.print_help()
            return
        args = self.args
        env_proxy = os.getenv("http_proxy")
        if args.version:
            print(f"jvav-{jvav.VERSION}")
            return
        if args.proxy == "" and env_proxy:
            args.proxy = env_proxy
        if args.av1 != "":
            self.handle_code(
                *jvav.JavBusUtil(proxy_addr=args.proxy).get_av_by_id(
                    id=args.av1, is_nice=args.nc, is_uncensored=args.uc
                )
            )
        elif args.av2 != "":
            self.handle_code(
                *jvav.SukebeiUtil(proxy_addr=args.proxy).get_av_by_id(
                    id=args.av2, is_nice=args.nc, is_uncensored=args.uc
                )
            )
        elif args.tp:
            self.handle_code(*jvav.DmmUtil(proxy_addr=args.proxy).get_top_stars(1))
        elif args.sr != "" or args.srn != "":
            star_name = args.sr if args.sr != "" else args.srn
            flag_srn = True if args.srn != "" else False
            if langdetect.detect(star_name) != "ja":  # zh
                wiki_json = jvav.WikiUtil(proxy_addr=args.proxy).get_wiki_page_by_lang(
                    topic=star_name, from_lang="zh", to_lang="ja"
                )
                if wiki_json and wiki_json["lang"] == "ja":
                    star_name = wiki_json["title"]
            if not flag_srn:
                self.handle_code(
                    *jvav.DmmUtil(proxy_addr=args.proxy).get_nice_avs_by_star_name(
                        args.sr
                    )
                )
            else:
                self.handle_code(
                    *jvav.JavBusUtil(proxy_addr=args.proxy).get_new_ids_by_star_name(
                        args.srn
                    )
                )
        elif args.pv1 != "":
            self.handle_code(
                *jvav.DmmUtil(proxy_addr=args.proxy).get_pv_by_id(args.pv1)
            )
        elif args.pv2 != "":
            self.handle_code(
                *jvav.AvgleUtil(proxy_addr=args.proxy).get_pv_by_id(args.pv2)
            )
        elif args.tg != "":
            self.handle_code(
                *jvav.JavDbUtil(proxy_addr=args.proxy).get_ids_by_tag(args.tg)
            )
        else:
            self.parser.print_help()


def main():
    parser = JvavArgsParser()
    parser.parse()
    parser.exec()


# pyinstaller --onefile cmd.py --name jvav # to build an exe named jvav.exe
# python -m jvav.cmd
if __name__ == "__main__":
    main()
