# conftest.py (项目根目录下)
import os
import pytest
import yaml
from unit_tools.log_util.logger import get_logger
from api.request_api import APIRequest
from unit_tools.assertions.assert_util import AssertUtil
from unit_tools.http_client.request_util import RequestUtil
from unit_tools.handel_data.extract_util import ExtractUtil
from unit_tools.handel_data.configParse import ConfigParser

# ---------------- 全局日志 ----------------
logger = get_logger(__name__)

# ---------------- 提取文件清理 ----------------
@pytest.fixture(scope="session", autouse=True)
def clear_extract_file():
    """
    测试会话开始前清理 extract.yaml 文件，保证环境干净
    """
    filepath = os.path.join(os.path.dirname(__file__), "extract.yaml")
    if os.path.exists(filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.safe_dump({}, f, allow_unicode=True)
        logger.info(f"[全局清理] 会话开始前已清空提取文件: {filepath}")
    else:
        logger.info(f"[全局清理] 未找到提取文件: {filepath}")

    yield
    logger.info("[全局清理] 测试执行完成")

# ---------------- 类级初始化 ----------------
@pytest.fixture(scope="class", autouse=True)
def init_test_class(request):
    """
    类级公共初始化：
    - 初始化 APIRequest、RequestUtil、AssertUtil
    - 挂载到测试类
    """
    config = ConfigParser()
    db_conf = config.get_mysql_conf()

    client = APIRequest()
    request_util = RequestUtil(client)
    assert_util = AssertUtil(db_conf=db_conf)

    request.cls.client = client
    request.cls.request_util = request_util
    request.cls.assert_util = assert_util

# ---------------- 执行顺序控制 ----------------
def pytest_collection_modifyitems(session, config, items):
    """
    按文件名排序执行用例：
    - test_login.py/test_auth.py -> test_address.py -> test_cart.py -> test_order.py
    """
    order = {
        "test_login": 0,     # 登录用例最先执行
        "test_auth": 0,      # 兼容 test_auth.py
        "test_address": 1,
        "test_cart": 2,
        "test_order": 3
    }

    def sort_key(item):
        for key, value in order.items():
            if key in str(item.fspath):
                return value
        return 99  # 默认排最后

    items.sort(key=sort_key)

    # 打印排序结果，方便调试
    for i, item in enumerate(items, start=1):
        logger.info(f"[排序结果] {i}. {item.nodeid}")

    logger.info("[执行顺序控制] 已按文件名排序执行用例")

