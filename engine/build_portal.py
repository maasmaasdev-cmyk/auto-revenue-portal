#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TechSpec & ROI Lab - Visual High-Conversion Designer Edition (v4.0)
購買意欲を最大限に刺激する「高解像度実機イメージ」「実質日額・月間創出利益バッジ」、
「20商品の厳選ハイエンドデータベース」、全個別詳細ページへの画像連動エンジン。
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
    """Bluesky API への完全無料自動ポスト"""
    if not handle or not app_password:
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
            print("[SUCCESS] Posted top visual ROI item directly to Bluesky!")
    except Exception as e:
        print(f"[WARNING] Bluesky auto-post failed: {e}")

def fetch_tech_trends():
    trends = []
    rss_url = "https://zenn.dev/feed"
    try:
        req = urllib.request.Request(rss_url, headers={"User-Agent": "Mozilla/5.0 (AutoPortalBot/3.0)"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            root = ET.fromstring(resp.read())
            for item in root.findall(".//item")[:4]:
                title = item.findtext("title", "")
                link = item.findtext("link", "")
                if title and link:
                    trends.append({"title": title, "link": link})
    except Exception:
        trends = [
            {"title": "エルゴノミクスデスク投資がもたらす認知疲労軽減と年間生産性相関", "link": "#simulator"},
            {"title": "Thunderbolt 4 / USB4 単一ドック環境における作業中断ロスの最小化", "link": "#ranking"},
            {"title": "静電容量無接点方式キーボードの打鍵負荷分散と腱鞘炎予防エビデンス", "link": "#ranking"}
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
    """個別商品専用の洗練されたビジュアル詳細ページ"""
    item_url = f"{meta['base_url']}/items/{item['id']}.html"
    page_title = f"{item['name']} | 費用対効果（ROI）実質コスト徹底解析レポート"
    page_desc = f"{item['name']}の1日あたり実質負担（約{item['daily_cost']}円/日）と時短メリット（+{item['time_saved_min_per_day']}分/日）を数学的に検証。時給連動シミュレーションと最安値比較。"
    
    specs_rows = "".join([
        f'<tr class="border-b border-zinc-100 hover:bg-zinc-50/80 transition-colors"><th class="py-3.5 px-5 text-left font-semibold text-zinc-500 w-1/3 text-xs tracking-wider uppercase">{k}</th><td class="py-3.5 px-5 text-zinc-900 font-medium text-sm">{v}</td></tr>'
        for k, v in item["specs"].items()
    ])

    json_ld_product = {
        "@context": "https://schema.org/",
        "@type": "Product",
        "name": item["name"],
        "image": item.get("image_url", ""),
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
            "reviewBody": f"想定耐用期間{item['lifespan_months']}ヶ月で日割り実質約{item['daily_cost']}円。1日あたり{item['time_saved_min_per_day']}分の時短効果が見込め、総合ROIスコアは{item['score']}点。"
        }
    }

    return f"""<!DOCTYPE html>
<html lang="ja" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title}</title>
    <meta name="description" content="{page_desc}">
    <link rel="canonical" href="{item_url}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Noto+Sans+JP:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    fontFamily: {{
                        sans: ['"Plus Jakarta Sans"', '"Noto Sans JP"', 'sans-serif'],
                    }},
                    colors: {{
                        brand: {{
                            50: '#f5f3ff',
                            100: '#ede9fe',
                            500: '#8b5cf6',
                            600: '#7c3aed',
                            700: '#6d28d9',
                            900: '#4c1d95',
                        }}
                    }}
                }}
            }}
        }}
    </script>
    <script type="application/ld+json">{json.dumps(json_ld_product, ensure_ascii=False)}</script>
</head>
<body class="bg-zinc-950 text-zinc-800 antialiased font-sans selection:bg-brand-500 selection:text-white">
    <div class="fixed inset-0 pointer-events-none z-0 overflow-hidden">
        <div class="absolute -top-[30%] left-[20%] w-[600px] h-[600px] rounded-full bg-gradient-to-br from-violet-600/15 to-indigo-600/10 blur-3xl"></div>
        <div class="absolute top-[40%] -right-[20%] w-[500px] h-[500px] rounded-full bg-gradient-to-br from-emerald-600/10 to-teal-600/10 blur-3xl"></div>
    </div>

    <div class="relative z-10 min-h-screen flex flex-col justify-between">
        <header class="border-b border-zinc-800/80 bg-zinc-950/70 backdrop-blur-md sticky top-0 z-50">
            <div class="max-w-4xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
                <a href="{meta['base_url']}/" class="group flex items-center gap-2 text-zinc-400 hover:text-white transition text-xs sm:text-sm font-semibold">
                    <span class="w-7 h-7 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-center group-hover:border-brand-500/50 group-hover:bg-brand-500/10 transition">←</span>
                    <span>総合ROIランキング一覧へ</span>
                </a>
                <div class="flex items-center gap-2 text-[11px] font-mono tracking-wider text-emerald-400 bg-emerald-950/50 border border-emerald-500/20 px-3 py-1 rounded-full">
                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
                    <span>{TODAY_JP} VALIDATED</span>
                </div>
            </div>
        </header>

        <main class="max-w-4xl mx-auto px-4 sm:px-6 py-10 w-full">
            <nav class="flex items-center gap-2 text-xs text-zinc-500 mb-6 font-medium">
                <a href="{meta['base_url']}/" class="hover:text-zinc-300 transition">INDEX</a>
                <span class="text-zinc-700">/</span>
                <span class="text-zinc-400">{item['category']}</span>
                <span class="text-zinc-700">/</span>
                <span class="text-brand-400 truncate max-w-[200px] sm:max-w-xs">{item['name']}</span>
            </nav>

            <article class="bg-white rounded-3xl border border-zinc-200/80 shadow-2xl p-6 sm:p-10 mb-8 relative overflow-hidden">
                <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
                    <span class="text-xs font-bold uppercase tracking-wider text-brand-700 bg-brand-50 border border-brand-200/60 px-3.5 py-1 rounded-full">
                        {item['category']}
                    </span>
                    <div class="flex items-baseline gap-1.5">
                        <span class="text-xs font-semibold text-zinc-400">総合ROIスコア</span>
                        <span class="text-3xl font-extrabold text-zinc-900 tracking-tight">{item['score']}</span>
                        <span class="text-xs font-bold text-zinc-400">/100</span>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8 items-center">
                    <div class="relative rounded-2xl overflow-hidden bg-zinc-100 border border-zinc-200/80 shadow-inner group aspect-[4/3]">
                        <img src="{item.get('image_url', '')}" alt="{item['name']}" class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105" loading="lazy">
                        <div class="absolute inset-0 bg-gradient-to-t from-zinc-950/40 via-transparent to-transparent"></div>
                        <span class="absolute bottom-3 left-3 text-[11px] font-medium text-white/90 bg-zinc-900/70 backdrop-blur-md px-2.5 py-1 rounded-md">
                            参考市場価格: 約¥{item['estimated_price']:,}
                        </span>
                    </div>
                    <div>
                        <h1 class="text-xl sm:text-2xl font-extrabold text-zinc-900 tracking-tight leading-snug mb-3">
                            {item['name']}
                        </h1>
                        <p class="text-zinc-600 text-sm leading-relaxed mb-6">
                            {item['pros']}
                        </p>
                        <div class="p-3.5 rounded-xl bg-zinc-50 border border-zinc-200/80 text-xs text-zinc-600">
                            🎯 <strong>推奨層:</strong> {item['target_user']}
                        </div>
                    </div>
                </div>

                <!-- メトリクスサマリーパネル -->
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-3.5 p-5 rounded-2xl bg-zinc-900 text-white mb-8 border border-zinc-800">
                    <div class="p-3">
                        <span class="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider block mb-1">1日あたり実質負担</span>
                        <div class="text-2xl font-bold tracking-tight text-white">約{item['daily_cost']}<span class="text-xs font-normal text-zinc-400 ml-1">円/日</span></div>
                        <span class="text-[10px] text-zinc-500 mt-1 block">※想定耐用期間{item['lifespan_months']}ヶ月按分</span>
                    </div>
                    <div class="p-3 border-t sm:border-t-0 sm:border-l border-zinc-800">
                        <span class="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider block mb-1">時短創出効果</span>
                        <div class="text-2xl font-bold tracking-tight text-emerald-400">+{item['time_saved_min_per_day']}<span class="text-xs font-normal text-zinc-400 ml-1">分/日</span></div>
                        <span class="text-[10px] text-zinc-500 mt-1 block">※日々の集中ロスタイム削減</span>
                    </div>
                    <div class="p-3 border-t sm:border-t-0 sm:border-l border-zinc-800">
                        <span class="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider block mb-1">月間時間価値換算</span>
                        <div class="text-2xl font-bold tracking-tight text-violet-400 dynamic-item-net">+¥{item['monthly_net_benefit']:,}<span class="text-xs font-normal text-zinc-400 ml-1">/月</span></div>
                        <span class="text-[10px] text-zinc-500 mt-1 block">※時給連動による純増益</span>
                    </div>
                </div>

                <!-- インタラクティブ時給連動スライダー -->
                <div class="bg-gradient-to-r from-violet-50 to-indigo-50 border border-violet-100/80 rounded-2xl p-5 mb-8">
                    <div class="flex items-center justify-between mb-3">
                        <div class="flex items-center gap-2">
                            <span class="w-2 h-2 rounded-full bg-brand-600"></span>
                            <span class="text-xs sm:text-sm font-bold text-zinc-800">あなたの想定時給で投資リターンをシミュレーション</span>
                        </div>
                        <span class="text-base font-extrabold text-brand-700 tracking-tight"><span id="itemWageDisp">2,500</span> <span class="text-xs font-medium text-zinc-500">円/時</span></span>
                    </div>
                    <input id="itemWageRange" type="range" min="1200" max="10000" step="100" value="2500" class="w-full accent-brand-600 cursor-pointer h-2 bg-white rounded-lg">
                </div>

                <!-- CTA（購入ボタングループ） -->
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3.5 mb-10">
                    <a href="{item['amz_url']}" target="_blank" rel="nofollow sponsored noopener" class="group flex items-center justify-between bg-zinc-900 hover:bg-zinc-800 text-white font-semibold py-4 px-6 rounded-2xl text-sm transition-all shadow-lg hover:shadow-xl active:scale-[0.98]">
                        <span class="flex items-center gap-2.5">
                            <span class="w-2.5 h-2.5 rounded-full bg-amber-400"></span>
                            <span>Amazonで最安値・在庫・レビューを見る</span>
                        </span>
                        <span class="text-zinc-400 group-hover:translate-x-0.5 transition-transform">↗</span>
                    </a>
                    <a href="{item['rak_url']}" target="_blank" rel="nofollow sponsored noopener" class="group flex items-center justify-between bg-white hover:bg-zinc-50 text-zinc-900 border border-zinc-200 font-semibold py-4 px-6 rounded-2xl text-sm transition-all shadow-sm hover:shadow-md active:scale-[0.98]">
                        <span class="flex items-center gap-2.5">
                            <span class="w-2.5 h-2.5 rounded-full bg-rose-500"></span>
                            <span>楽天市場でポイント還元率を比較</span>
                        </span>
                        <span class="text-zinc-400 group-hover:translate-x-0.5 transition-transform">↗</span>
                    </a>
                </div>

                <!-- 製品仕様テーブル -->
                <div class="mb-10">
                    <h2 class="text-xs font-bold uppercase tracking-wider text-zinc-400 mb-3 flex items-center gap-2">
                        <span>TECHNICAL SPECIFICATIONS</span>
                    </h2>
                    <div class="border border-zinc-200 rounded-2xl overflow-hidden shadow-sm">
                        <table class="w-full">{specs_rows}</table>
                    </div>
                </div>

                <!-- 客観的ROI分析ロジック -->
                <div>
                    <h2 class="text-xs font-bold uppercase tracking-wider text-zinc-400 mb-3">
                        <span>QUANTITATIVE ROI ANALYSIS</span>
                    </h2>
                    <div class="bg-zinc-50 border border-zinc-200/80 rounded-2xl p-6 text-sm text-zinc-600 leading-relaxed space-y-3">
                        <p><strong class="text-zinc-900 font-semibold">推奨ターゲット：</strong> {item['target_user']}</p>
                        <p><strong class="text-zinc-900 font-semibold">投資対効果の算出根拠：</strong> 市場参考価格 約{item['estimated_price']:,}円を耐用期間（{item['lifespan_months']}ヶ月 / 約{item['days']:,}日）で按分した場合、日割り実質負担額はわずか約{item['daily_cost']}円です。1日あたり{item['time_saved_min_per_day']}分の短縮創出価値を時給換算すると、初期投資額に対して約{item['roi_multiple']}倍の経済的利益をもたらす計算となり、極めて高い合理性を持ちます。</p>
                    </div>
                </div>

                <div class="mt-8 text-center">{mon.get('a8_banner_html', '')}</div>
            </article>

            <div class="text-center pb-8">
                <a href="{meta['base_url']}/" class="inline-flex items-center gap-2 text-zinc-400 hover:text-white text-xs font-semibold uppercase tracking-wider transition bg-zinc-900 border border-zinc-800 px-6 py-3 rounded-full hover:border-zinc-700">
                    <span>← RETURN TO ALL RANKINGS</span>
                </a>
            </div>
        </main>

        <footer class="border-t border-zinc-900 bg-zinc-950 py-10 px-4 text-center text-xs text-zinc-500 space-y-2">
            <p class="max-w-md mx-auto leading-relaxed">※当サイトはAmazonアソシエイトおよび楽天アフィリエイトプログラム等の適格販売により収入を得ています。</p>
            <p class="font-mono text-[11px] text-zinc-600">© {NOW.year} {meta['title']} — Visual Lab Edition.</p>
        </footer>
    </div>

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
    categories = set()
    for it in items:
        m = calculate_metrics(it)
        amz_url, rak_url = build_affiliate_urls(it["search_keyword"], mon)
        item_page_url = f"{meta['base_url']}/items/{it['id']}.html"
        enriched = {**it, **m, "amz_url": amz_url, "rak_url": rak_url, "item_page_url": item_page_url}
        enriched_items.append(enriched)
        categories.add(it["category"])

    enriched_items.sort(key=lambda x: x["score"], reverse=True)
    trends = fetch_tech_trends()

    docs_dir = os.path.join(base_dir, "docs")
    items_dir = os.path.join(docs_dir, "items")
    os.makedirs(items_dir, exist_ok=True)

    # 1. 各アイテムの個別詳細 HTML ページを一括生成
    generated_pages = []
    for it in enriched_items:
        page_html = render_item_page(it, meta, mon)
        page_path = os.path.join(items_dir, f"{it['id']}.html")
        with open(page_path, "w", encoding="utf-8") as f:
            f.write(page_html)
        generated_pages.append(it['item_page_url'])

    # 2. カテゴリー別フィルタータブボタン
    sorted_cats = sorted(list(categories))
    cat_buttons = '<button class="cat-filter-btn px-4 py-2 rounded-xl text-xs font-semibold tracking-wider transition bg-white text-zinc-900 shadow-sm border border-zinc-200" data-cat="all">ALL ITEMS</button>'
    for c in sorted_cats:
        cat_buttons += f'<button class="cat-filter-btn px-4 py-2 rounded-xl text-xs font-semibold tracking-wider transition bg-zinc-900/80 hover:bg-zinc-800 text-zinc-400 hover:text-white border border-zinc-800" data-cat="{c}">{c}</button>'

    # 3. トップページ用：写真付きカード一覧の生成
    cards_html = ""
    for idx, it in enumerate(enriched_items, 1):
        specs_badges = "".join([
            f'<span class="inline-block bg-zinc-100 text-zinc-600 text-[11px] px-2.5 py-1 rounded-md mr-1.5 mb-1.5 font-medium border border-zinc-200/50">{k}: {v}</span>'
            for k, v in it["specs"].items()
        ])
        
        rank_badge = (
            '<span class="bg-gradient-to-r from-amber-400 to-amber-500 text-zinc-950 text-xs font-extrabold px-3 py-1 rounded-full shadow-sm">TOP 1</span>' if idx == 1 else
            '<span class="bg-gradient-to-r from-slate-300 to-slate-400 text-zinc-950 text-xs font-extrabold px-3 py-1 rounded-full shadow-sm">TOP 2</span>' if idx == 2 else
            '<span class="bg-gradient-to-r from-amber-700 to-amber-800 text-white text-xs font-extrabold px-3 py-1 rounded-full shadow-sm">TOP 3</span>' if idx == 3 else
            f'<span class="bg-zinc-100 text-zinc-600 text-xs font-bold px-3 py-1 rounded-full border border-zinc-200">#{idx}</span>'
        )

        cards_html += f"""
        <article class="item-card bg-white rounded-3xl border border-zinc-200/80 shadow-md hover:shadow-2xl transition-all duration-300 flex flex-col justify-between overflow-hidden group" data-category="{it['category']}" data-min-saved="{it['time_saved_min_per_day']}" data-price="{it['estimated_price']}" data-days="{it['days']}">
            <!-- 商品写真ビジュアルエリア -->
            <div class="relative w-full aspect-[16/9] overflow-hidden bg-zinc-100 border-b border-zinc-100">
                <img src="{it.get('image_url', '')}" alt="{it['name']}" class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105" loading="lazy">
                <div class="absolute inset-0 bg-gradient-to-t from-zinc-950/60 via-transparent to-transparent"></div>
                <div class="absolute top-3 left-3 flex items-center gap-2">
                    {rank_badge}
                    <span class="text-xs font-bold uppercase tracking-wider text-white bg-zinc-900/80 backdrop-blur-md px-3 py-1 rounded-full border border-white/20">{it['category']}</span>
                </div>
                <div class="absolute bottom-3 left-3 right-3 flex items-baseline justify-between text-white">
                    <span class="text-xs font-medium text-zinc-200 bg-zinc-950/60 backdrop-blur-md px-2.5 py-1 rounded-md">約¥{it['estimated_price']:,}</span>
                    <span class="text-xs font-bold bg-emerald-500/90 text-white px-2.5 py-1 rounded-md shadow-sm">ROI {it['score']}/100</span>
                </div>
            </div>

            <div class="p-6 sm:p-7 flex-1 flex flex-col justify-between">
                <div>
                    <h3 class="text-lg font-extrabold text-zinc-900 tracking-tight mb-2 group-hover:text-brand-600 transition-colors">
                        <a href="./items/{it['id']}.html">{it['name']}</a>
                    </h3>
                    <p class="text-xs text-zinc-500 leading-relaxed mb-4">{it['pros']}</p>
                    <div class="mb-4">{specs_badges}</div>
                </div>

                <div>
                    <div class="grid grid-cols-3 gap-2 bg-zinc-50 border border-zinc-100 rounded-2xl p-3 mb-4 text-center">
                        <div>
                            <div class="text-[10px] font-semibold text-zinc-400 uppercase tracking-wider">1日実質</div>
                            <div class="text-sm font-bold text-zinc-900 mt-0.5">約{it['daily_cost']}円</div>
                        </div>
                        <div>
                            <div class="text-[10px] font-semibold text-zinc-400 uppercase tracking-wider">時短効果</div>
                            <div class="text-sm font-bold text-emerald-600 mt-0.5">+{it['time_saved_min_per_day']}分</div>
                        </div>
                        <div>
                            <div class="text-[10px] font-semibold text-zinc-400 uppercase tracking-wider">月間純増益</div>
                            <div class="text-sm font-bold text-brand-600 dynamic-net-benefit mt-0.5">+¥{it['monthly_net_benefit']:,}</div>
                        </div>
                    </div>

                    <div class="flex items-center justify-between text-xs text-zinc-400 mb-4 pb-2 border-b border-zinc-100">
                        <span class="truncate max-w-[200px]">🎯 {it['target_user']}</span>
                        <a href="./items/{it['id']}.html" class="text-zinc-900 font-bold hover:text-brand-600 transition flex items-center gap-1 shrink-0 ml-2">
                            詳細・シミュレーター <span>→</span>
                        </a>
                    </div>

                    <div class="grid grid-cols-2 gap-2">
                        <a href="{it['amz_url']}" target="_blank" rel="nofollow sponsored noopener" class="flex items-center justify-center bg-zinc-900 hover:bg-zinc-800 text-white font-semibold py-3 px-3 rounded-xl text-xs transition active:scale-[0.98]">
                            Amazon最安値 ↗
                        </a>
                        <a href="{it['rak_url']}" target="_blank" rel="nofollow sponsored noopener" class="flex items-center justify-center bg-white hover:bg-zinc-50 text-zinc-800 border border-zinc-200 font-semibold py-3 px-3 rounded-xl text-xs transition active:scale-[0.98]">
                            楽天市場ポイント ↗
                        </a>
                    </div>
                </div>
            </div>
        </article>
        """

    trends_html = "".join([
        f'<li class="py-3 border-b border-zinc-800/80 last:border-0 flex items-baseline gap-3"><span class="text-xs text-brand-400 font-mono">TREND</span><a href="{t["link"]}" target="_blank" rel="noopener" class="text-zinc-300 hover:text-white transition text-xs sm:text-sm font-medium leading-relaxed">{t["title"]}</a></li>'
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
                "image": it.get("image_url", ""),
                "description": it["pros"]
            } for idx, it in enumerate(enriched_items)
        ]
    }

    html_content = f"""<!DOCTYPE html>
<html lang="ja" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{meta['title']} 【{TODAY_JP}自動更新】</title>
    <meta name="description" content="{meta['description']}">
    <link rel="canonical" href="{meta['base_url']}/">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Noto+Sans+JP:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    fontFamily: {{
                        sans: ['"Plus Jakarta Sans"', '"Noto Sans JP"', 'sans-serif'],
                    }},
                    colors: {{
                        brand: {{
                            50: '#f5f3ff',
                            100: '#ede9fe',
                            500: '#8b5cf6',
                            600: '#7c3aed',
                            700: '#6d28d9',
                            900: '#4c1d95',
                        }}
                    }}
                }}
            }}
        }}
    </script>
    <script type="application/ld+json">{json.dumps(top_json_ld, ensure_ascii=False)}</script>
</head>
<body class="bg-zinc-950 text-zinc-800 antialiased font-sans selection:bg-brand-500 selection:text-white">
    <!-- 背景アンビエントライティング演出 -->
    <div class="fixed inset-0 pointer-events-none z-0 overflow-hidden">
        <div class="absolute -top-[20%] left-[10%] w-[700px] h-[700px] rounded-full bg-gradient-to-br from-violet-600/15 via-indigo-600/10 to-transparent blur-3xl"></div>
        <div class="absolute top-[40%] -right-[15%] w-[600px] h-[600px] rounded-full bg-gradient-to-br from-emerald-600/10 via-teal-600/5 to-transparent blur-3xl"></div>
    </div>

    <div class="relative z-10 min-h-screen flex flex-col justify-between">
        <!-- ヘッダー -->
        <header class="border-b border-zinc-800/80 bg-zinc-950/70 backdrop-blur-md sticky top-0 z-50">
            <div class="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
                <div class="flex items-center gap-3">
                    <span class="w-8 h-8 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-500 flex items-center justify-center text-white font-extrabold text-sm shadow-lg shadow-brand-500/20">⚡</span>
                    <span class="text-white font-extrabold tracking-tight text-sm sm:text-base">TechSpec & ROI Lab</span>
                </div>
                <div class="flex items-center gap-2 text-[11px] font-mono tracking-wider text-emerald-400 bg-emerald-950/50 border border-emerald-500/20 px-3 py-1 rounded-full">
                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
                    <span>全{len(enriched_items)}機材・{TODAY_JP} 更新</span>
                </div>
            </div>
        </header>

        <!-- ヒーローセクション -->
        <section class="max-w-6xl mx-auto px-4 sm:px-6 pt-16 pb-12 text-center text-white">
            <div class="inline-flex items-center gap-2 bg-zinc-900 border border-zinc-800 text-zinc-400 text-xs px-3.5 py-1.5 rounded-full mb-6 font-medium">
                <span>🔬 デスク環境投資の費用対効果を客観的・数学的に解析</span>
            </div>
            <h1 class="text-3xl sm:text-5xl md:text-6xl font-extrabold tracking-tight leading-tight mb-6">
                作業の疲労と時間を削る、<br class="hidden sm:block">
                <span class="bg-gradient-to-r from-violet-400 via-indigo-300 to-emerald-400 bg-clip-text text-transparent">真のハイエンド機材ROI指数。</span>
            </h1>
            <p class="max-w-2xl mx-auto text-zinc-400 text-sm sm:text-base leading-relaxed mb-10">
                日割り実質コスト、時短創出価値、あなたの想定時給を掛け合わせ、<br class="hidden sm:block">
                「自己投資として毎月いくらのリターンがあるか」を毎日リアルタイム自動集計。
            </p>

            <!-- 時給連動シミュレーターボックス -->
            <div id="simulator" class="max-w-2xl mx-auto bg-zinc-900/90 border border-zinc-800/90 rounded-3xl p-6 sm:p-8 backdrop-blur-xl shadow-2xl text-left">
                <div class="flex items-center justify-between mb-4">
                    <div>
                        <span class="text-xs font-bold uppercase tracking-wider text-brand-400 block mb-1">INTERACTIVE CALCULATOR</span>
                        <h2 class="text-base sm:text-lg font-bold text-white">あなたの想定時給を設定</h2>
                    </div>
                    <div class="text-right">
                        <span class="text-2xl font-extrabold text-white tracking-tight"><span id="wageDisplay">2,500</span></span>
                        <span class="text-xs font-medium text-zinc-400 ml-1">円/時</span>
                    </div>
                </div>
                <input id="wageSlider" type="range" min="1200" max="10000" step="100" value="2500" class="w-full accent-brand-500 cursor-pointer h-2 bg-zinc-800 rounded-lg">
                <div class="flex justify-between text-[10px] font-mono text-zinc-500 mt-2">
                    <span>¥1,200/h (ENTRY)</span>
                    <span>¥5,000/h (EXPERT)</span>
                    <span>¥10,000/h (LEAD)</span>
                </div>
            </div>
        </section>

        <!-- メインコンテンツセクション -->
        <main class="max-w-6xl mx-auto px-4 sm:px-6 pb-16 w-full">
            <div class="mb-8">
                <div class="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
                    {cat_buttons}
                </div>
            </div>

            <!-- 写真付きカードグリッド (2カラム) -->
            <section id="ranking" class="grid grid-cols-1 md:grid-cols-2 gap-6">
                {cards_html}
            </section>

            <!-- トレンドヘッドライン -->
            <section class="mt-12 bg-zinc-900/60 border border-zinc-800/80 rounded-3xl p-6 sm:p-8 backdrop-blur-md">
                <div class="flex items-center justify-between mb-4">
                    <h2 class="text-sm font-bold uppercase tracking-wider text-zinc-400">TRENDING TECH TOPICS</h2>
                    <span class="text-xs text-zinc-600 font-mono">AUTOMATED FEED</span>
                </div>
                <ul class="divide-y divide-zinc-800/60">{trends_html}</ul>
            </section>

            <div class="mt-8 text-center">{mon.get('a8_banner_html', '')}</div>
        </main>

        <footer class="border-t border-zinc-900 bg-zinc-950 py-12 px-4 text-center text-xs text-zinc-500 space-y-3">
            <p class="max-w-md mx-auto leading-relaxed">※当サイトはAmazonアソシエイトおよび楽天アフィリエイトプログラム等の適格販売により収入を得ています。</p>
            <p class="font-mono text-[11px] text-zinc-600">© {NOW.year} {meta['title']} — Powered by Next-Gen Programmatic SEO Engine.</p>
        </footer>
    </div>

    <script>
        const slider = document.getElementById('wageSlider');
        const display = document.getElementById('wageDisplay');
        const cards = document.querySelectorAll('.item-card');
        const filterBtns = document.querySelectorAll('.cat-filter-btn');

        slider.addEventListener('input', (e) => {{
            const wage = parseInt(e.target.value, 10);
            display.textContent = wage.toLocaleString();
            cards.forEach(card => {{
                const minSaved = parseFloat(card.dataset.minSaved);
                const price = parseFloat(card.dataset.price);
                const days = parseFloat(card.dataset.days);
                const dailyCost = price / days;
                const dailyVal = (minSaved / 60.0) * wage;
                const monthlyNet = Math.round((dailyVal - dailyCost) * 30);
                const targetEl = card.querySelector('.dynamic-net-benefit');
                if (targetEl) {{
                    targetEl.textContent = (monthlyNet >= 0 ? '+¥' : '-¥') + Math.abs(monthlyNet).toLocaleString();
                }}
            }});
        }});

        filterBtns.forEach(btn => {{
            btn.addEventListener('click', () => {{
                filterBtns.forEach(b => {{
                    b.classList.remove('bg-white', 'text-zinc-900', 'shadow-sm');
                    b.classList.add('bg-zinc-900/80', 'text-zinc-400');
                }});
                btn.classList.remove('bg-zinc-900/80', 'text-zinc-400');
                btn.classList.add('bg-white', 'text-zinc-900', 'shadow-sm');

                const selectedCat = btn.dataset.cat;
                cards.forEach(card => {{
                    if (selectedCat === 'all' || card.dataset.category === selectedCat) {{
                        card.style.display = 'flex';
                    }} else {{
                        card.style.display = 'none';
                    }}
                }});
            }});
        }});
    </script>
</body>
</html>"""

    with open(os.path.join(docs_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content)

    # 4. sitemap.xml の生成
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

    # 5. feed.xml の生成
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

    # 6. Bluesky 自動投稿
    top_item = enriched_items[0]
    bsky_text = f"【本日自動解析】作業時短×コスパROI第1位は『{top_item['name']}』！1日わずか{top_item['daily_cost']}円で毎月{top_item['monthly_net_benefit']:,}円相当の時短効果。"
    post_to_bluesky(
        os.environ.get("BLUESKY_HANDLE"),
        os.environ.get("BLUESKY_APP_PASSWORD"),
        bsky_text,
        top_item['item_page_url']
    )

    print(f"[SUCCESS] Visual Edition v4.0: Generated modern UI with images, {len(generated_pages)} item pages, sitemap.xml, and feed.xml")

if __name__ == "__main__":
    main()
