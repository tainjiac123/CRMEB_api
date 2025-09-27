# Crmeb_api/api/auth_api.py
from api.request_api import APIRequest
from unit_tools.handel_data.extract_handler import handle_extract


class AuthAPI:
    def __init__(self):
        self.client = APIRequest()

    def login(self, account, password):
        """
        登录接口：提交账号密码，提取 token
        """
        url = "/api/login"
        payload = {"account": account, "password": password}

        # 注意：如果是表单格式提交，用 data=
        res = self.client.post(url, data=payload)

        # 自动提取 token（根据 extract_handler.py 配置）
        handle_extract(url, res)

        return res

    def logout(self):
        """
        登出接口：清除登录状态
        """
        url = "/api/logout"
        return self.client.post(url)

    def get_user_info(self, user_id):
        """
        获取用户信息接口：需要鉴权
        """
        url = f"/api/users/{user_id}"
        return self.client.get(url)


# ================== main 调试 ==================
if __name__ == "__main__":
    api = AuthAPI()
    res = api.login("19122674903", "123123")
    print("✅ 登录返回：", res)
