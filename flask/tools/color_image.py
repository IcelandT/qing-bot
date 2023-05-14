# -*- coding: utf-8 -*-
import requests
import os
import random


def send_color_image(group_number=None):
    """
    发送图片
    :return:
    """
    path = os.getcwd().replace("\\", "/")
    setu_path = "/db/色图"
    db_path = path + setu_path
    for _, _, image_list in os.walk(db_path):
        image_path = "file:///" + db_path.replace("/", "\\") + "\\" + random.choice(image_list)
        message = "[CQ:image,file={}]".format(image_path)

        url = "http://127.0.0.1:5700/send_group_msg?group_id={0}&message={1}".format(group_number, message)
        headers = {
            'Connection': 'close'
        }
        requests.get(url=url, headers=headers)


if __name__ == '__main__':
    send_color_image()