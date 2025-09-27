import os, shutil, subprocess, pytest, json
from datetime import datetime

def set_allure_title(html_dir: str, new_title: str):
    """修改 Allure 报告首页标题"""
    # 修改 index.html 的浏览器窗口标题
    index_file = os.path.join(html_dir, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r+", encoding="utf-8") as f:
            content = f.read().replace("Allure Report", new_title)
            f.seek(0)
            f.write(content)
            f.truncate()

    # 修改 summary.json 的报告标题
    summary_file = os.path.join(html_dir, "widgets", "summary.json")
    if os.path.exists(summary_file):
        with open(summary_file, "r", encoding="utf-8") as f:
            summary = json.load(f)
        summary["reportName"] = new_title
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=4)


def run_allure(allure_cmd, result_dir, html_dir, logger):
    start_time = datetime.now()
    logger.info("=== 测试执行开始 ===")

    # 清理结果目录
    os.makedirs(result_dir, exist_ok=True)
    for f in os.listdir(result_dir):
        path = os.path.join(result_dir, f)
        if os.path.isfile(path) or os.path.islink(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)

    # 执行 pytest
    exit_code = pytest.main(["--alluredir", result_dir])
    logger.info("pytest 执行完成，退出码=%s", exit_code)

    # 生成报告
    if os.path.exists(html_dir):
        shutil.rmtree(html_dir, ignore_errors=True)
    subprocess.run([allure_cmd, "generate", result_dir, "-o", html_dir, "--clean"], check=True)
    logger.info("Allure 报告已生成: %s", html_dir)

    # ✅ 新增：修改首页标题
    set_allure_title(html_dir, "CRMEB接口测试报告")
    logger.info("Allure 报告标题已修改为: CRMEB接口测试报告")

    # 打开报告
    try:
        subprocess.Popen([allure_cmd, "open", html_dir])
        logger.info("正在打开 Allure 报告...")
    except Exception as e:
        logger.warning("无法自动打开 Allure 报告: %s", e)

    duration = (datetime.now() - start_time).total_seconds()
    logger.info("=== 测试执行结束，总耗时 %.2f 秒 ===", duration)
    return exit_code
