#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
性能测试脚本 - 测试优化后的ERA5L处理性能
运行单日数据处理以验证优化效果
"""

import sys
import datetime as dt
import time
from deal_ERA5L_MultiCategory import process_era5l_data_multi

def test_single_day():
    """测试单日处理性能"""
    print("=== ERA5L 性能测试 ===")
    print("本测试将处理单日数据以验证优化效果")
    
    # 模拟用户输入，设置同一天作为开始和结束日期
    test_date = "20240101"  # 可以根据实际可用数据调整
    
    print(f"测试日期: {test_date}")
    print("开始性能测试...")
    
    start_time = time.time()
    
    # 这里需要修改原函数以支持程序化调用
    # 暂时先打印说明
    print("注意：需要修改主函数以支持程序化测试")
    print("建议运行方式：")
    print("1. 直接运行 deal_ERA5L_MultiCategory.py")
    print("2. 输入测试日期（如20240101）作为开始和结束日期")
    print("3. 观察输出的各阶段耗时信息")
    
    end_time = time.time()
    print(f"测试准备耗时: {end_time - start_time:.2f}秒")

if __name__ == '__main__':
    test_single_day()