#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zero-Cost Automated Revenue Portal Generator
外部有料APIを一切使わず、config.jsonと公開トレンドデータから
高CVRのインタラクティブROIシミュレーター付き比較サイト・Sitemap・RSSを完全自動生成します。
"""
import json
import os
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=9))
NOW = datetime.now(JST)
TODAY_STR = NOW.strftime("%Y-%m-%d")
TODAY_JP = NOW.strftime("%Y年%m月%d日")

def fetch_tech_trends():
    """公開RSS（Zenn / HackerNews等）から本日の注目技術キーワードを安全に取得（オフライン時はフォールバック）"""
    trends = []
    rss_url = "https://zenn.dev/feed"
    try:
        req = urllib.request.Request(rss_url, headers={"User-Agent": "Mozilla/5.0 (AutoPortalBot/1.0)"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            xml_data = resp.read()
            root = ET.fromstring(xml_data)
            for item in root.findall(".//item")[:4]:
                title = item.findtext("title", "")
                link = item.findtext("link", "")
                if title and link:
                    trends.append({"title": title, "link": link})
    except Exception:
        trends = [
            {"title": "デスク環境のエルゴノミクス投資と生産性ROIの相関分析", "link": "#simulator"},
            {"title": "USB-C単一ケーブル化によるワークスペース構築ベストプラクティス", "link": "#ranking"},
            {"title": "眼精疲労とタイピング負荷を下げる最新ハードウェア選定基準", "link": "#ranking"}
        ]
    return trends

def calculate_metrics(item, hourly_wage=2500):
    """日次コスパ指数・1日あたり実質コスト・年間時間創出価値を算出"""
    price = item["estimated_price"]
    days = item["lifespan_months"] * 30
    daily_cost = round(price / days, 1)
    daily_value_yen = round((item["time_saved_min_per_day"] / 60.0) * hourly_wage)
    monthly_net_benefit = (daily_value_yen - daily_cost) * 30
    roi_Multiple = round((daily_value_yen * days) / max(price, 1), 1)
    # 日替わりで微細な注目度スコア変動を算出（クローラーに鮮度シグナルを送信）
    day_seed = (NOW.day * 7 + len(item["id"])) % 9
    score = min(99, round(78 + roi_Multiple * 1.2 + day_seed * 0.4, 1))
    return {
        "daily_cost": daily_cost,
        "daily_value_yen": daily_value_yen,
        "monthly_net_benefit": round(monthly_net_benefit),
        "roi_multiple": roi_Multiple,
        "score": score
    }

def build_affiliate_urls(keyword, mon_cfg):
    q = urllib.parse.quote(keyword)
    amz_tag = mon_cfg.get("amazon_associate_tag", "YOUR_AMAZON_TAG-22")
    rak_id = mon_cfg.get("rakuten_affiliate_id", "")
    amz_url = f"https://www.amazon.co.jp/s?k={q}&tag={amz_tag}"
    if rak_id and rak_id != "YOUR_RAKUTEN_ID":
        rak_dest = urllib.parse.quote(f"https://search.rakuten.co.jp/search/mall/{q}/")
        rak_url = f"https://hb.afl.rakuten.co.jp/hgc/{rak_id}/?pc={rak_dest}"
    else:
        rak_url = f"https://search.rakuten.co.jp/search/mall/{q}/"
    return amz_url, rak_url

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(base_dir, "config.json"), "r", encoding="utf-8") as f:
        cfg = json.load(f)

    meta = cfg["site_meta"]
    mon = cfg["monetization"]
    items = cfg["items_database"]

    enriched_items = []
    for it in items:
        m = calculate_metrics(it)
        amz_url, rak_url = build_affiliate_urls(it["search_keyword"], mon)
        enriched = {**it, **m, "amz_url": amz_url, "rak_url": rak_url}
        enriched_items.append(enriched)

    # スコア順にソート
    enriched_items.sort(key=lambda x: x["score"], reverse=True)
    trends = fetch_tech_trends()

    # JSON-LD 構造化データ生成 (リッチリザルト対応)
    json_ld = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": meta["title"],
        "description": meta["description"],
        "dateModified": TODAY_STR,
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": idx + 1,
                "name": it["name"],
                "description": it["pros"]
            } for idx, it in enumerate(enriched_items)
        ]
    }

    cards_html = ""
    for idx, it in enumerate(enriched_items, 1):
        specs_badges = "".join([
            f'<span class="inline-block bg-slate-100 text-slate-700 text-xs px-2.5 py-1 rounded-md mr-1.5 mb-1.5 font-medium">{k}: {v}</span>'
            for k, v in it["specs"].items()
        ])
        cards_html += f"""
        <article class="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 mb-6 transition hover:shadow-md" data-category="{it['category']}" data-min-saved="{it['time_saved_min_per_day']}" data-price="{it['estimated_price']}" data-days="{it['lifespan_months']*30}">
            <div class="flex flex-wrap items-center justify-between gap-2 mb-3">
                <div class="flex items-center gap-2">
                    <span class="bg-indigo-600 text-white text-xs font-bold px-3 py-1 rounded-full">第{idx}位</span>
                    <span class="text-xs font-semibold text-indigo-700 bg-indigo-50 px-2.5 py-1 rounded-md">{it['category']}</span>
                </div>
                <div class="text-right">
                    <span class="text-xs text-slate-500">総合ROIスコア</span>
                    <span class="text-xl font-extrabold text-emerald-600 ml-1">{it['score']}</span><span class="text-xs text-slate-400">/100</span>
                </div>
            </div>
            <h3 class="text-lg md:text-xl font-bold text-slate-900 mb-2">{it['name']}</h3>
            <p class="text-sm text-slate-600 mb-4">{it['pros']}</p>
            <div class="mb-4">{specs_badges}</div>
            <div class="grid grid-cols-3 gap-2 bg-slate-50 p-3.5 rounded-xl border border-slate-100 mb-5 text-center">
                <div>
                    <div class="text-xs text-slate-500">1日あたり実質負担</div>
                    <div class="text-base font-bold text-slate-800">約{it['daily_cost']}円/日</div>
                </div>
                <div>
                    <div class="text-xs text-slate-500">時短換算メリット</div>
                    <div class="text-base font-bold text-emerald-600">+{it['time_saved_min_per_day']}分/日</div>
                </div>
                <div>
                    <div class="text-xs text-slate-500">あなたの月間純利益換算</div>
                    <div class="text-base font-bold text-indigo-600 dynamic-net-benefit">+¥{it['monthly_net_benefit']:,}/月</div>
                </div>
            </div>
            <div class="text-xs text-slate-500 mb-4">🎯 <strong>推奨対象:</strong> {it['target_user']}</div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <a href="{it['amz_url']}" target="_blank" rel="nofollow sponsored noopener" class="flex items-center justify-center bg-amber-500 hover:bg-amber-600 text-white font-bold py-3 px-4 rounded-xl text-sm transition shadow-sm">
                    Amazonで最新価格・在庫を見る ↗
                </a>
                <a href="{it['rak_url']}" target="_blank" rel="nofollow sponsored noopener" class="flex items-center justify-center bg-rose-600 hover:bg-rose-700 text-white font-bold py-3 px-4 rounded-xl text-sm transition shadow-sm">
                    楽天市場でポイント還元を比較 ↗
                </a>
            </div>
        </article>
        """

    trends_html = "".join([
        f'<li class="py-2 border-b border-slate-100 last:border-0 text-sm"><a href="{t["link"]}" target="_blank" rel="noopener" class="text-indigo-600 hover:underline font-medium">{t["title"]}</a></li>'
        for t in trends
    ])

    html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{meta['title']} 【{TODAY_JP}自動更新】</title>
    <meta name="description" content="{meta['description']}">
    <script src="https://cdn.tailwindcss.com"></script>
    <script type="application/ld+json">{json.dumps(json_ld, ensure_ascii=False)}</script>
</head>
<body class="bg-slate-50 text-slate-800 antialiased">
    <header class="bg-slate-900 text-white py-10 px-4 border-b border-slate-800">
        <div class="max-w-4xl mx-auto">
            <div class="inline-flex items-center gap-2 bg-emerald-500/20 text-emerald-300 text-xs font-semibold px-3 py-1 rounded-full mb-3 border border-emerald-500/30">
                <span>⚡ GitHub Actions 自動解析エンジン稼働中</span>
                <span>最終更新: {TODAY_JP}</span>
            </div>
            <h1 class="text-2xl md:text-4xl font-extrabold tracking-tight mb-3">{meta['title']}</h1>
            <p class="text-slate-300 text-sm md:text-base">{meta['description']}</p>
        </div>
    </header>

    <main class="max-w-4xl mx-auto px-4 py-8">
        <!-- インタラクティブROIシミュレーター (SEO滞在時間最大化モジュール) -->
        <section id="simulator" class="bg-white rounded-2xl shadow-sm border border-indigo-100 p-6 mb-8">
            <h2 class="text-lg font-bold text-slate-900 mb-2">🧮 あなたの時給換算・投資回収（ROI）リアルタイム計算機</h2>
            <p class="text-xs text-slate-500 mb-4">スライダーを動かすと、各機材が「あなたに毎月いくらの時間価値（純利益）をもたらすか」を自動再計算します。</p>
            <div class="flex flex-col sm:flex-row items-center gap-4 bg-indigo-50/60 p-4 rounded-xl">
                <label for="wageSlider" class="text-sm font-bold text-slate-700 whitespace-nowrap">あなたの想定時給: <span id="wageDisplay" class="text-indigo-600 text-lg">2,500</span> 円/時</label>
                <input id="wageSlider" type="range" min="1200" max="10000" step="100" value="2500" class="w-full accent-indigo-600 cursor-pointer">
            </div>
        </section>

        <!-- ランキング一覧 -->
        <section id="ranking">
            <div class="flex items-center justify-between mb-4">
                <h2 class="text-xl font-extrabold text-slate-900">🏆 本日の費用対効果（ROI）総合ランキング</h2>
                <span class="text-xs text-slate-500">※毎日AM6:00自動再集計</span>
            </div>
            {cards_html}
        </section>

        <!-- 自動取得トレンドモジュール -->
        <section class="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 mt-8">
            <h2 class="text-base font-bold text-slate-900 mb-3">📡 本日のテック・生産性トレンドヘッドライン（自動取得）</h2>
            <ul>{trends_html}</ul>
        </section>

        <div class="mt-6 text-center">{mon.get('a8_banner_html', '')}</div>
    </main>

    <footer class="bg-slate-900 text-slate-400 text-xs py-8 px-4 mt-12">
        <div class="max-w-4xl mx-auto text-center space-y-2">
            <p>※当サイトはAmazonアソシエイトおよび楽天アフィリエイトプログラム等の適格販売により収入を得ています。</p>
            <p>© {NOW.year} {meta['title']} - Powered by Serverless GitHub Actions Engine.</p>
        </div>
    </footer>

    <script>
        const slider = document.getElementById('wageSlider');
        const display = document.getElementById('wageDisplay');
        const articles = document.querySelectorAll('article[data-min-saved]');
        slider.addEventListener('input', (e) => {{
            const wage = parseInt(e.target.value, 10);
            display.textContent = wage.toLocaleString();
            articles.forEach(card => {{
                const minSaved = parseFloat(card.dataset.minSaved);
                const price = parseFloat(card.dataset.price);
                const days = parseFloat(card.dataset.days);
                const dailyCost = price / days;
                const dailyVal = (minSaved / 60.0) * wage;
                const monthlyNet = Math.round((dailyVal - dailyCost) * 30);
                const targetEl = card.querySelector('.dynamic-net-benefit');
                if (targetEl) {{
                    targetEl.textContent = (monthlyNet >= 0 ? '+¥' : '-¥') + Math.abs(monthlyNet).toLocaleString() + '/月';
                }}
            }});
        }});
    </script>
</body>
</html>"""

    docs_dir = os.path.join(base_dir, "docs")
    os.makedirs(docs_dir, exist_ok=True)
    with open(os.path.join(docs_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content)

    # Sitemap.xml の自動生成
    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{meta['base_url']}/</loc>
    <lastmod>{TODAY_STR}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>"""
    with open(os.path.join(docs_dir, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap_xml)

    # RSS feed.xml の自動生成 (SNS自動投稿連携用)
    rss_items = ""
    for it in enriched_items[:3]:
        rss_items += f"""
    <item>
      <title>【ROIスコア {it['score']}点】{it['name']}（1日実質{it['daily_cost']}円）</title>
      <link>{meta['base_url']}/#ranking</link>
      <description>{it['pros']}（時短目安: +{it['time_saved_min_per_day']}分/日）</description>
      <pubDate>{NOW.strftime('%a, %d %b %Y %H:%M:%S +0900')}</pubDate>
    </item>"""

    rss_xml = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
  <channel>
    <title>{meta['title']}</title>
    <link>{meta['base_url']}/</link>
    <description>{meta['description']}</description>
    <lastBuildDate>{NOW.strftime('%a, %d %b %Y %H:%M:%S +0900')}</lastBuildDate>{rss_items}
  </channel>
</rss>"""
    with open(os.path.join(docs_dir, "feed.xml"), "w", encoding="utf-8") as f:
        f.write(rss_xml)

    print(f"[SUCCESS] Generated docs/index.html, docs/sitemap.xml, docs/feed.xml ({TODAY_STR})")

if __name__ == "__main__":
    main()
