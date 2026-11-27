"""把 scans/YYYY-MM-DD.md 轉成網站。

讀最新一份掃描檔（每份都是當天的完整特典一覽），解析各區表格，
輸出 public/index.html 與 public/data/*.json。只用 Python 標準函式庫。

用法：python site/build.py [輸出資料夾，預設 public]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCANS = ROOT / "scans"
TEMPLATE = ROOT / "site" / "template.html"

LINK = re.compile(r"\[([^\]]*)\]\((https?://[^)\s]+)\)")
DRIVE_ID = re.compile(r"drive\.google\.com/file/d/([\w-]+)")
# 「特典」欄常見寫法：說明文字（[圖](url) [圖2](url)）
IMG_PAREN = re.compile(r"（(?:\s*\[圖\d*\]\([^)]+\)\s*)+）")


def section_key(title: str) -> str:
    for key, words in [("this_week", ["這週"]), ("next_week", ["新的一週"]),
                       ("upcoming", ["之後", "預售"]), ("special", ["特別場"]),
                       ("new", ["本日新掃描"])]:
        if any(w in title for w in words):
            return key
    return "other"


def split_row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split(" | ")]


def images_of(*cells: str) -> list[dict]:
    out = []
    for cell in cells:
        for _, url in LINK.findall(cell):
            m = DRIVE_ID.search(url)
            if m:
                out.append({"id": m.group(1), "url": url})
    return out


def source_of(cell: str) -> dict:
    m = LINK.search(cell)
    return {"name": m.group(1), "url": m.group(2)} if m else {"name": cell, "url": ""}


def plain(cell: str) -> str:
    cell = IMG_PAREN.sub("", cell)
    return LINK.sub(r"\1", cell).strip()


def parse_scan(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    updated = next((re.sub(r"^最後更新：", "", l) for l in lines if l.startswith("最後更新")), path.stem)
    intro = next((l for l in lines if l.startswith("資料來源")), "")
    sections, cur, header = [], None, None
    for line in lines:
        if line.startswith("## "):
            title = line[3:].strip()
            cur = {"key": section_key(title), "title": title, "items": []}
            sections.append(cur)
            header = None
        elif line.startswith("|") and cur is not None:
            cells = split_row(line)
            if header is None:
                header = cells
                continue
            if all(set(c) <= set("-: ") for c in cells[1:]):
                continue  # 分隔列
            row = dict(zip(header, cells))
            item_cell = row.get("特典") or row.get("內容", "")
            cur["items"].append({
                "no": row.get("編號", ""),
                "movie": row.get("片名", ""),
                "item": plain(item_cell),
                "size": row.get("尺寸", ""),
                "period": row.get("期間", ""),
                "condition": plain(row.get("領取條件", "")),
                "images": images_of(item_cell, row.get("圖片", "")),
                "source": source_of(row.get("出處", "")),
            })
    sections = [s for s in sections if s["items"]]
    return {"date": path.stem, "updated": updated, "intro": intro, "sections": sections}


def main() -> None:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "public"
    scans = sorted(SCANS.glob("[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].md"))
    if not scans:
        sys.exit("scans/ 裡沒有掃描檔")
    (out / "data").mkdir(parents=True, exist_ok=True)
    for p in scans:
        (out / "data" / f"{p.stem}.json").write_text(
            json.dumps(parse_scan(p), ensure_ascii=False), encoding="utf-8")
    latest = parse_scan(scans[-1])
    latest["archive"] = [p.stem for p in reversed(scans)]
    (out / "data" / "latest.json").write_text(json.dumps(latest, ensure_ascii=False), encoding="utf-8")

    blob = json.dumps(latest, ensure_ascii=False).replace("</", "<\\/")
    body = re.sub(r"/\*DATA\*/.*?/\*END\*/", lambda _: blob, TEMPLATE.read_text(encoding="utf-8"), flags=re.S)
    if "--fragment" in sys.argv:  # 預覽用，不包 <html>
        (out / "index.html").write_text(body, encoding="utf-8")
    else:
        (out / "index.html").write_text(
            '<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
            "</head><body>" + body + "</body></html>", encoding="utf-8")
    (out / ".nojekyll").write_text("", encoding="utf-8")
    n = sum(len(s["items"]) for s in latest["sections"])
    print(f"已輸出 {out}：{latest['date']}，{len(latest['sections'])} 區、{n} 項；歷史 {len(scans)} 份")


if __name__ == "__main__":
    main()
