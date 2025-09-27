import pytest
from unit_tools.handel_data.data_loader import load_yaml
from unit_tools.test_util.case_util import group_cases
from unit_tools.test_util.runner import TestRunnerMixin
import allure
# 读取 login.yaml（展开）
all_cases = load_yaml("login.yaml", expand=True)
grouped_cases = group_cases(all_cases)

@pytest.mark.usefixtures("init_test_class")
class TestLogin(TestRunnerMixin):
    """登录模块测试"""

    @pytest.mark.order(1)
    @pytest.mark.parametrize(
        "base_info,testcase",
        grouped_cases.get("login", []),
        ids=[tc.get("case_name", "未命名用例") for _, tc in grouped_cases.get("login", [])]
    )
    def test_login(self, base_info, testcase):
        """通用登录接口测试"""
        self.run_test(base_info, testcase)


if __name__ == "__main__":
    pytest.main(["-vs", __file__])
