# ERA5-Land Daily Aggregate - Multi-Category Processor

[中文](#中文文档) | [English](#english-documentation)

---

## 中文文档

### 📋 项目简介

ERA5-Land Daily Aggregate 是一个高效的数据处理工具，用于将 ERA5-Land 再分析数据从 GeoTIFF 格式转换为 NetCDF 格式。该工具支持多类别数据处理，包括蒸发、植被、辐射、土壤和径流降水等五大类别的气象数据。

**v5.0 版本新特性：**
- ✨ **交互式类别选择**：通过图形界面选择要处理的数据类别
- 🚀 **性能优化**：仅处理用户选择的类别，避免不必要的计算
- 🎯 **智能跳过**：自动跳过已存在的文件，支持断点续传
- ⚡ **并行I/O**：使用多线程并行读取数据，显著提升处理速度

### 🎯 核心功能

#### 1. 交互式GUI操作
- **路径选择**：通过文件对话框选择输入/输出目录
- **日期范围**：命令行交互式输入起止日期
- **类别选择**：通过复选框界面选择要处理的数据类别

#### 2. 支持的数据类别

| 类别 | 说明 | 变量数量 |
|------|------|----------|
| 🌊 **Evaporation (蒸发)** | 包含裸土蒸发、水面蒸发、冠层蒸发、植被蒸腾等 | 6个变量 |
| 🌱 **Vegetation (植被)** | 包含高低植被叶面积指数及其最小最大值 | 6个变量 |
| ☀️ **Radiation (辐射)** | 包含反照率、热通量、太阳辐射、热辐射等 | 21个变量 |
| 🏔️ **Soil (土壤)** | 包含4层土壤温度和4层土壤水分及其最小最大值 | 24个变量 |
| 💧 **Runoff+Precip (径流+降水)** | 包含总径流、地表径流、地下径流、总降水等 | 12个变量 |

#### 3. 数据处理流程

```
GeoTIFF输入 → 并行读取 → 数据缩放 → 坐标转换 → NetCDF输出
    ↓            ↓          ↓          ↓          ↓
 两个半球    多线程I/O   蒸发修正   重新插值   按类别分类
```

### 📦 安装要求

#### Python版本
- Python 3.7+

#### 依赖库
```bash
pip install numpy xarray rasterio netCDF4
```

详细依赖列表：
- `numpy` - 数组计算
- `xarray` - 多维数据处理
- `rasterio` - GeoTIFF读取
- `netCDF4` - NetCDF文件I/O
- `tkinter` - GUI界面（通常随Python自带）

### 🚀 使用方法

#### 基本使用流程

1. **运行脚本**
```bash
python deal_ERA5L_MultiCategory.py
```

2. **选择输入目录**
   - 弹出文件对话框，选择包含 GeoTIFF 文件的基础目录
   - 目录结构应为：`BASE_DIR/YYYY/MM/ERA5_LAND_DAILY_YYYYMMDD*.tif`

3. **选择输出目录**
   - 弹出文件对话框，选择输出NetCDF文件的基础目录
   - 程序会自动创建子目录：`Evaporation_Flux/ERA5L`, `Vegetation`, `Radiation`, `SoilMoisture`, `Precipitation_Runoff`

4. **输入日期范围**
```
请输入开始日期 (yyyymmdd): 20200101
请输入结束日期 (yyyymmdd): 20201231
```

5. **选择数据类别**
   - 弹出图形界面，勾选要处理的类别
   - 可选择一个或多个类别
   - 点击"确认选择"继续

6. **自动处理**
   - 程序自动处理选定日期范围内的所有数据
   - 实时显示处理进度和耗时
   - 自动跳过已存在的文件

#### 高级配置

在脚本开头可以配置以下参数：

```python
# 蒸发数据交换修正（默认：True）
APPLY_EVAP_SWAP = True

# 默认输入输出路径（可通过GUI覆盖）
BASE_INPUT_DIR = r'D:'
OUT_EVAP = r'Z:\Evaporation_Flux\ERA5L'
OUT_VEG  = r'G:\Vegetation'
OUT_RAD  = r'G:\Radiation'
OUT_SOIL = r'G:\SoilMoisture'
OUT_ROPR = r'G:\Precipitation_Runoff'
```

### 📂 目录结构

#### 输入数据结构
```
BASE_INPUT_DIR/
├── 2020/
│   ├── 01/
│   │   ├── ERA5_LAND_DAILY_20200101_S1.tif  (北半球)
│   │   ├── ERA5_LAND_DAILY_20200101_S2.tif  (南半球)
│   │   ├── ERA5_LAND_DAILY_20200102_S1.tif
│   │   └── ERA5_LAND_DAILY_20200102_S2.tif
│   └── 02/
│       └── ...
└── 2021/
    └── ...
```

#### 输出数据结构
```
BASE_OUTPUT_DIR/
├── Evaporation_Flux/ERA5L/
│   └── 2020/
│       └── 01/
│           ├── ERA5_Land_Daily_ET_20200101.nc
│           └── ERA5_Land_Daily_ET_20200102.nc
├── Vegetation/
│   └── 2020/01/ERA5_Land_Daily_Vegetation_20200101.nc
├── Radiation/
│   └── 2020/01/ERA5_Land_Daily_Radiation_20200101.nc
├── SoilMoisture/
│   └── 2020/01/ERA5_Land_Daily_Soil_20200101.nc
└── Precipitation_Runoff/
    └── 2020/01/ERA5_Land_Daily_RunoffPrecip_20200101.nc
```

### ⚙️ 技术特性

#### 1. 并行I/O优化
使用 `ThreadPoolExecutor` 并行读取两个半球的 GeoTIFF 文件，显著提升读取速度。

#### 2. 内存优化
- 仅读取用户选择的类别所需的波段
- 及时释放不再使用的数据结构
- 使用垃圾回收优化内存占用

#### 3. 数据完整性
- 自动检查输入文件完整性
- 异常处理机制，失败不影响后续处理
- 自动清理异常产生的空文件

#### 4. 可追溯性
- NetCDF文件包含完整的元数据
- 记录创建时间、创建者、数据来源等信息
- 符合 CF-1.6 规范

### 📊 变量说明

#### 蒸发类 (Evaporation)
| 变量名 | 长名称 | 单位 |
|--------|--------|------|
| `Es` | 裸土蒸发 | mm day⁻¹ |
| `Ew` | 水面蒸发 | mm day⁻¹ |
| `Ec` | 冠层蒸发 | mm day⁻¹ |
| `Et` | 植被蒸腾 | mm day⁻¹ |
| `Ep` | 潜在蒸发 | mm day⁻¹ |
| `E` | 总蒸发 | mm day⁻¹ |

#### 植被类 (Vegetation)
| 变量名 | 长名称 | 单位 |
|--------|--------|------|
| `lai_high` | 高植被叶面积指数 | 1 |
| `lai_low` | 低植被叶面积指数 | 1 |
| `lai_high_min/max` | 高植被LAI最小/最大值 | 1 |
| `lai_low_min/max` | 低植被LAI最小/最大值 | 1 |

#### 辐射类 (Radiation)
包含反照率、潜热通量、净太阳辐射、净热辐射、感热通量、向下太阳辐射、向下热辐射及其日最小最大值，共21个变量。

#### 土壤类 (Soil)
包含4层土壤温度 (0-7cm, 7-28cm, 28-100cm, 100-289cm) 和4层土壤水分及其日最小最大值，共24个变量。

#### 径流降水类 (Runoff+Precip)
| 变量名 | 长名称 | 单位 |
|--------|--------|------|
| `ro` | 总径流 | m |
| `ro_sub` | 地下径流 | m |
| `ro_sfc` | 地表径流 | m |
| `tp` | 总降水 | m |
| `*_min/max` | 各变量的日最小最大值 | m |

### 🔧 故障排除

#### 问题1：tkinter 无法导入
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# CentOS/RHEL
sudo yum install python3-tkinter

# macOS (通常不需要额外安装)
```

#### 问题2：文件未找到
- 检查输入目录结构是否符合 `YYYY/MM/` 格式
- 确认 GeoTIFF 文件命名为 `ERA5_LAND_DAILY_YYYYMMDD_S1.tif` 和 `S2.tif`

#### 问题3：内存不足
- 减少同时处理的日期范围
- 选择较少的数据类别
- 考虑在更大内存的机器上运行

#### 问题4：处理速度慢
- 确保输入输出目录在高速存储设备上
- 检查是否有足够的系统资源
- 考虑使用SSD而非机械硬盘

### 📝 版本历史

#### v5.0 (2025-11-11) - 交互式类别选择
- 新增交互式类别选择GUI界面
- 优化处理逻辑，仅处理用户选择的类别
- 改进用户体验和错误提示

#### v4.1 - Bug修复
- 修复跳过逻辑导致的类别漏处理问题
- 优化内存使用和波段读取策略

#### v4.0 - 并行I/O
- 引入多线程并行读取
- 显著提升处理速度

### 👥 贡献者

- **Changming Li** - 原始开发
- **Claude Assistant** - 功能扩展与优化

### 📧 联系方式

- Email: licm@scut.edu.cn
- 数据源: [Copernicus Climate Data Store](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land)

### 📄 许可证

本项目用于科学研究目的。使用本工具处理的数据应遵循 ERA5-Land 数据的使用条款。

---

## English Documentation

### 📋 Project Overview

ERA5-Land Daily Aggregate is an efficient data processing tool for converting ERA5-Land reanalysis data from GeoTIFF format to NetCDF format. The tool supports multi-category data processing, including five major categories: evaporation, vegetation, radiation, soil, and runoff/precipitation meteorological data.

**v5.0 New Features:**
- ✨ **Interactive Category Selection**: Choose data categories via GUI
- 🚀 **Performance Optimization**: Process only selected categories
- 🎯 **Smart Skip**: Automatically skip existing files, supports resume
- ⚡ **Parallel I/O**: Multi-threaded data reading for faster processing

### 🎯 Core Features

#### 1. Interactive GUI Operation
- **Path Selection**: Choose input/output directories via file dialogs
- **Date Range**: Interactive command-line input for start/end dates
- **Category Selection**: Select data categories via checkbox interface

#### 2. Supported Data Categories

| Category | Description | Variables |
|----------|-------------|-----------|
| 🌊 **Evaporation** | Bare soil, open water, canopy evaporation, transpiration, etc. | 6 variables |
| 🌱 **Vegetation** | High/low vegetation leaf area index with min/max values | 6 variables |
| ☀️ **Radiation** | Albedo, heat flux, solar radiation, thermal radiation, etc. | 21 variables |
| 🏔️ **Soil** | 4-layer soil temperature and moisture with min/max values | 24 variables |
| 💧 **Runoff+Precip** | Total/surface/subsurface runoff, total precipitation | 12 variables |

#### 3. Data Processing Workflow

```
GeoTIFF Input → Parallel Read → Data Scaling → Coord Transform → NetCDF Output
      ↓              ↓              ↓                ↓                ↓
  2 Hemispheres  Multi-thread   Evap Correction  Reinterpolation  By Category
```

### 📦 Installation Requirements

#### Python Version
- Python 3.7+

#### Dependencies
```bash
pip install numpy xarray rasterio netCDF4
```

Detailed dependencies:
- `numpy` - Array computations
- `xarray` - Multi-dimensional data processing
- `rasterio` - GeoTIFF reading
- `netCDF4` - NetCDF file I/O
- `tkinter` - GUI interface (usually comes with Python)

### 🚀 Usage

#### Basic Workflow

1. **Run the script**
```bash
python deal_ERA5L_MultiCategory.py
```

2. **Select input directory**
   - File dialog appears, select base directory containing GeoTIFF files
   - Directory structure: `BASE_DIR/YYYY/MM/ERA5_LAND_DAILY_YYYYMMDD*.tif`

3. **Select output directory**
   - File dialog appears, select base directory for NetCDF output
   - Subdirectories created automatically: `Evaporation_Flux/ERA5L`, `Vegetation`, `Radiation`, `SoilMoisture`, `Precipitation_Runoff`

4. **Input date range**
```
Please enter start date (yyyymmdd): 20200101
Please enter end date (yyyymmdd): 20201231
```

5. **Select data categories**
   - GUI window appears with checkboxes
   - Select one or more categories
   - Click "确认选择" (Confirm) to continue

6. **Automatic processing**
   - Program processes all data within selected date range
   - Real-time progress and timing display
   - Automatically skips existing files

#### Advanced Configuration

Configure parameters at the beginning of the script:

```python
# Evaporation data swap correction (default: True)
APPLY_EVAP_SWAP = True

# Default input/output paths (overrideable via GUI)
BASE_INPUT_DIR = r'D:'
OUT_EVAP = r'Z:\Evaporation_Flux\ERA5L'
OUT_VEG  = r'G:\Vegetation'
OUT_RAD  = r'G:\Radiation'
OUT_SOIL = r'G:\SoilMoisture'
OUT_ROPR = r'G:\Precipitation_Runoff'
```

### 📂 Directory Structure

#### Input Data Structure
```
BASE_INPUT_DIR/
├── 2020/
│   ├── 01/
│   │   ├── ERA5_LAND_DAILY_20200101_S1.tif  (Northern hemisphere)
│   │   ├── ERA5_LAND_DAILY_20200101_S2.tif  (Southern hemisphere)
│   │   ├── ERA5_LAND_DAILY_20200102_S1.tif
│   │   └── ERA5_LAND_DAILY_20200102_S2.tif
│   └── 02/
│       └── ...
└── 2021/
    └── ...
```

#### Output Data Structure
```
BASE_OUTPUT_DIR/
├── Evaporation_Flux/ERA5L/
│   └── 2020/
│       └── 01/
│           ├── ERA5_Land_Daily_ET_20200101.nc
│           └── ERA5_Land_Daily_ET_20200102.nc
├── Vegetation/
│   └── 2020/01/ERA5_Land_Daily_Vegetation_20200101.nc
├── Radiation/
│   └── 2020/01/ERA5_Land_Daily_Radiation_20200101.nc
├── SoilMoisture/
│   └── 2020/01/ERA5_Land_Daily_Soil_20200101.nc
└── Precipitation_Runoff/
    └── 2020/01/ERA5_Land_Daily_RunoffPrecip_20200101.nc
```

### ⚙️ Technical Features

#### 1. Parallel I/O Optimization
Uses `ThreadPoolExecutor` to read two hemisphere GeoTIFF files in parallel, significantly improving read speed.

#### 2. Memory Optimization
- Only reads bands required by selected categories
- Timely release of unused data structures
- Garbage collection for optimized memory usage

#### 3. Data Integrity
- Automatic input file integrity check
- Exception handling mechanism, failures don't affect subsequent processing
- Automatic cleanup of empty files from exceptions

#### 4. Traceability
- NetCDF files contain complete metadata
- Records creation time, creator, data source, etc.
- Complies with CF-1.6 conventions

### 📊 Variable Descriptions

#### Evaporation Category
| Variable | Long Name | Units |
|----------|-----------|-------|
| `Es` | Evaporation from bare soil | mm day⁻¹ |
| `Ew` | Evaporation from open water surfaces | mm day⁻¹ |
| `Ec` | Evaporation from the top of canopy | mm day⁻¹ |
| `Et` | Evaporation from vegetation transpiration | mm day⁻¹ |
| `Ep` | Potential evaporation | mm day⁻¹ |
| `E` | Total evaporation | mm day⁻¹ |

#### Vegetation Category
| Variable | Long Name | Units |
|----------|-----------|-------|
| `lai_high` | Leaf area index - high vegetation | 1 |
| `lai_low` | Leaf area index - low vegetation | 1 |
| `lai_high_min/max` | Daily min/max LAI - high vegetation | 1 |
| `lai_low_min/max` | Daily min/max LAI - low vegetation | 1 |

#### Radiation Category
Includes albedo, latent heat flux, net solar radiation, net thermal radiation, sensible heat flux, downward solar radiation, downward thermal radiation, and their daily min/max values (21 variables total).

#### Soil Category
Includes 4-layer soil temperature (0-7cm, 7-28cm, 28-100cm, 100-289cm) and 4-layer soil moisture with daily min/max values (24 variables total).

#### Runoff+Precipitation Category
| Variable | Long Name | Units |
|----------|-----------|-------|
| `ro` | Runoff (total) | m |
| `ro_sub` | Sub-surface runoff | m |
| `ro_sfc` | Surface runoff | m |
| `tp` | Total precipitation | m |
| `*_min/max` | Daily min/max for each variable | m |

### 🔧 Troubleshooting

#### Issue 1: tkinter import fails
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# CentOS/RHEL
sudo yum install python3-tkinter

# macOS (usually no additional installation needed)
```

#### Issue 2: File not found
- Check if input directory structure follows `YYYY/MM/` format
- Verify GeoTIFF files are named `ERA5_LAND_DAILY_YYYYMMDD_S1.tif` and `S2.tif`

#### Issue 3: Out of memory
- Reduce date range processed simultaneously
- Select fewer data categories
- Consider running on a machine with more memory

#### Issue 4: Slow processing
- Ensure input/output directories are on fast storage devices
- Check for sufficient system resources
- Consider using SSD instead of HDD

### 📝 Version History

#### v5.0 (2025-11-11) - Interactive Category Selection
- Added interactive category selection GUI
- Optimized processing logic to handle only selected categories
- Improved user experience and error messages

#### v4.1 - Bug Fix
- Fixed skip logic causing category omission
- Optimized memory usage and band reading strategy

#### v4.0 - Parallel I/O
- Introduced multi-threaded parallel reading
- Significantly improved processing speed

### 👥 Contributors

- **Changming Li** - Original development
- **Claude Assistant** - Feature expansion and optimization

### 📧 Contact

- Email: licm@scut.edu.cn
- Data Source: [Copernicus Climate Data Store](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land)

### 📄 License

This project is for scientific research purposes. Data processed using this tool should comply with ERA5-Land data usage terms.

---

**Note**: This tool is designed for processing ERA5-Land reanalysis data. Please ensure you have appropriate data access permissions before use.
