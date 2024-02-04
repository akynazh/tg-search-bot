#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

from io import BytesIO

from pyrogram.raw.core.primitives import Int, Long, Int128, Int256, Bool, Bytes, String, Double, Vector
from pyrogram.raw.core import TLObject
from pyrogram import raw
from typing import List, Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


class SentCodeTypeEmailCode(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyrogram.raw.base.auth.SentCodeType`.

    Details:
        - Layer: ``151``
        - ID: ``5A159841``

    Parameters:
        email_pattern (``str``):
            N/A

        length (``int`` ``32-bit``):
            N/A

        apple_signin_allowed (``bool``, *optional*):
            N/A

        google_signin_allowed (``bool``, *optional*):
            N/A

        next_phone_login_date (``int`` ``32-bit``, *optional*):
            N/A

    """

    __slots__: List[str] = ["email_pattern", "length", "apple_signin_allowed", "google_signin_allowed", "next_phone_login_date"]

    ID = 0x5a159841
    QUALNAME = "types.auth.SentCodeTypeEmailCode"

    def __init__(self, *, email_pattern: str, length: int, apple_signin_allowed: Optional[bool] = None, google_signin_allowed: Optional[bool] = None, next_phone_login_date: Optional[int] = None) -> None:
        self.email_pattern = email_pattern  # string
        self.length = length  # int
        self.apple_signin_allowed = apple_signin_allowed  # flags.0?true
        self.google_signin_allowed = google_signin_allowed  # flags.1?true
        self.next_phone_login_date = next_phone_login_date  # flags.2?int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "SentCodeTypeEmailCode":
        
        flags = Int.read(b)
        
        apple_signin_allowed = True if flags & (1 << 0) else False
        google_signin_allowed = True if flags & (1 << 1) else False
        email_pattern = String.read(b)
        
        length = Int.read(b)
        
        next_phone_login_date = Int.read(b) if flags & (1 << 2) else None
        return SentCodeTypeEmailCode(email_pattern=email_pattern, length=length, apple_signin_allowed=apple_signin_allowed, google_signin_allowed=google_signin_allowed, next_phone_login_date=next_phone_login_date)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.apple_signin_allowed else 0
        flags |= (1 << 1) if self.google_signin_allowed else 0
        flags |= (1 << 2) if self.next_phone_login_date is not None else 0
        b.write(Int(flags))
        
        b.write(String(self.email_pattern))
        
        b.write(Int(self.length))
        
        if self.next_phone_login_date is not None:
            b.write(Int(self.next_phone_login_date))
        
        return b.getvalue()
