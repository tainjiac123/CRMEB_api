import os
import yaml

def load_yaml(file_name, expand=False):
    """
    通用 YAML 读取器
    :param file_name: YAML 文件名（位于 data 目录下）
    :param expand: 是否展开为 [(base_info, test_case), ...] 列表
    :return: 原始数据 或 展开后的列表
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    file_path = os.path.join(base_dir, "data", file_name)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"❌ YAML 文件不存在: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        raw_data = yaml.safe_load(f)

    # 如果不需要展开，直接返回原始数据
    if not expand:
        return raw_data

    # 展开成 [(base_info, test_case), ...]
    cases = []
    for block in raw_data or []:
        base_info = block.get("baseInfo", {})
        for tc in block.get("testCase", []):
            cases.append((base_info, tc))
    return cases


if __name__ == "__main__":
    # 调试读取 login.yaml（原始数据）
    data = load_yaml("login.yaml")
    print("✅ 原始数据：", data)

    # 调试读取 cart.yaml（展开后的数据）
    expanded = load_yaml("cart.yaml", expand=True)
    print("✅ 展开后的数据：", expanded)
