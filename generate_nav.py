import os
import yaml
from collections import OrderedDict

def generate_nav():
    docs_dir = "docs"
    exclude_dirs = ["js",".obsidian"]
    exclude_files = ["index.md"]
    
    nav = OrderedDict()
    
    for item in os.listdir(docs_dir):
        item_path = os.path.join(docs_dir, item)
        if not os.path.isdir(item_path) or item in exclude_dirs:
            continue
            
        md_files = []
        for root, _, files in os.walk(item_path):
            for file in files:
                if file.endswith(".md") and file not in exclude_files:
                    rel_path = os.path.relpath(os.path.join(root, file), docs_dir)
                    md_files.append(rel_path.replace("\\", "/"))
        
        if md_files:
            nav[item] = sorted(md_files)
    
    return nav

def update_mkdocs_config(nav_data):
    # 使用 ruamel.yaml 替代 PyYAML 以保留特殊标签
    from ruamel.yaml import YAML
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.width = 4096  # 避免长行换行
    
    with open("mkdocs.yml", "r", encoding='utf-8') as f:
        config = yaml.load(f) or {}
    
    # 保留原有配置结构
    if "nav" not in config:
        config["nav"] = []
    
    # 清除现有导航（保留首页）
    config["nav"] = [item for item in config["nav"] if "首页" in item]
    
    # 添加新导航
    for category, files in nav_data.items():
        config["nav"].append({category: files})
    
    with open("mkdocs.yml", "w", encoding='utf-8') as f:
        yaml.dump(config, f)

if __name__ == "__main__":
    nav_structure = generate_nav()
    update_mkdocs_config(nav_structure)
    print("导航配置已更新，特殊标签已保留！")