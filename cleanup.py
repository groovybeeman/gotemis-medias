import json, os, urllib.request, urllib.error
from datetime import datetime, timezone, timedelta

token = os.environ["GITHUB_TOKEN"]
owner = "groovybeeman"
repo  = "gotemis-medias"
cutoff = datetime.now(timezone.utc) - timedelta(days=60)

def api_get(url):
    req = urllib.request.Request(url, headers={"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def api_delete(url, sha, msg):
    payload = json.dumps({"message": msg, "sha": sha}).encode()
    req = urllib.request.Request(url, data=payload, method="DELETE", headers={"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json", "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

try:
    files = api_get(f"https://api.github.com/repos/{owner}/{repo}/contents/events")
except urllib.error.HTTPError as e:
    if e.code == 404:
        print("Dossier events/ vide — rien à nettoyer.")
        exit(0)
    raise

deleted, kept = 0, 0
for f in files:
    if f["type"] != "file": continue
    commits = api_get(f"https://api.github.com/repos/{owner}/{repo}/commits?path={f['path']}&per_page=1")
    if not commits: continue
    date = datetime.fromisoformat(commits[0]["commit"]["committer"]["date"].replace("Z", "+00:00"))
    age = (datetime.now(timezone.utc) - date).days
    if date < cutoff:
        api_delete(f"https://api.github.com/repos/{owner}/{repo}/contents/{f['path']}", f["sha"], f"Cleanup: {f['name']}")
        print(f"SUPPRIMÉ: {f['name']} ({age}j)")
        deleted += 1
    else:
        print(f"Conservé: {f['name']} ({age}j)")
        kept += 1

print(f"\nRésultat: {deleted} supprimé(s), {kept} conservé(s)")
