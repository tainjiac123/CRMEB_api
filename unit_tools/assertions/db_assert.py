# db_assert.py
import pymysql
import time

class DBAssert:
    def __init__(self, db_conf: dict):
        self.db_conf = db_conf

    def _get_conn(self):
        return pymysql.connect(
            host=self.db_conf["host"],
            user=self.db_conf["username"],
            password=self.db_conf["password"],
            database=self.db_conf["database"],
            port=self.db_conf.get("port", 3306),
            charset=self.db_conf.get("charset", "utf8mb4"),
            cursorclass=pymysql.cursors.DictCursor
        )

    def query_one(self, sql: str):
        with self._get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                return cursor.fetchone()

    def assert_equal(self, sql: str, expected: dict):
        result = self.query_one(sql)
        if not result:
            raise AssertionError(f"[DB断言失败] SQL无结果: {sql}")
        for k, v in expected.items():
            actual = result.get(k)
            assert actual == v, f"[DB断言失败] 字段{k} 期望{v} 实际{actual}"
        print(f"[DB断言成功] {sql} => {expected}")

    def assert_equal_with_wait(self, sql: str, expected: dict, timeout=10, interval=1):
        start = time.time()
        while time.time() - start < timeout:
            try:
                self.assert_equal(sql, expected)
                return
            except AssertionError:
                time.sleep(interval)
        raise AssertionError(f"[DB断言失败] 超时 {timeout}s，条件未满足: {sql} 期望 {expected}")


if __name__ == "__main__":
    # 数据库配置（测试环境）
    db_conf = {
        "host": "127.0.0.1",
        "user": "root",
        "password": "123456",
        "database": "crmeb",
        "port": 3306
    }

    # 创建 DBAssert 实例
    db_assert = DBAssert(db_conf)

    # 示例：检查订单状态是否为已支付（status=1）
    order_id = "cp492386580737744995"
    sql = f"SELECT status FROM eb_store_order WHERE order_id = '{order_id}'"
    expected = {"status": 0}

    try:
        db_assert.assert_equal(sql, expected)
    except AssertionError as e:
        print(e)
