# -*- coding: utf-8 -*-
import time
import requests
import json
import queue
import threading
import random
import sqlite3
import tips
import argparse

# 待爬取的id队列
work_id_queue = queue.Queue()


# 代理设置
proxies = {
    "https": "127.0.0.1:7890"
}


def get_response(request_url, request_headers, request_method, request_params,
                 request_form=None):
    """
    发送请求
    :param request_url: 请求的url地址
    :param request_headers: request headers
    :param request_method: 请求方式
    :param request_params: 请求参数
    :param request_form: POST 请求所需的表单
    :return: response
    """
    if request_method == "GET":
        res = requests.get(url=request_url, headers=request_headers, params=request_params,
                           proxies=proxies)
    else:
        res = requests.post(url=request_url, headers=request_headers, params=request_params,
                            proxies=proxies)

    if res.status_code == 200:
        return res.text
    else:
        print("{} \n请求失败".format(request_url))


def get_work_image_id(group_number, url="https://www.pixiv.net/ajax/follow_latest/illust"):
    """
    获取关注用户的作品id，检测数量
    :param group_number: qq群号
    :param url: 接口
    :return:
    """
    headers = {
        "Connection": "close",
        "Cookie": "first_visit_datetime_pc=2023-05-12+15%3A17%3A57; p_ab_id=4; p_ab_id_2=2; p_ab_d_id=850076202; yuid_b=FpmTMEY; _fbp=fb.1.1683872277891.263841267; _gid=GA1.2.27316184.1683872279; _gcl_au=1.1.555878850.1683872298; PHPSESSID=94084444_gUfm9BADjdMn6Jq873m1ww0R709GcwUE; device_token=7b78d2b66b7ba0dfa2679da9d9ed7ba0; privacy_policy_agreement=5; c_type=21; privacy_policy_notification=0; a_type=0; b_type=1; QSI_S_ZN_5hF4My7Ad6VNNAi=v:0:0; login_ever=yes; _im_vid=01H079T9MQXZMVDYSE7D1DFN9Z; user_language=zh; _ga_MZ1NL4PHH0=GS1.1.1683872311.1.1.1683872411.0.0.0; __cf_bm=JBm8GtVO6REJzHYI7cD_KZZWoZLUBoLCBXV29LHMYnc-1683877809-0-ATOm/4ESqJ4sdXBv5uBHmuEwhDU5UJg5Ss67AX+wgtLUtNSjGWncnE5hYIx2+XXZw+zlxnkv1Ltseju8FLiNYKh/bWsomrlc8scP7i9qGCY78qJMfEhhw+dVCuMU3PcKyBqw4RqWUPLnI/cntUWsVDT2hymWhTd7Z9a2wvRtmAkI; cto_bundle=0RWarF9weFRFd2pDNWVUVENoaE5DR3FleXZZWFk3UjNVOWpaJTJGdHBhU3E5dUhHY003JTJCelJLMTVna0QwMDJlemdGNzhpQXR1cWpZc0RWYiUyQjVGWnpYOGZwejBiRGJHWkxrVERlMnMlMkIwTDQ5MHBwVkd4bWVNOU9kT01tREtiOUQyeGhROCUyQll4YjV2S3F2Rm9MUVdDdk1WRU1NSEtRJTNEJTNE; _ga=GA1.1.1298717784.1683872277; tag_view_ranking=Lt-oEicbBr~tgP8r-gOe_~CiSfl_AE0h~azESOjmQSV~uW5495Nhg-~Ie2c51_4Sp~faHcYIP1U0~OcphT8vZeM~mxDE3obNef~kHJk-sR8-P~ZeMHmcDGS6~QVg7ebWJdM~rjhT-2evFj~KN7uxuR89w~4fhov5mA8J~QOlvfk_Wxj; _ga_75BBYNYN9J=GS1.1.1683877718.2.1.1683878104.0.0.0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    }
    last_first_id = None
    page_num = 0

    for page in range(1, 31):
        page_num = page
        params = {
            "p": page,
            "mode": "all",
            "lang": "zh",
            "version": "da9d6feae015556b41789902d72b2d9b648608bb"
        }

        response = get_response(url, headers, "GET", params)
        res_json = json.loads(response)
        work_id_list = res_json["body"]["page"]["ids"]
        if last_first_id == work_id_list[0]:
            # 最后一页则暂停采集
            break
        else:
            last_first_id = work_id_list[0]

        for work_id in work_id_list:
            # 查询id是否存在，不存在则加入至爬取队列中
            if not query_id_whether_existence(work_id):
                work_id_queue.put(work_id)

    # 向所在QQ群反馈信息
    work_id_queue_size = work_id_queue.qsize()
    message = "Ice检测到前{}页中共{}张图不在图库中".format(page_num, work_id_queue_size)
    tips.normal_tip(group_number, message)


def save_image_id_fingerprint(image_id):
    """
    保存图片id指纹
    :param image_id:
    :return:
    """
    conn = sqlite3.connect("./db/image_id.db")
    cursor = conn.cursor()

    # 建表
    cursor.execute("""
                    create table if not exists pixiv_image_id(
                    image_id varchar(30) primary key
                            )""")

    # 插入数据
    insert_sql = """insert into pixiv_image_id(
                    image_id) values ('%s')""" % image_id
    cursor.execute(insert_sql)
    conn.commit()

    # 关闭
    cursor.close()
    conn.close()


def query_id_whether_existence(image_id):
    """
    查询 image_id 是否在数据库中
    :param image_id:
    :return:
    """
    conn = sqlite3.connect("./db/image_id.db")
    cursor = conn.cursor()

    # 建表
    cursor.execute("""
                        create table if not exists pixiv_image_id(
                        image_id varchar(30) primary key
                                )""")

    # 查询
    query_sql = """select * from pixiv_image_id where image_id=%s""" % image_id
    cursor.execute(query_sql)
    image_id = cursor.fetchall()

    # 关闭
    cursor.close()
    conn.close()

    # 存在则返回 True
    if image_id:
        return True
    else:
        return False


def download_image(group_number, download_url="https://www.pixiv.net/ajax/illust/{}/pages"):
    """
    下载图片
    :param group_number: qq群号
    :param download_url:
    :return:
    """
    print("开始爬取")
    while not work_id_queue.empty():
        work_id = work_id_queue.get()
        url = download_url.format(work_id)
        headers = {
            "Connection": "close",
            "Referer": "https://www.pixiv.net/artworks/{}".format(work_id),
            "Cookie": "first_visit_datetime_pc=2023-05-12+15%3A17%3A57; p_ab_id=4; p_ab_id_2=2; p_ab_d_id=850076202; yuid_b=FpmTMEY; _fbp=fb.1.1683872277891.263841267; _gid=GA1.2.27316184.1683872279; _gcl_au=1.1.555878850.1683872298; PHPSESSID=94084444_gUfm9BADjdMn6Jq873m1ww0R709GcwUE; device_token=7b78d2b66b7ba0dfa2679da9d9ed7ba0; privacy_policy_agreement=5; c_type=21; privacy_policy_notification=0; a_type=0; b_type=1; QSI_S_ZN_5hF4My7Ad6VNNAi=v:0:0; login_ever=yes; _im_vid=01H079T9MQXZMVDYSE7D1DFN9Z; user_language=zh; _ga_MZ1NL4PHH0=GS1.1.1683872311.1.1.1683872411.0.0.0; __cf_bm=JBm8GtVO6REJzHYI7cD_KZZWoZLUBoLCBXV29LHMYnc-1683877809-0-ATOm/4ESqJ4sdXBv5uBHmuEwhDU5UJg5Ss67AX+wgtLUtNSjGWncnE5hYIx2+XXZw+zlxnkv1Ltseju8FLiNYKh/bWsomrlc8scP7i9qGCY78qJMfEhhw+dVCuMU3PcKyBqw4RqWUPLnI/cntUWsVDT2hymWhTd7Z9a2wvRtmAkI; cto_bundle=0RWarF9weFRFd2pDNWVUVENoaE5DR3FleXZZWFk3UjNVOWpaJTJGdHBhU3E5dUhHY003JTJCelJLMTVna0QwMDJlemdGNzhpQXR1cWpZc0RWYiUyQjVGWnpYOGZwejBiRGJHWkxrVERlMnMlMkIwTDQ5MHBwVkd4bWVNOU9kT01tREtiOUQyeGhROCUyQll4YjV2S3F2Rm9MUVdDdk1WRU1NSEtRJTNEJTNE; _ga=GA1.1.1298717784.1683872277; tag_view_ranking=Lt-oEicbBr~tgP8r-gOe_~CiSfl_AE0h~azESOjmQSV~uW5495Nhg-~Ie2c51_4Sp~faHcYIP1U0~OcphT8vZeM~mxDE3obNef~kHJk-sR8-P~ZeMHmcDGS6~QVg7ebWJdM~rjhT-2evFj~KN7uxuR89w~4fhov5mA8J~QOlvfk_Wxj; _ga_75BBYNYN9J=GS1.1.1683877718.2.1.1683878104.0.0.0",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
        }

        params = {
            "lang": "zh",
            "version": "da9d6feae015556b41789902d72b2d9b648608bb"
        }

        response = get_response(url, headers, "GET", params)
        res_json = json.loads(response)
        if len(res_json["body"]) > 1:
            for data in res_json["body"]:
                image_url = data["urls"]["original"]

                # download image
                image_content = requests.get(url=image_url, headers=headers, proxies=proxies).content
                image_name = image_url.split("/")[-1].split(".")[0]
                with open(f"./db/色图/{image_name}.{image_url.split('.')[-1]}", mode="wb") as image:
                    image.write(image_content)

        save_image_id_fingerprint(work_id)
        time.sleep(random.uniform(0.5, 1.5))
        surplus_image = work_id_queue.qsize()
        if surplus_image % 100 == 0:
            message = "目前剩余{}张图待处理".format(surplus_image)
            print(message)


def crawling_images_in_the_queue(group_number):
    """
    对 work_id_queue 队列中的图片进行爬取
    :return:
    """
    my_thread = list()
    for _ in range(10):
        thread = threading.Thread(target=download_image, args=(group_number, ))
        my_thread.append(thread)
        thread.start()

    for t in my_thread:
        t.join()


def run_pixiv_image_spider(args):
    """
    运行 pixiv 爬虫
    :param args:
    :return:
    """
    # 检测图片数量
    get_work_image_id(args.group)

    # 运行爬虫
    tips.normal_tip(args.group, "Ice立马派出爬虫前往pixiv消灭它们！")
    crawling_images_in_the_queue(args.group)
    tips.normal_tip(args.group, "主人, 图库更新完毕")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="it's pixiv image spider"
    )
    parser.add_argument("-g", "--group", help="group number")
    args = parser.parse_args()

    run_pixiv_image_spider(args)
