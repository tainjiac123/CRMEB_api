import requests
import yaml
import os
from urllib.parse import urljoin
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from unit_tools.handel_data.configParse import ConfigParser


class APIRequest:
    def __init__(self, headers=None):
        # 读取配置
        config = ConfigParser()
        self.base_url = config.get("base_url")
        self.mysql_config = config.get("mysql")  # 如果后续需要数据库连接，可以直接用
        self.headers = headers or {}
        self.timeout = 10

        # Session + 重试机制
        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE", "PATCH"]
        )
        self.session.mount("http://", HTTPAdapter(max_retries=retries))
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def _get_token(self):
        """从 extract.yaml 读取 Token"""
        extract_path = os.path.join(os.getcwd(), "extract.yaml")
        if os.path.exists(extract_path):
            with open(extract_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                return data.get("token")
        return None

    def _send(self, method, endpoint, **kwargs):
        """统一请求入口（内部方法）"""
        url = urljoin(self.base_url, endpoint)
        headers = kwargs.pop("headers", self.headers.copy())

        # 自动加 Token
        token = self._get_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"

        try:
            response = self.session.request(
                method, url, headers=headers, timeout=self.timeout, **kwargs
            )
            try:
                res_json = response.json()
            except ValueError:
                res_json = {"raw_text": response.text}

            return {
                "http_status": response.status_code,  # HTTP 状态码
                "status": True,                       # 请求是否成功（网络层）
                "data": res_json                      # 接口返回的 JSON 数据
            }
        except requests.exceptions.RequestException as e:
            return {
                "http_status": None,
                "status": False,
                "error": str(e)
            }

    def get(self, endpoint, **kwargs):
        """GET 请求"""
        return self._send("GET", endpoint, **kwargs)

    def post(self, endpoint, **kwargs):
        """POST 请求"""
        return self._send("POST", endpoint, **kwargs)

    def send(self, method: str, endpoint: str, **kwargs):
        """
        对外暴露的统一请求方法
        - method: 请求方法（GET/POST/PUT/DELETE等）
        - endpoint: 接口路径（相对路径）
        - kwargs: 其他 requests 支持的参数
        """
        return self._send(method.upper(), endpoint, **kwargs)


# ================== 运行示例 ==================
if __name__ == "__main__":
    """
    运行方式：
    python Crmeb_api/api/request_api.py
    """
    client = APIRequest()

    print("当前 Base URL:", client.base_url)
    print("当前 MySQL 配置:", client.mysql_config)

    # GET 请求示例
    # res_get = client.get("/get", params={"test": "123"})
    # print("GET 请求结果：", res_get)

    # POST 请求示例
    res_post = client.post("/api/login", data={"account": "19122674903", "password": "123123"})
    print("POST 请求结果：", res_post)
