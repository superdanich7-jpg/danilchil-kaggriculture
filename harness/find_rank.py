"""Find our rank on the kaggriculture leaderboard (full pagination via kagglesdk)."""
import sys
from kaggle.api.kaggle_api_extended import KaggleApi
from kagglesdk import KaggleClient
from kagglesdk.competitions.types.competition_api_service import (
    ApiListLeaderboardSubmissionsRequest)

sys.stdout.reconfigure(encoding="utf-8")
api = KaggleApi()
api.authenticate()

client = KaggleClient()
client.authenticate()

rank = 0
rows_all = []
page_token = None
for page in range(60):
    req = ApiListLeaderboardSubmissionsRequest()
    req.competition_name = "kaggriculture"
    req.page_size = 100
    req.page_token = page_token
    resp = client.competitions.competition_client.list_leaderboard_submissions(req)
    subs = resp.submissions
    if not subs:
        break
    for row in subs:
        rank += 1
        name = str(getattr(row, "team_name", ""))
        score = str(getattr(row, "score", None))
        rows_all.append((rank, name, score))
        if "dan" in name.lower() or "chil" in name.lower():
            print(f"CANDIDATE: rank {rank} {name} {score}")
    page_token = resp.next_page_token
    if not page_token:
        break
print("total rows:", len(rows_all))
for r, n, s in rows_all[89:105]:
    print(f"  rank {r}: {n} {s}")

