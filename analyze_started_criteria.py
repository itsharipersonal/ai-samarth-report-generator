#!/usr/bin/env python3
"""
Analyze users with valid Start Date to check if they have any video/quiz completions
"""

import csv
import re
from pathlib import Path
from typing import List, Tuple, Dict
from datetime import datetime

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

def has_24char_id(header: str) -> Tuple[bool, str]:
    """Check if header ends with ' - ' followed by exactly 24 alphanumeric characters"""
    match = re.search(r' - ([a-zA-Z0-9]{24})$', header)
    return (True, match.group(1)) if match else (False, None)

def is_completed(cell_value: str) -> bool:
    """Check if a cell indicates completion"""
    if not cell_value:
        return False
    return 'completed' in cell_value.lower()

def analyze_file(filepath: str):
    """Analyze a single CSV file"""
    COL_R = 17
    COL_BR = 69
    COL_AP = 41
    COL_BU = 72
    COL_START_DATE = 12
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = list(reader)
    
    # Identify video chapters
    video_chapter_indices = []
    for i in range(COL_R, min(COL_BR + 1, len(headers))):
        has_24, _ = has_24char_id(headers[i])
        if has_24 and 'quiz' not in headers[i].lower():
            video_chapter_indices.append(i)
    
    quiz_indices = [COL_AP, COL_BU]
    
    stats = {
        'total_rows': len(rows),
        'with_valid_start_date': 0,
        'with_start_date_but_no_completions': 0,
        'with_start_date_and_completions': 0,
        'examples_no_completions': []
    }
    
    for row_idx, row in enumerate(rows, start=2):  # Start at 2 (row 1 is header)
        if len(row) <= COL_START_DATE:
            continue
        
        start_date_str = row[COL_START_DATE] if COL_START_DATE < len(row) else ""
        date_obj = parse_start_date(start_date_str)
        
        if date_obj is None:
            continue
        
        stats['with_valid_start_date'] += 1
        
        # Check for completions
        videos_completed = 0
        quizzes_completed = 0
        
        # Count videos
        for idx in video_chapter_indices:
            if idx < len(row) and is_completed(row[idx]):
                videos_completed += 1
        
        # Count quizzes
        for idx in quiz_indices:
            if idx < len(row) and is_completed(row[idx]):
                quizzes_completed += 1
        
        if videos_completed == 0 and quizzes_completed == 0:
            stats['with_start_date_but_no_completions'] += 1
            if len(stats['examples_no_completions']) < 5:
                email = row[3] if len(row) > 3 else "N/A"
                name = row[2] if len(row) > 2 else "N/A"
                stats['examples_no_completions'].append({
                    'row': row_idx,
                    'name': name,
                    'email': email,
                    'start_date': start_date_str
                })
        else:
            stats['with_start_date_and_completions'] += 1
    
    return stats

def main():
    files = [
        '/Users/krishnands/Downloads/learning data/AI Samarth - Bengali-1767932245825.csv',
        '/Users/krishnands/Downloads/learning data/AI Samarth - English-1767933164063.csv',
        '/Users/krishnands/Downloads/learning data/AI Samarth - Hindi-1767932947412.csv',
        '/Users/krishnands/Downloads/learning data/AI Samarth - Marathi-1767932241092.csv',
        '/Users/krishnands/Downloads/learning data/AI Samarth - Odia-1767932247363.csv'
    ]
    
    all_stats = []
    
    for filepath in files:
        if not Path(filepath).exists():
            print(f"⚠️  File not found: {filepath}")
            continue
        
        print(f"\n{'='*80}")
        print(f"Analyzing: {Path(filepath).name}")
        print(f"{'='*80}")
        
        stats = analyze_file(filepath)
        all_stats.append(stats)
        
        print(f"\nTotal Rows: {stats['total_rows']}")
        print(f"Users with Valid Start Date: {stats['with_valid_start_date']}")
        print(f"  ├─ With Start Date BUT NO Completions: {stats['with_start_date_but_no_completions']} ({stats['with_start_date_but_no_completions']/stats['with_valid_start_date']*100:.1f}%)")
        print(f"  └─ With Start Date AND Has Completions: {stats['with_start_date_and_completions']} ({stats['with_start_date_and_completions']/stats['with_valid_start_date']*100:.1f}%)")
        
        if stats['examples_no_completions']:
            print(f"\n📋 Examples of users with Start Date but NO completions:")
            for ex in stats['examples_no_completions']:
                print(f"   Row {ex['row']}: {ex['name']} ({ex['email']}) - Start Date: {ex['start_date']}")
    
    # Overall summary
    print(f"\n\n{'='*80}")
    print("OVERALL SUMMARY ACROSS ALL FILES")
    print(f"{'='*80}")
    
    total_rows = sum(s['total_rows'] for s in all_stats)
    total_with_start_date = sum(s['with_valid_start_date'] for s in all_stats)
    total_no_completions = sum(s['with_start_date_but_no_completions'] for s in all_stats)
    total_with_completions = sum(s['with_start_date_and_completions'] for s in all_stats)
    
    print(f"\nTotal Rows Across All Files: {total_rows}")
    print(f"Total Users with Valid Start Date: {total_with_start_date}")
    print(f"\n  ⚠️  Users with Start Date BUT NO Completions: {total_no_completions} ({total_no_completions/total_with_start_date*100:.1f}%)")
    print(f"  ✓  Users with Start Date AND Has Completions: {total_with_completions} ({total_with_completions/total_with_start_date*100:.1f}%)")
    
    print(f"\n{'='*80}")
    print("CONCLUSION")
    print(f"{'='*80}")
    print(f"\nCurrent 'Total Users Started' counts users with valid Start Date.")
    print(f"This includes {total_no_completions} users ({total_no_completions/total_with_start_date*100:.1f}%) who have a Start Date")
    print(f"but have NOT completed any videos or quizzes.")
    print(f"\nIf 'Started' should mean 'actually attempted content', the count should use")
    print(f"the has_started() function which checks for at least one completion.")

if __name__ == "__main__":
    main()
