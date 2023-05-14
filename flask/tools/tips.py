# -*- coding: utf-8 -*-
import requests


headers = {
    "Connection": "close"
}


def normal_tip(group_number, message, qq_number=None):
    """
    提示
    :param group_number:
    :param qq_number:
    :param message:
    :return:
    """
    if qq_number:
        cq_code = "[CQ:at,qq={}]".format(qq_number)
        message = cq_code + message

    url = "http://127.0.0.1:5700/send_group_msg?group_id={}&message={}".format(group_number, message)
    requests.get(url=url, headers=headers)

