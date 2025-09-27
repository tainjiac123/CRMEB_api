import traceback
import logging
from unit_tools.handel_data.var_util import replace_variables
from unit_tools.log_util.logger import get_logger   # ✅ 引入你写的日志函数

logger = get_logger(__name__)

class RequestUtil:
    def __init__(self, client):
        """
        :param client: requests.Session 或其他 HTTP 客户端实例
        """
        self.client = client

    def send_request(self, base_info: dict, case: dict):
        """
        统一发送 HTTP 请求，支持 JSON、表单、multipart/form-data 自动识别
        """
        try:
            # 1. 基础信息
            method = base_info.get("method", "").lower()
            url = replace_variables(base_info.get("url", ""))
            headers = base_info.get("headers", {}) or {}

            # 2. 请求参数
            params = case.get("params")
            json_data = case.get("json")
            form_data = case.get("data")
            files_data = case.get("files")

            # 3. 变量替换
            if params:
                params = replace_variables(params)
            if json_data:
                json_data = replace_variables(json_data)
            if form_data:
                form_data = replace_variables(form_data)
            if files_data:
                # 文件字段格式：{"file_field": "path/to/file"}
                files_data = {k: (None, replace_variables(v)) for k, v in files_data.items()}

            # 4. multipart/form-data 自动处理
            if form_data and not headers.get("Content-Type"):
                files_data = {k: (None, v) for k, v in form_data.items()}
                form_data = None  # 避免同时传 data 和 files

            # 5. 组装请求参数
            request_kwargs = {
                "headers": headers,
                "params": params,
                "json": json_data,
                "data": form_data,
                "files": files_data
            }
            # 去掉 None
            request_kwargs = {k: v for k, v in request_kwargs.items() if v is not None}

            # 6. 请求前日志
            self._before_request(method, url, request_kwargs)

            # 7. 发送请求
            res = getattr(self.client, method)(url, **request_kwargs)

            # 8. 请求后日志
            self._after_request(res)

            return res

        except Exception as e:
            logger.error("请求发送失败: %s", e, exc_info=True)
            return {
                "http_status": None,
                "status": False,
                "error": str(e)
            }

    def _before_request(self, method, url, kwargs):
        logger.info("[Request] %s %s", method.upper(), url)
        for k, v in kwargs.items():
            logger.debug("  %s: %s", k, v)

    def _after_request(self, res):
        try:
            if isinstance(res, dict):
                logger.info("[Response] 状态码: %s 响应数据: %s", res.get("http_status"), res)
            else:
                # 如果是 requests.Response 对象
                logger.info("[Response] 状态码: %s 响应数据: %s", res.status_code, res.text)
        except Exception as e:
            logger.error("[Response] 日志打印失败: %s", e)
