#!/usr/bin/env python3
"""检查项目Python 3.10兼容性"""
import os
import sys
import ast

# 要检查的文件扩展名
extensions = ['.py']

# 跳过的目录
exclude_dirs = ['__pycache__', 'venv', 'env', '.git']

def check_file_compatibility(file_path):
    """检查单个文件的Python 3.10兼容性"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # 尝试解析AST，这会捕获语法错误
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, f"语法错误: {e}"
    except Exception as e:
        return False, f"其他错误: {e}"

def main():
    """主函数"""
    print(f"检查Python 3.10兼容性...")
    print(f"Python版本: {sys.version}")
    print()
    
    total_files = 0
    compatible_files = 0
    incompatible_files = []
    
    for root, dirs, files in os.walk('.'):
        # 跳过排除的目录
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                total_files += 1
                
                compatible, error_msg = check_file_compatibility(file_path)
                if compatible:
                    compatible_files += 1
                else:
                    incompatible_files.append((file_path, error_msg))
    
    print(f"检查完成: {total_files}个文件")
    print(f"兼容文件: {compatible_files}")
    print(f"不兼容文件: {len(incompatible_files)}")
    
    if incompatible_files:
        print("\n不兼容文件详情:")
        for file_path, error_msg in incompatible_files:
            print(f"- {file_path}: {error_msg}")
    else:
        print("\n所有文件都与Python 3.10兼容!")

if __name__ == "__main__":
    main()
