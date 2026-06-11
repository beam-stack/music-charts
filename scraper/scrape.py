import requests
import json
import re
import time
from datetime import datetime, timezone, timedelta

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
    "Referer": "https://y.qq.com/",
}

def fetch_qq_chart(toplist_id, chart_name, platform="QQ音樂"):
    url = f"https://c.y.qq.com/node/pc/close/page/toplist.js?g_tk=5381&uin=0&format=json&inCharset=utf-8&outCharset=utf-8&notice=0&platform=h5&needNewCode=1&tpl=3&page=detail&type=top&topid={toplist_id}&_=1"
    songs = []
    try:
        r = requests.get(url, headers={**HEADERS, "Referer": "https://y.qq.com/"}, timeout=15)
        data = r.json()
        song_list = data.get("songlist", [])
        for i, item in enumerate(song_list[:10]):
            song = item.get("data", item)
            name = song.get("songname") or song.get("name", "")
            artists = song.get("singer", [])
            artist = "/".join(a.get("name", "") for a in artists) if isinstance(artists, list) else str(artists)
            songs.append({"rank": i+1, "name": name, "artist": artist, "trend": "flat"})
    except Exception as e:
        print(f"[QQ] {chart_name} error: {e}")

    if not songs:
        try:
            api_url = f"https://c.y.qq.com/v8/fcg-bin/fcg_v8_toplist_cp.fcg?g_tk=5381&uin=0&format=json&inCharset=utf-8&outCharset=utf-8&notice=0&platform=h5&needNewCode=1&tpl=3&page=detail&type=top&topid={toplist_id}&_=1"
            r = requests.get(api_url, headers={**HEADERS, "Referer": "https://y.qq.com/"}, timeout=15)
            data = r.json()
            song_list = data.get("songlist", [])
            for i, item in enumerate(song_list[:10]):
                song = item.get("data", item)
                name = song.get("songname") or song.get("name", "")
                artists = song.get("singer", [])
                artist = "/".join(a.get("name","") for a in artists) if isinstance(artists, list) else str(artists)
                songs.append({"rank": i+1, "name": name, "artist": artist, "trend": "flat"})
        except Exception as e:
            print(f"[QQ fallback] {chart_name} error: {e}")

    return {"platform": "QQ音樂", "badge": "badge-qq", "name": chart_name, "freq": "每日更新", "songs": songs}


def fetch_netease_chart(list_id, chart_name):
    url = f"https://music.163.com/api/playlist/detail?id={list_id}"
    songs = []
    try:
        r = requests.get(url, headers={**HEADERS, "Referer": "https://music.163.com/"}, timeout=15)
        data = r.json()
        tracks = data.get("result", {}).get("tracks", [])
        for i, t in enumerate(tracks[:10]):
            name = t.get("name", "")
            artists = t.get("artists", [])
            artist = "/".join(a.get("name","") for a in artists)
            songs.append({"rank": i+1, "name": name, "artist": artist, "trend": "flat"})
    except Exception as e:
        print(f"[NetEase] {chart_name} error: {e}")
    return {"platform": "網易雲", "badge": "badge-wangyiyun", "name": chart_name, "freq": "每天", "songs": songs}


def fetch_kugou_chart(rank_id, chart_name):
    url = f"https://www.kugou.com/yy/rank/home/1-{rank_id}.html?from=rank"
    songs = []
    try:
        r = requests.get(url, headers={**HEADERS, "Referer": "https://www.kugou.com/"}, timeout=15)
        r.encoding = "utf-8"
        html = r.text
        pattern = r'<a[^>]+class="[^"]*pc_temp_songname[^"]*"[^>]*title="([^"]+)"'
        matches = re.findall(pattern, html)
        if not matches:
            pattern2 = r'<li[^>]*>\s*<span[^>]*>\d+</span>.*?<a[^>]*>([^<]+)</a>.*?<span[^>]*class="[^"]*singer[^"]*"[^>]*>([^<]*)</span>'
            matches2 = re.findall(pattern2, html, re.DOTALL)
            for i, (name, artist) in enumerate(matches2[:10]):
                songs.append({"rank": i+1, "name": name.strip(), "artist": artist.strip(), "trend": "flat"})
        else:
            for i, name in enumerate(matches[:10]):
                songs.append({"rank": i+1, "name": name.strip(), "artist": "", "trend": "flat"})
    except Exception as e:
        print(f"[KuGou] {chart_name} error: {e}")

    if not songs:
        try:
            api_url = f"http://mobilecdnbj.kugou.com/api/v3/rank/song?rankid={rank_id}&pagesize=10&page=1"
            r2 = requests.get(api_url, headers=HEADERS, timeout=15)
            data = r2.json()
            for i, item in enumerate(data.get("data", {}).get("info", [])[:10]):
                name = item.get("filename", "").split(" - ")[-1] if " - " in item.get("filename","") else item.get("filename","")
                artist = item.get("filename", "").split(" - ")[0] if " - " in item.get("filename","") else ""
                songs.append({"rank": i+1, "name": name.strip(), "artist": artist.strip(), "trend": "flat"})
        except Exception as e2:
            print(f"[KuGou API] {chart_name} error: {e2}")

    return {"platform": "酷狗", "badge": "badge-kugou", "name": chart_name, "freq": "每天", "songs": songs}


def build_cross_chart(charts):
    song_map = {}
    for chart in charts:
        for song in chart["songs"]:
            key = song["name"]
            if key not in song_map:
                song_map[key] = {"name": song["name"], "artist": song["artist"], "tags": [], "count": 0}
            label = f"{chart['platform']}#{song['rank']}"
            c = "tag-green" if chart["platform"]=="網易雲" else \
                "tag-blue" if chart["platform"]=="QQ音樂" else \
                "tag-orange" if chart["platform"]=="酷狗" else \
                "tag-red"
            song_map[key]["tags"].append({"label": label, "c": c})
            song_map[key]["count"] += 1
    cross = [v for v in song_map.values() if v["count"] >= 2]
    cross.sort(key=lambda x: -x["count"])
    return cross[:10]


def main():
    tz = timezone(timedelta(hours=8))
    now = datetime.now(tz).strftime("%Y-%m-%d %H:%M")

    charts = []

    print("Fetching QQ charts...")
    charts.append(fetch_qq_chart(4,  "熱歌榜"))
    time.sleep(1)
    charts.append(fetch_qq_chart(26, "飆升榜"))
    time.sleep(1)
    charts.append(fetch_qq_chart(60, "流行指數榜"))
    time.sleep(1)
    charts.append(fetch_qq_chart(62, "新歌榜"))
    time.sleep(1)

    print("Fetching NetEase charts...")
    charts.append(fetch_netease_chart(19723756, "熱歌榜"))
    time.sleep(1)
    charts.append(fetch_netease_chart(3779629,  "飆升榜"))
    time.sleep(1)
    charts.append(fetch_netease_chart(3778678,  "新歌榜"))
    time.sleep(1)

    print("Fetching KuGou charts...")
    charts.append(fetch_kugou_chart(6666,  "酷狗TOP500"))
    time.sleep(1)
    charts.append(fetch_kugou_chart(8888,  "飆升榜"))
    time.sleep(1)
    charts.append(fetch_kugou_chart(52144, "新歌榜"))
    time.sleep(1)
    charts.append(fetch_kugou_chart(52767, "熱歌榜"))

    cross = build_cross_chart(charts)

    output = {"updated": now, "charts": charts, "cross": cross}

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Done. {len(charts)} charts, {len(cross)} cross-chart songs. Updated: {now}")


if __name__ == "__main__":
    main()
