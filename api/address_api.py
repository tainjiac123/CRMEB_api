from typing import Any, Dict, List, Union
from api.request_api import APIRequest


class AddressApi(APIRequest):
    """
    地址模块接口封装（企业级健壮版）
    """

    # ===================== 基础接口 =====================

    def list_address(self) -> Dict[str, Any]:
        """
        获取地址列表
        """
        url = "/api/address/list"
        return self.get(url)

    def add_address(self, address_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        新增地址
        - address_data: 包含收货人、电话、省市区、详细地址等信息
        """
        url = "/api/address/add"
        return self.post(url, data=address_data)

    def delete_address(self, address_ids: Union[int, List[int]]) -> Dict[str, Any]:
        """
        删除地址
        - address_ids: 单个 ID 或 ID 列表
        """
        if isinstance(address_ids, int):
            address_ids = [address_ids]
        url = "/api/address/del"
        payload = {"ids": address_ids}
        return self.post(url, json=payload)

    def get_default_address(self) -> Dict[str, Any]:
        """
        获取默认地址
        """
        url = "/api/address/default"
        return self.get(url)

    # ===================== 高级封装 =====================

    def get_or_create_default_address_id(self) -> int:
        """
        获取默认地址 ID：
        1. 如果有默认地址 → 返回它的 ID
        2. 如果没有默认地址 → 返回地址列表第一个的 ID
        3. 如果没有任何地址 → 创建一个默认地址并返回它的 ID
        """
        # Step 1: 获取默认地址
        default_res = self.get_default_address()
        default_data = default_res.get("data", {}).get("data") or {}

        if isinstance(default_data, dict) and default_data.get("id"):
            return int(default_data["id"])

        # Step 2: 获取地址列表
        list_res = self.list_address()
        addr_list = list_res.get("data", {}).get("data") or []

        if isinstance(addr_list, list) and addr_list:
            return int(addr_list[0].get("id", 0))

        # Step 3: 新增一个默认地址
        new_addr = {
            "real_name": "测试收货人",
            "phone": "13800000000",
            "province": "北京市",
            "city": "北京市",
            "district": "东城区",
            "detail": "测试详细地址",
            "is_default": 1
        }
        add_res = self.add_address(new_addr)
        add_data = add_res.get("data", {}).get("data") or {}

        if isinstance(add_data, dict) and add_data.get("id"):
            return int(add_data["id"])

        raise RuntimeError("无法获取或创建默认地址 ID")
