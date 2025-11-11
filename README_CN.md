# ERA5L 日数据聚合工具

中文 | [English](README.md)

一个高性能的 Python 工具，用于处理 ERA5-Land 再分析数据，将日 GeoTIFF 文件转换为按类别组织的 NetCDF 格式，具有优化的 I/O 和内存管理。

## 📋 概述

本项目处理 ERA5-Land 小时数据聚合到日值，将多波段 GeoTIFF 文件转换为按数据类别分类的独立 NetCDF 文件。该工具通过批量 I/O 操作和智能内存管理优化，可高效处理大型数据集。

### 数据类别

该工具处理 **5 个类别**的 **68 个变量**：

1. **蒸发 (6 个变量)**
   - 裸土蒸发 (Es)
   - 开阔水面蒸发 (Ew)
   - 冠层蒸发 (Ec)
   - 植被蒸腾 (Et)
   - 潜在蒸发 (Ep)
   - 总蒸发 (E)

2. **植被 (6 个变量)**
   - 高植被和低植被的叶面积指数 (LAI)
   - 日最小/最大 LAI 值

3. **辐射 (20 个变量)**
   - 反照率
   - 潜热/显热通量
   - 太阳/热辐射（净辐射和向下辐射）
   - 所有辐射变量的日最小/最大值

4. **土壤 (24 个变量)**
   - 土壤温度（4 层：0-7cm、7-28cm、28-100cm、100-289cm）
   - 体积土壤水分（4 层）
   - 所有土壤变量的日最小/最大值

5. **径流和降水 (12 个变量)**
   - 总径流、地表径流、地下径流
   - 总降水
   - 日最小/最大值

## ✨ 特性

- **多类别处理**：将 68 个 ERA5-Land 变量组织成 5 个逻辑类别
- **性能优化**：
  - 批量波段读取（I/O 时间减少 50-80%）
  - 向量化数据处理
  - 高效的内存管理和自动清理
- **智能跳过逻辑**：仅处理缺失的数据文件以节省时间
- **灵活配置**：易于修改的输入/输出路径和处理选项
- **性能监控**：每个处理阶段的详细计时信息
- **交互式日期选择**：用户友好的日期范围输入
- **符合 CF 标准的 NetCDF**：输出遵循 CF-1.6 规范并包含适当的元数据

## 🚀 安装

### 推荐方式：使用 Conda (Windows/Linux/macOS)

```bash
# 1. 安装 Miniconda
# 下载地址：https://docs.conda.io/en/latest/miniconda.html

# 2. 创建新环境
conda create -n era5l python=3.11

# 3. 激活环境
conda activate era5l

# 4. 安装依赖
conda install -c conda-forge rasterio xarray netcdf4 numpy
```

### 替代方式：使用 pip（Windows 上需要 Visual C++ Build Tools）

```bash
pip install numpy xarray rasterio netcdf4
```

详细的安装故障排除，请运行：
```bash
python install_dependencies.py
```

## 📖 使用方法

### 基本用法

1. **配置路径**，在 `deal_ERA5L_MultiCategory.py` 中：

```python
# 包含年/月 GeoTIFF 文件的输入目录
BASE_INPUT_DIR = r'D:'

# 每个类别的输出目录
OUT_EVAP = r'Z:\Evaporation_Flux\ERA5L'
OUT_VEG  = r'G:\Vegetation'
OUT_RAD  = r'G:\Radiation'
OUT_SOIL = r'G:\SoilMoisture'
OUT_ROPR = r'G:\Precipitation_Runoff'
```

2. **运行处理脚本**：

```bash
python deal_ERA5L_MultiCategory.py
```

3. **输入日期范围**（按提示）：
```
请输入开始日期 (yyyymmdd): 20240101
请输入结束日期 (yyyymmdd): 20240131
```

### 输入数据结构

脚本期望 GeoTIFF 文件按以下方式组织：
```
BASE_INPUT_DIR/
  └── YYYY/
      └── MM/
          ├── ERA5_LAND_DAILY_YYYYMMDD_1.tif
          └── ERA5_LAND_DAILY_YYYYMMDD_2.tif
```

每个日期需要 2 个 GeoTIFF 文件（北半球和南半球）。

### 输出结构

NetCDF 文件按年、月和类别组织：
```
OUTPUT_DIR/
  └── YYYY/
      └── MM/
          ├── ERA5_Land_Daily_ET_YYYYMMDD.nc
          ├── ERA5_Land_Daily_Vegetation_YYYYMMDD.nc
          ├── ERA5_Land_Daily_Radiation_YYYYMMDD.nc
          ├── ERA5_Land_Daily_Soil_YYYYMMDD.nc
          └── ERA5_Land_Daily_RunoffPrecip_YYYYMMDD.nc
```

## ⚙️ 配置选项

### 蒸发变量交换修正

```python
APPLY_EVAP_SWAP = True  # 启用蒸发变量交换修正
```

这修正了历史 ERA5-Land 数据中已知的问题，其中 Es、Ew 和 Et 变量的顺序不正确。

## 🏎️ 性能优化

代码包含多项优化：

### 1. 批量波段读取
- **优化前**：顺序读取单个波段（O(n) 次 I/O 调用）
- **优化后**：一次性批量读取所有需要的波段（O(1) 次 I/O 调用）
- **效益**：I/O 时间减少 50-80%

### 2. 向量化处理
- 基于 Numpy 的数组操作进行缩放和转换
- 减少 Python 循环开销

### 3. 内存管理
- 每个类别处理后立即清理
- 显式垃圾回收
- 最小化内存拷贝

### 性能监控输出

```
=== 2024-01-01 ===
  读取所需波段中 …
  波段读取完成，耗时: 2.35秒
  写出 Evap 完成。
  写出 Vegetation 完成。
  写出 Radiation 完成。
  写出 Soil 完成。
  写出 Runoff+Precip 完成。
  处理耗时: 1.87秒, 本日总耗时: 4.22秒
  本日完成。
```

## 📁 项目结构

```
ERA5L-Daily-Aggregate/
├── deal_ERA5L_MultiCategory.py   # 主处理脚本
├── install_dependencies.py        # 安装指南
├── test_performance.py            # 性能测试脚本
├── OPTIMIZATION_SUMMARY.md        # 优化详情
├── PERFORMANCE_OPTIMIZATION_REPORT.md  # 性能分析报告
├── ERA5-Land波段.xlsx             # 波段参考信息
├── README.md                      # 英文文档
└── README_CN.md                   # 本文件（中文文档）
```

## 🔧 故障排除

### 常见问题

1. **ImportError: No module named 'rasterio'**
   - 解决方案：使用 conda 安装（推荐），或确保已为 pip 安装 Visual C++ Build Tools

2. **处理过程中的内存错误**
   - 解决方案：处理较小的日期范围，或增加系统 RAM

3. **缺少输入文件**
   - 错误：「未找到2块tif」
   - 解决方案：确保该日期的两个半球 GeoTIFF 文件都存在

4. **输出目录错误**
   - 解决方案：脚本会自动创建目录，但需确保父路径存在

## 📊 数据源

ERA5-Land 小时数据聚合到日值：
- **来源**：[哥白尼气候数据存储](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land)
- **空间分辨率**：0.1° × 0.1°（约 9 公里）
- **时间覆盖**：1950 年至今
- **时间分辨率**：日（从小时数据聚合）

## 📝 引用

如果您在研究中使用此工具，请引用 ERA5-Land 数据集：

```
Muñoz Sabater, J., (2019): ERA5-Land hourly data from 1950 to present. 
Copernicus Climate Change Service (C3S) Climate Data Store (CDS). 
DOI: 10.24381/cds.e2161bac
```

## 👥 作者

- **李长明** - 初始开发
- 联系方式：licm@scut.edu.cn

## 📄 许可证

本项目可用于学术和研究用途。商业用途请联系作者。

## 🤝 贡献

欢迎贡献！请随时提交问题或拉取请求。

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/licm13/ERA5L-Daily-Aggregate.git
cd ERA5L-Daily-Aggregate

# 设置 conda 环境
conda create -n era5l python=3.11
conda activate era5l
conda install -c conda-forge rasterio xarray netcdf4 numpy

# 运行测试
python test_performance.py
```

## 🔮 未来改进

潜在改进（详见 OPTIMIZATION_SUMMARY.md）：

- **并行处理**：多线程写入不同类别
- **Dask 集成**：支持分布式处理
- **Zarr 格式**：针对并行 I/O 优化的替代输出格式
- **多进程日期处理**：并行处理多个日期

## 📚 其他文档

- [OPTIMIZATION_SUMMARY.md](OPTIMIZATION_SUMMARY.md) - 详细的性能优化指南
- [PERFORMANCE_OPTIMIZATION_REPORT.md](PERFORMANCE_OPTIMIZATION_REPORT.md) - 性能分析报告
- [English Documentation](README.md) - 完整英文文档

## 🔬 技术细节

### 变量处理详解

#### 蒸发类变量处理
- 应用 -1000 缩放因子（从米转换为毫米/天）
- 可选的变量交换修正（APPLY_EVAP_SWAP）
- 包含 Es（裸土）、Ew（水面）、Ec（冠层）、Et（蒸腾）、Ep（潜在）和 E（总计）

#### 辐射类变量处理
- 热通量以 J/m² 为单位
- 包含日均值、最小值和最大值
- 涵盖反照率、潜热通量、显热通量、净太阳辐射、净热辐射等

#### 土壤类变量处理
- 4 个深度层次的温度（单位：K）
- 4 个深度层次的体积土壤水分（单位：m³/m³）
- 每个变量都有日均值、最小值和最大值

#### 径流降水类变量处理
- 径流以米为单位
- 包含总径流、地表径流和地下径流
- 降水以米为单位
- 所有变量都有日均值、最小值和最大值

### 坐标系统
- **输入**：1800×3600 网格（0.1° 分辨率）
- **纬度**：90°N 到 90°S
- **经度**：180°W 到 180°E
- **输出**：重新分配坐标以中心对齐（-179.95 到 179.95，89.95 到 -89.95）

### NetCDF 元数据
输出文件包含完整的 CF-1.6 兼容元数据：
- 全局属性（标题、公约、创建日期、联系信息）
- 变量属性（长名称、单位、标准名称）
- 坐标属性（纬度/经度单位和描述）

### 数据压缩
- 使用 zlib 压缩，级别为 5
- 在文件大小和压缩速度之间取得平衡
- 典型压缩比：50-70%（取决于变量）

## 📈 性能基准

基于典型硬件配置（SSD、16GB RAM）：

| 操作 | 优化前 | 优化后 | 改进 |
|------|--------|--------|------|
| 单日读取 | ~8-12秒 | ~2-4秒 | 60-75% |
| 单日处理 | ~3-5秒 | ~1.5-2.5秒 | 40-50% |
| 单日总计 | ~12-18秒 | ~4-7秒 | 55-65% |
| 内存峰值 | ~4-6GB | ~2-3GB | 40-50% |

*注：实际性能取决于硬件、数据大小和系统负载*

## ⚡ 优化建议

### 对于大批量处理
1. 使用 SSD 存储以获得更快的 I/O
2. 确保足够的 RAM（建议 8GB 以上）
3. 分批处理日期（例如，每次 1 个月）
4. 使用性能监控输出识别瓶颈

### 对于内存受限系统
1. 一次处理更少的日期
2. 考虑禁用不需要的类别
3. 调整 NetCDF 压缩级别（降低 complevel）

### 对于网络存储
1. 尽可能使用本地临时存储
2. 完成后批量复制输出文件
3. 考虑使用 rsync 进行增量传输

## 🔍 代码质量

### 已实现的最佳实践
- ✅ 符合 PEP 8 的代码风格
- ✅ 全面的错误处理
- ✅ 详细的文档字符串
- ✅ 性能优化
- ✅ 内存管理
- ✅ 进度报告
- ✅ 输入验证

### 测试
- 语法检查：`python -m py_compile deal_ERA5L_MultiCategory.py`
- 性能测试：`python test_performance.py`
- 单日测试：使用相同的开始和结束日期运行主脚本

## 📞 支持

如有问题或需要帮助：
1. 检查[故障排除](#故障排除)部分
2. 查看现有的 GitHub Issues
3. 创建新的 Issue 并提供详细信息
4. 联系作者：licm@scut.edu.cn

## 🙏 致谢

- ERA5-Land 数据由 Copernicus Climate Change Service 提供
- 感谢所有为开源科学 Python 生态系统做出贡献的人
- 特别感谢 rasterio、xarray 和 netCDF4 项目

---

**最后更新**：2024-11
