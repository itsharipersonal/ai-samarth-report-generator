#!/usr/bin/env python3
"""
Check what dates are present in Bengali data
"""

import csv
from datetime import datetime
from collections import Counter

def parse_start_date(date_str: str):
    """Parse Start Date string and return datetime.date object or None"""
    if not date_str or not date_str.strip():
        return None
    
    date_str = date_str.strip()
    
    if date_str.lower() in ['not started', '']:
        return None
    
    try:
        parts = date_str.split('/')
        if len(parts) == 3:
            if len(parts[0]) == 4:
                year = int(parts[0])
                month = int(parts[1])
                day = int(parts[2])
            else:
                day = int(parts[0])
                month = int(parts[1])
                year = int(parts[2])
                if year < 50:
                    year += 2000
                else:
                    year += 1900
            
            if 1 <= month <= 12 and 1 <= day <= 31:
                return datetime(year, month, day).date()
    except (ValueError, IndexError):
        pass
    
    return None

def check_file(filepath: str):
    """Check dates in a CSV file"""
    COL_START_DATE = 12
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = list(reader)
    
    year_month_counts = Counter()
    year_counts = Counter()
    dates_with_completions = []
    dates_without_completions = []
    
    # Check for completions (simplified - just check if any cell has "Completed")
    for row in rows:
        if len(row) <= COL_START_DATE:
            continue
        
        start_date_str = row[COL_START_DATE] if COL_START_DATE < len(row) else ""
        date_obj = parse_start_date(start_date_str)
        
        # Check if row has any completions
        has_completion = False
        for cell in row:
            if cell and 'completed' in cell.lower():
                has_completion = True
                break
        
        if date_obj:
            year_month = (date_obj.year, date_obj.month)
            year_month_counts[year_month] += 1
            year_counts[date_obj.year] += 1
            
            if has_completion:
                dates_with_completions.append((date_obj.year, date_obj.month, date_obj))
            else:
                dates_without_completions.append((date_obj.year, date_obj.month, date_obj))
    
    return {
        'total_rows': len(rows),
        'year_month_counts': year_month_counts,
        'year_counts': year_counts,
        'dates_with_completions': dates_with_completions,
        'dates_without_completions': dates_without_completions
    }

filepath = '/Users/krishnands/Downloads/learning data/AI Samarth - Bengali-1767932245825.csv'

print(f"Analyzing: {filepath}")
print("="*80)

stats = check_file(filepath)

print(f"\nTotal Rows: {stats['total_rows']}")
print(f"\nYear Distribution:")
for year in sorted(stats['year_counts'].keys()):
    print(f"  {year}: {stats['year_counts'][year]} users")

print(f"\nYear-Month Distribution (all users with Start Date):")
for (year, month) in sorted(stats['year_month_counts'].keys()):
    month_name = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][month-1]
    print(f"  {year}-{month:02d} ({month_name}): {stats['year_month_counts'][(year, month)]} users")

print(f"\nUsers with Start Date AND completions: {len(stats['dates_with_completions'])}")
print(f"Users with Start Date BUT NO completions: {len(stats['dates_without_completions'])}")

print(f"\nYear-Month for users WITH completions:")
completion_year_months = Counter([(y, m) for y, m, d in stats['dates_with_completions']])
for (year, month) in sorted(completion_year_months.keys()):
    month_name = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][month-1]
    print(f"  {year}-{month:02d} ({month_name}): {completion_year_months[(year, month)]} users")

print(f"\nYear-Month for users WITHOUT completions:")
no_completion_year_months = Counter([(y, m) for y, m, d in stats['dates_without_completions']])
for (year, month) in sorted(no_completion_year_months.keys()):
    month_name = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][month-1]
    print(f"  {year}-{month:02d} ({month_name}): {no_completion_year_months[(year, month)]} users")

# Check specifically for January 2026
jan_2026_with = sum(1 for y, m, d in stats['dates_with_completions'] if y == 2026 and m == 1)
jan_2026_without = sum(1 for y, m, d in stats['dates_without_completions'] if y == 2026 and m == 1)
jan_2026_total = stats['year_month_counts'].get((2026, 1), 0)

print(f"\n" + "="*80)
print("JANUARY 2026 ANALYSIS:")
print(f"  Total users with Start Date in Jan 2026: {jan_2026_total}")
print(f"  Users with Start Date in Jan 2026 AND completions: {jan_2026_with}")
print(f"  Users with Start Date in Jan 2026 BUT NO completions: {jan_2026_without}")

if jan_2026_total == 0:
    print(f"\n  ⚠️  No users have a Start Date in January 2026")
    print(f"  This is why there's no column for 'Up to January 2026 End'")
    print(f"  The code only creates columns for year-months that exist in the Start Date data")
