#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ERA5L 依赖安装指南 - Windows 环境

由于rasterio在Windows上的安装比较复杂，这里提供几种解决方案：
"""

def show_installation_options():
    print("=== ERA5L 数据处理依赖安装指南 ===\n")
    
    print("问题：rasterio 在 Windows 上需要 GDAL，而 GDAL 需要 Visual C++ Build Tools")
    print("你的 Python 版本：3.14.0（很新的版本，可能缺少预编译wheel）\n")
    
    print("解决方案（按推荐程度排序）：\n")
    
    print("1. 【推荐】使用 Miniconda/Anaconda")
    print("   - 下载并安装 Miniconda: https://docs.conda.io/en/latest/miniconda.html")
    print("   - 然后运行: conda install -c conda-forge rasterio xarray netcdf4")
    print("   - 这会自动处理所有GDAL依赖\n")
    
    print("2. 安装 Microsoft Visual C++ Build Tools")
    print("   - 下载: https://visualstudio.microsoft.com/visual-cpp-build-tools/")
    print("   - 安装后运行: pip install rasterio")
    print("   - 可能仍然有问题，因为还需要GDAL库文件\n")
    
    print("3. 使用 OSGeo4W")
    print("   - 下载: https://trac.osgeo.org/osgeo4w/")
    print("   - 安装后会有完整的地理空间软件栈")
    print("   - 在OSGeo4W shell中运行python代码\n")
    
    print("4. 【临时方案】使用Docker")
    print("   - 使用预配置的地理空间容器")
    print("   - 例如: docker run -it --rm -v ${PWD}:/workspace osgeo/gdal:ubuntu-small-latest\n")
    
    print("5. 【代码修改】替换rasterio依赖")
    print("   - 如果只是读取GeoTIFF，可以考虑使用其他库")
    print("   - 例如: gdal（如果能单独安装）、PIL/Pillow + PyTIFF等")
    print("   - 但这需要修改代码逻辑\n")
    
    print("当前推荐：")
    print("1. 安装Miniconda")
    print("2. 创建新环境：conda create -n era5l python=3.11")
    print("3. 激活环境：conda activate era5l") 
    print("4. 安装依赖：conda install -c conda-forge rasterio xarray netcdf4 numpy")
    print("5. 在这个环境中运行代码")

if __name__ == "__main__":
    show_installation_options()