"""Challenge backup module."""

import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from .logger import log, print_lock

MAX_WORKERS_CHALLENGES = 10
MAX_WORKERS_FILES = 5
CHUNK_SIZE = 8192
PROGRESS_THRESHOLD_MB = 5

def download_file(client, f_url, f_name, save_path):
    """下載單個檔案（支援大檔案串流下載）"""
    try:
        response = client.session.get(f_url, timeout=client.file_timeout, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(f"{save_path}/{f_name}", "wb") as f_out:
            if total_size > 0:
                downloaded = 0
                last_progress = 0
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:
                        f_out.write(chunk)
                        downloaded += len(chunk)
                        if downloaded - last_progress >= PROGRESS_THRESHOLD_MB * 1024 * 1024:
                            mb_downloaded = downloaded / (1024 * 1024)
                            log('file', '*', f"{f_name}: {mb_downloaded:.1f} MB")
                            last_progress = downloaded
            else:
                f_out.write(response.content)
        
        if total_size > 1024 * 1024:
            mb_size = total_size / (1024 * 1024)
            log('file', '+', f"{f_name} ({mb_size:.1f} MB)")
        return True
    except Exception as e:
        log('file', '-', f"{f_name}: {e}")
        return False

def process_challenge(client, chal_data, idx, total, backup_dir):
    """處理單個題目的備份"""
    try:
        detail = client.session.get(
            f"{client.base_url}/api/v1/challenges/{chal_data['id']}", 
            timeout=15
        ).json()['data']
        
        name = detail['name'].replace("/", "_").strip()
        category = detail.get('category', 'Uncategorized').replace("/", "_").strip()
        
        log('chal', '*', f"{name} | {category} | {detail.get('value', 'N/A')} pts")
        
        path = f"{backup_dir}/Challenges/{category}/{name}"
        os.makedirs(path, exist_ok=True)
        
        # 獲取解題紀錄
        solves_list = []
        try:
            solves_url = f"{client.base_url}/api/v1/challenges/{chal_data['id']}/solves"
            solves_r = client.session.get(solves_url, timeout=15)
            if solves_r.status_code == 200:
                solves_data = solves_r.json().get('data', [])
                for solve in solves_data:
                    solver_name = solve.get('name', solve.get('user', 'Unknown'))
                    solve_time = solve.get('date', 'N/A')
                    solves_list.append((solver_name, solve_time))
        except Exception as e:
            log('chal', '!', f"{name} 無法取得解題紀錄: {e}")
        
        # 存下題目說明
        desc_content = f"""# {detail['name']}

**Category:** {detail.get('category', 'N/A')}  
**Points:** {detail.get('value', 'N/A')}  
**Solves:** {detail.get('solves', 'N/A')}

## Description

{detail.get('description', 'No description')}

## Solves

"""
        
        if solves_list:
            desc_content += "| Solver | Time |\n"
            desc_content += "|--------|------|\n"
            for solver_name, solve_time in solves_list:
                desc_content += f"| {solver_name} | {solve_time} |\n"
        else:
            desc_content += "No solves yet.\n"
        
        # 附件清單
        desc_content += "\n## Files\n\n"
        if 'files' in detail and detail['files']:
            for f_link in detail['files']:
                f_name = f_link.split("/")[-1].split("?")[0]
                desc_content += f"- `{f_name}`\n"
        else:
            desc_content += "No files.\n"
        
        with open(f"{path}/description.md", "w", encoding="utf-8") as f:
            f.write(desc_content)
        
        # 下載附件
        files_to_download = []
        if 'files' in detail and detail['files']:
            log('chal', '*', f"{name} 發現 {len(detail['files'])} 個附件")
            
            for f_link in detail['files']:
                f_url = f"{client.base_url}{f_link.split('?')[0]}"
                f_name = f_url.split("/")[-1]
                files_to_download.append((f_url, f_name, path))
            
            if files_to_download:
                with ThreadPoolExecutor(max_workers=min(MAX_WORKERS_FILES, len(files_to_download))) as file_executor:
                    file_futures = [
                        file_executor.submit(download_file, client, f_url, f_name, save_path)
                        for f_url, f_name, save_path in files_to_download
                    ]
                    for future in as_completed(file_futures):
                        future.result()
        
        log('chal', '+', f"{name} 備份完成")
        
        return {
            'name': detail['name'],
            'folder_name': name,
            'category': category,
            'value': detail.get('value', 0),
            'solves': len(solves_list),
            'author': detail.get('author', 'Unknown')
        }
        
    except Exception as e:
        log('chal', '-', f"ID {chal_data.get('id')} 處理失敗: {e}")
        return None

def backup_challenges(client, backup_dir):
    """備份所有題目"""
    log('chal', '*', "開始備份題目")
    
    try:
        r = client.session.get(f"{client.base_url}/api/v1/challenges", timeout=15)
        if r.status_code != 200:
            log('chal', '-', f"無法獲取題目列表，狀態碼：{r.status_code}")
            return []
    except Exception as e:
        log('chal', '-', f"無法連接到 API: {e}")
        return []

    challenges = r.json()['data']
    log('chal', '+', f"找到 {len(challenges)} 個題目")
    log('chal', '*', f"使用 {MAX_WORKERS_CHALLENGES} 個並行線程")
    
    success_list = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS_CHALLENGES) as executor:
        futures = {
            executor.submit(process_challenge, client, chal, idx, len(challenges), backup_dir): chal
            for idx, chal in enumerate(challenges, 1)
        }
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                success_list.append(result)
    
    log('chal', '+', f"題目備份完成！成功 {len(success_list)}/{len(challenges)} 個")
    
    # 生成 README
    generate_challenges_readme(success_list, backup_dir)
    
    return success_list

def generate_challenges_readme(challenges_list, backup_dir):
    """生成 Challenges README.md"""
    # 按分類分組
    categories = {}
    for chal in challenges_list:
        cat = chal['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(chal)
    
    # 每個分類內按分數排序
    for cat in categories:
        categories[cat].sort(key=lambda x: x['value'])
    
    # 生成 Markdown
    md_content = "# Challenges\n\n"
    md_content += f"總計 {len(challenges_list)} 個題目，{len(categories)} 個分類\n\n"
    
    for cat in sorted(categories.keys()):
        md_content += f"## {cat}\n\n"
        md_content += "| 題目 | 作者 | 分數 | 解題人數 |\n"
        md_content += "|------|------|-----:|---------:|\n"
        
        for chal in categories[cat]:
            display_name = chal['name'].replace("|", "\\|")
            from urllib.parse import quote
            safe_cat = quote(chal['category'])
            safe_name = quote(chal['folder_name'])
            
            md_content += f"| [{display_name}](./{safe_cat}/{safe_name}/) | {chal['author']} | {chal['value']} | {chal['solves']} |\n"
        
        md_content += "\n"
    
    readme_path = f"{backup_dir}/Challenges/README.md"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    log('chal', '+', "Challenges README.md 已生成")
