from typing import Any, Dict, Optional, Union
from api.request_api import APIRequest


class OrderApi(APIRequest):
    """
    订单模块接口封装
    接口地址：
      - 确认订单: POST /api/order/confirm
      - 创建订单: POST /api/order/create/{order_key}
      - 支付订单: POST /api/order/pay
      - 订单详情: GET  /api/order/detail/{order_no}
      - 取消订单: POST /api/order/cancel
    """

    def confirm_order(self, cart_id: Union[str, list], address_id: Optional[int] = None) -> Dict[str, Any]:
        """
        确认订单
        :param cart_id: 购物车ID（字符串或数组）
        :param address_id: 地址ID（可选）
        :return: 包含 orderKey 的响应
        """
        payload: Dict[str, Any] = {"cartId": cart_id}
        if address_id:
            payload["addressId"] = address_id
        return self.send("post", "/api/order/confirm", json=payload)

    def create_order(self, order_key: str, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建订单
        :param order_key: 订单信息缓存标识（订单确认返回的 orderKey）
        :param order_data: 创建订单所需参数（地址ID、支付方式等）
        """
        return self.send("post", f"/api/order/create/{order_key}", json=order_data)

    def pay_order(self, order_no: str, pay_type: str = "yue", is_mock: bool = False) -> Dict[str, Any]:
        """
        支付订单
        :param order_no: 订单号
        :param pay_type: 支付方式（yue=余额，wechat=微信，alipay=支付宝）
        :param is_mock: 是否模拟支付（测试环境用）
        """
        payload: Dict[str, Any] = {
            "orderNo": order_no,
            "payType": pay_type
        }
        if is_mock:
            payload["is_mock"] = 1
        return self.send("post", "/api/order/pay", json=payload)

    def get_order_detail(self, order_no: str) -> Dict[str, Any]:
        """
        获取订单详情
        :param order_no: 订单号
        """
        return self.send("get", f"/api/order/detail/{order_no}")

    def cancel_order(self, order_no: str) -> Dict[str, Any]:
        """
        取消订单
        :param order_no: 订单号
        """
        return self.send("post", "/api/order/cancel", json={"orderNo": order_no})

    # ====== 便捷方法 ======
    def confirm_and_create_order(
        self,
        cart_id: Union[str, list],
        address_id: int,
        pay_type: str = "yue"
    ) -> str:
        """
        一步确认并创建订单，返回订单号
        """
        confirm_resp = self.confirm_order(cart_id, address_id)
        order_key = (confirm_resp.get("data") or {}).get("orderKey")
        if not order_key:
            raise ValueError("订单确认失败，未返回 orderKey")
        create_resp = self.create_order(order_key, {
            "addressId": address_id,
            "payType": pay_type
        })
        return (create_resp.get("data") or {}).get("orderNo", "")
