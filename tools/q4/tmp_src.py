# 临时：把上一轮核对资料时存进“检查结果”的原文清空（原文有版权，不公开保留）。完成后连同工作流一起删除。
import os, requests
api = f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}"
hd = {'Authorization': 'Bearer ' + os.environ['GH_TOKEN'], 'Accept': 'application/vnd.github+json'}
for sha in ('4812f4b6d472202f22c9a125dea7db3087be4e93', 'cb904d7d2253db3f9a83eeb949ead96cd18d2bd5'):
    runs = requests.get(f'{api}/commits/{sha}/check-runs?per_page=100', headers=hd).json().get('check_runs', [])
    for r in runs:
        if r['name'].startswith('src:'):
            x = requests.patch(f"{api}/check-runs/{r['id']}", headers=hd, json={'name': 'src-cleared', 'output': {'title': 'cleared', 'summary': '已清空', 'text': ''}})
            print(r['name'], x.status_code, flush=True)
