# 台灣電影海報特典一覽

網站：https://legendmmm.github.io/taiwan-cinema-bonuses/

每天掃描 Facebook、Threads 公開貼文整理的台灣上映電影特典（影城與片商觀影禮）。

## 最新一覽

- [2026-11-27](scans/2026-11-27.md) — 36 項

## 歷次掃描

- [2026-11-27](scans/2026-11-27.md)
- [2026-11-26](scans/2026-11-26.md)

---

每次掃描存成一個檔案（`scans/YYYY-MM-DD.md`），檔案內是當次掃描時完整的特典一覽。另一個 AI 只要讀最新的那一個檔案就能拿到完整現況，不用翻舊檔。資料來源：Facebook、Threads 公開貼文（影城與片商官方帳號）。

## 網站

`site/build.py` 會讀最新一份 `scans/*.md`，把各區表格（這週、新的一週、之後・預售、特別場、本日新掃描）解析成資料，產生可搜尋、可依出處篩選的網頁，特典圖片直接用表格裡的 Google Drive 連結顯示縮圖。舊的掃描檔也會轉成 `data/YYYY-MM-DD.json`，網頁上可以切換日期。

每次有新的掃描檔推到 `main`，GitHub Actions（`.github/workflows/pages.yml`）會自動重建並部署到 GitHub Pages，不需要另外排程。

本機預覽：

```bash
python site/build.py public   # 只用 Python 標準函式庫
open public/index.html
```

掃描檔格式維持現狀即可：每區用 `## 標題`，表格第一欄是「編號」，欄位名稱（片名、特典／內容、尺寸、期間、領取條件、圖片、出處）照目前的寫法。新增欄位不會壞，只是網頁暫時不顯示。
