python .\parse_all_runs.py hyrod_bitmp_1year_Tota -i E:\ArgosBatch\grotsund_arp_12h-max 
python .\parse_all_runs.py hyrod_bitmp_1year_Tota -i E:\ArgosBatch\grotsund_arp_12h-100m_5km
@REM -c iodine_child
python .\parse_all_runs.py 4800_grid_toteffout_bitmp_Adults_Total -i E:\ArgosBatch\grotsund_arp_12h-max 
python .\parse_all_runs.py 4800_grid_toteffout_bitmp_Adults_Total -i E:\ArgosBatch\grotsund_arp_12h-100m_5km
@REM -c sheltering_full
@REM python .\parse_all_runs.py 4800_grid_toteffout_bitmp_Adults_Total -i E:\ArgosBatch\grotsund_arp_12h-max -c sheltering_partial

python .\parse_all_runs.py hyrod_bitmp_Adults_Tota -i E:\ArgosBatch\grotsund_arp_12h-max
python .\parse_all_runs.py hyrod_bitmp_Adults_Tota -i E:\ArgosBatch\grotsund_arp_12h-100m_5km
@REM  -c iodine_adult

@REM TODO:
python .\parse_all_runs.py 16800_grid_toteffout_bitmp_Adults_Total -i E:\ArgosBatch\grotsund_arp_12h-max
python .\parse_all_runs.py 16800_grid_toteffout_bitmp_Adults_Total -i E:\ArgosBatch\grotsund_arp_12h-100m_5km