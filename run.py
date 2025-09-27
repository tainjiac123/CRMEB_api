import sys
from configs.setting import RESULT_DIR, HTML_DIR, ALLURE_CMD
from unit_tools.log_util.logger import get_logger
from unit_tools.runner.allure_runner import run_allure

logger = get_logger(__name__)

if __name__ == "__main__":
    code = run_allure(ALLURE_CMD, RESULT_DIR, HTML_DIR, logger)
    sys.exit(code)
