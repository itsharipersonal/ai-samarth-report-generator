import csv
from collections import defaultdict, Counter
from pathlib import Path

def analyze_progress_completed(filepath: str):
    """Analyze progress and completed episodes for each user"""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = list(reader)
    
    # Episode columns start from index 15 (after Progress column)
    episode_start_col = 15
    
    user_stats = []
    
    for row in rows:
        if len(row) < 3:
            continue
        
        email = row[4] if len(row) > 4 else ""
        name = row[3] if len(row) > 3 else ""
        language = row[2] if len(row) > 2 else ""
        progress = row[14] if len(row) > 14 else ""
        start_date = row[12] if len(row) > 12 else ""
        
        progress_count = 0
        completed_count = 0
        
        # Check all episode columns
        for col_idx in range(episode_start_col, len(row)):
            cell_value = row[col_idx] if col_idx < len(row) else ""
            
            if not cell_value or cell_value.strip() == "":
                continue
            
            cell_lower = cell_value.lower()
            
            if "in progress" in cell_lower:
                progress_count += 1
            elif "completed" in cell_lower:
                completed_count += 1
        
        # Check if start_date has a value (not empty, not "Not Started", not "-")
        start_date_clean = start_date.strip() if start_date else ""
        has_start_date = bool(start_date_clean and 
                             start_date_clean.lower() not in ['', 'not started', '-', 'n/a', 'na'])
        
        user_stats.append({
            'email': email,
            'name': name,
            'language': language,
            'progress_value': progress,
            'start_date': start_date,
            'has_start_date': has_start_date,
            'progress_episodes': progress_count,
            'completed_episodes': completed_count,
            'total_episodes': progress_count + completed_count
        })
    
    return user_stats

def main():
    files = [
        '/Users/krishnands/Downloads/learning_data_new/AI Samarth - Bengali-1768555852943.csv',
        '/Users/krishnands/Downloads/learning_data_new/AI Samarth - English-1768556785688.csv',
        '/Users/krishnands/Downloads/learning_data_new/AI Samarth - Hindi-1768556553927.csv',
        '/Users/krishnands/Downloads/learning_data_new/AI Samarth - Marathi-1768555851113.csv',
        '/Users/krishnands/Downloads/learning_data_new/AI Samarth - Odia-1768555855572.csv'
    ]
    
    all_user_stats = []
    
    print("Analyzing files...")
    for filepath in files:
        if not Path(filepath).exists():
            print(f"Warning: File not found: {filepath}")
            continue
        
        stats = analyze_progress_completed(filepath)
        all_user_stats.extend(stats)
        print(f"Processed: {Path(filepath).name} - {len(stats)} users")
    
    if not all_user_stats:
        print("No data found!")
        return
    
    print("\n" + "="*80)
    print("ANALYSIS: Progress and Completed Episodes")
    print("="*80)
    
    # 1. Users with progress values
    users_with_progress = [u for u in all_user_stats if u['progress_episodes'] > 0]
    users_with_completed = [u for u in all_user_stats if u['completed_episodes'] > 0]
    users_with_any_activity = [u for u in all_user_stats if u['total_episodes'] > 0]
    
    total_users = len(all_user_stats)
    
    # Count users with start date
    users_with_start_date = [u for u in all_user_stats if u['has_start_date']]
    users_without_start_date = [u for u in all_user_stats if not u['has_start_date']]
    
    print(f"\n1. OVERALL STATISTICS")
    print(f"   Total Users: {total_users}")
    print(f"   Users with Start Date: {len(users_with_start_date)} ({len(users_with_start_date)/total_users*100:.1f}%)")
    print(f"   Users without Start Date: {len(users_without_start_date)} ({len(users_without_start_date)/total_users*100:.1f}%)")
    print(f"   Users with Progress Episodes: {len(users_with_progress)} ({len(users_with_progress)/total_users*100:.1f}%)")
    print(f"   Users with Completed Episodes: {len(users_with_completed)} ({len(users_with_completed)/total_users*100:.1f}%)")
    print(f"   Users with Any Activity (Progress or Completed): {len(users_with_any_activity)} ({len(users_with_any_activity)/total_users*100:.1f}%)")
    
    # 2. Group by language
    print(f"\n2. BY LANGUAGE")
    lang_stats = defaultdict(lambda: {'total': 0, 'with_start_date': 0, 'total_progress': 0, 'users_with_progress': 0, 
                                      'total_completed': 0, 'users_with_completed': 0})
    
    for user in all_user_stats:
        lang = user['language']
        lang_stats[lang]['total'] += 1
        if user['has_start_date']:
            lang_stats[lang]['with_start_date'] += 1
        lang_stats[lang]['total_progress'] += user['progress_episodes']
        lang_stats[lang]['total_completed'] += user['completed_episodes']
        if user['progress_episodes'] > 0:
            lang_stats[lang]['users_with_progress'] += 1
        if user['completed_episodes'] > 0:
            lang_stats[lang]['users_with_completed'] += 1
    
    print("   Language          | Total Users | With Start Date | Total Progress | Users w/ Progress | Total Completed | Users w/ Completed")
    print("   " + "-"*130)
    for lang in sorted(lang_stats.keys()):
        stats = lang_stats[lang]
        print(f"   {lang:17s} | {stats['total']:11d} | {stats['with_start_date']:15d} | {stats['total_progress']:14d} | {stats['users_with_progress']:17d} | {stats['total_completed']:15d} | {stats['users_with_completed']:19d}")
    
    # 3. Distribution of progress episodes per user
    print(f"\n3. DISTRIBUTION: Progress Episodes per User")
    progress_dist = Counter(u['progress_episodes'] for u in all_user_stats)
    print("   Progress Episodes | Count of Users")
    print("   " + "-"*50)
    for episodes in sorted(progress_dist.keys()):
        count = progress_dist[episodes]
        print(f"   {episodes:3d} episodes        | {count:5d} users ({count/total_users*100:5.1f}%)")
    
    # 4. Distribution of completed episodes per user
    print(f"\n4. DISTRIBUTION: Completed Episodes per User")
    completed_dist = Counter(u['completed_episodes'] for u in all_user_stats)
    print("   Completed Episodes | Count of Users")
    print("   " + "-"*50)
    for episodes in sorted(completed_dist.keys()):
        count = completed_dist[episodes]
        print(f"   {episodes:3d} episodes         | {count:5d} users ({count/total_users*100:5.1f}%)")
    
    # 5. Combined analysis: Progress vs Completed
    print(f"\n5. COMBINED ANALYSIS: Progress vs Completed Episodes")
    print("   Users grouped by (Progress Episodes, Completed Episodes):")
    
    combined_groups = Counter((u['progress_episodes'], u['completed_episodes']) for u in all_user_stats)
    sorted_combined = sorted(combined_groups.items(), key=lambda x: x[1], reverse=True)
    
    print("   Progress | Completed | Count | Percentage")
    print("   " + "-"*60)
    for (prog, comp), count in sorted_combined[:20]:
        pct = (count / total_users) * 100
        print(f"   {prog:8d} | {comp:9d} | {count:5d} | {pct:6.2f}%")
    
    if len(sorted_combined) > 20:
        print(f"   ... and {len(sorted_combined) - 20} more combinations")
    
    # 6. Summary statistics
    progress_episodes = [u['progress_episodes'] for u in all_user_stats]
    completed_episodes = [u['completed_episodes'] for u in all_user_stats]
    
    def mean(lst):
        return sum(lst) / len(lst) if lst else 0
    
    def median(lst):
        sorted_lst = sorted(lst)
        n = len(sorted_lst)
        if n == 0:
            return 0
        if n % 2 == 0:
            return (sorted_lst[n//2 - 1] + sorted_lst[n//2]) / 2
        return sorted_lst[n//2]
    
    def std_dev(lst):
        if not lst:
            return 0
        m = mean(lst)
        variance = sum((x - m) ** 2 for x in lst) / len(lst)
        return variance ** 0.5
    
    print(f"\n6. SUMMARY STATISTICS")
    print(f"   Progress Episodes:")
    print(f"      Mean: {mean(progress_episodes):.2f}")
    print(f"      Median: {median(progress_episodes):.2f}")
    print(f"      Max: {max(progress_episodes) if progress_episodes else 0}")
    print(f"      Std Dev: {std_dev(progress_episodes):.2f}")
    
    print(f"\n   Completed Episodes:")
    print(f"      Mean: {mean(completed_episodes):.2f}")
    print(f"      Median: {median(completed_episodes):.2f}")
    print(f"      Max: {max(completed_episodes) if completed_episodes else 0}")
    print(f"      Std Dev: {std_dev(completed_episodes):.2f}")
    
    # 7. Users with only progress, only completed, or both
    print(f"\n7. USER CATEGORIES")
    only_progress = [u for u in all_user_stats if u['progress_episodes'] > 0 and u['completed_episodes'] == 0]
    only_completed = [u for u in all_user_stats if u['progress_episodes'] == 0 and u['completed_episodes'] > 0]
    both = [u for u in all_user_stats if u['progress_episodes'] > 0 and u['completed_episodes'] > 0]
    neither = [u for u in all_user_stats if u['progress_episodes'] == 0 and u['completed_episodes'] == 0]
    
    print(f"   Only Progress (no completed): {len(only_progress)} ({len(only_progress)/total_users*100:.1f}%)")
    print(f"   Only Completed (no progress): {len(only_completed)} ({len(only_completed)/total_users*100:.1f}%)")
    print(f"   Both Progress and Completed: {len(both)} ({len(both)/total_users*100:.1f}%)")
    print(f"   No Activity: {len(neither)} ({len(neither)/total_users*100:.1f}%)")
    
    # 7a. No Activity users with start date
    no_activity_with_start = [u for u in neither if u['has_start_date']]
    no_activity_without_start = [u for u in neither if not u['has_start_date']]
    
    print(f"\n7a. NO ACTIVITY USERS - START DATE ANALYSIS")
    print(f"   No Activity users: {len(neither)}")
    print(f"   No Activity users WITH start date: {len(no_activity_with_start)} ({len(no_activity_with_start)/len(neither)*100:.1f}% of no activity users)")
    print(f"   No Activity users WITHOUT start date: {len(no_activity_without_start)} ({len(no_activity_without_start)/len(neither)*100:.1f}% of no activity users)")
    
    # Breakdown by language for no activity with start date
    print(f"\n   No Activity with Start Date - By Language:")
    no_activity_by_lang = defaultdict(lambda: {'total': 0, 'with_start': 0, 'without_start': 0})
    for u in neither:
        lang = u['language']
        no_activity_by_lang[lang]['total'] += 1
        if u['has_start_date']:
            no_activity_by_lang[lang]['with_start'] += 1
        else:
            no_activity_by_lang[lang]['without_start'] += 1
    
    print("   Language          | Total No Activity | With Start Date | Without Start Date")
    print("   " + "-"*80)
    for lang in sorted(no_activity_by_lang.keys()):
        stats = no_activity_by_lang[lang]
        print(f"   {lang:17s} | {stats['total']:17d} | {stats['with_start']:15d} | {stats['without_start']:18d}")
    
    # 7b. Users WITH START DATE - Breakdown by Progress/Completed
    print(f"\n7b. USERS WITH START DATE - PROGRESS/COMPLETED BREAKDOWN")
    users_with_start = [u for u in all_user_stats if u['has_start_date']]
    
    # Categorize users with start date
    start_only_progress = [u for u in users_with_start if u['progress_episodes'] > 0 and u['completed_episodes'] == 0]
    start_only_completed = [u for u in users_with_start if u['progress_episodes'] == 0 and u['completed_episodes'] > 0]
    start_both = [u for u in users_with_start if u['progress_episodes'] > 0 and u['completed_episodes'] > 0]
    start_neither = [u for u in users_with_start if u['progress_episodes'] == 0 and u['completed_episodes'] == 0]
    
    print(f"   Total Users with Start Date: {len(users_with_start)}")
    print(f"   ──────────────────────────────────────────────────────────────")
    print(f"   Only In Progress (no completed): {len(start_only_progress)} ({len(start_only_progress)/len(users_with_start)*100:.1f}%)")
    print(f"   Only Completed (no in progress): {len(start_only_completed)} ({len(start_only_completed)/len(users_with_start)*100:.1f}%)")
    print(f"   Both In Progress AND Completed: {len(start_both)} ({len(start_both)/len(users_with_start)*100:.1f}%)")
    print(f"   Neither (no activity): {len(start_neither)} ({len(start_neither)/len(users_with_start)*100:.1f}%)")
    
    # Breakdown by language
    print(f"\n   By Language:")
    start_by_lang = defaultdict(lambda: {'total': 0, 'only_progress': 0, 'only_completed': 0, 'both': 0, 'neither': 0})
    
    for u in users_with_start:
        lang = u['language']
        start_by_lang[lang]['total'] += 1
        if u['progress_episodes'] > 0 and u['completed_episodes'] == 0:
            start_by_lang[lang]['only_progress'] += 1
        elif u['progress_episodes'] == 0 and u['completed_episodes'] > 0:
            start_by_lang[lang]['only_completed'] += 1
        elif u['progress_episodes'] > 0 and u['completed_episodes'] > 0:
            start_by_lang[lang]['both'] += 1
        else:
            start_by_lang[lang]['neither'] += 1
    
    print("   Language          | Total | Only Progress | Only Completed | Both | Neither")
    print("   " + "-"*90)
    for lang in sorted(start_by_lang.keys()):
        stats = start_by_lang[lang]
        print(f"   {lang:17s} | {stats['total']:5d} | {stats['only_progress']:13d} | {stats['only_completed']:15d} | {stats['both']:4d} | {stats['neither']:7d}")
    
    # 7c. Detailed breakdown of users with BOTH progress and completed
    print(f"\n7c. USERS WITH BOTH IN PROGRESS AND COMPLETED - DETAILED BREAKDOWN")
    print(f"   Total: {len(start_both)} users")
    
    # Distribution by number of progress episodes
    print(f"\n   Distribution by Number of Progress Episodes:")
    progress_dist_both = Counter(u['progress_episodes'] for u in start_both)
    print("   Progress Episodes | Count | Percentage")
    print("   " + "-"*50)
    for episodes in sorted(progress_dist_both.keys()):
        count = progress_dist_both[episodes]
        print(f"   {episodes:17d} | {count:5d} | {count/len(start_both)*100:6.2f}%")
    
    # Distribution by number of completed episodes
    print(f"\n   Distribution by Number of Completed Episodes:")
    completed_dist_both = Counter(u['completed_episodes'] for u in start_both)
    print("   Completed Episodes | Count | Percentage")
    print("   " + "-"*50)
    for episodes in sorted(completed_dist_both.keys()):
        count = completed_dist_both[episodes]
        print(f"   {episodes:18d} | {count:5d} | {count/len(start_both)*100:6.2f}%")
    
    # Combined distribution (progress, completed) pairs
    print(f"\n   Top 20 Combinations (Progress Episodes, Completed Episodes):")
    combined_both = Counter((u['progress_episodes'], u['completed_episodes']) for u in start_both)
    sorted_combined_both = sorted(combined_both.items(), key=lambda x: x[1], reverse=True)
    print("   Progress | Completed | Count | Percentage")
    print("   " + "-"*60)
    for (prog, comp), count in sorted_combined_both[:20]:
        pct = (count / len(start_both)) * 100
        print(f"   {prog:8d} | {comp:9d} | {count:5d} | {pct:6.2f}%")
    
    if len(sorted_combined_both) > 20:
        print(f"   ... and {len(sorted_combined_both) - 20} more combinations")
    
    # Summary statistics for "both" users
    progress_episodes_both = [u['progress_episodes'] for u in start_both]
    completed_episodes_both = [u['completed_episodes'] for u in start_both]
    
    print(f"\n   Summary Statistics:")
    print(f"   Progress Episodes:")
    print(f"      Mean: {mean(progress_episodes_both):.2f}")
    print(f"      Median: {median(progress_episodes_both):.2f}")
    print(f"      Min: {min(progress_episodes_both) if progress_episodes_both else 0}")
    print(f"      Max: {max(progress_episodes_both) if progress_episodes_both else 0}")
    print(f"   Completed Episodes:")
    print(f"      Mean: {mean(completed_episodes_both):.2f}")
    print(f"      Median: {median(completed_episodes_both):.2f}")
    print(f"      Min: {min(completed_episodes_both) if completed_episodes_both else 0}")
    print(f"      Max: {max(completed_episodes_both) if completed_episodes_both else 0}")
    
    # Breakdown by language
    print(f"\n   By Language:")
    both_by_lang = defaultdict(lambda: {'total': 0, 'progress_episodes': [], 'completed_episodes': []})
    for u in start_both:
        lang = u['language']
        both_by_lang[lang]['total'] += 1
        both_by_lang[lang]['progress_episodes'].append(u['progress_episodes'])
        both_by_lang[lang]['completed_episodes'].append(u['completed_episodes'])
    
    print("   Language          | Count | Avg Progress | Avg Completed | Total Progress | Total Completed")
    print("   " + "-"*90)
    for lang in sorted(both_by_lang.keys()):
        stats = both_by_lang[lang]
        avg_prog = mean(stats['progress_episodes'])
        avg_comp = mean(stats['completed_episodes'])
        total_prog = sum(stats['progress_episodes'])
        total_comp = sum(stats['completed_episodes'])
        print(f"   {lang:17s} | {stats['total']:5d} | {avg_prog:12.2f} | {avg_comp:13.2f} | {total_prog:14d} | {total_comp:15d}")
    
    # 8. Save detailed results to CSV
    output_file = 'progress_completed_analysis.csv'
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        if all_user_stats:
            writer = csv.DictWriter(f, fieldnames=all_user_stats[0].keys())
            writer.writeheader()
            writer.writerows(all_user_stats)
    print(f"\n8. DETAILED RESULTS")
    print(f"   Saved detailed user-level data to: {output_file}")
    
    # 9. Language-specific breakdown
    print(f"\n9. LANGUAGE-SPECIFIC BREAKDOWN")
    languages = set(u['language'] for u in all_user_stats)
    for lang in sorted(languages):
        lang_users = [u for u in all_user_stats if u['language'] == lang]
        lang_progress = [u for u in lang_users if u['progress_episodes'] > 0]
        lang_completed = [u for u in lang_users if u['completed_episodes'] > 0]
        lang_progress_episodes = [u['progress_episodes'] for u in lang_users]
        lang_completed_episodes = [u['completed_episodes'] for u in lang_users]
        
        print(f"\n   {lang} ({len(lang_users)} users):")
        print(f"      Users with Progress: {len(lang_progress)} ({len(lang_progress)/len(lang_users)*100:.1f}%)")
        print(f"      Users with Completed: {len(lang_completed)} ({len(lang_completed)/len(lang_users)*100:.1f}%)")
        print(f"      Avg Progress Episodes: {mean(lang_progress_episodes):.2f}")
        print(f"      Avg Completed Episodes: {mean(lang_completed_episodes):.2f}")
        print(f"      Total Progress Episodes: {sum(lang_progress_episodes)}")
        print(f"      Total Completed Episodes: {sum(lang_completed_episodes)}")
    
    print("\n" + "="*80)
    print("Analysis Complete!")
    print("="*80)

if __name__ == "__main__":
    main()
