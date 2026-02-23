"""Teams backup module."""

import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from .logger import log, print_lock

MAX_WORKERS_TEAMS = 20

processed_count = {"teams": 0}
failed_count = {"teams": 0}


def process_team(client, team_data, idx, total, backup_dir):
    """處理單個隊伍的備份"""
    team_id = team_data.get("id")
    team_name = team_data.get("name", f"Team_{team_id}").replace("/", "_").strip()

    team_detail = client.fetch_api(f"/api/v1/teams/{team_id}")
    if not team_detail:
        with print_lock:
            failed_count["teams"] += 1
        return None

    solves_data = client.fetch_api(f"/api/v1/teams/{team_id}/solves")
    if not solves_data:
        log("team", "!", f"{team_name} (ID:{team_id}) 無解題紀錄，跳過")
        with print_lock:
            failed_count["teams"] += 1
        return None

    solves_list = []
    for solve in solves_data:
        solves_list.append(
            {
                "challenge": solve.get("challenge", {}).get("name", "Unknown"),
                "challenge_id": solve.get("challenge_id"),
                "date": solve.get("date", "N/A"),
                "user": solve.get("user", "Unknown"),
            }
        )

    # 取得隊伍成員
    member_ids = team_detail.get("members", [])
    members_list = []
    if member_ids:
        for member_id in member_ids:
            member_info = client.fetch_api(f"/api/v1/users/{member_id}")
            if member_info:
                members_list.append(
                    {
                        "name": member_info.get("name", "Unknown"),
                        "id": member_id,
                        "score": member_info.get("score", 0),
                    }
                )

    # 取得獎項
    awards_data = client.fetch_api(f"/api/v1/teams/{team_id}/awards")
    awards_list = []
    if awards_data:
        for award in awards_data:
            awards_list.append(
                {
                    "name": award.get("name", "Unknown"),
                    "value": award.get("value", 0),
                    "date": award.get("date", "N/A"),
                }
            )

    current_count = 0
    with print_lock:
        processed_count["teams"] += 1
        current_count = processed_count["teams"]

    if current_count % 10 == 0:
        log("team", "*", f"進度: {current_count}/{total} 隊伍")

    return {
        "id": team_id,
        "name": team_detail.get("name", team_name),
        "rank": team_detail.get("place", "N/A"),
        "score": team_detail.get("score", 0),
        "bracket": team_detail.get("bracket", "N/A"),
        "country": team_detail.get("country", "N/A"),
        "affiliation": team_detail.get("affiliation", "N/A"),
        "website": team_detail.get("website", "N/A"),
        "members": members_list,
        "solves": solves_list,
        "awards": awards_list,
        "fields": team_detail.get("fields", []),
    }


def backup_teams(client, backup_dir):
    """備份所有隊伍資訊"""
    log("team", "*", "開始備份隊伍資訊")

    log("team", "*", "正在獲取隊伍列表...")
    teams_data = client.fetch_all_pages("/api/v1/teams")
    if not teams_data:
        log("team", "-", "無法取得隊伍列表")
        return

    log("team", "+", f"找到 {len(teams_data)} 個隊伍")
    log("team", "*", f"使用 {MAX_WORKERS_TEAMS} 個並行線程處理")

    teams_dir = f"{backup_dir}/Teams"
    os.makedirs(teams_dir, exist_ok=True)

    all_teams_summary = []
    processed_count["teams"] = 0
    failed_count["teams"] = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS_TEAMS) as executor:
        futures = {
            executor.submit(process_team, client, team, idx, len(teams_data), backup_dir): team
            for idx, team in enumerate(teams_data, 1)
        }

        for future in as_completed(futures):
            team_info = future.result()
            if team_info:
                team_name = team_info["name"].replace("/", "_").strip()
                team_id = team_info["id"]
                team_folder = f"{teams_dir}/{team_name}_{team_id}"
                os.makedirs(team_folder, exist_ok=True)

                with open(f"{team_folder}/team_info.json", "w", encoding="utf-8") as f:
                    json.dump(team_info, f, indent=2, ensure_ascii=False)

                # 建立 Markdown
                md_content = f"""# {team_info['name']}

## 基本資訊

- **隊伍 ID:** {team_info['id']}
- **排名:** #{team_info['rank']}
- **總分:** {team_info['score']}
- **國家:** {team_info['country']}
- **所屬單位:** {team_info['affiliation']}

## 成員列表 ({len(team_info['members'])} 人)

"""
                if team_info["members"]:
                    md_content += "| 姓名 | ID | 分數 |\n"
                    md_content += "|------|----:|-----:|\n"
                    for member in team_info["members"]:
                        md_content += f"| {member['name']} | {member['id']} | {member['score']} |\n"
                else:
                    md_content += "無成員資料\n"

                md_content += f"\n## 解題紀錄 ({len(team_info['solves'])} 題)\n\n"
                if team_info["solves"]:
                    md_content += "| 題目 | 解題者 | 時間 |\n"
                    md_content += "|------|--------|------|\n"
                    for solve in team_info["solves"]:
                        md_content += (
                            f"| {solve['challenge']} | {solve['user']} | {solve['date']} |\n"
                        )

                with open(f"{team_folder}/README.md", "w", encoding="utf-8") as f:
                    f.write(md_content)

                all_teams_summary.append(team_info)

    log("team", "+", f"隊伍備份完成: {len(all_teams_summary)} 個隊伍")

    # Generate Teams Index README.md
    try:
        log("team", "*", "正在生成 Teams/README.md 索引...")
        sorted_teams = sorted(all_teams_summary, key=lambda x: x["name"].lower())

        readme_content = "# Teams Index\n\n"
        readme_content += f"總計 {len(sorted_teams)} 個隊伍\n\n"
        readme_content += "| 隊伍名稱 | ID | 成員數 | 分數 |\n"
        readme_content += "|----------|---:|-------:|-----:|\n"

        for team in sorted_teams:
            safe_name = team["name"].replace("/", "_").strip()
            # Escape pipes in team name for markdown table
            display_name = team["name"].replace("|", "\\|")
            folder_name = f"{safe_name}_{team['id']}"
            # Ensure proper URL encoding for the link if needed, but for local files consistent naming is key
            # Using urllib.parse.quote for the link part is safer for special chars
            from urllib.parse import quote

            link = quote(folder_name)

            member_count = len(team.get("members", []))
            readme_content += f"| [{display_name}](./{link}/) | {team['id']} | {member_count} | {team['score']} |\n"

        with open(f"{teams_dir}/README.md", "w", encoding="utf-8") as f:
            f.write(readme_content)
        log("team", "+", "Teams/README.md 生成完成")

    except Exception as e:
        log("team", "!", f"生成 Teams/README.md 失敗: {str(e)}")

    if failed_count["teams"] > 0:
        log("team", "!", f"跳過 {failed_count['teams']} 個隊伍（無解題紀錄或無權限）")
