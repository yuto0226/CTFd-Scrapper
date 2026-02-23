"""Scoreboard backup module."""

import json
import os

from .logger import log


def backup_scoreboard(client, backup_dir):
    """備份完整 Scoreboard"""
    log("scoreboard", "*", "開始備份 Scoreboard")

    scoreboard_dir = f"{backup_dir}/Scoreboard"
    os.makedirs(scoreboard_dir, exist_ok=True)

    log("scoreboard", "*", "正在獲取 Scoreboard...")
    scoreboard_response = client.session.get(f"{client.base_url}/api/v1/scoreboard", timeout=15)

    if scoreboard_response.status_code == 200:
        scoreboard_data = scoreboard_response.json().get("data", [])

        # 儲存完整 JSON
        with open(f"{scoreboard_dir}/team_ranking.json", "w", encoding="utf-8") as f:
            json.dump(scoreboard_data, f, indent=2, ensure_ascii=False)

        log("scoreboard", "+", f"找到 {len(scoreboard_data)} 個隊伍")

        # 建立 Markdown 排行榜
        md_content = "# Team Ranking\n\n"
        md_content += f"總計 {len(scoreboard_data)} 個隊伍\n\n"
        md_content += "| 排名 | 隊伍名稱 | 分數 | 成員數 | 成員列表 |\n"
        md_content += "|-----:|----------|-----:|-------:|----------|\n"

        for team in scoreboard_data:
            pos = team.get("pos", "N/A")
            name = team.get("name", "Unknown")
            score = team.get("score", 0)
            members = team.get("members", [])
            member_count = len(members)

            member_names = ", ".join([m.get("name", "Unknown") for m in members[:5]])
            if len(members) > 5:
                member_names += f" ... ({len(members)-5} more)"

            md_content += f"| {pos} | {name} | {score} | {member_count} | {member_names} |\n"

        with open(f"{scoreboard_dir}/TEAM_RANKING.md", "w", encoding="utf-8") as f:
            f.write(md_content)

        log("scoreboard", "+", "完整 Scoreboard 已儲存")

        # 建立詳細的成員排行榜
        all_members = []
        for team in scoreboard_data:
            team_name = team.get("name", "Unknown")
            for member in team.get("members", []):
                all_members.append(
                    {
                        "name": member.get("name", "Unknown"),
                        "id": member.get("id"),
                        "score": member.get("score", 0),
                        "team": team_name,
                    }
                )

        all_members.sort(key=lambda x: -x["score"])

        # 建立成員排行榜
        members_md = "# User Ranking\n\n"
        members_md += f"總計 {len(all_members)} 位成員\n\n"
        members_md += "| 排名 | 成員名稱 | 分數 | 隊伍 |\n"
        members_md += "|-----:|----------|-----:|------|\n"

        for idx, member in enumerate(all_members, 1):
            members_md += f"| {idx} | {member['name']} | {member['score']} | {member['team']} |\n"

        with open(f"{scoreboard_dir}/USER_RANKING.md", "w", encoding="utf-8") as f:
            f.write(members_md)

        with open(f"{scoreboard_dir}/user_ranking.json", "w", encoding="utf-8") as f:
            json.dump(all_members, f, indent=2, ensure_ascii=False)

        log("scoreboard", "+", f"成員排行榜已儲存 ({len(all_members)} 位成員)")
    else:
        log("scoreboard", "-", f"無法獲取 Scoreboard (狀態碼: {scoreboard_response.status_code})")
