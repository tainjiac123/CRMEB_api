from pathlib import Path

# ================== 项目根目录 ==================
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ================== 常用目录路径 ==================
CONFIGS_DIR   = PROJECT_ROOT / "configs"       # 配置文件目录
DATA_DIR      = PROJECT_ROOT / "data"          # 测试数据目录
API_DIR       = PROJECT_ROOT / "api"           # 接口封装目录
TESTCASE_DIR  = PROJECT_ROOT / "testcase"      # 测试用例目录
UNIT_TOOLS_DIR= PROJECT_ROOT / "unit_tools"    # 工具类目录
LOGS_DIR      = PROJECT_ROOT / "logs"          # 日志目录
REPORT_DIR    = PROJECT_ROOT / "report"        # 报告总目录
RESULT_DIR    = REPORT_DIR / "allure-results"  # pytest 原始结果
HTML_DIR      = REPORT_DIR / "allure-report"   # Allure HTML 报告

# ================== 常用文件路径 ==================
CONFIG_FILE  = CONFIGS_DIR / "config.yaml"     # 全局配置文件
EXTRACT_FILE = PROJECT_ROOT / "extract.yaml"   # 接口提取数据文件

# ================== 工具配置 ==================
ALLURE_CMD = r"D:\project_Tool\allure-2.35.1\bin\allure.bat"  # Allure CLI 路径

# ================== 路径获取方法 ==================
def get_project_root():
    """获取项目根目录路径"""
    return PROJECT_ROOT

def get_path(*parts):
    """
    根据相对路径获取绝对路径
    :param parts: 路径片段，例如 get_path("data", "login.yaml")
    :return: Path 对象
    """
    return PROJECT_ROOT.joinpath(*parts)

def get_config_file_path():
    """获取 config.yaml 配置文件的绝对路径（兼容旧代码）"""
    return CONFIG_FILE

# ================== main 调试 ==================
if __name__ == "__main__":
    print("项目根目录:", get_project_root())
    print("配置文件路径:", CONFIG_FILE)
    print("extract.yaml 路径:", EXTRACT_FILE)
    print("data/login.yaml 路径:", get_path("data", "login.yaml"))
    print("allure-results 路径:", RESULT_DIR)
    print("allure-report 路径:", HTML_DIR)
