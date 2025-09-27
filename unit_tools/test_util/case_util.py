from collections import defaultdict

def group_cases(all_cases, key="group", default="other"):
    """
    根据指定 key 对用例进行分组
    :param all_cases: [(baseInfo, testCase), ...]
    :param key: 用例里用于分组的字段，默认是 'group'
    :param default: 如果没有该字段，归类到 default
    :return: dict，key=分组名，value=[(baseInfo, testCase), ...]
    """
    grouped = defaultdict(list)
    for base_info, testcase in all_cases:
        group = base_info.get(key, default) if isinstance(base_info, dict) else testcase.get(key, default)
        grouped[group].append((base_info, testcase))
    return grouped
