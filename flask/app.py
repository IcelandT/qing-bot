from flask import Flask, request
from flask_migrate import Migrate
from parsel_message import parsel


app = Flask(__name__)


@app.route('/', methods=['POST'])
def Get_Message():
    '''
    监听消息
    :return:
    '''
    # 群聊
    if request.get_json().get('message_type') == 'group':  # 如果是群聊信息 private 私聊消息
        group_number = request.get_json().get('group_id')  # 获取群号
        qq_number = request.get_json().get('sender').get('user_id')  # 获取信息发送者的 QQ 号码
        message = request.get_json().get('raw_message')  # 获取原始信息
        parsel(message, qq_number, group_number)

    return 'OK'


if __name__ == '__main__':
    app.run()
