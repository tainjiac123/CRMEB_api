import yaml
import json
import os
from configs.setting import get_config_file_path


class ConfigParser:
    def __init__(self, config_file=None):
        """
        初始化配置解析类，默认加载 config.yaml 文件
        """
        self.config_file = config_file or get_config_file_path()
        self.config_data = self.load_config()

    def load_config(self):
        """读取配置文件并解析为 Python 字典"""
        ext = os.path.splitext(self.config_file)[1].lower()
        try:
            if ext in ('.yaml', '.yml'):
                return self.load_yaml()
            elif ext == '.json':
                return self.load_json()
            else:
                raise ValueError(f"Unsupported file format: {ext}")
        except Exception as e:
            raise RuntimeError(f"配置文件加载失败: {e}")

    def load_yaml(self):
        """读取 YAML 格式配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file) or {}
        except FileNotFoundError:
            return {}  # CI 环境可能没有配置文件，返回空字典
        except yaml.YAMLError as e:
            raise ValueError(f"YAML 文件解析出错: {e}")

    def load_json(self):
        """读取 JSON 格式配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 文件解析出错: {e}")

    def get(self, key, default=None):
        """获取配置项，支持嵌套 key（如 mysql.host）"""
        keys = key.split('.')
        value = self.config_data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value

    def exists(self, key):
        """判断配置项是否存在"""
        return self.get(key, default=None) is not None

    def set(self, key, value):
        """设置配置项，支持嵌套 key"""
        keys = key.split('.')
        data = self.config_data
        for k in keys[:-1]:
            if k not in data or not isinstance(data[k], dict):
                data[k] = {}
            data = data[k]
        data[keys[-1]] = value
        self.save_config()

    def save_config(self):
        """保存配置文件"""
        ext = os.path.splitext(self.config_file)[1].lower()
        if ext in ('.yaml', '.yml'):
            self.save_yaml()
        elif ext == '.json':
            self.save_json()
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    def save_yaml(self):
        with open(self.config_file, 'w', encoding='utf-8') as file:
            yaml.dump(self.config_data, file, default_flow_style=False, allow_unicode=True)

    def save_json(self):
        with open(self.config_file, 'w', encoding='utf-8') as file:
            json.dump(self.config_data, file, ensure_ascii=False, indent=4)

    def reload(self):
        """重新加载配置文件"""
        self.config_data = self.load_config()

    # ---------------- 兼容 CI 的环境变量覆盖 ----------------
    def get_base_url(self):
        """
        获取 API 基础地址
        优先级：环境变量 > 配置文件
        """
        return os.getenv("BASE_URL", self.get("base_url", "http://127.0.0.1:8000"))

    def get_mysql_conf(self):
        """
        获取 MySQL 数据库配置
        优先级：环境变量 > 配置文件
        """
        mysql_conf = self.config_data.get("mysql", {})
        return {
            "host": os.getenv("MYSQL_HOST", mysql_conf.get("host", "127.0.0.1")),
            "username": os.getenv("MYSQL_USER", mysql_conf.get("username", "root")),
            "password": os.getenv("MYSQL_PASSWORD", mysql_conf.get("password", "")),
            "database": os.getenv("MYSQL_DB", mysql_conf.get("database", "test")),
            "port": int(os.getenv("MYSQL_PORT", mysql_conf.get("port", 3306))),
        }


# 运行示例
if __name__ == "__main__":
    config_parser = ConfigParser()
    print("Base URL:", config_parser.get_base_url())
    print("MySQL 配置:", config_parser.get_mysql_conf())