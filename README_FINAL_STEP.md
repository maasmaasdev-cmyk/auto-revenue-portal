# 完全無料・完全自動マイクロツール型アフィリエイトシステム (Auto-Revenue Portal v1.0)

## システム構成概要
- **サーバー費用**: 0円（GitHub Pages 静的ホスティング）
- **定期実行サーバー費用**: 0円（GitHub Actions Cronジョブ：毎日朝06:00 JSTに自動起動）
- **外部AI/API課金**: 0円（Python標準ライブラリのみでROI演算・公開RSS取得・JSON-LD構造化HTML・Sitemap・RSSフィードを生成）
- **SNS自動集客**: 自動生成される `docs/feed.xml` を Make.com（無料枠）または IFTTT（無料枠）に接続することで、X（旧Twitter）やBlueskyへ毎日自動投稿。

## 最終確認・稼働開始までの3ステップ（所要時間5分）
1. `config.json` 内の `YOUR_AMAZON_TAG-22` と `YOUR_RAKUTEN_ID` をご自身のアフィリエイトID（もしもアフィリエイト / Amazonアソシエイト / 楽天アフィリエイト）に書き換えます。
2. GitHubで新規Publicリポジトリを作成し、このフォルダ一式をPushします。
3. GitHubリポジトリの **Settings > Pages** にて、Branchを `main` / フォルダを `/docs` に設定して **Save** を押せば稼働開始です！
