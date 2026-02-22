"""Users backup module."""

import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from .logger import log, print_lock

MAX_WORKERS_TEAMS = 20

processed_count = {'users': 0}
failed_count = {'users': 0}

def process_user(client, user_data, idx, total, backup_dir):
    """處理單個使用者的備份"""
    user_id = user_data.get('id')
    user_name = user_data.get('name', f'User_{user_id}').replace("/", "_").strip()
    
    user_detail = client.fetch_api(f"/api/v1/users/{user_id}")
    if not user_detail:
        with print_lock:
            failed_count['users'] += 1
        return None
    
    solves_data = client.fetch_api(f"/api/v1/users/{user_id}/solves")
    if not solves_data:
        log('user', '!', f"{user_name} (ID:{user_id}) 無解題紀錄，跳過")
        with print_lock:
            failed_count['users'] += 1
        return None
    
    solves_list = []
    for solve in solves_data:
        solves_list.append({
            'challenge': solve.get('challenge', {}).get('name', 'Unknown'),
            'challenge_id': solve.get('challenge_id'),
            'category': solve.get('challenge', {}).get('category', 'N/A'),
            'value': solve.get('challenge', {}).get('value', 0),
            'date': solve.get('date', 'N/A')
        })
    
    awards_data = client.fetch_api(f"/api/v1/users/{user_id}/awards")
    awards_list = []
    if awards_data:
        for award in awards_data:
            awards_list.append({
                'name': award.get('name', 'Unknown'),
                'value': award.get('value', 0),
                'date': award.get('date', 'N/A')
            })
    
    current_count = 0
    with print_lock:
        processed_count['users'] += 1
        current_count = processed_count['users']
    
    if current_count % 10 == 0:
        log('user', '*', f"進度: {current_count}/{total} 位使用者")
    
    return {
        'id': user_id,
        'name': user_detail.get('name', user_name),
        'rank': user_detail.get('place', 'N/A'),
        'score': user_detail.get('score', 0),
        'bracket': user_detail.get('bracket', 'N/A'),
        'country': user_detail.get('country', 'N/A'),
        'affiliation': user_detail.get('affiliation', 'N/A'),
        'website': user_detail.get('website', 'N/A'),
        'team_id': user_detail.get('team_id', None),
        'team_name': user_detail.get('team', None),
        'solves': solves_list,
        'awards': awards_list,
        'fields': user_detail.get('fields', [])
    }

def backup_users(client, backup_dir):
    """備份所有使用者資訊"""
    log('user', '*', "開始備份使用者資訊")
    
    log('user', '*', "正在獲取使用者列表...")
    users_data = client.fetch_all_pages("/api/v1/users")
    if not users_data:
        log('user', '-', "無法取得使用者列表")
        return
    
    log('user', '+', f"找到 {len(users_data)} 位使用者")
    log('user', '*', f"使用 {MAX_WORKERS_TEAMS} 個並行線程處理")
    
    users_dir = f"{backup_dir}/Users"
    os.makedirs(users_dir, exist_ok=True)
    
    all_users_summary = []
    processed_count['users'] = 0
    failed_count['users'] = 0
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS_TEAMS) as executor:
        futures = {
            executor.submit(process_user, client, user, idx, len(users_data), backup_dir): user
            for idx, user in enumerate(users_data, 1)
        }
        
        for future in as_completed(futures):
            user_info = future.result()
            if user_info:
                user_name = user_info['name'].replace("/", "_").strip()
                user_id = user_info['id']
                user_folder = f"{users_dir}/{user_name}_{user_id}"
                os.makedirs(user_folder, exist_ok=True)
                
                with open(f"{user_folder}/user_info.json", "w", encoding="utf-8") as f:
                    json.dump(user_info, f, indent=2, ensure_ascii=False)
                
                # 建立 Markdown
                md_content = f"""# {user_info['name']}

## 基本資訊

- **使用者 ID:** {user_info['id']}
- **排名:** #{user_info['rank']}
- **總分:** {user_info['score']}
- **隊伍:** {user_info['team_name']} (ID: {user_info['team_id']})
- **國家:** {user_info['country']}
- **所屬單位:** {user_info['affiliation']}

"""
                
                if user_info.get('fields'):
                    md_content += "## 個人資料\n\n"
                    for field in user_info['fields']:
                        md_content += f"- **{field.get('name', 'Unknown')}:** {field.get('value', 'N/A')}\n"
                    md_content += "\n"
                
                md_content += f"## 解題紀錄 ({len(user_info['solves'])} 題)\n\n"
                if user_info['solves']:
                    md_content += "| 題目 | 分類 | 分數 | 時間 |\n"
                    md_content += "|------|------|-----:|------|\n"
                    for solve in user_info['solves']:
                        md_content += f"| {solve['challenge']} | {solve['category']} | {solve['value']} | {solve['date']} |\n"
                
                with open(f"{user_folder}/README.md", "w", encoding="utf-8") as f:
                    f.write(md_content)
                
                all_users_summary.append(user_info)
    
    log('user', '+', f"使用者備份完成: {len(all_users_summary)} 位使用者")

    # Generate Users Index README.md
    try:
        log('user', '*', "正在生成 Users/README.md 索引...")
        sorted_users = sorted(all_users_summary, key=lambda x: x['name'].lower())
        
        readme_content = "# Users Index\n\n"
        readme_content += f"總計 {len(sorted_users)} 位使用者\n\n"
        readme_content += "| 使用者名稱 | ID | 隊伍 | 分數 |\n"
        readme_content += "|------------|---:|------|-----:|\n"
        
        for user in sorted_users:
            safe_name = user['name'].replace("/", "_").strip()
            display_name = user['name'].replace("|", "\\|")
            folder_name = f"{safe_name}_{user['id']}"
            
            from urllib.parse import quote
            link = quote(folder_name)
            
            team_display = user.get('team_name', 'N/A')
            if team_display:
                team_display = team_display.replace("|", "\\|")
            
            readme_content += f"| [{display_name}](./{link}/) | {user['id']} | {team_display} | {user['score']} |\n"
            
        with open(f"{users_dir}/README.md", "w", encoding="utf-8") as f:
            f.write(readme_content)
        log('user', '+', "Users/README.md 生成完成")

    except Exception as e:
        log('user', '!', f"生成 Users/README.md 失敗: {str(e)}")

    if failed_count['users'] > 0:
        log('user', '!', f"跳過 {failed_count['users']} 位使用者（無解題紀錄或無權限）")
