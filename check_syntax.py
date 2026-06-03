#!/usr/bin/env python3
"""
前后端语法检查脚本
"""

import subprocess
import sys
import os
from pathlib import Path

def check_python_files():
    """检查所有 Python 文件语法"""
    print("=" * 80)
    print("  后端 Python 语法检查")
    print("=" * 80)
    
    errors = []
    python_files = list(Path("app").rglob("*.py")) + \
                   list(Path("tests").rglob("*.py")) + \
                   list(Path("scripts").rglob("*.py"))
    
    for py_file in python_files:
        try:
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", str(py_file)],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                errors.append(f"❌ {py_file}: {result.stderr.strip()}")
            else:
                print(f"✓ {py_file}")
        except Exception as e:
            errors.append(f"❌ {py_file}: {str(e)}")
    
    return errors


def check_typescript_files():
    """检查 TypeScript 文件语法"""
    print("\n" + "=" * 80)
    print("  前端 TypeScript 语法检查")
    print("=" * 80)
    
    if not Path("frontend").exists():
        print("⚠️ 前端目录不存在，跳过检查")
        return []
    
    errors = []
    try:
        # 检查 package.json 是否存在
        if Path("frontend/package.json").exists():
            # 运行 TypeScript 编译检查
            result = subprocess.run(
                ["npm", "run", "lint"],
                cwd="frontend",
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode != 0:
                errors.append(f"❌ TSLint/ESLint 检查失败:\n{result.stdout}\n{result.stderr}")
            else:
                print("✓ ESLint/TSLint 检查通过")
        
        # 尝试 TypeScript 编译
        result = subprocess.run(
            ["npx", "tsc", "--noEmit"],
            cwd="frontend",
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode != 0 and result.stdout.strip():
            errors.append(f"❌ TypeScript 编译错误:\n{result.stdout}")
        else:
            print("✓ TypeScript 类型检查通过")
            
    except FileNotFoundError:
        print("⚠️ 未找到 npm，跳过前端检查")
    except subprocess.TimeoutExpired:
        errors.append("❌ 前端检查超时")
    except Exception as e:
        errors.append(f"❌ 前端检查错误：{str(e)}")
    
    return errors


def main():
    print("\n🔍 开始语法检查...\n")
    
    # 检查后端
    py_errors = check_python_files()
    
    # 检查前端
    ts_errors = check_typescript_files()
    
    # 汇总结果
    print("\n" + "=" * 80)
    print("  检查结果汇总")
    print("=" * 80)
    
    total_errors = len(py_errors) + len(ts_errors)
    
    if total_errors == 0:
        print("\n✅ 所有文件语法检查通过！\n")
        return 0
    else:
        print(f"\n❌ 发现 {total_errors} 个错误:\n")
        for error in py_errors + ts_errors:
            print(error)
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
