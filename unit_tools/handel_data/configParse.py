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
            raise FileNotFoundError(f"配置文件 {self.config_file} 未找到！")
        except yaml.YAMLError as e:
            raise ValueError(f"YAML 文件解析出错: {e}")

    def load_json(self):
        """读取 JSON 格式配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"配置文件 {self.config_file} 未找到！")
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

    def get_mysql_conf(self):
        """
        获取 MySQL 数据库配置，并映射成常用连接参数格式
        """
        mysql_conf = self.config_data.get("mysql", {})
        return {
            "host": mysql_conf.get("host"),
            "username": mysql_conf.get("username"),  # 注意映射
            "password": mysql_conf.get("password"),
            "database": mysql_conf.get("database"),
            "port": mysql_conf.get("port", 3306)
        }

# 运行示例
if __name__ == "__main__":
    config_parser = ConfigParser()
    print("Base URL:", config_parser.get("base_url"))
    print("MySQL 配置:", config_parser.get_mysql_conf())

    print(f"Base URL: {config_parser.get('base_url')}")
    print(f"MySQL Host: {config_parser.get('mysql.host')}")
    print(f"MySQL Config: {config_parser.get('mysql')}")

    # 修改配置
    config_parser.set("mysql.password", "newpass123")
    print("修改后的 MySQL 配置：", config_parser.get("mysql"))

    # 判断配置项是否存在
    print("是否存在 mysql.port:", config_parser.exists("mysql.port"))
