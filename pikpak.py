# -*- coding: UTF-8 -*-
"""PikPak 官方 OpenAPI 客户端。

通过用户名 / 密码登录获取 token，再调用官方 drive API 直接提交磁力链接的
离线下载任务，取代原先「向 PikPak6_Bot 发送消息」的保存方式。

参考实现: https://pypi.org/project/pikpakapi/
"""

import hashlib
import json
import logging
import os
import time

import requests

LOG = logging.getLogger(__name__)

CLIENT_ID = "YNxT9w7GMdWvEOKa"
CLIENT_SECRET = "dbw2OtmVEeuUvIptb1Coyg"
CLIENT_VERSION = "1.47.1"
PACKAGE_NAME = "com.pikcloud.pikpak"

API_HOST = "https://api-drive.mypikpak.com"
USER_HOST = "https://user.mypikpak.com"

# PikPak 客户端内置的验签盐值
SALTS = [
    "Gez0T9ijiI9WCeTsKSg3SMlx",
    "zQdbalsolyb1R/",
    "ftOjr52zt51JD68C3s",
    "yeOBMH0JkbQdEFNNwQ0RI9T3wU/v",
    "BRJrQZiTQ65WtMvwO",
    "je8fqxKPdQVJiy1DM6Bc9Nb1",
    "niV",
    "9hFCW2R1",
    "sHKHpe2i96",
    "p7c5E6AcXQ/IJUuAEC9W6",
    "",
    "aRv9hjc9P+Pbn+u3krN6",
    "BzStcgE8qVdqjEH16l4",
    "SqgeZvL5j9zoHP95xWHt",
    "zVof5yaJkPe3VFpadPof",
]


def captcha_sign(device_id: str, timestamp: str) -> str:
    """生成登录所需的 captcha_sign。"""
    sign = CLIENT_ID + CLIENT_VERSION + PACKAGE_NAME + device_id + timestamp
    for salt in SALTS:
        sign = hashlib.md5((sign + salt).encode()).hexdigest()
    return "1." + sign


class PikPakClient:
    def __init__(
        self,
        username: str = "",
        password: str = "",
        proxy: str = "",
        token_path: str = "",
    ):
        self.username = username or ""
        self.password = password or ""
        self.proxy = proxy or ""
        self.proxies = {"http": self.proxy, "https": self.proxy} if self.proxy else None
        self.token_path = token_path or os.path.expanduser(
            "~/.tg_search_bot/pikpak_token.json"
        )
        self.access_token = None
        self.refresh_token = None
        self.user_id = None
        self.device_id = None
        self.expires_at = 0
        self._load_token()

    @property
    def enabled(self):
        return bool(self.username and self.password)

    # ---- token 持久化 ----
    def _load_token(self):
        try:
            if os.path.exists(self.token_path):
                with open(self.token_path, "r", encoding="utf8") as f:
                    data = json.load(f)
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                self.user_id = data.get("user_id")
                self.device_id = data.get("device_id")
                self.expires_at = data.get("expires_at", 0)
        except Exception as e:
            LOG.error(f"Failed to load PikPak token: {e}")

    def _save_token(self):
        try:
            os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
            with open(self.token_path, "w", encoding="utf8") as f:
                json.dump(
                    {
                        "access_token": self.access_token,
                        "refresh_token": self.refresh_token,
                        "user_id": self.user_id,
                        "device_id": self.device_id,
                        "expires_at": self.expires_at,
                    },
                    f,
                    ensure_ascii=False,
                    indent=4,
                )
        except Exception as e:
            LOG.error(f"Failed to save PikPak token: {e}")

    # ---- 基础请求 ----
    def _device_id(self) -> str:
        if not self.device_id:
            self.device_id = hashlib.md5(
                f"{self.username}{self.password}".encode()
            ).hexdigest()
            self._save_token()
        return self.device_id

    def _post_json(self, url: str, data: dict, headers: dict = None, timeout: int = 30):
        h = {"Content-Type": "application/json; charset=utf-8"}
        if headers:
            h.update(headers)
        return requests.post(
            url, json=data, headers=h, proxies=self.proxies, timeout=timeout
        )

    def _post_form(self, url: str, data: dict, headers: dict = None, timeout: int = 30):
        h = {"Content-Type": "application/x-www-form-urlencoded"}
        if headers:
            h.update(headers)
        return requests.post(
            url, data=data, headers=h, proxies=self.proxies, timeout=timeout
        )

    def _authorized_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "X-Device-Id": self._device_id(),
        }

    # ---- 登录 / 刷新 ----
    def _captcha_init(self, action: str):
        device_id = self._device_id()
        ts = str(int(time.time() * 1000))
        meta = {
            "captcha_sign": captcha_sign(device_id, ts),
            "client_version": CLIENT_VERSION,
            "package_name": PACKAGE_NAME,
            "user_id": self.user_id or "",
            "timestamp": ts,
            "username": self.username,
        }
        payload = {
            "client_id": CLIENT_ID,
            "action": action,
            "device_id": device_id,
            "meta": meta,
        }
        resp = self._post_json(f"{USER_HOST}/v1/shield/captcha/init", payload)
        if resp.status_code != 200:
            LOG.error(
                f"PikPak captcha init failed: {resp.status_code} {resp.text[:300]}"
            )
            return None
        data = resp.json()
        token = data.get("captcha_token")
        if not token:
            LOG.error(f"PikPak captcha init returned no token: {data}")
            return None
        return token

    def login(self):
        if not self.enabled:
            return False, "未配置 PikPak 账号"
        captcha_token = self._captcha_init(f"POST:{USER_HOST}/v1/auth/signin")
        if not captcha_token:
            return False, "验证码初始化失败"
        data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "password": self.password,
            "username": self.username,
            "captcha_token": captcha_token,
        }
        resp = self._post_form(f"{USER_HOST}/v1/auth/signin", data)
        if resp.status_code != 200:
            reason = "登录失败（账号或密码错误）"
            try:
                j = resp.json()
                reason = j.get("error_description") or j.get("error") or reason
            except Exception:
                pass
            LOG.error(f"PikPak login failed: {resp.status_code} {resp.text[:300]}")
            return False, reason
        j = resp.json()
        if "access_token" not in j:
            reason = j.get("error_description") or j.get("error") or "登录失败"
            LOG.error(f"PikPak login returned error: {j}")
            return False, reason
        self.access_token = j["access_token"]
        self.refresh_token = j["refresh_token"]
        self.user_id = j.get("sub")
        self.expires_at = int(time.time()) + int(j.get("expires_in", 7200))
        self._save_token()
        LOG.info("PikPak login success")
        return True, "登录成功"

    def refresh(self):
        if not self.refresh_token:
            return False, "缺少 refresh_token"
        data = {
            "client_id": CLIENT_ID,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token",
        }
        resp = self._post_json(f"{USER_HOST}/v1/auth/token", data)
        if resp.status_code != 200:
            LOG.error(f"PikPak refresh failed: {resp.status_code} {resp.text[:300]}")
            return False, "令牌刷新失败"
        j = resp.json()
        if "access_token" not in j:
            return False, j.get("error_description") or j.get("error") or "令牌刷新失败"
        self.access_token = j["access_token"]
        self.refresh_token = j["refresh_token"]
        self.user_id = j.get("sub")
        self.expires_at = int(time.time()) + int(j.get("expires_in", 7200))
        self._save_token()
        return True, "刷新成功"

    def ensure_login(self):
        if not self.enabled:
            return False, "未配置 PikPak 账号"
        if not self.access_token:
            return self.login()
        if self.expires_at and time.time() > self.expires_at - 60:
            ok, msg = self.refresh()
            if ok:
                return True, msg
            return self.login()
        return True, "已登录"

    # ---- 离线下载 ----
    def offline_download(
        self, magnet_url: str, name: str = None, parent_id: str = None
    ):
        """将磁力链接提交为 PikPak 离线下载任务。

        :return tuple[bool, str]: (是否成功, 提示信息)
        """
        if not self.enabled:
            return False, "未配置 PikPak 账号"
        ok, msg = self.ensure_login()
        if not ok:
            return False, msg
        data = {
            "kind": "drive#file",
            "upload_type": "UPLOAD_TYPE_URL",
            "url": {"url": magnet_url},
            "folder_type": "DOWNLOAD" if not parent_id else "",
        }
        if name:
            data["name"] = name
        if parent_id:
            data["parent_id"] = parent_id
        for attempt in range(2):
            resp = self._post_json(
                f"{API_HOST}/drive/v1/files", data, headers=self._authorized_headers()
            )
            if resp.status_code == 200:
                j = resp.json()
                if "error" in j:
                    if j.get("error_code") == 16 and attempt == 0:
                        self.refresh()
                        continue
                    return (
                        False,
                        j.get("error_description") or j.get("error") or "未知错误",
                    )
                return True, "已提交离线任务到 PikPak"
            if resp.status_code in (401, 403) and attempt == 0:
                self.refresh()
                continue
            reason = f"HTTP {resp.status_code}"
            try:
                j = resp.json()
                reason = j.get("error_description") or j.get("error") or reason
            except Exception:
                pass
            LOG.error(f"PikPak offline download failed: {resp.text[:300]}")
            return False, reason
        return False, "离线任务提交失败"
