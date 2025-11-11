#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ERA5-Land GeoTIFF -> NetCDF (Multi-Category) - v4.1 (bugfix)
------------------------------------------------------------
修复：当 Evap 与 Runoff+Precip 已存在时，之前版本直接 continue 跳过了当天**所有**类别的处理。
本版本改为**仅跳过相应类别的写出**，其他类别（Vegetation/Radiation/Soil）仍会正常处理。
同时仅为“需要”的类别读取/构建波段以节约内存与时间。

其他调整：
- APPLY_EVAP_SWAP 默认 False（与用户历史数据一致，可自行改为 True）。
- 按 yyyy/mm 子目录存储保持不变。
- 仅蒸发变量保留 *-1000 缩放，其余变量不缩放。
"""

import os
import sys
import datetime as dt
import time
import glob
import gc
import numpy as np
import xarray as xr
import rasterio
import traceback
import tkinter as tk
from tkinter import filedialog
from concurrent.futures import ThreadPoolExecutor, as_completed

# ===== 可配置项 =====
APPLY_EVAP_SWAP = True  # 历史数据已修正；如需在新数据上继续应用交换修正，改为 True
BASE_INPUT_DIR = r'D:'
OUT_EVAP = r'Z:\\Evaporation_Flux\\ERA5L'
OUT_VEG  = r'G:\\Vegetation'
OUT_RAD  = r'G:\\Radiation'
OUT_SOIL = r'G:\\SoilMoisture'
OUT_ROPR = r'G:\\Precipitation_Runoff'

def process_era5l_data_multi():
    # ========= GUI 路径选择 =========
    print('正在启动路径选择对话框...')
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    # 选择基础输入目录
    BASE_INPUT_DIR = filedialog.askdirectory(title='请选择基础输入目录 (例如: D:)')
    if not BASE_INPUT_DIR:
        print('未选择输入目录，程序退出。', file=sys.stderr)
        sys.exit(1)
    print(f'已选择输入目录: {BASE_INPUT_DIR}')

    # 选择基础输出目录
    BASE_OUTPUT_DIR = filedialog.askdirectory(title='请选择基础输出目录')
    if not BASE_OUTPUT_DIR:
        print('未选择输出目录，程序退出。', file=sys.stderr)
        sys.exit(1)
    print(f'已选择输出目录: {BASE_OUTPUT_DIR}')

    # 构建各个输出子目录路径
    OUT_EVAP = os.path.join(BASE_OUTPUT_DIR, 'Evaporation_Flux', 'ERA5L')
    OUT_VEG  = os.path.join(BASE_OUTPUT_DIR, 'Vegetation')
    OUT_RAD  = os.path.join(BASE_OUTPUT_DIR, 'Radiation')
    OUT_SOIL = os.path.join(BASE_OUTPUT_DIR, 'SoilMoisture')
    OUT_ROPR = os.path.join(BASE_OUTPUT_DIR, 'Precipitation_Runoff')

    root.destroy()  # 销毁tkinter窗口

    # ========= 交互式日期 =========
    def ask_date(prompt):
        while True:
            s = input(prompt).strip()
            try:
                return dt.datetime.strptime(s, '%Y%m%d')
            except Exception:
                print('格式需为 yyyymmdd，例如 20250101')
    start_dt = ask_date('请输入开始日期 (yyyymmdd): ')
    end_dt   = ask_date('请输入结束日期 (yyyymmdd): ')
    if end_dt < start_dt:
        print('结束日期早于开始日期。', file=sys.stderr); sys.exit(1)

    # ========= 变量表 =========
    evap_bands = [
        {'Index': 35, 'VarName': 'Es', 'LongName': 'Evaporation from bare soil', 'Units': 'mm day-1'},
        {'Index': 36, 'VarName': 'Ew', 'LongName': 'Evaporation from open water surfaces excluding oceans', 'Units': 'mm day-1'},
        {'Index': 37, 'VarName': 'Ec', 'LongName': 'Evaporation from the top of canopy', 'Units': 'mm day-1'},
        {'Index': 38, 'VarName': 'Et', 'LongName': 'Evaporation from vegetation transpiration', 'Units': 'mm day-1'},
        {'Index': 39, 'VarName': 'Ep', 'LongName': 'Potential evaporation', 'Units': 'mm day-1'},
        {'Index': 44, 'VarName': 'E',  'LongName': 'Total evaporation', 'Units': 'mm day-1'}
    ]
    veg_bands = [
        {'Index': 49,  'VarName': 'lai_high',     'LongName': 'Leaf area index of high vegetation (half of total green leaf area)', 'Units': '1'},
        {'Index': 50,  'VarName': 'lai_low',      'LongName': 'Leaf area index of low vegetation (half of total green leaf area)',  'Units': '1'},
        {'Index': 147, 'VarName': 'lai_high_min', 'LongName': 'Daily minimum leaf_area_index_high_vegetation', 'Units': '1'},
        {'Index': 148, 'VarName': 'lai_high_max', 'LongName': 'Daily maximum leaf_area_index_high_vegetation', 'Units': '1'},
        {'Index': 149, 'VarName': 'lai_low_min',  'LongName': 'Daily minimum leaf_area_index_low_vegetation',  'Units': '1'},
        {'Index': 150, 'VarName': 'lai_low_max',  'LongName': 'Daily maximum leaf_area_index_low_vegetation',  'Units': '1'},
    ]
    rad_bands = [
        {'Index': 28,  'VarName': 'albedo',      'LongName': 'Forecast albedo', 'Units': '1'},
        {'Index': 29,  'VarName': 'lhf_sum',     'LongName': 'Surface latent heat flux sum', 'Units': 'J m-2'},
        {'Index': 30,  'VarName': 'nsr_sum',     'LongName': 'Surface net solar radiation sum', 'Units': 'J m-2'},
        {'Index': 31,  'VarName': 'ntr_sum',     'LongName': 'Surface net thermal radiation sum', 'Units': 'J m-2'},
        {'Index': 32,  'VarName': 'shf_sum',     'LongName': 'Surface sensible heat flux sum', 'Units': 'J m-2'},
        {'Index': 33,  'VarName': 'srd_sum',     'LongName': 'Surface solar radiation downwards sum', 'Units': 'J m-2'},
        {'Index': 34,  'VarName': 'trd_sum',     'LongName': 'Surface thermal radiation downwards sum', 'Units': 'J m-2'},
        {'Index': 105, 'VarName': 'albedo_min',  'LongName': 'Daily minimum forecast albedo', 'Units': '1'},
        {'Index': 106, 'VarName': 'albedo_max',  'LongName': 'Daily maximum forecast albedo', 'Units': '1'},
        {'Index': 107, 'VarName': 'lhf_min',     'LongName': 'Daily minimum surface latent heat flux', 'Units': 'J m-2'},
        {'Index': 108, 'VarName': 'lhf_max',     'LongName': 'Daily maximum surface latent heat flux', 'Units': 'J m-2'},
        {'Index': 109, 'VarName': 'nsr_min',     'LongName': 'Daily minimum surface net solar radiation', 'Units': 'J m-2'},
        {'Index': 110, 'VarName': 'nsr_max',     'LongName': 'Daily maximum surface net solar radiation', 'Units': 'J m-2'},
        {'Index': 111, 'VarName': 'ntr_min',     'LongName': 'Daily minimum surface net thermal radiation', 'Units': 'J m-2'},
        {'Index': 112, 'VarName': 'ntr_max',     'LongName': 'Daily maximum surface net thermal radiation', 'Units': 'J m-2'},
        {'Index': 113, 'VarName': 'shf_min',     'LongName': 'Daily minimum surface sensible heat flux', 'Units': 'J m-2'},
        {'Index': 114, 'VarName': 'shf_max',     'LongName': 'Daily maximum surface sensible heat flux', 'Units': 'J m-2'},
        {'Index': 115, 'VarName': 'srd_min',     'LongName': 'Daily minimum surface solar radiation downwards', 'Units': 'J m-2'},
        {'Index': 116, 'VarName': 'srd_max',     'LongName': 'Daily maximum surface solar radiation downwards', 'Units': 'J m-2'},
        {'Index': 117, 'VarName': 'trd_min',     'LongName': 'Daily minimum surface thermal radiation downwards', 'Units': 'J m-2'},
        {'Index': 118, 'VarName': 'trd_max',     'LongName': 'Daily maximum surface thermal radiation downwards', 'Units': 'J m-2'},
    ]
    soil_bands = [
        {'Index': 4,  'VarName': 'stl1', 'LongName': 'Soil temperature level 1 (0-7 cm)',   'Units': 'K'},
        {'Index': 5,  'VarName': 'stl2', 'LongName': 'Soil temperature level 2 (7-28 cm)',  'Units': 'K'},
        {'Index': 6,  'VarName': 'stl3', 'LongName': 'Soil temperature level 3 (28-100 cm)','Units': 'K'},
        {'Index': 7,  'VarName': 'stl4', 'LongName': 'Soil temperature level 4 (100-289 cm)','Units': 'K'},
        {'Index': 57, 'VarName': 'stl1_min', 'LongName': 'Daily minimum soil temperature level 1', 'Units': 'K'},
        {'Index': 58, 'VarName': 'stl1_max', 'LongName': 'Daily maximum soil temperature level 1', 'Units': 'K'},
        {'Index': 59, 'VarName': 'stl2_min', 'LongName': 'Daily minimum soil temperature level 2', 'Units': 'K'},
        {'Index': 60, 'VarName': 'stl2_max', 'LongName': 'Daily maximum soil temperature level 2', 'Units': 'K'},
        {'Index': 61, 'VarName': 'stl3_min', 'LongName': 'Daily minimum soil temperature level 3', 'Units': 'K'},
        {'Index': 62, 'VarName': 'stl3_max', 'LongName': 'Daily maximum soil temperature level 3', 'Units': 'K'},
        {'Index': 63, 'VarName': 'stl4_min', 'LongName': 'Daily minimum soil temperature level 4', 'Units': 'K'},
        {'Index': 64, 'VarName': 'stl4_max', 'LongName': 'Daily maximum soil temperature level 4', 'Units': 'K'},
        {'Index': 24, 'VarName': 'vsw1', 'LongName': 'Volumetric soil water layer 1 (0-7 cm)',    'Units': 'm3 m-3'},
        {'Index': 25, 'VarName': 'vsw2', 'LongName': 'Volumetric soil water layer 2 (7-28 cm)',   'Units': 'm3 m-3'},
        {'Index': 26, 'VarName': 'vsw3', 'LongName': 'Volumetric soil water layer 3 (28-100 cm)', 'Units': 'm3 m-3'},
        {'Index': 27, 'VarName': 'vsw4', 'LongName': 'Volumetric soil water layer 4 (100-289 cm)','Units': 'm3 m-3'},
        {'Index': 97,  'VarName': 'vsw1_min', 'LongName': 'Daily minimum volumetric soil water layer 1', 'Units': 'm3 m-3'},
        {'Index': 98,  'VarName': 'vsw1_max', 'LongName': 'Daily maximum volumetric soil water layer 1', 'Units': 'm3 m-3'},
        {'Index': 99,  'VarName': 'vsw2_min', 'LongName': 'Daily minimum volumetric soil water layer 2', 'Units': 'm3 m-3'},
        {'Index': 100, 'VarName': 'vsw2_max', 'LongName': 'Daily maximum volumetric soil water layer 2', 'Units': 'm3 m-3'},
        {'Index': 101, 'VarName': 'vsw3_min', 'LongName': 'Daily minimum volumetric soil water layer 3', 'Units': 'm3 m-3'},
        {'Index': 102, 'VarName': 'vsw3_max', 'LongName': 'Daily maximum volumetric soil water layer 3', 'Units': 'm3 m-3'},
        {'Index': 103, 'VarName': 'vsw4_min', 'LongName': 'Daily minimum volumetric soil water layer 4', 'Units': 'm3 m-3'},
        {'Index': 104, 'VarName': 'vsw4_max', 'LongName': 'Daily maximum volumetric soil water layer 4', 'Units': 'm3 m-3'},
    ]
    ropr_bands = [
        {'Index': 40,  'VarName': 'ro',     'LongName': 'Runoff (total)',          'Units': 'm'},
        {'Index': 42,  'VarName': 'ro_sub', 'LongName': 'Sub-surface runoff',      'Units': 'm'},
        {'Index': 43,  'VarName': 'ro_sfc', 'LongName': 'Surface runoff',          'Units': 'm'},
        {'Index': 48,  'VarName': 'tp',     'LongName': 'Total precipitation',     'Units': 'm'},
        {'Index': 129, 'VarName': 'ro_min',     'LongName': 'Daily minimum runoff',              'Units': 'm'},
        {'Index': 130, 'VarName': 'ro_max',     'LongName': 'Daily maximum runoff',              'Units': 'm'},
        {'Index': 133, 'VarName': 'ro_sub_min', 'LongName': 'Daily minimum sub-surface runoff',  'Units': 'm'},
        {'Index': 134, 'VarName': 'ro_sub_max', 'LongName': 'Daily maximum sub-surface runoff',  'Units': 'm'},
        {'Index': 135, 'VarName': 'ro_sfc_min', 'LongName': 'Daily minimum surface runoff',      'Units': 'm'},
        {'Index': 136, 'VarName': 'ro_sfc_max', 'LongName': 'Daily maximum surface runoff',      'Units': 'm'},
        {'Index': 145, 'VarName': 'tp_min',     'LongName': 'Daily minimum total precipitation', 'Units': 'm'},
        {'Index': 146, 'VarName': 'tp_max',     'LongName': 'Daily maximum total precipitation', 'Units': 'm'},
    ]

    global_attrs = {
        'title': 'ERA5-Land daily data from 1950 to present',
        'long_title': 'hourly-daily sum/24',
        'Conventions': 'CF-1.6',
        'Conventions_help': 'http://cfconventions.org/Data/cf-standard-names/docs/guidelines.html',
        'CreationDate': dt.datetime.now().strftime('%d-%b-%Y %H:%M:%S'),
        'CreatedBy': 'Changming Li & Assistant - Python 扩展版',
        'Download_source': 'https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land?tab=overview',
        'contact_info': 'licm@scut.edu.cn'
    }
    lat_initial = np.linspace(90, -90, 1800)
    lon_initial = np.linspace(-180, 180, 3600)
    new_lat = np.arange(89.95, -90.0, -0.1)
    new_lon = np.arange(-179.95, 180.0, 0.1)

    date_vec = [start_dt + dt.timedelta(days=i) for i in range((end_dt - start_dt).days + 1)]
    ok = skip = fail = 0
    t0 = time.time()
    print(f'将处理 {len(date_vec)} 天 …')

    for d in date_vec:
        y, m = d.year, d.month
        ds_date = d.strftime('%Y%m%d')
        print(f'\n=== {d:%Y-%m-%d} ===')

        out_evap_nc = os.path.join(OUT_EVAP, str(y), f'{m:02d}', f'ERA5_Land_Daily_ET_{ds_date}.nc')
        out_veg_nc  = os.path.join(OUT_VEG,  str(y), f'{m:02d}', f'ERA5_Land_Daily_Vegetation_{ds_date}.nc')
        out_rad_nc  = os.path.join(OUT_RAD,  str(y), f'{m:02d}', f'ERA5_Land_Daily_Radiation_{ds_date}.nc')
        out_soil_nc = os.path.join(OUT_SOIL, str(y), f'{m:02d}', f'ERA5_Land_Daily_Soil_{ds_date}.nc')
        out_ropr_nc = os.path.join(OUT_ROPR, str(y), f'{m:02d}', f'ERA5_Land_Daily_RunoffPrecip_{ds_date}.nc')

        # —— 按需判断每个类别是否需要写出 ——
        need_evap = not os.path.isfile(out_evap_nc)
        need_veg  = not os.path.isfile(out_veg_nc)
        need_rad  = not os.path.isfile(out_rad_nc)
        need_soil = not os.path.isfile(out_soil_nc)
        need_ropr = not os.path.isfile(out_ropr_nc)

        if not any([need_evap, need_veg, need_rad, need_soil, need_ropr]):
            print('  当日所有类别产物均已存在，跳过写出。')
            skip += 1
            continue

        # 依据“需要”的类别汇总所需波段索引，避免不必要读取
        bands_by_cat = []
        if need_evap: bands_by_cat += evap_bands
        if need_veg:  bands_by_cat += veg_bands
        if need_rad:  bands_by_cat += rad_bands
        if need_soil: bands_by_cat += soil_bands
        if need_ropr: bands_by_cat += ropr_bands
        needed_indices = sorted(set([b['Index'] for b in bands_by_cat]))
        evap_index_set = {b['Index'] for b in evap_bands}

        try:
            day_start_time = time.time()
            in_dir = os.path.join(BASE_INPUT_DIR, str(y), f'{m:02d}')
            tif_list = sorted(glob.glob(os.path.join(in_dir, f'ERA5_LAND_DAILY_{ds_date}*.tif')))
            if len(tif_list) != 2:
                print(f'  未找到2块tif（找到{len(tif_list)}），跳过。')
                fail += 1
                continue

            print('  读取所需波段中 (使用并行I/O) …')
            read_start_time = time.time()

            # 定义辅助函数：读取单个TIF文件的指定波段
            def read_tif_bands(tif_path, band_indices):
                """
                读取指定TIF文件的所需波段

                Args:
                    tif_path: TIF文件路径
                    band_indices: 需要读取的波段索引列表

                Returns:
                    读取到的波段数据 (n_bands, height, width)
                """
                with rasterio.open(tif_path) as src:
                    bands = src.read(band_indices)
                return bands

            # 使用 ThreadPoolExecutor 并行读取两个TIF文件
            with ThreadPoolExecutor(max_workers=2) as executor:
                # 并行提交两个读取任务
                future_s1 = executor.submit(read_tif_bands, tif_list[0], needed_indices)
                future_s2 = executor.submit(read_tif_bands, tif_list[1], needed_indices)

                # 获取两个future的结果
                s1_bands = future_s1.result()  # shape: (n_bands, height, width)
                s2_bands = future_s2.result()  # shape: (n_bands, height, width)

            # 拼接两个半球数据
            full_bands = np.concatenate((s1_bands, s2_bands), axis=2).astype(np.float32)

            # 向量化处理蒸发数据的缩放 - 性能优化
            evap_positions = [i for i, idx in enumerate(needed_indices) if idx in evap_index_set]
            if evap_positions:
                full_bands[evap_positions] *= -1000.0

            # 构建索引映射
            idx_to_position = {idx: i for i, idx in enumerate(needed_indices)}

            # 函数：从全数据中提取指定波段的数据
            def get_band_data(band_idx):
                return full_bands[idx_to_position[band_idx]]

            read_time = time.time() - read_start_time
            print(f'  波段读取完成 (并行I/O)，耗时: {read_time:.2f}秒')
            
            process_start_time = time.time()

            def build_dataset(band_list):
                data_vars = {}
                for b in band_list:
                    # 使用优化后的数据访问方式
                    data_vars[b['VarName']] = xr.DataArray(
                        get_band_data(b['Index']), dims=['lat','lon'], name=b['VarName'],
                        attrs={'long_name': b['LongName'], 'units': b['Units']}
                    )
                ds = xr.Dataset(data_vars,
                                coords={'lat': ('lat', lat_initial), 'lon': ('lon', lon_initial)},
                                attrs={'Conventions':'CF-1.6'})
                ds['lat'].attrs = {'units':'degrees_north', 'long_name':'latitude'}
                ds['lon'].attrs = {'units':'degrees_east',  'long_name':'longitude'}
                return ds

            def finalize(ds):
                ds = ds.assign_coords(lat=('lat', new_lat), lon=('lon', new_lon))
                ds.attrs.update(global_attrs)
                ds.attrs['ProcessingStatus'] = f'Finalized on {dt.datetime.now():%Y-%m-%d %H:%M:%S}'
                return ds

            # —— 仅对需要的类别构建与写出 ——
            def save_nc(ds, path):
                os.makedirs(os.path.dirname(path), exist_ok=True)
                enc = {v:{'zlib':True,'complevel':5} for v in ds.data_vars}
                ds.to_netcdf(path, encoding=enc)

            if need_evap:
                ds_evap = finalize(build_dataset(evap_bands))
                if APPLY_EVAP_SWAP:
                    # 优化：使用numpy操作进行交换，避免深拷贝
                    es_data = ds_evap['Es'].values.copy()
                    ew_data = ds_evap['Ew'].values.copy()
                    et_data = ds_evap['Et'].values.copy()
                    ds_evap['Es'].values = ew_data
                    ds_evap['Ew'].values = et_data
                    ds_evap['Et'].values = es_data
                    del es_data, ew_data, et_data  # 释放临时数组
                save_nc(ds_evap, out_evap_nc)
                print('  写出 Evap 完成。')
                del ds_evap; gc.collect()  # 及时释放内存
            else:
                print('  Evap 已存在，跳过写出。')

            if need_veg:
                ds_veg = finalize(build_dataset(veg_bands))
                save_nc(ds_veg, out_veg_nc)
                print('  写出 Vegetation 完成。')
                del ds_veg; gc.collect()  # 及时释放内存
            else:
                print('  Vegetation 已存在，跳过写出。')

            if need_rad:
                ds_rad = finalize(build_dataset(rad_bands))
                save_nc(ds_rad, out_rad_nc)
                print('  写出 Radiation 完成。')
                del ds_rad; gc.collect()  # 及时释放内存
            else:
                print('  Radiation 已存在，跳过写出。')

            if need_soil:
                ds_soil = finalize(build_dataset(soil_bands))
                save_nc(ds_soil, out_soil_nc)
                print('  写出 Soil 完成。')
                del ds_soil; gc.collect()  # 及时释放内存
            else:
                print('  Soil 已存在，跳过写出。')

            if need_ropr:
                ds_ropr = finalize(build_dataset(ropr_bands))
                save_nc(ds_ropr, out_ropr_nc)
                print('  写出 Runoff+Precip 完成。')
                del ds_ropr; gc.collect()  # 及时释放内存
            else:
                print('  Runoff+Precip 已存在，跳过写出。')

            # 释放主要数据结构
            del full_bands
            gc.collect()
            
            process_time = time.time() - process_start_time
            day_total_time = time.time() - day_start_time
            print(f'  处理耗时: {process_time:.2f}秒, 本日总耗时: {day_total_time:.2f}秒')
            
            ok += 1
            print('  本日完成。')

        except Exception:
            print('  失败，执行清理。', file=sys.stderr)
            traceback.print_exc()
            # 不删除已存在的历史产物；仅清理本轮新写入的半成品
            for f in [out_evap_nc, out_veg_nc, out_rad_nc, out_soil_nc, out_ropr_nc]:
                try:
                    if os.path.isfile(f) and os.path.getsize(f)==0:
                        os.remove(f)
                except Exception:
                    pass
            fail += 1

    print('\n==== 总结 ====')
    print(f'成功: {ok} 跳过: {skip} 失败: {fail} 用时: {(time.time()-t0)/60:.2f} 分钟')

if __name__ == '__main__':
    process_era5l_data_multi()
