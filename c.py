# SCP-079-NOPORN - Auto delete NSFW media messages
# Copyright (C) 2019-2020 SCP-079 <https://scp-079.org>
#
# This file is part of SCP-079-NOPORN.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import argparse
from keras.preprocessing import image
from keras.applications.imagenet_utils import preprocess_input
from model import OpenNsfw
import keras
#from image_utils import create_yahoo_image_loader
import tensorflow
from tensorflow.keras.utils import load_img, img_to_array 
import cv2
import math
import numpy as np
# Enable logging
logger = logging.getLogger(__name__)


def porn_test(client: Client, message: Message) -> bool:
    # Test image porn score in the test group
    try:
        origin_text = get_text(message)

        if re.search(f"^{lang('admin')}{lang('colon')}[0-9]", origin_text):
            aid = get_int(origin_text.split("\n\n")[0].split(lang('colon'))[1])
        else:
            aid = message.from_user.id

        text = ""

        # Detected record
        content = get_content(message)
        detection = glovar.contents.get(content, "")

        if detection == "nsfw":
            text += f"{lang('record_content')}{lang('colon')}{code('True')}\n"

        # Detected url
        detection = is_detected_url(message, True)

        if detection:
            text += f"{lang('record_link')}{lang('colon')}{code(code('True'))}\n"

        # Restricted channel
        if is_restricted_channel(message):
            text += f"{lang('restricted_channel')}{lang('colon')}{code('True')}\n"

        # Get the image
        file_id, file_ref, _ = get_file_id(message)
        image_path = get_downloaded_path(client, file_id, file_ref)
        image_hash = image_path and get_md5sum("file", image_path)

        # Get porn score
        porn = (image_path and get_porn(image_path))

        if porn:
            text += f"{lang('porn_score')}{lang('colon')}{code(f'{porn:.8f}')}\n"

        # Get color
        color = image_path and get_color(image_path)

        if color:
            text += f"{lang('color')}{lang('colon')}{code(color)}\n"

        # Get promote sticker
        sticker = is_promote_sticker(client, message)

        if sticker:
            text += f"{lang('promote_sticker')}{lang('colon')}{code('True')}\n"

        # Send the result
        if text:
            whitelisted = ((content and (content in glovar.except_ids["long"] or content in glovar.except_ids["temp"]))
                           or image_hash in glovar.except_ids["temp"])
            text += f"{lang('white_listed')}{lang('colon')}{code(whitelisted)}\n"
            text = f"{lang('admin')}{lang('colon')}{mention_id(aid)}\n\n" + text
            thread(send_message, (client, glovar.test_group_id, text, message.message_id))

        # Delete the image file
        image_path and thread(delete_file, (image_path,))

        return True
    except Exception as e:
        logger.warning(f"Porn test error: {e}", exc_info=True)

    return False