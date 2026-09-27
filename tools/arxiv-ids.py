import re, sys, urllib.request
UA={"User-Agent":"omarchy-english-toolkit/1.0"}
ids=sys.argv[1]
url=f"https://export.arxiv.org/api/query?id_list={ids}&max_results=60"
x=urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=90).read().decode("utf-8","replace")
found={}
for e in re.findall(r"<entry>(.*?)</entry>",x,re.S):
    a=re.search(r"<id>http[s]?://arxiv\.org/abs/([^<]+)</id>",e); t=re.search(r"<title>(.*?)</title>",e,re.S)
    if a and t:
        base=a.group(1).split("v")[0]
        found[base]=(" ".join(t.group(1).split()), " ".join(re.search(r"<summary>(.*?)</summary>",e,re.S).group(1).split()) if re.search(r"<summary>(.*?)</summary>",e,re.S) else "")
for k,v in found.items():
    print(f"{k:12} {v[0][:70]}")
    print(f"             {v[1][:100]}")
