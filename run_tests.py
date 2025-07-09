#!/usr/bin/env python3
"""
BlogCommerce 測試運行腳本
提供各種測試選項和配置
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description=""):
    """運行命令並檢查結果"""
    if description:
        print(f"🔄 {description}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ 成功: {description}")
        if result.stdout:
            print(result.stdout)
    else:
        print(f"❌ 失敗: {description}")
        if result.stderr:
            print(result.stderr)
        if result.stdout:
            print(result.stdout)
        return False
    
    return True


def setup_test_environment():
    """設置測試環境"""
    print("🔧 設置測試環境...")
    
    # 檢查虛擬環境
    if not os.path.exists(".venv"):
        print("❌ 虛擬環境不存在，請先運行 ./install.sh")
        return False
    
    # 激活虛擬環境並安裝依賴
    if not run_command("source .venv/bin/activate && pip install -r requirements.txt", "安裝依賴"):
        return False
    
    # 創建測試目錄
    os.makedirs("logs", exist_ok=True)
    os.makedirs("test-results", exist_ok=True)
    
    print("✅ 測試環境設置完成")
    return True


def run_unit_tests(verbose=False, coverage=False):
    """運行單元測試"""
    print("🧪 運行單元測試...")
    
    cmd = "source .venv/bin/activate && python -m pytest tests/test_models.py -m unit"
    
    if verbose:
        cmd += " -v"
    
    if coverage:
        cmd += " --cov=app --cov-report=html --cov-report=term-missing"
    
    cmd += " --junit-xml=test-results/unit-tests.xml"
    
    return run_command(cmd, "單元測試")


def run_api_tests(verbose=False, coverage=False):
    """運行 API 測試"""
    print("🌐 運行 API 測試...")
    
    cmd = "source .venv/bin/activate && python -m pytest tests/test_api_*.py -m api"
    
    if verbose:
        cmd += " -v"
    
    if coverage:
        cmd += " --cov=app --cov-report=html --cov-report=term-missing"
    
    cmd += " --junit-xml=test-results/api-tests.xml"
    
    return run_command(cmd, "API 測試")


def run_e2e_tests(verbose=False):
    """運行端到端測試"""
    print("🔄 運行端到端測試...")
    
    cmd = "source .venv/bin/activate && python -m pytest tests/test_e2e.py -m e2e"
    
    if verbose:
        cmd += " -v"
    
    cmd += " --junit-xml=test-results/e2e-tests.xml"
    
    return run_command(cmd, "端到端測試")


def run_integration_tests(verbose=False):
    """運行集成測試"""
    print("🔗 運行集成測試...")
    
    cmd = "source .venv/bin/activate && python -m pytest tests/ -m integration"
    
    if verbose:
        cmd += " -v"
    
    cmd += " --junit-xml=test-results/integration-tests.xml"
    
    return run_command(cmd, "集成測試")


def run_all_tests(verbose=False, coverage=False):
    """運行所有測試"""
    print("🚀 運行所有測試...")
    
    cmd = "source .venv/bin/activate && python -m pytest tests/"
    
    if verbose:
        cmd += " -v"
    
    if coverage:
        cmd += " --cov=app --cov-report=html --cov-report=term-missing"
    
    cmd += " --junit-xml=test-results/all-tests.xml"
    
    return run_command(cmd, "所有測試")


def run_specific_test(test_path, verbose=False):
    """運行特定測試"""
    print(f"🎯 運行特定測試: {test_path}")
    
    cmd = f"source .venv/bin/activate && python -m pytest {test_path}"
    
    if verbose:
        cmd += " -v"
    
    return run_command(cmd, f"特定測試: {test_path}")


def run_tests_by_marker(marker, verbose=False):
    """按標記運行測試"""
    print(f"🏷️ 運行標記為 {marker} 的測試...")
    
    cmd = f"source .venv/bin/activate && python -m pytest tests/ -m {marker}"
    
    if verbose:
        cmd += " -v"
    
    cmd += f" --junit-xml=test-results/{marker}-tests.xml"
    
    return run_command(cmd, f"標記為 {marker} 的測試")


def check_test_coverage():
    """檢查測試覆蓋率"""
    print("📊 檢查測試覆蓋率...")
    
    cmd = "source .venv/bin/activate && python -m pytest tests/ --cov=app --cov-report=html --cov-report=term-missing --cov-report=xml"
    
    return run_command(cmd, "測試覆蓋率檢查")


def lint_code():
    """代碼風格檢查"""
    print("🔍 代碼風格檢查...")
    
    # 檢查是否安裝了 flake8 和 black
    cmd = "source .venv/bin/activate && pip install flake8 black isort"
    run_command(cmd, "安裝代碼檢查工具")
    
    # 運行 flake8
    if not run_command("source .venv/bin/activate && flake8 app tests --max-line-length=88", "Flake8 檢查"):
        return False
    
    # 運行 black 檢查
    if not run_command("source .venv/bin/activate && black --check app tests", "Black 格式檢查"):
        return False
    
    # 運行 isort 檢查
    if not run_command("source .venv/bin/activate && isort --check-only app tests", "isort 導入檢查"):
        return False
    
    return True


def generate_test_report():
    """生成測試報告"""
    print("📋 生成測試報告...")
    
    # 創建報告目錄
    os.makedirs("test-reports", exist_ok=True)
    
    # 生成 HTML 報告
    cmd = "source .venv/bin/activate && python -m pytest tests/ --html=test-reports/report.html --self-contained-html"
    
    return run_command(cmd, "生成測試報告")


def main():
    parser = argparse.ArgumentParser(description="BlogCommerce 測試運行器")
    
    # 測試類型選項
    parser.add_argument("--unit", action="store_true", help="運行單元測試")
    parser.add_argument("--api", action="store_true", help="運行 API 測試")
    parser.add_argument("--e2e", action="store_true", help="運行端到端測試")
    parser.add_argument("--integration", action="store_true", help="運行集成測試")
    parser.add_argument("--all", action="store_true", help="運行所有測試")
    
    # 標記選項
    parser.add_argument("--marker", help="按標記運行測試 (例如: auth, products, cart)")
    
    # 特定測試選項
    parser.add_argument("--test", help="運行特定測試文件或測試函數")
    
    # 其他選項
    parser.add_argument("--verbose", "-v", action="store_true", help="詳細輸出")
    parser.add_argument("--coverage", action="store_true", help="生成覆蓋率報告")
    parser.add_argument("--lint", action="store_true", help="運行代碼風格檢查")
    parser.add_argument("--report", action="store_true", help="生成測試報告")
    parser.add_argument("--setup", action="store_true", help="設置測試環境")
    
    args = parser.parse_args()
    
    # 如果沒有指定任何選項，顯示幫助
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    # 設置測試環境
    if args.setup or not os.path.exists("logs"):
        if not setup_test_environment():
            sys.exit(1)
    
    success = True
    
    # 運行代碼風格檢查
    if args.lint:
        success &= lint_code()
    
    # 運行特定測試
    if args.test:
        success &= run_specific_test(args.test, args.verbose)
    
    # 按標記運行測試
    if args.marker:
        success &= run_tests_by_marker(args.marker, args.verbose)
    
    # 運行不同類型的測試
    if args.unit:
        success &= run_unit_tests(args.verbose, args.coverage)
    
    if args.api:
        success &= run_api_tests(args.verbose, args.coverage)
    
    if args.e2e:
        success &= run_e2e_tests(args.verbose)
    
    if args.integration:
        success &= run_integration_tests(args.verbose)
    
    if args.all:
        success &= run_all_tests(args.verbose, args.coverage)
    
    # 生成測試報告
    if args.report:
        success &= generate_test_report()
    
    # 檢查覆蓋率
    if args.coverage and not (args.unit or args.api or args.all):
        success &= check_test_coverage()
    
    if success:
        print("\n✅ 所有測試成功完成！")
    else:
        print("\n❌ 某些測試失敗了，請檢查上面的錯誤信息。")
        sys.exit(1)


if __name__ == "__main__":
    main() 