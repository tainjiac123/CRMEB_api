import os
import yaml
from configs.setting import EXTRACT_FILE  # 从路径管理工具获取 extract.yaml 路径
from unit_tools.log_util.logger import get_logger   # ✅ 引入统一日志函数

# 使用统一日志工具（每天切换文件，写入 logs 目录）
logger = get_logger(__name__)

class ExtractUtil:
    """统一管理接口提取数据的工具类（支持保存策略）"""

    # 保存策略
    SINGLE_KEYS = {"token", "order_id", "single_cart_id"}   # 永远覆盖
    LIST_KEYS = {"cart_ids", "product_ids"}  # 列表追加 + 去重

    @classmethod
    def save(cls, key, value):
        """
        保存数据到 extract.yaml
        - 单值型：覆盖
        - 列表型：追加且去重
        - 其他：覆盖
        """
        data = {}
        if os.path.exists(EXTRACT_FILE):
            with open(EXTRACT_FILE, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

        # 单值覆盖型
        if key in cls.SINGLE_KEYS:
            data[key] = value

        # 列表追加型
        elif key in cls.LIST_KEYS:
            if key not in data:
                data[key] = [value]
            else:
                if not isinstance(data[key], list):
                    data[key] = [data[key]]
                if value not in data[key]:
                    data[key].append(value)

        # 默认覆盖
        else:
            data[key] = value

        with open(EXTRACT_FILE, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False)

        logger.info("已保存 %s: %s 到 %s", key, value, EXTRACT_FILE)

    @classmethod
    def set(cls, key, value):
        """强制覆盖写入（不管原来是什么类型）"""
        data = {}
        if os.path.exists(EXTRACT_FILE):
            with open(EXTRACT_FILE, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        data[key] = value
        with open(EXTRACT_FILE, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False)
        logger.info("已覆盖 %s: %s 到 %s", key, value, EXTRACT_FILE)

    @classmethod
    def get(cls, key):
        """获取 extract.yaml 中的值"""
        if os.path.exists(EXTRACT_FILE):
            with open(EXTRACT_FILE, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            return data.get(key)
        return None

    @classmethod
    def get_all(cls):
        """获取 extract.yaml 中的所有键值对"""
        if os.path.exists(EXTRACT_FILE):
            with open(EXTRACT_FILE, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}

    @classmethod
    def clear(cls):
        """清空 extract.yaml 文件"""
        with open(EXTRACT_FILE, "w", encoding="utf-8") as f:
            yaml.safe_dump({}, f, allow_unicode=True)
        logger.warning("已清空 %s", EXTRACT_FILE)


# ================== main 调试 ==================
if __name__ == "__main__":
    # 清空文件
    ExtractUtil.clear()

    # 测试保存（追加模式 + 策略）
    ExtractUtil.save("cart_ids", 4)
    ExtractUtil.save("cart_ids", 5)
    ExtractUtil.save("cart_ids", 4)  # 重复值不会追加
    ExtractUtil.save("token", "abc123456")
    ExtractUtil.save("token", "xyz789")  # 会覆盖
    ExtractUtil.save("order_id", 1001)
    ExtractUtil.save("order_id", 1002)   # 会覆盖
    ExtractUtil.save("other_key", "first")
    ExtractUtil.save("other_key", "second")  # 默认覆盖

    # 测试读取
    logger.info("读取 cart_ids: %s", ExtractUtil.get("cart_ids"))
    logger.info("读取 token: %s", ExtractUtil.get("token"))
    logger.info("读取 order_id: %s", ExtractUtil.get("order_id"))
    logger.info("读取 other_key: %s", ExtractUtil.get("other_key"))

    # 测试获取全部
    logger.info("当前变量池: %s", ExtractUtil.get_all())

    # 测试覆盖写
    ExtractUtil.set("cart_ids", [99])
    logger.info("覆盖后 cart_ids: %s", ExtractUtil.get("cart_ids"))

    # 测试清空
    ExtractUtil.clear()
