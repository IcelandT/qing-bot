# -*- coding: utf-8 -*-
from tools import color_image, tips
import os


def parsel(message, qq_number, group_number=None):
    """
    处理信息
    :param message:
    :param qq_number:
    :param group_number:
    :return:
    """
    # 判断用户输入
    if "色图" in message:
        color_image.send_color_image(group_number)
    if "更新图库" in message:
        if qq_number == 1185330343:
            tips.normal_tip(group_number, "Ice收到主人的命令: 更新图库")
            this_path = os.getcwd()
            path = this_path + "\\tools\\image_spider.py"
            os.system(f"start cmd.exe /c python {path} -g {group_number}")
        else:
            tips.normal_tip(group_number, "对不起, 你没有权限这样做", qq_number)











