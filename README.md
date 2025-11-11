# ERA5L Daily Aggregate

[中文文档](README_CN.md) | English

A high-performance Python tool for processing ERA5-Land reanalysis data, converting daily GeoTIFF files into categorized NetCDF format with optimized I/O and memory management.

## 📋 Overview

This project processes ERA5-Land hourly data aggregated to daily values, converting multi-band GeoTIFF files into separate NetCDF files organized by data categories. The tool is optimized for processing large datasets efficiently with batch I/O operations and intelligent memory management.

### Data Categories

The tool processes **68 variables** across **5 categories**:

1. **Evaporation (6 variables)**
   - Bare soil evaporation (Es)
   - Open water evaporation (Ew)
   - Canopy evaporation (Ec)
   - Vegetation transpiration (Et)
   - Potential evaporation (Ep)
   - Total evaporation (E)

2. **Vegetation (6 variables)**
   - Leaf Area Index (LAI) for high and low vegetation
   - Daily min/max LAI values

3. **Radiation (20 variables)**
   - Albedo
   - Latent/Sensible heat flux
   - Solar/Thermal radiation (net and downward)
   - Daily min/max values for all radiation variables

4. **Soil (24 variables)**
   - Soil temperature (4 levels: 0-7cm, 7-28cm, 28-100cm, 100-289cm)
   - Volumetric soil water (4 layers)
   - Daily min/max values for all soil variables

5. **Runoff & Precipitation (12 variables)**
   - Total runoff, surface runoff, sub-surface runoff
   - Total precipitation
   - Daily min/max values

## ✨ Features

- **Multi-category Processing**: Organizes 68 ERA5-Land variables into 5 logical categories
- **Optimized Performance**: 
  - Batch band reading (50-80% I/O time reduction)
  - Vectorized data processing
  - Efficient memory management with automatic cleanup
- **Smart Skip Logic**: Only processes missing data files to save time
- **Flexible Configuration**: Easy-to-modify input/output paths and processing options
- **Performance Monitoring**: Detailed timing information for each processing stage
- **Interactive Date Selection**: User-friendly date range input
- **CF-Compliant NetCDF**: Output follows CF-1.6 conventions with proper metadata

## 🚀 Installation

### Recommended: Using Conda (Windows/Linux/macOS)

```bash
# 1. Install Miniconda
# Download from: https://docs.conda.io/en/latest/miniconda.html

# 2. Create a new environment
conda create -n era5l python=3.11

# 3. Activate the environment
conda activate era5l

# 4. Install dependencies
conda install -c conda-forge rasterio xarray netcdf4 numpy
```

### Alternative: Using pip (requires Visual C++ Build Tools on Windows)

```bash
pip install numpy xarray rasterio netcdf4
```

For detailed installation troubleshooting, run:
```bash
python install_dependencies.py
```

## 📖 Usage

### Basic Usage

1. **Configure paths** in `deal_ERA5L_MultiCategory.py`:

```python
# Input directory containing yearly/monthly GeoTIFF files
BASE_INPUT_DIR = r'D:'

# Output directories for each category
OUT_EVAP = r'Z:\Evaporation_Flux\ERA5L'
OUT_VEG  = r'G:\Vegetation'
OUT_RAD  = r'G:\Radiation'
OUT_SOIL = r'G:\SoilMoisture'
OUT_ROPR = r'G:\Precipitation_Runoff'
```

2. **Run the processing script**:

```bash
python deal_ERA5L_MultiCategory.py
```

3. **Enter date range** when prompted:
```
请输入开始日期 (yyyymmdd): 20240101
请输入结束日期 (yyyymmdd): 20240131
```

### Input Data Structure

The script expects GeoTIFF files organized as:
```
BASE_INPUT_DIR/
  └── YYYY/
      └── MM/
          ├── ERA5_LAND_DAILY_YYYYMMDD_1.tif
          └── ERA5_LAND_DAILY_YYYYMMDD_2.tif
```

Each date requires 2 GeoTIFF files (northern and southern hemispheres).

### Output Structure

NetCDF files are organized by year, month, and category:
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

## ⚙️ Configuration Options

### Evaporation Swap Correction

```python
APPLY_EVAP_SWAP = True  # Enable evaporation variable swap correction
```

This corrects a known issue in historical ERA5-Land data where Es, Ew, and Et variables were incorrectly ordered.

## 🏎️ Performance Optimization

The code includes several optimizations:

### 1. Batch Band Reading
- **Before**: Sequential reading of individual bands (O(n) I/O calls)
- **After**: Single batch read of all needed bands (O(1) I/O calls)
- **Benefit**: 50-80% reduction in I/O time

### 2. Vectorized Processing
- Numpy-based array operations for scaling and transformations
- Reduces Python loop overhead

### 3. Memory Management
- Immediate cleanup after each category
- Explicit garbage collection
- Minimal memory copies

### Performance Monitoring Output

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

## 📁 Project Structure

```
ERA5L-Daily-Aggregate/
├── deal_ERA5L_MultiCategory.py   # Main processing script
├── install_dependencies.py        # Installation guide
├── test_performance.py            # Performance testing script
├── OPTIMIZATION_SUMMARY.md        # Optimization details
├── PERFORMANCE_OPTIMIZATION_REPORT.md  # Performance analysis
├── ERA5-Land波段.xlsx             # Band reference information
├── README.md                      # This file (English)
└── README_CN.md                   # Chinese documentation
```

## 🔧 Troubleshooting

### Common Issues

1. **ImportError: No module named 'rasterio'**
   - Solution: Install using conda (recommended) or ensure Visual C++ Build Tools are installed for pip

2. **Memory Error during processing**
   - Solution: Process smaller date ranges, or increase system RAM

3. **Missing input files**
   - Error: "未找到2块tif"
   - Solution: Ensure both hemisphere GeoTIFF files exist for the date

4. **Output directory errors**
   - Solution: The script automatically creates directories, but ensure parent paths exist

## 📊 Data Source

ERA5-Land hourly data aggregated to daily values:
- **Source**: [Copernicus Climate Data Store](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land)
- **Spatial Resolution**: 0.1° × 0.1° (approximately 9km)
- **Temporal Coverage**: 1950 - present
- **Temporal Resolution**: Daily (aggregated from hourly)

## 📝 Citation

If you use this tool in your research, please cite the ERA5-Land dataset:

```
Muñoz Sabater, J., (2019): ERA5-Land hourly data from 1950 to present. 
Copernicus Climate Change Service (C3S) Climate Data Store (CDS). 
DOI: 10.24381/cds.e2161bac
```

## 👥 Authors

- **Changming Li** - Initial development
- Contact: licm@scut.edu.cn

## 📄 License

This project is available for academic and research use. Please contact the authors for commercial use.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/licm13/ERA5L-Daily-Aggregate.git
cd ERA5L-Daily-Aggregate

# Set up conda environment
conda create -n era5l python=3.11
conda activate era5l
conda install -c conda-forge rasterio xarray netcdf4 numpy

# Run tests
python test_performance.py
```

## 🔮 Future Enhancements

Potential improvements (see OPTIMIZATION_SUMMARY.md for details):

- **Parallel Processing**: Multi-threaded writing of different categories
- **Dask Integration**: Support for distributed processing
- **Zarr Format**: Alternative output format optimized for parallel I/O
- **Multi-process Date Processing**: Process multiple dates in parallel

## 📚 Additional Documentation

- [OPTIMIZATION_SUMMARY.md](OPTIMIZATION_SUMMARY.md) - Detailed performance optimization guide
- [PERFORMANCE_OPTIMIZATION_REPORT.md](PERFORMANCE_OPTIMIZATION_REPORT.md) - Performance analysis report
- [中文文档](README_CN.md) - Complete Chinese documentation

---

**Last Updated**: 2024-11
