import os
from jsonpath_ng import parse
from unit_tools.handel_data.extract_util import ExtractUtil
from unit_tools.log_util.logger import get_logger   # ✅ 引入你写的日志函数

# 使用统一的日志工具
logger = get_logger(__name__)

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
EXTRACT_FILE = os.path.join(ROOT_DIR, "extract.yaml")

EXTRACT_RULES = {
    "/api/login": {
        "token": "data.data.token"
    },
    "/api/cart/add": {
        "cart_ids": "data.data.cartId",
        "single_cart_id": "data.data.cartId",
        "multi_cart_ids": "data.data.cartId"
    },
    "/api/order/confirm": {
        "orderKey": "data.data.orderKey"
    },
    "/api/order/create": {
        "orderId": "data.result.orderId"
    },
    "/api/address/edit": {
        "new_address_id": "data.data.id"
    },
}

SINGLE_KEYS = {"token", "order_id", "single_cart_id", "orderKey"}
LIST_KEYS = {"cart_ids", "multi_cart_ids"}


def get_value_by_path(data, path):
    """根据路径字符串获取嵌套字典的值，例如 'data.data.token'"""
    keys = path.split(".")
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key)
        else:
            return None
    return data


def handle_extract(url, res, extract_conf=None):
    """
    根据规则表和用例内的 extract 字段提取数据（按策略保存，统一转字符串）
    """
    if not url:
        logger.warning("handle_extract 调用时 URL 为空，规则表提取将被跳过")

    extracted_data = {}

    # 1. 按规则表提取
    if url in EXTRACT_RULES:
        for key, path in EXTRACT_RULES[url].items():
            value = get_value_by_path(res, path)
            if value is not None:
                extracted_data[key] = value
                logger.info("规则表提取 %s = %s", key, value)
            else:
                logger.debug("规则表提取 %s 失败，路径: %s", key, path)

    # 2. 按用例内 extract 配置提取（支持 JSONPath）
    if extract_conf:
        for key, jsonpath_expr in extract_conf.items():
            try:
                matches = parse(jsonpath_expr).find(res)
                if matches:
                    value = matches[0].value
                    extracted_data[key] = value
                    logger.info("用例提取 %s = %s", key, value)
                else:
                    logger.debug("用例提取 %s 失败，路径: %s", key, jsonpath_expr)
            except Exception as e:
                logger.error("用例提取 %s 异常: %s", key, e)

    # 3. 按策略保存（统一转字符串）
    for k, v in extracted_data.items():
        if isinstance(v, list):
            v = [str(i) for i in v]
        else:
            v = str(v)

        existing = ExtractUtil.get(k)

        if k in SINGLE_KEYS:
            ExtractUtil.set(k, v)
            continue

        if k in LIST_KEYS:
            if existing is None:
                ExtractUtil.set(k, [v])
            else:
                if not isinstance(existing, list):
                    existing = [str(existing)]
                if v not in existing:
                    existing.append(v)
                ExtractUtil.set(k, existing)
            continue

        ExtractUtil.set(k, v)

    # 4. 调试输出当前变量池
    logger.debug("提取结束，当前变量池: %s", ExtractUtil.get_all())


# ================== main 调试 ==================
if __name__ == "__main__":
    ExtractUtil.clear()

    fake_responses = [
        {"status": 200, "msg": "success", "data": {"cartId": 26}},
        {"status": 200, "msg": "success", "data": {"cartId": "24"}},
        {"status": 200, "msg": "success", "data": {"cartId": 27}},
    ]
    for res in fake_responses:
        handle_extract("/api/cart/add", res, {"cart_ids": "$.data.cartId"})

    handle_extract("/api/cart/add", {"status": 200, "data": {"cartId": 26}}, {"single_cart_id": "$.data.cartId"})
    handle_extract("/api/cart/add", {"status": 200, "data": {"cartId": 24}}, {"multi_cart_ids": "$.data.cartId"})
    handle_extract("/api/cart/add", {"status": 200, "data": {"cartId": 27}}, {"multi_cart_ids": "$.data.cartId"})
