import requests


class WechatSubscribe:
    def __init__(self):
        self.appid = "wx0d22019eaad3050c"
        self.secret = "a16cb285fca4fc4f7c710df712cc4a56"
        self.url = f"https://api.weixin.qq.com/cgi-bin/" \
                   f"token?grant_type=client_credential" \
                   f"&appid={self.appid}&secret={self.secret}"

    def get_access_token(self):
        """
        获取小程序全局唯一后台接口调用凭据 access_token
        :return:
        """
        res = requests.get(self.url, timeout=3).json()
        access_token = res.get("access_token", None)
        return access_token

    def sendMsg(self, buying: str, price: str):
        """
        发送订阅消息
        :param
        :param
        :return:
        """
        access_token = self.get_access_token()
        api = f"https://api.weixin.qq.com/cgi-bin/" \
              f"message/subscribe/send?access_token={access_token}"
        # key是模板的字段名称，value是字段对应的值
        # e.g. data = {"name3": {"value": "红烧茄子鸡肉"}, "amount5": {"value": "5"}}
        data = {"name3": {"value": buying}, "amount5": {"value": price}}

        post_data = {
            "touser": "ogsmF4n85zcKIRRKPqiWG6KmusDI",  # 微信用户的open_id
            "template_id": "4HskV0UGpaaPqojLHWqCl3m-8Ktvy6nPLVIv3MQoG2M",  # 订阅消息模板id
            "data": data,  # 模板字段及其对应的字段，注意字段类型
            "page": "pages/mine/mine",  # 需要跳转的路径（前端提供）
        }
        try:
            result = requests.post(api, json=post_data, timeout=3).json()  # 发送订阅消息
        except:
            result = {}
        # print(post_data)
        print(result)
        errcode = result.get("errcode")
        if errcode == 0:
            return True
        return False


if __name__ == '__main__':
    ws = WechatSubscribe()
    name = " 红烧肉 蒸鲈鱼 土豆丝"
    test = "14"
    ws.sendMsg(name, test)
