import os
import yaml
from collections import OrderedDict


def generate_nav():
    docs_dir = "docs"
    exclude_dirs = ["js", ".obsidian"]
    exclude_files = ["index.md"]

    nav = OrderedDict()

    for item in os.listdir(docs_dir):
        item_path = os.path.join(docs_dir, item)
        if not os.path.isdir(item_path) or item in exclude_dirs:
            continue

        # 递归处理子目录，构建嵌套结构
        nav[item] = build_nested_structure(item_path, docs_dir, exclude_files)

    return nav


def build_nested_structure(root_dir, base_dir, exclude_files):
    """将文件路径转换为嵌套的导航结构"""
    structure = OrderedDict()

    for root, dirs, files in os.walk(root_dir):
        # 过滤掉不需要的文件
        md_files = [f for f in files if f.endswith(".md") and f not in exclude_files]

        if not md_files:
            continue

        # 计算相对于 base_dir 的相对路径
        rel_path = os.path.relpath(root, base_dir).replace("\\", "/")
        path_parts = rel_path.split("/")

        # 构建嵌套字典
        current_level = structure
        for part in path_parts[1:]:  # 跳过第一级（已在主函数中处理）
            if part not in current_level:
                current_level[part] = OrderedDict()
            current_level = current_level[part]

        # 添加当前目录下的文件
        current_level["_files"] = sorted(
            [os.path.join(rel_path, f).replace("\\", "/") for f in md_files]
        )

    return structure


def update_mkdocs_config(nav_data):
    from ruamel.yaml import YAML

    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.width = 4096

    with open("mkdocs.yml", "r", encoding="utf-8") as f:
        config = yaml.load(f) or {}

    if "nav" not in config:
        config["nav"] = []

    # 清除现有导航（保留首页）
    config["nav"] = [
        item for item in config["nav"] if isinstance(item, str) and "首页" in item
    ]

    # 将嵌套结构转换为 MkDocs 兼容的导航格式
    for category, content in nav_data.items():
        nav_entry = flatten_nested_structure(content, category)
        config["nav"].extend(nav_entry)

    with open("mkdocs.yml", "w", encoding="utf-8") as f:
        yaml.dump(config, f)


def flatten_nested_structure(structure, current_path=""):
    """将嵌套结构转换为 MkDocs 兼容的导航格式"""
    result = []

    if "_files" in structure:
        # 如果当前层级有文件，直接添加
        if current_path:
            result.append({current_path: structure["_files"]})
        else:
            result.extend(structure["_files"])

    for key, value in structure.items():
        if key == "_files":
            continue

        new_path = f"{current_path}/{key}" if current_path else key
        nested = flatten_nested_structure(value, new_path)

        if nested:
            if current_path:
                # 如果当前层级有子目录，构建嵌套字典
                result.append({current_path: nested})
            else:
                # 如果是顶级目录，直接添加
                result.append({key: nested})

    return result


if __name__ == "__main__":
    nav_structure = generate_nav()
    update_mkdocs_config(nav_structure)
    print("导航配置已更新，支持子目录分级显示！")
