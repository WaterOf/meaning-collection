import os
import yaml
from collections import OrderedDict


def generate_nav():
    """生成 MkDocs 导航结构"""
    docs_dir = "docs"
    exclude_dirs = ["js", ".obsidian"]
    exclude_files = ["index.md"]
    
    nav = []
    
    # 处理 docs 目录下的所有子目录
    for item in os.listdir(docs_dir):
        item_path = os.path.join(docs_dir, item)
        if os.path.isdir(item_path) and item not in exclude_dirs:
            nav_entry = process_directory(item_path, docs_dir, exclude_files)
            if nav_entry:
                nav.append(nav_entry)
    
    return nav


def process_directory(dir_path, base_dir, exclude_files):
    """处理单个目录，返回导航条目"""
    dir_name = os.path.basename(dir_path)
    rel_path = os.path.relpath(dir_path, base_dir).replace("\\", "/")
    
    # 获取当前目录下的 Markdown 文件
    md_files = []
    for file in os.listdir(dir_path):
        if file.endswith(".md") and file not in exclude_files:
            md_files.append(os.path.join(rel_path, file).replace("\\", "/"))
    
    # 获取子目录
    subdirs = []
    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)
        if os.path.isdir(item_path) and item not in ["js", ".obsidian"]:
            subdir_entry = process_directory(item_path, base_dir, exclude_files)
            if subdir_entry:
                subdirs.append(subdir_entry)
    
    # 构建导航条目
    if md_files or subdirs:
        if subdirs:
            # 如果有子目录，创建嵌套结构
            entry = {dir_name: []}
            # 添加当前目录的文件
            if md_files:
                entry[dir_name].extend(sorted(md_files))
            # 添加子目录
            entry[dir_name].extend(subdirs)
            return entry
        else:
            # 只有文件，直接返回文件列表
            return {dir_name: sorted(md_files)}
    
    return None


def update_mkdocs_config(nav_data):
    """更新 MkDocs 配置文件"""
    from ruamel.yaml import YAML
    
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.width = 4096
    
    with open("mkdocs.yml", "r", encoding="utf-8") as f:
        config = yaml.load(f) or {}
    
    # 更新导航配置
    config["nav"] = nav_data
    
    with open("mkdocs.yml", "w", encoding="utf-8") as f:
        yaml.dump(config, f)


if __name__ == "__main__":
    nav_structure = generate_nav()
    update_mkdocs_config(nav_structure)
    print("导航配置已更新，支持子目录分级显示！")
