"""Build the same 9,889-row / 34-column USGS dataset used by SEISMOSCOPE.

The course project data are sourced from the user-provided USGS `query.csv`.
Run this only if you want to reproduce the supplied prepared data.
"""
import csv
import datetime as dt
import math
from pathlib import Path

START=dt.datetime(2023,2,1,tzinfo=dt.timezone.utc)
END=dt.datetime(2024,6,1,tzinfo=dt.timezone.utc)
EXTRAS=['event_date_utc','event_year','event_month','event_year_month','event_quarter','event_weekday_utc','event_hour_utc','magnitude_band','depth_category','latitude_hemisphere','latitude_band','depth_exactly_10km']

def mag_band(m):
    if m<5:return 'M4.5–4.9'
    if m<6:return 'M5.0–5.9'
    if m<7:return 'M6.0–6.9'
    return 'M7.0+'

def depth_band(d):
    if d<70:return 'Shallow (<70 km)'
    if d<300:return 'Intermediate (70–299 km)'
    return 'Deep (>=300 km)'

def latitude_band(lat):
    for t, label in [(-60,'60–90°S'),(-30,'30–60°S'),(0,'0–30°S'),(30,'0–30°N'),(60,'30–60°N')]:
        if lat<t:return label
    return '60–90°N'

def main(source, target):
    with open(source,encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        original_columns=reader.fieldnames
        data=[]
        for row in reader:
            if row['type']!='earthquake': continue
            timestamp=dt.datetime.fromisoformat(row['time'].replace('Z','+00:00'))
            if not START <= timestamp < END: continue
            lat=float(row['latitude']);lon=float(row['longitude']);depth=float(row['depth']);mag=float(row['mag'])
            assert math.isfinite(lat) and math.isfinite(lon) and math.isfinite(depth) and math.isfinite(mag)
            row.update({
               'event_date_utc':timestamp.strftime('%Y-%m-%d'),
               'event_year':str(timestamp.year), 'event_month':str(timestamp.month),
               'event_year_month':timestamp.strftime('%Y-%m'),
               'event_quarter':f'{timestamp.year}-Q{(timestamp.month-1)//3+1}',
               'event_weekday_utc':timestamp.strftime('%A'), 'event_hour_utc':str(timestamp.hour),
               'magnitude_band':mag_band(mag), 'depth_category':depth_band(depth),
               'latitude_hemisphere':'Northern' if lat>=0 else 'Southern',
               'latitude_band':latitude_band(lat),
               'depth_exactly_10km':str(depth==10),
            })
            data.append(row)
    data.sort(key=lambda r:(r['time'],r['id']))
    assert len(data)==9889 and len(original_columns)==22
    assert len({r['id'] for r in data})==9889
    assert {'us6000jllz','us6000jlqa'}.issubset({r['id'] for r in data})
    dest=Path(target);dest.parent.mkdir(parents=True,exist_ok=True)
    with open(dest,'w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=original_columns+EXTRAS)
        writer.writeheader();writer.writerows(data)
    print(f'Prepared {len(data)} rows x {len(original_columns+EXTRAS)} columns: {dest}')

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',required=True)
    ap.add_argument('--output',default='data/earthquakes_dashboard_ready.csv')
    a=ap.parse_args()
    main(a.source,a.output)
