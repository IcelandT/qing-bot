# -*- coding: utf-8 -*-
import sqlite3
from tools import tips


class QueryTableSize:
    def __init__(self, table_name, query_data=None):
        self.table = table_name
        if query_data:
            self.query_data = query_data
        self.conn = sqlite3.connect("./db/image_id.db")
        self.cursor = self.conn.cursor()

    def query_table_size(self, group_number=None):
        """
        查询表的大小
        :return:
        """
        # 查询语句
        query_sql = f"""select image_id from {self.table}"""
        try:
            self.cursor.execute(query_sql)
            length = len(self.cursor.fetchall())
            print(length)
            message = f"图库中共有{length}张图片"
            tips.normal_tip(group_number, message)
        except sqlite3.OperationalError:
            tips.normal_tip(group_number, "查询的表不存在")

        # 关闭
        self.cursor.close()
        self.conn.cursor()


if __name__ == '__main__':
    QueryTableSize("pixiv_image_id").query_table_size()

