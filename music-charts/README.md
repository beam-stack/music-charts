# 🎵 音樂榜單監控

每日自動抓取 QQ音樂、網易雲音樂、酷狗 最新榜單，部署於 GitHub Pages。

## 一次性設定（約 5 分鐘）

### 1. 建立 GitHub Repo

1. 登入 [github.com](https://github.com) → 右上角 **+** → **New repository**
2. Repository name 填 `music-charts`（或任何名稱）
3. 選 **Public**（GitHub Pages 免費版需要公開）
4. 按 **Create repository**

### 2. 上傳所有檔案

把這個資料夾的所有檔案上傳到 repo：

```
music-charts/
├── index.html
├── data.json
├── scraper/
│   └── scrape.py
└── .github/
    └── workflows/
        └── update.yml
```

> **最簡單的方式**：在 GitHub repo 頁面點 **uploading an existing file**，把全部檔案拖進去。
> 注意：`.github/workflows/update.yml` 需要先在本機建立資料夾結構再上傳，或用 GitHub 網頁介面逐一建立。

### 3. 開啟 GitHub Pages

1. 進入 repo → **Settings** → 左側 **Pages**
2. Source 選 **Deploy from a branch**
3. Branch 選 **main**，資料夾選 **/ (root)**
4. 按 **Save**

約 1 分鐘後，網址會出現：`https://你的帳號.github.io/music-charts/`

### 4. 手動執行一次爬蟲（取得即時資料）

1. 進入 repo → **Actions** 頁籤
2. 左側選 **Daily Chart Update**
3. 右側點 **Run workflow** → **Run workflow**
4. 等待約 30 秒完成
5. 重新整理網站即可看到最新榜單

## 自動更新時間

每天 **台灣時間凌晨 01:00** 自動執行（UTC 17:00）。
可在 `.github/workflows/update.yml` 修改 cron 時間。

## 檔案說明

| 檔案 | 說明 |
|------|------|
| `index.html` | 前端網站 |
| `data.json` | 榜單資料（由爬蟲自動更新） |
| `scraper/scrape.py` | Python 爬蟲 |
| `.github/workflows/update.yml` | GitHub Actions 排程設定 |

## 新增更多榜單

在 `scraper/scrape.py` 的 `main()` 函式中加入：

```python
# QQ音樂（填入 topid）
charts.append(fetch_qq_chart(topid, "榜單名稱"))

# 網易雲（填入歌單 id）
charts.append(fetch_netease_chart(playlist_id, "榜單名稱"))

# 酷狗（填入 rank_id）
charts.append(fetch_kugou_chart(rank_id, "榜單名稱"))
```
