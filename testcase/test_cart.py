import pytest
from unit_tools.handel_data.data_loader import load_yaml
from unit_tools.test_util.case_util import group_cases
from unit_tools.test_util.runner import TestRunnerMixin
import allure

# 读取 cart.yaml（展开）
all_cases = load_yaml("cart.yaml", expand=True)
grouped_cases = group_cases(all_cases)


@pytest.mark.usefixtures("init_test_class")
class TestCart(TestRunnerMixin):

    @pytest.mark.order(1)
    @pytest.mark.parametrize(
        "base_info,testcase",
        grouped_cases["add"],
        ids=[tc.get("case_name", "未命名用例") for _, tc in grouped_cases["add"]]
    )
    def test_add_cart(self, base_info, testcase):
        """添加购物车接口"""
        self.run_test(base_info, testcase)


    @pytest.mark.order(2)
    @pytest.mark.parametrize(
        "base_info,testcase",
        grouped_cases["delete"],
        ids=[tc.get("case_name", "未命名用例") for _, tc in grouped_cases["delete"]]
    )
    def test_delete_cart(self, base_info, testcase):
        """删除购物车接口"""
        self.run_test(base_info, testcase)


    @pytest.mark.order(3)
    @pytest.mark.parametrize(
        "base_info,testcase",
        grouped_cases["count"],
        ids=[tc.get("case_name", "未命名用例") for _, tc in grouped_cases["count"]]
    )
    def test_get_cart_count(self, base_info, testcase):
        """获取购物车数量接口"""
        self.run_test(base_info, testcase)


    @pytest.mark.order(4)
    @pytest.mark.parametrize(
        "base_info,testcase",
        grouped_cases["list"],
        ids=[tc.get("case_name", "未命名用例") for _, tc in grouped_cases["list"]]
    )
    def test_get_cart_list(self, base_info, testcase):
        """获取购物车列表接口"""
        self.run_test(base_info, testcase)


if __name__ == "__main__":
    pytest.main(["-vs", __file__])
