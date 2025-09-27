# testcase/conftest.py
import pytest
import pymysql
from unit_tools.handel_data.extract_util import ExtractUtil
from unit_tools.handel_data.configParse import ConfigParser
from api.cart_api import CartApi
from api.address_api import AddressApi

# ---------------- 购物车清理 ----------------
@pytest.fixture(scope="session", autouse=True)
def clear_cart_once():
    """
    测试会话开始时清空一次购物车（自动执行）
    建议在 WHERE 子句中限定测试账号 uid，避免误删。
    """
    config = ConfigParser()
    db_conf = config.get_mysql_conf()
    db_user = db_conf.get("user") or db_conf.get("username")

    # 可选：如果你能拿到测试账号 uid，替换为真实值
    test_uid = db_conf.get("test_uid")  # 例如在 config 里配置 test_uid
    where_clause = "WHERE uid = %s" if test_uid else ""  # 没有 uid 就清空全表（谨慎）

    conn = pymysql.connect(
        host=db_conf["host"],
        user=db_user,
        password=db_conf["password"],
        database=db_conf["database"],
        port=int(db_conf.get("port", 3306)),
        charset="utf8mb4"
    )
    try:
        with conn.cursor() as cursor:
            sql = f"DELETE FROM eb_store_cart {where_clause}"
            if test_uid:
                cursor.execute(sql, (test_uid,))
            else:
                cursor.execute(sql)
        conn.commit()
        print("[全局清理] 已清空购物车表")
    finally:
        conn.close()

    # 重置可能用于多商品删除的缓存
    ExtractUtil().save("multi_cart_ids", [])
    print("[全局清理] 已重置 multi_cart_ids")
# ---------------- 删除多个商品前置 ----------------
@pytest.fixture(scope="function", autouse=True)
def auto_prepare_multi_cart_ids(request):
    """
    删除多个商品用例前置：
    - 仅对标记了 @pytest.mark.delete_multi 的用例生效
    """
    if "delete_multi" in request.keywords:
        extract = ExtractUtil()
        token = extract.get("token")
        if not token:
            raise RuntimeError("未获取到 token，请确保登录用例先执行")

        headers = {"Authorization": f"Bearer {token}"}
        cart_api = CartApi(headers=headers)

        cart_id_b = cart_api.add_and_get_cart_id(product_id=2, cart_num=1)
        cart_id_c = cart_api.add_and_get_cart_id(product_id=3, cart_num=1)

        if not cart_id_b or not cart_id_c:
            raise RuntimeError("自动添加商品失败")

        extract.save("multi_cart_ids", [cart_id_b, cart_id_c])
        print(f"[前置准备] 已自动添加商品B和C，multi_cart_ids={[cart_id_b, cart_id_c]}")

# ---------------- 订单模块前置 ----------------
@pytest.fixture(scope="class")
def init_order_data():
    """
    订单模块专属前置：
    - 依赖登录用例先执行
    - 创建购物车记录并保存 cart_id
    - 获取/创建默认地址并保存 address_id
    """
    extract = ExtractUtil()
    token = extract.get("token")
    if not token:
        raise RuntimeError("订单前置失败：未获取到 token，请确保登录用例先执行")
    headers = {"Authorization": f"Bearer {token}"}

    cart_api = CartApi(headers=headers)
    cart_id = cart_api.add_and_get_cart_id(product_id=1, cart_num=1)
    if not cart_id:
        raise RuntimeError("生成购物车 ID 失败")
    extract.save("order_cart_id", cart_id)

    addr_api = AddressApi(headers=headers)
    address_id = addr_api.get_or_create_default_address_id()
    if not address_id:
        raise RuntimeError("生成地址 ID 失败")
    extract.save("order_address_id", address_id)

    print(f"[订单前置] 已生成 cart_id={cart_id}, address_id={address_id}")
    yield
    print("[订单清理] 可在此处添加订单数据清理逻辑")
