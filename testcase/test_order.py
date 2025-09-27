import pytest
from unit_tools.handel_data.data_loader import load_yaml
from unit_tools.test_util.case_util import group_cases
from unit_tools.test_util.runner import TestRunnerMixin
import allure
# 读取 order.yaml（展开）
all_cases = load_yaml("order.yaml", expand=True)
grouped_cases = group_cases(all_cases)

@pytest.mark.usefixtures("init_test_class", "init_order_data")
class TestOrder(TestRunnerMixin):
    """
    订单模块测试类（单模块链路）
    - 使用 init_order_data 前置生成 order_cart_id / order_address_id
    - 按业务顺序执行：确认 → 创建 → 支付 → 详情 → 取消
    """

    @pytest.mark.order(1)
    @pytest.mark.parametrize(
        "base_info,testcase",
        grouped_cases.get("confirm", []),
        ids=[tc.get("case_name", "未命名用例") for _, tc in grouped_cases.get("confirm", [])]
    )
    def test_confirm_order(self, base_info, testcase):
        """确认订单接口"""
        self.run_test(base_info, testcase)

    @pytest.mark.order(2)
    @pytest.mark.parametrize(
        "base_info,testcase",
        grouped_cases.get("create", []),
        ids=[tc.get("case_name", "未命名用例") for _, tc in grouped_cases.get("create", [])]
    )
    def test_create_order(self, base_info, testcase):
        """创建订单接口"""
        self.run_test(base_info, testcase)

    @pytest.mark.order(3)
    @pytest.mark.parametrize(
        "base_info,testcase",
        grouped_cases.get("pay", []),
        ids=[tc.get("case_name", "未命名用例") for _, tc in grouped_cases.get("pay", [])]
    )
    def test_pay_order(self, base_info, testcase):
        """支付订单接口"""
        self.run_test(base_info, testcase)

    @pytest.mark.order(4)
    @pytest.mark.parametrize(
        "base_info,testcase",
        grouped_cases.get("detail", []),
        ids=[tc.get("case_name", "未命名用例") for _, tc in grouped_cases.get("detail", [])]
    )
    def test_order_detail(self, base_info, testcase):
        """订单详情接口"""
        self.run_test(base_info, testcase)

    @pytest.mark.order(5)
    @pytest.mark.parametrize(
        "base_info,testcase",
        grouped_cases.get("cancel", []),
        ids=[tc.get("case_name", "未命名用例") for _, tc in grouped_cases.get("cancel", [])]
    )
    def test_cancel_order(self, base_info, testcase):
        """取消订单接口"""
        self.run_test(base_info, testcase)


if __name__ == "__main__":
    pytest.main(["-vs", __file__])
