import logging
import allure
from unit_tools.log_util.logger import get_logger

logger = get_logger(__name__)

# 优先级映射
severity_map = {
    "P0": allure.severity_level.BLOCKER,
    "P1": allure.severity_level.CRITICAL,
    "P2": allure.severity_level.NORMAL,
    "P3": allure.severity_level.MINOR,
    "P4": allure.severity_level.TRIVIAL,
}

class TestRunnerMixin:
    """
    通用测试执行器，封装请求发送、断言和调试输出
    """

    def run_test(self, base_info, testcase):
        """
        执行单个测试用例：
        1. 动态设置 Allure 标签
        2. 发送请求
        3. 执行断言
        4. 打印调试信息
        """
        # 1. 动态设置 Allure 标签
        allure.dynamic.feature(base_info.get("module", "未分组模块"))
        allure.dynamic.story(base_info.get("api_name", "未分组接口"))
        allure.dynamic.title(testcase.get("case_name", "未命名用例"))
        allure.dynamic.severity(
            severity_map.get(base_info.get("priority", "P2"), allure.severity_level.NORMAL)
        )

        # 2. 附件：把 base_info 和 testcase 挂到报告
        allure.attach(str(base_info), "BaseInfo 参数", allure.attachment_type.JSON)
        allure.attach(str(testcase), "TestCase 参数", allure.attachment_type.JSON)

        # 3. 发送请求
        with allure.step("发送请求"):
            res = self.request_util.send_request(base_info, testcase)
            allure.attach(str(res), "响应结果", allure.attachment_type.JSON)

        # 4. 执行断言
        with allure.step("断言结果"):
            self.assert_util.assert_response(
                res,
                testcase.get("validation", []),
                base_info,
                testcase
            )

        # 5. 打印调试日志
        extract_conf = testcase.get("extract")
        if extract_conf:
            logger.debug("extract 配置: %s", extract_conf)
            allure.attach(str(extract_conf), "提取配置", allure.attachment_type.JSON)

        logger.debug("接口返回: %s", res)

        return res
