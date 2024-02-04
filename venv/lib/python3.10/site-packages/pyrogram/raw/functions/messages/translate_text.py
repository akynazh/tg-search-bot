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


class TranslateText(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``151``
        - ID: ``24CE6DEE``

    Parameters:
        to_lang (``str``):
            N/A

        peer (:obj:`InputPeer <pyrogram.raw.base.InputPeer>`, *optional*):
            N/A

        msg_id (``int`` ``32-bit``, *optional*):
            N/A

        text (``str``, *optional*):
            N/A

        from_lang (``str``, *optional*):
            N/A

    Returns:
        :obj:`messages.TranslatedText <pyrogram.raw.base.messages.TranslatedText>`
    """

    __slots__: List[str] = ["to_lang", "peer", "msg_id", "text", "from_lang"]

    ID = 0x24ce6dee
    QUALNAME = "functions.messages.TranslateText"

    def __init__(self, *, to_lang: str, peer: "raw.base.InputPeer" = None, msg_id: Optional[int] = None, text: Optional[str] = None, from_lang: Optional[str] = None) -> None:
        self.to_lang = to_lang  # string
        self.peer = peer  # flags.0?InputPeer
        self.msg_id = msg_id  # flags.0?int
        self.text = text  # flags.1?string
        self.from_lang = from_lang  # flags.2?string

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "TranslateText":
        
        flags = Int.read(b)
        
        peer = TLObject.read(b) if flags & (1 << 0) else None
        
        msg_id = Int.read(b) if flags & (1 << 0) else None
        text = String.read(b) if flags & (1 << 1) else None
        from_lang = String.read(b) if flags & (1 << 2) else None
        to_lang = String.read(b)
        
        return TranslateText(to_lang=to_lang, peer=peer, msg_id=msg_id, text=text, from_lang=from_lang)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.peer is not None else 0
        flags |= (1 << 0) if self.msg_id is not None else 0
        flags |= (1 << 1) if self.text is not None else 0
        flags |= (1 << 2) if self.from_lang is not None else 0
        b.write(Int(flags))
        
        if self.peer is not None:
            b.write(self.peer.write())
        
        if self.msg_id is not None:
            b.write(Int(self.msg_id))
        
        if self.text is not None:
            b.write(String(self.text))
        
        if self.from_lang is not None:
            b.write(String(self.from_lang))
        
        b.write(String(self.to_lang))
        
        return b.getvalue()
