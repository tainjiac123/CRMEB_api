import re
import time
import logging
from unit_tools.assertions.db_assert import DBAssert
from unit_tools.handel_data.extract_util import ExtractUtil
from unit_tools.handel_data.var_util import replace_variables
from unit_tools.handel_data.extract_handler import handle_extract
from unit_tools.log_util.logger import get_logger   # ✅ 引入你写的日志函数

logger = get_logger(__name__)

class AssertUtil:
    SUCCESS_MSGS = {"success", "修改成功", "新增成功", "操作成功"}

    def __init__(self, db_conf=None):
        self.db_conf = db_conf
        self.db_assert = DBAssert(db_conf) if db_conf else None

    def assert_response(self, res: dict, validations: list, base_info=None, testcase=None):
        # ===== 自动兜底获取 URL =====
        url = None
        if base_info and base_info.get("url"):
            url = base_info.get("url")
        elif testcase and testcase.get("url"):
            url = testcase.get("url")
        url = replace_variables(url or "")

        # ===== 提取变量 =====
        logger.debug(">>> 提取变量开始 url=%s", url if url else "未知")
        handle_extract(url, res, testcase.get("extract") if testcase else None)
        logger.debug(">>> 提取变量结束，当前变量池: %s", ExtractUtil.get_all())

        # ===== 执行断言 =====
        logger.debug(">>> 开始执行断言: %s", validations)
        for rule in validations:
            for k, v in rule.items():
                method_name = f"_assert_{k}"
                if hasattr(self, method_name):
                    getattr(self, method_name)(res, v)
                else:
                    raise ValueError(f"[断言失败] 未知断言类型: {k}")

    # ===== 接口断言 =====
    def _assert_http_code(self, res, expected):
        assert res.get("http_status") == expected, \
            f"[断言失败] HTTP状态码不符: 期望 {expected}, 实际 {res.get('http_status')}"

    def _assert_eq(self, res, expected_dict):
        for field, expected in expected_dict.items():
            actual = res["data"].get(field)
            if field == "msg" and expected == "success":
                if actual not in self.SUCCESS_MSGS and "成功" not in str(actual):
                    raise AssertionError(
                        f"[断言失败] 字段 {field} 期望包含成功提示，实际 {actual}"
                    )
                continue
            assert actual == expected, \
                f"[断言失败] 字段 {field} 期望 {expected}, 实际 {actual}"

    def _assert_contains(self, res, expected_dict):
        for field, expected in expected_dict.items():
            actual = res["data"].get(field)
            assert expected in str(actual), \
                f"[断言失败] 字段 {field} 不包含 {expected}, 实际 {actual}"

    def _assert_not_empty(self, res, value):
        actual = replace_variables(value)
        assert actual not in (None, "", []), f"[断言失败] 变量/字段为空: {value}"

    # ===== 数据库断言 =====
    def _assert_db(self, res, db_rule: dict):
        if not self.db_assert:
            raise ValueError("[断言失败] 未配置数据库连接信息")

        sql_template = db_rule["sql"]

        logger.debug("原始 SQL 模板: %s", sql_template)
        logger.debug("接口返回数据: %s", res)
        logger.debug("当前变量池 single_cart_id = %s", ExtractUtil.get("single_cart_id"))

        # 先用接口返回值替换 {变量}
        try:
            sql_filled = sql_template.format(**res.get("data", {}))
        except KeyError:
            sql_filled = sql_template
        logger.debug(".format() 替换后的 SQL: %s", sql_filled)

        # 优先替换 ${single_cart_id}
        if "${single_cart_id}" in sql_filled:
            cart_id = res.get("data", {}).get("data", {}).get("cartId")
            if cart_id:
                logger.debug("从当前响应中获取 cartId = %s 用于替换", cart_id)
                sql_filled = sql_filled.replace("${single_cart_id}", str(cart_id))

        # 列表变量过滤（统一括号逻辑）
        latest_count = db_rule.get("latest_count", 1)
        for key in ["multi_cart_ids", "cart_ids"]:
            placeholder = "${" + key + "}"
            if placeholder in sql_filled:
                val = ExtractUtil.get(key)
                if isinstance(val, list) and val:
                    if any(k.lower() in db_rule.get("expected", {}) for k in ["cnt", "count"]):
                        ids_to_use = val
                        logger.debug("批量断言，保留全部 ID: %s", ids_to_use)
                    else:
                        ids_to_use = val[-latest_count:]
                        logger.debug("单条断言，取最新 %s 个 ID: %s", latest_count, ids_to_use)
                    joined = ",".join(str(i) for i in ids_to_use)
                    pattern = r"\(\s*" + re.escape(placeholder) + r"\s*\)"
                    sanitized = re.sub(pattern, placeholder, sql_filled)
                    sql_filled = sanitized.replace(placeholder, f"({joined})")

        # 再替换其他变量
        sql_final = replace_variables(sql_filled)

        logger.debug("replace_variables() 替换后的 SQL: %s", sql_final)
        logger.debug("预期值: %s", db_rule["expected"])

        expected = db_rule["expected"]
        wait_time = db_rule.get("wait", 0)

        if wait_time > 0:
            time.sleep(wait_time)
        actual_data = self.db_assert.query_one(sql_final)

        # 打印 actual_data 的完整内容和类型
        logger.info("[DB-ASSERT] actual_data 原始内容: %s (类型: %s)", actual_data, type(actual_data))

        # ===== 类型统一比较 + 打印字段值和类型 =====
        for field, expected_value in expected.items():
            actual_val = actual_data.get(field)
            logger.info("[DB-ASSERT] 字段 %s 实际值: %s (类型: %s)", field, actual_val, type(actual_val))
            logger.info("[DB-ASSERT] 字段 %s 预期值: %s (类型: %s)", field, expected_value, type(expected_value))

            if isinstance(actual_val, (int, float)) and isinstance(expected_value, (int, float, str)):
                try:
                    actual_cast = int(actual_val)
                    expected_cast = int(expected_value)
                except ValueError:
                    actual_cast = str(actual_val)
                    expected_cast = str(expected_value)
            else:
                actual_cast = str(actual_val) if actual_val is not None else ""
                expected_cast = str(expected_value) if expected_value is not None else ""

            assert actual_cast == expected_cast, \
                f"[断言失败] 字段 {field} 期望 {expected_cast}，实际 {actual_cast}"
