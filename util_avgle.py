# -*- coding: UTF-8 -*-
import cfg
import requests

BASE_URL = "https://api.avgle.com"
proxies = {}
if cfg.USE_PROXY == 1:
    proxies = {"http": cfg.PROXY_ADDR, "https": cfg.PROXY_ADDR}


def get_video(id: str) -> dict:
    """avgle.com获取预览视频

    :param str id: 番号
    :return dict: 完整视频链接和预览视频链接
    """
    page = 0
    limit = 2
    url = f"{BASE_URL}/v1/jav/{id}/{page}?limit={limit}"

    resp = requests.get(url, proxies=proxies)
    if resp.status_code == 200 and resp.json()["success"]:
        videos = resp.json()["response"]["videos"]
        if videos != []:
            return {"v": videos[0]["video_url"], "pv": videos[0]["preview_video_url"]}
        else:
            return None
    else:
        return None


if __name__ == "__main__":
    v = get_video("ipx-369")
    print(v)
