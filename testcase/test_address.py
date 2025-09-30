import allure
import pytest
from unit_tools.handel_data.data_loader import load_yaml
from unit_tools.test_util.case_util import group_cases
from unit_tools.test_util.runner import TestRunnerMixin

# 读取 address.yaml（展开）
all_cases = load_yaml("address.yaml", expand=True)
grouped_cases = group_cases(all_cases)


@pytest.mark.usefixtures("init_test_class")
class TestAddress(TestRunnerMixin):

    @pytest.mark.order(2)
    @pytest.mark.parametrize(
        "base_info,testcase",
        grouped_cases.get("list", []),
        ids=[tc.get("case_name", "未命名用例") for _, tc in grouped_cases.get("list", [])]
    )
    def test_list_address(self, base_info, testcase):
        """获取地址列表"""
        self.run_test(base_info, testcase)

    @pytest.mark.order(1)
    @pytest.mark.parametrize(
        "base_info,testcase",
        grouped_cases.get("add", []),
        ids=[tc.get("case_name", "未命名用例") for _, tc in grouped_cases.get("add", [])]
    )
    def test_add_address(self, base_info, testcase):
        """新增地址"""
        self.run_test(base_info, testcase)

    @pytest.mark.order(3)
    @pytest.mark.parametrize(
        "base_info,testcase",
        grouped_cases.get("update", []),
        ids=[tc.get("case_name", "未命名用例") for _, tc in grouped_cases.get("update", [])]
    )
    def test_edit_address(self, base_info, testcase):
        """修改地址"""
        self.run_test(base_info, testcase)

    @pytest.mark.order(4)
    @pytest.mark.parametrize(
        "base_info,testcase",
        grouped_cases.get("set_default", []),
        ids=[tc.get("case_name", "未命名用例") for _, tc in grouped_cases.get("set_default", [])]
    )
    def test_set_default_address(self, base_info, testcase):
        """设置默认地址"""
        self.run_test(base_info, testcase)

    @pytest.mark.order(5)
    @pytest.mark.parametrize(
        "base_info,testcase",
        grouped_cases.get("delete", []),
        ids=[tc.get("case_name", "未命名用例") for _, tc in grouped_cases.get("delete", [])]
    )
    def test_delete_address(self, base_info, testcase):
        """删除地址"""
        self.run_test(base_info, testcase)


if __name__ == "__main__":
    # 运行时会自动读取 pytest.ini 配置
    pytest.main(["-vs", __file__])
