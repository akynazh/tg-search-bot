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


class UploadContactProfilePhoto(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``151``
        - ID: ``B91A83BF``

    Parameters:
        user_id (:obj:`InputUser <pyrogram.raw.base.InputUser>`):
            N/A

        suggest (``bool``, *optional*):
            N/A

        save (``bool``, *optional*):
            N/A

        file (:obj:`InputFile <pyrogram.raw.base.InputFile>`, *optional*):
            N/A

        video (:obj:`InputFile <pyrogram.raw.base.InputFile>`, *optional*):
            N/A

        video_start_ts (``float`` ``64-bit``, *optional*):
            N/A

    Returns:
        :obj:`photos.Photo <pyrogram.raw.base.photos.Photo>`
    """

    __slots__: List[str] = ["user_id", "suggest", "save", "file", "video", "video_start_ts"]

    ID = 0xb91a83bf
    QUALNAME = "functions.photos.UploadContactProfilePhoto"

    def __init__(self, *, user_id: "raw.base.InputUser", suggest: Optional[bool] = None, save: Optional[bool] = None, file: "raw.base.InputFile" = None, video: "raw.base.InputFile" = None, video_start_ts: Optional[float] = None) -> None:
        self.user_id = user_id  # InputUser
        self.suggest = suggest  # flags.3?true
        self.save = save  # flags.4?true
        self.file = file  # flags.0?InputFile
        self.video = video  # flags.1?InputFile
        self.video_start_ts = video_start_ts  # flags.2?double

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "UploadContactProfilePhoto":
        
        flags = Int.read(b)
        
        suggest = True if flags & (1 << 3) else False
        save = True if flags & (1 << 4) else False
        user_id = TLObject.read(b)
        
        file = TLObject.read(b) if flags & (1 << 0) else None
        
        video = TLObject.read(b) if flags & (1 << 1) else None
        
        video_start_ts = Double.read(b) if flags & (1 << 2) else None
        return UploadContactProfilePhoto(user_id=user_id, suggest=suggest, save=save, file=file, video=video, video_start_ts=video_start_ts)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 3) if self.suggest else 0
        flags |= (1 << 4) if self.save else 0
        flags |= (1 << 0) if self.file is not None else 0
        flags |= (1 << 1) if self.video is not None else 0
        flags |= (1 << 2) if self.video_start_ts is not None else 0
        b.write(Int(flags))
        
        b.write(self.user_id.write())
        
        if self.file is not None:
            b.write(self.file.write())
        
        if self.video is not None:
            b.write(self.video.write())
        
        if self.video_start_ts is not None:
            b.write(Double(self.video_start_ts))
        
        return b.getvalue()
