from typing import Any, Dict, List, Union
from api.request_api import APIRequest


class CartApi(APIRequest):
    """
    购物车模块接口封装（企业级健壮版 + 参数名兼容）
    """

    # ===================== 基础接口 =====================

    def add_cart(self, product_id: int, cart_num: int = 1) -> Dict[str, Any]:
        """
        添加商品到购物车
        - product_id: 商品 ID
        - cart_num: 数量
        """
        url = "/api/cart/add"
        payload = {
            "productId": product_id,  # 接口真实字段
            "cartNum": cart_num       # 接口真实字段
        }
        return self.post(url, data=payload)

    def list_cart(self) -> Dict[str, Any]:
        """
        获取购物车列表
        """
        url = "/api/cart/list"
        return self.get(url)

    def delete_cart(self, cart_ids: Union[int, List[int]]) -> Dict[str, Any]:
        """
        删除购物车商品
        - cart_ids: 单个 ID 或 ID 列表
        """
        if isinstance(cart_ids, int):
            cart_ids = [cart_ids]
        url = "/api/cart/del"
        payload = {"ids": cart_ids}
        return self.post(url, json=payload)

    def update_cart_num(self, cart_id: int, cart_num: int) -> Dict[str, Any]:
        """
        更新购物车商品数量
        """
        url = "/api/cart/num"
        payload = {
            "id": cart_id,
            "number": cart_num
        }
        return self.post(url, data=payload)

    # ===================== 高级封装 =====================

    def add_and_get_cart_id(self, *args, **kwargs) -> int:
        """
        添加商品到购物车并返回 cartId
        - 支持 product_id / productId
        - 支持 cart_num / cartNum
        - 兼容 add_cart 返回 cartId 或 id
        - 兼容 list_cart 返回嵌套 valid 列表
        """
        # 兼容参数名
        if "product_id" in kwargs:
            product_id = kwargs.pop("product_id")
        elif "productId" in kwargs:
            product_id = kwargs.pop("productId")
        else:
            raise ValueError("必须提供 product_id 或 productId 参数")

        cart_num = kwargs.pop("cart_num", kwargs.pop("cartNum", 1))

        # 调用添加接口
        resp = self.add_cart(product_id, cart_num)
        outer_data = resp.get("data") or {}

        # 兼容 add_cart 返回 cartId 或 id
        if isinstance(outer_data, dict):
            # 有些接口直接返回 id/cartId
            if "id" in outer_data:
                return int(outer_data["id"])
            if "cartId" in outer_data:
                return int(outer_data["cartId"])

            # 有些接口 data 里嵌套 data
            inner_data = outer_data.get("data") or {}
            if "id" in inner_data:
                return int(inner_data["id"])
            if "cartId" in inner_data:
                return int(inner_data["cartId"])

        # 从购物车列表取
        list_resp = self.list_cart()
        cart_data = list_resp.get("data", {}).get("data") or {}

        if isinstance(cart_data, dict):
            valid_list = cart_data.get("valid") or []
            if valid_list and isinstance(valid_list, list):
                return int(valid_list[0].get("id", 0))

        if isinstance(cart_data, list) and cart_data:
            return int(cart_data[0].get("id", 0))

        return 0

    def get_cart_ids(self) -> List[int]:
        """
        获取当前购物车所有有效商品的 ID 列表
        """
        cart_data = self.list_cart().get("data", {}).get("data") or {}
        ids = []

        if isinstance(cart_data, dict):
            valid_list = cart_data.get("valid") or []
            if isinstance(valid_list, list):
                ids = [item.get("id") for item in valid_list if "id" in item]
        elif isinstance(cart_data, list):
            ids = [item.get("id") for item in cart_data if "id" in item]

        return [int(i) for i in ids if i]

    def clear_cart(self) -> bool:
        """
        清空购物车
        """
        ids = self.get_cart_ids()
        if not ids:
            return True
        resp = self.delete_cart(ids)
        return resp.get("status") is True or resp.get("msg") == "success"
