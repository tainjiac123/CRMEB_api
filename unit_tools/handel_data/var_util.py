import re
import time
import random
import uuid
from unit_tools.handel_data.extract_util import ExtractUtil

# 匹配 ${var} 形式的占位符
_VAR_PATTERN = re.compile(r"\$\{(.+?)\}")

def _lookup_var(expr: str):
    """
    支持三类变量：
    1. 内置动态变量（不依赖 extract.yaml）：
       - ${timestamp} 当前时间戳（秒）
       - ${datetime}  当前时间（格式：YYYY-MM-DD HH:MM:SS）
       - ${date}      当前日期（格式：YYYY-MM-DD）
       - ${random}    6位随机数字
       - ${uuid}      UUID字符串
    2. 从 extract.yaml 获取的普通变量：${var}
    3. 从 extract.yaml 获取的列表变量并取索引：${var[0]}
    """

    # ===== 内置动态变量 =====
    if expr == "timestamp":
        return int(time.time())
    if expr == "datetime":
        return time.strftime("%Y-%m-%d %H:%M:%S")
    if expr == "date":
        return time.strftime("%Y-%m-%d")
    if expr == "random":
        return random.randint(100000, 999999)
    if expr == "uuid":
        return str(uuid.uuid4())

    # ===== 列表变量取索引 =====
    if "[" in expr and expr.endswith("]"):
        var_name, idx_str = expr[:-1].split("[", 1)
        try:
            idx = int(idx_str)
        except ValueError:
            return None
        value = ExtractUtil.get(var_name)
        if isinstance(value, list) and 0 <= idx < len(value):
            return value[idx]
        return None

    # ===== 普通变量 =====
    return ExtractUtil.get(expr)


def replace_variables(data):
    """
    递归替换 dict/list/str 中的 ${var} 占位符。
    - 字符串中出现多个变量会逐个替换
    - 如果替换值是 list，会转换成逗号分隔的字符串
    """
    if isinstance(data, dict):
        return {k: replace_variables(v) for k, v in data.items()}
    if isinstance(data, list):
        return [replace_variables(i) for i in data]
    if isinstance(data, str):
        matches = _VAR_PATTERN.findall(data)
        for expr in matches:
            value = _lookup_var(expr)
            if value is None:
                continue
            if isinstance(value, list):
                value_str = ",".join(map(str, value))
                data = data.replace("${" + expr + "}", value_str)
            else:
                data = data.replace("${" + expr + "}", str(value))
        return data
    return data
