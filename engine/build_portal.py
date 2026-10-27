#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zero-Cost Automated Revenue Portal Generator (v2.0: Multi-Page Programmatic SEO Engine)
トップページに加え、全アイテムごとの個別詳細ページ (docs/items/{id}.html) を自動生成。
個別のJSON-LD (Product / Review) と sitemap.xml への全URL自動登録、Bluesky自動投稿まで完結。
"""
import html
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

def post_to_bluesky(handle, app_password, text, target_url):
    """Bluesky API (AT Protocol) への完全無料自動ポスト"""
    if not handle or not app_password:
        print("[INFO] Bluesky credentials not found. Skipping auto-post.")
        return

    try:
        auth_url = "https://bsky.social/xrpc/com.atproto.server.createSession"
        auth_data = json.dumps({"identifier": handle, "password": app_password}).encode("utf-8")
        req = urllib.request.Request(auth_url, data=auth_data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            auth_res = json.loads(resp.read().decode("utf-8"))
            access_jwt = auth_res["accessJwt"]
            did = auth_res["did"]

        post_url = "https://bsky.social/xrpc/com.atproto.repo.createRecord"
        post_text = f"{text}\n\n▼詳細スペック＆時給換算シミュレーターはこちら👇\n{target_url}"
        
        start_idx = post_text.encode("utf-8").find(target_url.encode("utf-8"))
        facets = []
        if start_idx != -1:
            end_idx = start_idx + len(target_url.encode("utf-8"))
            facets.append({
                "index": {"byteStart": start_idx, "byteEnd": end_idx},
                "features": [{"$type": "app.bsky.richtext.facet#link", "uri": target_url}]
            })

        post_body = {
            "repo": did,
            "collection": "app.bsky.feed.post",
            "record": {
                "$type": "app.bsky.feed.post",
                "text": post_text,
                "facets": facets,
                "createdAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            }
        }
        
        post_req = urllib.request.Request(
            post_url,
            data=json.dumps(post_body).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {access_jwt}"}
        )
        with urllib.request.urlopen(post_req, timeout=10) as p_resp:
            print("[SUCCESS] Posted top ROI item directly to Bluesky!")
    except Exception as e:
        print(f"[WARNING] Bluesky auto-post failed: {e}")

def fetch_tech_trends():
    trends = []
    rss_url = "https://zenn.dev/feed"
    try:
        req = urllib.request.Request(rss_url, headers={"User-Agent": "Mozilla/5.0 (AutoPortalBot/1.0)"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            root = ET.fromstring(resp.read())
            for item in root.findall(".//item")[:4]:
                title = item.findtext("title", "")
                link = item.findtext("link", "")
                if title and link:
                    trends.append({"title": title, "link": link})
    except Exception:
        trends = [
            {"title": "デスク環境のエルゴノミクス投資と生産性ROIの相関分析", "link": "#simulator"},
            {"title": "USB-C単一ケーブル化によるワークスペース構築ベストプラクティス", "link": "#ranking"}
        ]
    return trends

def calculate_metrics(item, hourly_wage=2500):
    price = item["estimated_price"]
    days = item["lifespan_months"] * 30
    daily_cost = round(price / days, 1)
    daily_value_yen = round((item["time_saved_min_per_day"] / 60.0) * hourly_wage)
    monthly_net_benefit = (daily_value_yen - daily_cost) * 30
    roi_multiple = round((daily_value_yen * days) / max(price, 1), 1)
    day_seed = (NOW.day * 7 + len(item["id"])) % 9
    score = min(99, round(78 + roi_multiple * 1.2 + day_seed * 0.4, 1))
    return {
        "daily_cost": daily_cost,
        "daily_value_yen": daily_value_yen,
        "monthly_net_benefit": round(monthly_net_benefit),
        "roi_multiple": roi_multiple,
        "score": score,
        "days": days
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

def render_item_page(item, meta, mon):
    """個別商品専用のロングテールSEO特化詳細ページ HTML を生成"""
    item_url = f"{meta['base_url']}/items/{item['id']}.html"
    page_title = f"{item['name']}の費用対効果（ROI）＆実質コスト徹底解析 【{TODAY_JP}更新】"
    page_desc = f"{item['name']}の1日あたり実質負担（約{item['daily_cost']}円/日）と想定時短効果（+{item['time_saved_min_per_day']}分/日）を徹底検証。あなたの想定時給に連動した投資回収シミュレーションと最新最安値をリアルタイム比較。"
    
    specs_rows = "".join([
        f'<tr class="border-b border-slate-100"><th class="py-3 px-4 text-left font-semibold text-slate-700 bg-slate-50 w-1/3 text-xs md:text-sm">{k}</th><td class="py-3 px-4 text-slate-800 text-xs md:text-sm">{v}</td></tr>'
        for k, v in item["specs"].items()
    ])

    json_ld_product = {
        "@context": "https://schema.org/",
        "@type": "Product",
        "name": item["name"],
        "description": item["pros"],
        "category": item["category"],
        "offers": {
            "@type": "AggregateOffer",
            "priceCurrency": "JPY",
            "lowPrice": item["estimated_price"],
            "offerCount": 2,
            "availability": "https://schema.org/InStock"
        },
        "review": {
            "@type": "Review",
            "reviewRating": {
                "@type": "Rating",
                "ratingValue": round(min(5.0, item["score"] / 20.0), 1),
                "bestRating": "5"
            },
            "author": {
                "@type": "Person",
                "name": meta.get("author", "TechSpec Automated Analyst")
            },
            "datePublished": TODAY_STR,
            "reviewBody": f"想定耐用期間{item['lifespan_months']}ヶ月で1日あたり実質約{item['daily_cost']}円。1日あたり{item['time_saved_min_per_day']}分の時短効果が見込め、総合ROIスコアは{item['score']}点と算出。"
        }
    }

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title}</title>
    <meta name="description" content="{page_desc}">
    <link rel="canonical" href="{item_url}">
    <script src="https://cdn.tailwindcss.com"></script>
    <script type="application/ld+json">{json.dumps(json_ld_product, ensure_ascii=False)}</script>
</head>
<body class="bg-slate-50 text-slate-800 antialiased">
    <header class="bg-slate-900 text-white py-6 px-4 border-b border-slate-800">
        <div class="max-w-3xl mx-auto flex items-center justify-between">
            <a href="{meta['base_url']}/" class="text-sm font-bold text-slate-300 hover:text-white transition flex items-center gap-1.5">
                ← 総合ランキングTOPへ戻る
            </a>
            <span class="text-xs text-emerald-400 font-semibold bg-emerald-950/60 border border-emerald-500/30 px-2.5 py-1 rounded-full">
                ⚡ {TODAY_JP} 自動解析済
            </span>
        </div>
    </header>

    <main class="max-w-3xl mx-auto px-4 py-8">
        <!-- パンくずナビゲーション -->
        <nav class="text-xs text-slate-500 mb-4 flex items-center gap-2">
            <a href="{meta['base_url']}/" class="hover:underline">ホーム</a>
            <span>&gt;</span>
            <span class="text-slate-700 font-medium">{item['category']}</span>
            <span>&gt;</span>
            <span class="text-slate-900 font-bold truncate">{item['name']}</span>
        </nav>

        <article class="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 md:p-8 mb-8">
            <div class="flex flex-wrap items-center justify-between gap-2 mb-3">
                <span class="text-xs font-semibold text-indigo-700 bg-indigo-50 px-3 py-1 rounded-md">{item['category']}</span>
                <div class="text-right">
                    <span class="text-xs text-slate-500">総合ROI指数</span>
                    <span class="text-2xl font-extrabold text-emerald-600 ml-1">{item['score']}</span>
                    <span class="text-xs text-slate-400">/100</span>
                </div>
            </div>
            
            <h1 class="text-xl md:text-2xl font-extrabold text-slate-900 mb-3">{item['name']}</h1>
            <p class="text-slate-600 text-sm md:text-base leading-relaxed mb-6">{item['pros']}</p>

            <!-- 核心指標サマリーパネル -->
            <div class="grid grid-cols-3 gap-3 bg-indigo-50/50 p-4 rounded-xl border border-indigo-100 mb-6 text-center">
                <div>
                    <div class="text-xs text-slate-500">1日あたり実質負担</div>
                    <div class="text-lg md:text-xl font-bold text-slate-900 mt-1">約{item['daily_cost']}円/日</div>
                    <div class="text-[10px] text-slate-400 mt-0.5">※耐用{item['lifespan_months']}ヶ月換算</div>
                </div>
                <div>
                    <div class="text-xs text-slate-500">想定時短メリット</div>
                    <div class="text-lg md:text-xl font-bold text-emerald-600 mt-1">+{item['time_saved_min_per_day']}分/日</div>
                    <div class="text-[10px] text-slate-400 mt-0.5">※作業効率化目安</div>
                </div>
                <div>
                    <div class="text-xs text-slate-500">月間純利益換算</div>
                    <div class="text-lg md:text-xl font-bold text-indigo-600 mt-1 dynamic-item-net">+¥{item['monthly_net_benefit']:,}/月</div>
                    <div class="text-[10px] text-slate-400 mt-0.5">※時給2,500円想定</div>
                </div>
            </div>

            <!-- 動的時給シミュレーター -->
            <div class="bg-slate-50 rounded-xl p-4 border border-slate-200 mb-6">
                <div class="flex items-center justify-between mb-2">
                    <span class="text-xs md:text-sm font-bold text-slate-700">あなたの想定時給で再計算:</span>
                    <span class="text-sm font-extrabold text-indigo-600"><span id="itemWageDisp">2,500</span> 円/時</span>
                </div>
                <input id="itemWageRange" type="range" min="1200" max="10000" step="100" value="2500" class="w-full accent-indigo-600 cursor-pointer">
            </div>

            <!-- 購入ボタン -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-8">
                <a href="{item['amz_url']}" target="_blank" rel="nofollow sponsored noopener" class="flex items-center justify-center bg-amber-500 hover:bg-amber-600 text-white font-bold py-3.5 px-4 rounded-xl text-sm transition shadow-sm">
                    Amazonで実売価格・口コミを見る ↗
                </a>
                <a href="{item['rak_url']}" target="_blank" rel="nofollow sponsored noopener" class="flex items-center justify-center bg-rose-600 hover:bg-rose-700 text-white font-bold py-3.5 px-4 rounded-xl text-sm transition shadow-sm">
                    楽天市場で還元ポイントをチェック ↗
                </a>
            </div>

            <!-- スペック詳細テーブル -->
            <h2 class="text-base font-bold text-slate-900 mb-3 border-l-4 border-indigo-600 pl-2">製品スペック・検証仕様</h2>
            <table class="w-full text-left border border-slate-200 rounded-xl overflow-hidden mb-6">
                <tbody>{specs_rows}</tbody>
            </table>

            <!-- レビュー評価解説 -->
            <h2 class="text-base font-bold text-slate-900 mb-2 border-l-4 border-indigo-600 pl-2">客観的投資価値分析（ROI評価）</h2>
            <div class="space-y-3 text-xs md:text-sm text-slate-600 leading-relaxed bg-slate-50 p-4 rounded-xl border border-slate-200 mb-6">
                <p>・<strong>推奨ターゲット：</strong> {item['target_user']}</p>
                <p>・<strong>投資回収ロジック：</strong> 参考相場 {item['estimated_price']:,} 円を耐久年数（{item['lifespan_months']}ヶ月＝約{item['days']:,}日）で按分した場合、日割り費用は約 {item['daily_cost']} 円となります。1日あたり {item['time_saved_min_per_day']} 分の作業短縮・疲労軽減が実現できれば、投資対効果倍率は約 {item['roi_multiple']} 倍となり、極めて優れた機材投資と判定されます。</p>
            </div>

            <div class="text-center">{mon.get('a8_banner_html', '')}</div>
        </article>

        <div class="text-center">
            <a href="{meta['base_url']}/" class="inline-block bg-slate-900 hover:bg-slate-800 text-white text-xs md:text-sm font-bold py-3 px-6 rounded-xl transition shadow">
                ← 総合ROIランキング一覧へ戻る
            </a>
        </div>
    </main>

    <footer class="bg-slate-900 text-slate-400 text-xs py-8 px-4 mt-12 border-t border-slate-800">
        <div class="max-w-3xl mx-auto text-center space-y-2">
            <p>※当サイトはAmazonアソシエイトおよび楽天アフィリエイトプログラム等の適格販売により収入を得ています。</p>
            <p>© {NOW.year} {meta['title']} - Multi-Page SEO Programmatic Engine.</p>
        </div>
    </footer>

    <script>
        const slider = document.getElementById('itemWageRange');
        const disp = document.getElementById('itemWageDisp');
        const netEl = document.querySelector('.dynamic-item-net');
        const minSaved = {item['time_saved_min_per_day']};
        const dailyCost = {item['daily_cost']};
        slider.addEventListener('input', (e) => {{
            const wage = parseInt(e.target.value, 10);
            disp.textContent = wage.toLocaleString();
            const dailyVal = (minSaved / 60.0) * wage;
            const monthlyNet = Math.round((dailyVal - dailyCost) * 30);
            netEl.textContent = (monthlyNet >= 0 ? '+¥' : '-¥') + Math.abs(monthlyNet).toLocaleString() + '/月';
        }});
    </script>
</body>
</html>"""

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
        item_page_url = f"{meta['base_url']}/items/{it['id']}.html"
        enriched = {**it, **m, "amz_url": amz_url, "rak_url": rak_url, "item_page_url": item_page_url}
        enriched_items.append(enriched)

    enriched_items.sort(key=lambda x: x["score"], reverse=True)
    trends = fetch_tech_trends()

    docs_dir = os.path.join(base_dir, "docs")
    items_dir = os.path.join(docs_dir, "items")
    os.makedirs(items_dir, exist_ok=True)

    # 1. 各アイテムの個別詳細 HTML ページを一括自動生成
    generated_pages = []
    for it in enriched_items:
        page_html = render_item_page(it, meta, mon)
        page_path = os.path.join(items_dir, f"{it['id']}.html")
        with open(page_path, "w", encoding="utf-8") as f:
            f.write(page_html)
        generated_pages.append(it['item_page_url'])

    # 2. トップページ (index.html) のカード生成（各個別ページへの内部リンクを追加）
    cards_html = ""
    for idx, it in enumerate(enriched_items, 1):
        specs_badges = "".join([
            f'<span class="inline-block bg-slate-100 text-slate-700 text-xs px-2.5 py-1 rounded-md mr-1.5 mb-1.5 font-medium">{k}: {v}</span>'
            for k, v in it["specs"].items()
        ])
        cards_html += f"""
        <article class="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 mb-6 transition hover:shadow-md" data-category="{it['category']}" data-min-saved="{it['time_saved_min_per_day']}" data-price="{it['estimated_price']}" data-days="{it['days']}">
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
            <h3 class="text-lg md:text-xl font-bold text-slate-900 mb-2">
                <a href="./items/{it['id']}.html" class="hover:text-indigo-600 transition">{it['name']}</a>
            </h3>
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
            <div class="flex items-center justify-between text-xs text-slate-500 mb-4">
                <span>🎯 <strong>推奨対象:</strong> {it['target_user']}</span>
                <a href="./items/{it['id']}.html" class="text-indigo-600 font-bold hover:underline whitespace-nowrap ml-2">詳細スペック・徹底検証 ➔</a>
            </div>
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

    top_json_ld = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": meta["title"],
        "description": meta["description"],
        "dateModified": TODAY_STR,
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": idx + 1,
                "url": it["item_page_url"],
                "name": it["name"],
                "description": it["pros"]
            } for idx, it in enumerate(enriched_items)
        ]
    }

    html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{meta['title']} 【{TODAY_JP}自動更新】</title>
    <meta name="description" content="{meta['description']}">
    <link rel="canonical" href="{meta['base_url']}/">
    <script src="https://cdn.tailwindcss.com"></script>
    <script type="application/ld+json">{json.dumps(top_json_ld, ensure_ascii=False)}</script>
</head>
<body class="bg-slate-50 text-slate-800 antialiased">
    <header class="bg-slate-900 text-white py-10 px-4 border-b border-slate-800">
        <div class="max-w-4xl mx-auto">
            <div class="inline-flex items-center gap-2 bg-emerald-500/20 text-emerald-300 text-xs font-semibold px-3 py-1 rounded-full mb-3 border border-emerald-500/30">
                <span>⚡ GitHub Actions 自動解析エンジン稼働中</span>
                <span>全{len(enriched_items)}商品・{TODAY_JP} 更新</span>
            </div>
            <h1 class="text-2xl md:text-4xl font-extrabold tracking-tight mb-3">{meta['title']}</h1>
            <p class="text-slate-300 text-sm md:text-base">{meta['description']}</p>
        </div>
    </header>

    <main class="max-w-4xl mx-auto px-4 py-8">
        <section id="simulator" class="bg-white rounded-2xl shadow-sm border border-indigo-100 p-6 mb-8">
            <h2 class="text-lg font-bold text-slate-900 mb-2">🧮 あなたの時給換算・投資回収（ROI）リアルタイム計算機</h2>
            <p class="text-xs text-slate-500 mb-4">スライダーを動かすと、全機材が「あなたに毎月いくらの時間価値（純利益）をもたらすか」を一括再計算します。</p>
            <div class="flex flex-col sm:flex-row items-center gap-4 bg-indigo-50/60 p-4 rounded-xl">
                <label for="wageSlider" class="text-sm font-bold text-slate-700 whitespace-nowrap">あなたの想定時給: <span id="wageDisplay" class="text-indigo-600 text-lg">2,500</span> 円/時</label>
                <input id="wageSlider" type="range" min="1200" max="10000" step="100" value="2500" class="w-full accent-indigo-600 cursor-pointer">
            </div>
        </section>

        <section id="ranking">
            <div class="flex items-center justify-between mb-4">
                <h2 class="text-xl font-extrabold text-slate-900">🏆 本日の費用対効果（ROI）総合ランキング (全{len(enriched_items)}商品)</h2>
                <span class="text-xs text-slate-500">※毎日AM6:00自動再集計</span>
            </div>
            {cards_html}
        </section>

        <section class="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 mt-8">
            <h2 class="text-base font-bold text-slate-900 mb-3">📡 本日のテック・生産性トレンドヘッドライン（自動取得）</h2>
            <ul>{trends_html}</ul>
        </section>

        <div class="mt-6 text-center">{mon.get('a8_banner_html', '')}</div>
    </main>

    <footer class="bg-slate-900 text-slate-400 text-xs py-8 px-4 mt-12">
        <div class="max-w-4xl mx-auto text-center space-y-2">
            <p>※当サイトはAmazonアソシエイトおよび楽天アフィリエイトプログラム等の適格販売により収入を得ています。</p>
            <p>© {NOW.year} {meta['title']} - Powered by Multi-Page Programmatic SEO Engine.</p>
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

    with open(os.path.join(docs_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content)

    # 3. sitemap.xml の全自動生成（トップページ ＋ 個別15ページ = 全16URLを自動登録）
    sitemap_urls = f"""  <url>
    <loc>{meta['base_url']}/</loc>
    <lastmod>{TODAY_STR}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>"""
    for page_url in generated_pages:
        sitemap_urls += f"""
  <url>
    <loc>{page_url}</loc>
    <lastmod>{TODAY_STR}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.8</priority>
  </url>"""

    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{sitemap_urls}
</urlset>"""
    with open(os.path.join(docs_dir, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap_xml)

    # 4. feed.xml の生成
    rss_title = html.escape(meta['title'])
    rss_desc = html.escape(meta['description'])
    rss_items = ""
    for it in enriched_items[:3]:
        it_title = html.escape(f"【ROIスコア {it['score']}点】{it['name']}（1日実質{it['daily_cost']}円）")
        it_desc = html.escape(f"{it['pros']}（時短目安: +{it['time_saved_min_per_day']}分/日）")
        rss_items += f"""
    <item>
      <title>{it_title}</title>
      <link>{it['item_page_url']}</link>
      <guid isPermaLink="false">{it['id']}-{TODAY_STR}</guid>
      <description>{it_desc}</description>
      <pubDate>{NOW.strftime('%a, %d %b %Y %H:%M:%S +0900')}</pubDate>
    </item>"""

    rss_xml = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
  <channel>
    <title>{rss_title}</title>
    <link>{meta['base_url']}/</link>
    <description>{rss_desc}</description>
    <lastBuildDate>{NOW.strftime('%a, %d %b %Y %H:%M:%S +0900')}</lastBuildDate>{rss_items}
  </channel>
</rss>"""
    with open(os.path.join(docs_dir, "feed.xml"), "w", encoding="utf-8") as f:
        f.write(rss_xml)

    # 5. Bluesky 自動投稿（最上位アイテムの個別ページURL付きでポスト）
    top_item = enriched_items[0]
    bsky_text = f"【本日自動解析】作業時短×コスパROI第1位は『{top_item['name']}』！1日わずか{top_item['daily_cost']}円で毎月{top_item['monthly_net_benefit']:,}円相当の時短効果。"
    post_to_bluesky(
        os.environ.get("BLUESKY_HANDLE"),
        os.environ.get("BLUESKY_APP_PASSWORD"),
        bsky_text,
        top_item['item_page_url']
    )

    print(f"[SUCCESS] Multi-Page Engine: Generated index.html, {len(generated_pages)} item pages in docs/items/, sitemap.xml ({len(generated_pages)+1} URLs), and feed.xml")

if __name__ == "__main__":
    main()
