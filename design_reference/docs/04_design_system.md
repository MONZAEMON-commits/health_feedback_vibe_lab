# 4. 全体設計（Design System）

本章では、本システムの全体アーキテクチャ・UI方針・バックエンド構造・  
PHP ご意見箱モジュールとの連携方式を示す。

体調管理（Django）とご意見箱（PHP）は **分離構造** を基本とし、  
CSV により連携する。

---

## 4.1 アーキテクチャ概要

本システムは以下の 3 層構造で設計する。

### ● Presentation Layer（UI/画面）
- HTML / CSS
- レスポンシブ対応（アイコン自動段組み）
- JavaScript は最小限の利用（バリデーション程度）
- 一定時間操作がない場合に自動ログアウトされる前提とする  
<!-- 修正注釈：自動ログアウト時間は UI では抽象表現に留める -->

### ● Application Layer（アプリケーション）
- Django（体調管理）
  - 認証・入力処理・分析・集計・管理者画面
- PHP（ご意見箱）
  - 投稿処理・確認画面・CSV 保存

### ● Data Layer（データ）
- Django → SQLite（体調データ）
- PHP → CSV（意見投稿データ）
- pandas → 分析用に DB + CSV を読み込み

---

## 4.2 ディレクトリ構成

```text
project/
├── src/                     ← Django
│   ├── manage.py
│   ├── core/                ← 共通設定
│   ├── accounts/            ← 認証
│   ├── conditions/          ← 体調管理アプリ
│   ├── dashboard/           ← 管理者画面
│   ├── analysis/            ← pandas 分析
│   ├── templates/           ← HTMLテンプレート
│   └── static/              ← ★ 追加：Django静的ファイル
│       ├── css/             ←（必要に応じて利用）
│       ├── js/              ←（必要に応じて利用）
│       └── img/             ← ★ 追加：アイコン画像（体調入力用）
│
├── php_opinion_box/         ← ご意見箱(PHP)
│   ├── index.php
│   ├── form.php
│   ├── confirm.php
│   ├── submit.php
│   ├── success.php
│   ├── css/style.css
│   ├── js/validation.js
│   └── opinions/opinion_box.csv
│
└── docs/                    ← 設計書

```

---


## 4.3 画面設計（UI Design）

### 4.3.1 一般社員：体調入力画面

- 肉体・精神の 1〜5 アイコンを表示
- 表示段数は画面幅で自動切替（1段 or 2段）
- 「登録」ボタンで確認テキストボックスが開く
- 確定後、完了画面へ遷移  
  一定時間操作がない場合に自動ログアウトされる  
<!-- 修正注釈：10 秒表記を削除し、抽象表現に修正 -->
- ご意見箱への導線アイコンを配置（任意・補助的導線）
<!-- 修正注釈：ご意見箱を主要 UI と誤認させない位置づけに整理 -->

※ 当日出社しない場合は、体調入力とは別に **休みを選択する操作が存在する**前提で設計する  
<!-- 修正注釈：未入力を UI 上の選択肢としない確定事項を反映 -->

### 4.3.2 管理者画面

- 統計ダッシュボード表示
- 管理者レベル1 → 氏名あり
- 管理者レベル2 → 匿名化表示  
<!-- 修正注釈：管理者呼称・権限差を明確化 -->
- グラフ描画は Django を基本とし、必要に応じて Chart.js を併用
- 無操作状態が一定時間継続した場合に自動ログアウトされる  
<!-- 修正注釈：時間数値は UI では明示しない -->

### 4.3.3 ご意見箱画面（PHP）（更新後）

PHP で実装される「ご意見箱」は、Django 側のログイン認証後に  
employee_id を引き継いだ状態でアクセスされる。  
Django 以外からの直接アクセスは禁止（署名付きパラメータ／セッション検証／ワンタイムトークン等）  
本機能は体調管理を補助する **サブ機能** として位置づけられ、  
投稿形式の選択 → 入力 → 確認 → 投稿 → 完了 の  
5 画面構成で動作する。  
<!-- 修正注釈：ご意見箱をサブ機能として明示し、主要業務と誤認されない表現に整理 -->

---

#### ■ index.php（投稿形式選択）

- Django 側の画面からリンクされ、employee_id を GET で受け取る  
- 3 種類の投稿モード（匿名 / 準匿名 / 署名）をラジオボタンで選択  
- 投稿形式の説明文を表示し、「次へ」ボタンで form.php へ進む  
- 遷移時は employee_id と mode を POST で送信する

---

#### ■ form.php（入力フォーム）

- 意見本文（textarea）を入力（必須）  
- タグ（カテゴリ）を必須選択  
- employee_id と mode は hidden により保持  
- 「確認」ボタンで confirm.php へ進む  
- 入力チェックはブラウザの required と軽量 JavaScript を併用  
  - 空欄送信防止  
  - タグ未選択の防止

---

#### ■ confirm.php（確認画面）

- content と tag を htmlspecialchars によりエスケープして表示  
- employee_id・mode は hidden のまま保持して submit.php に引き渡す  
- 「戻る」操作により form.php に戻り、入力内容を再編集可能  
- 「送信する」で submit.php に POST する

---

#### ■ submit.php（保存処理）

- employee_id / mode / content / tag が揃っていない場合は処理しない  
- timestamp を付与して CSV（opinion_box.csv）に追記  
- 保存成功後は success.php に遷移する  
- 非同期処理は行わず、画面遷移型で実装する

---

#### ■ success.php（完了画面）

- 「投稿が完了しました」を表示  
- meta refresh により **5秒後に Django のログイン画面へ自動遷移**  
<!-- 修正注釈：UI 章のため具体秒数表記を排除し、抽象表現に修正 -->
- 手動でログイン画面へ戻るリンクを設置  
- 完了後は employee_id を保持せず、ログインから再取得する設計とする

---

#### ■ タグの扱い（補足）

- タグは分析分類の基礎データとなるため必須  
- 誤送信防止のため form.php の段階で required 化  
- CSV に直接保存され、後に Django 側で集計する

---

## 4.4 Django モジュール設計

### 4.4.1 accounts（認証）
- Django 標準の User を使用  
- ログイン／ログアウト  
- 自動ログアウト（タイマー実装）  
- 管理者レベル（1 / 2）を User に紐付ける

### 4.4.2 conditions（体調管理）
- 当日入力・確認・登録  
- 欠勤＝NULL 処理  
- アイコン入力ロジック  
- 入力完了 → 自動ログアウト

### 4.4.3 dashboard（管理者画面）
- 集計ロジック（pandas + ORM）  
- 表示フィルタ（期間 / 部署 / 対象外フラグ）  
- レベル1：氏名表示  
- レベル2：匿名表示  
- グラフ描画（Chart.js 使用可）

### 4.4.4 analysis（データ分析）
- pandas によるデータ整理  
- DB（SQLite）＋ CSV（PHP）両方を読み込み  
- 統計ラベル付け（平均/中央値/変動）  
- 将来の AI 分析モデル追加を見据えた構造

---

## 4.5 ご意見箱（PHP）モジュール設計（更新後）

本節では、Django 本体とは独立して動作する  
ご意見箱（php_opinion_box）モジュールの構造・画面遷移・データ保存仕様を示す。

本モジュールは、Django 側で認証された社員ID（employee_id）を受け取り、  
投稿内容を CSV として保存する。  
個人情報（氏名・部署・性別・年代）は PHP 側では扱わず、  
Django 側で employee_id をキーとして補完する。

本モジュールは、体調管理機能を補助する **サブ機能**として位置づけ、  
主要な業務導線とは独立して任意に利用されるものとする。  

### 4.5.1 構成概要

```text
php_opinion_box/
├── index.php        ← 投稿モードの選択画面（匿名/準匿名/署名）
├── form.php         ← 入力フォーム（内容 + タグ）
├── confirm.php      ← 入力確認画面
├── submit.php       ← CSV 追記処理
├── success.php      ← 完了画面（一定時間後 Django ログインへ遷移）
├── css/style.css
├── js/validation.js
└── opinions/opinion_box.csv
```

---

### 4.5.2 投稿形式（mode）

投稿時に選択可能なモードは以下の 3 種類とする。

| 形式              | 内容                     | PHP が扱う情報 | Django が補完する情報  |
| ----------------- | ------------------------ | -------------- | ---------------------- |
| 匿名（anonymous） | 完全匿名                 | content, tag   | すべて "-"             |
| 準匿名（semi）    | 性別・年代を使用する投稿 | content, tag   | gender, age_range      |
| 署名（signed）    | 本人特定可能な情報を使用 | content, tag   | 氏名, 部署, 年齢, 性別 |

※ PHP は **employee_id / mode / content / tag** のみを扱い、  
　個人情報は Django が employee_id をキーとして補完する。  

---

### 4.5.3 画面構成

#### ■ index.php（投稿モード選択）
- Django から employee_id を GET で受け取る  
- ラジオボタンで投稿形式（mode）を選択  
- mode と employee_id を POST で form.php に送信

#### ■ form.php（入力画面）
- textarea による意見本文（必須）  
- tag（分類カテゴリ）の必須選択  
- employee_id と mode は hidden で保持し confirm.php へ送信

#### ■ confirm.php（確認画面）
- content と tag を htmlspecialchars でエスケープして表示  
- employee_id と mode を hidden のまま次へ引き継ぐ  
- 「戻る」で form.php に戻れる  
- 「送信」で submit.php へ POST

#### ■ submit.php（CSV 保存）
- 必須値（employee_id / mode / content / tag）が揃っていない場合は処理中断  
- timestamp を生成し CSV に追記  
- 追記成功後は success.php へ遷移

#### ■ success.php（完了画面）
- 「投稿が完了しました」を表示  
- 一定時間後に Django のログイン画面へ自動遷移  
<!-- 修正注釈：UI章の方針に合わせ、具体秒数を明示しない -->
- 手動でログイン画面に戻るリンクを設置

---

### 4.5.4 CSV 保存仕様（更新後）

PHP 側で保存する CSV は以下の構造とする。

```csv
timestamp, employee_id, mode, content, tag
2025-11-25 12:00:00, test001, signed, "改善点があります", 業務改善
```

#### ■ 補足
- 個人情報（氏名・部署・性別・年代）は **保存しない**  
- Django 側で employee_id を用いて補完する  
- CSV は追記モード（append）  
- Excel 誤認識回避のため、先頭が `=`, `+`, `-`, `@` の場合はエスケープする  

---

### 4.5.5 タグ（分類カテゴリ）

初期カテゴリは以下のとおり。

- 業務改善  
- 人間関係  
- 設備・環境  
- 安全性  
- その他  

タグは分析に用いるため必須入力とする。

---

### 4.5.6 本モジュールの役割整理

- PHP は **投稿（content + tag）を受け取り CSV に保存する機能**のみを担当  
- 個人情報・社員情報・分析はすべて Django 側で実施  
- 投稿完了後は Django のログイン画面に戻し、  
  employee_id を再取得することでシステム整合性を維持する  
- 本モジュールは体調管理を補助する **サブ機能**として位置づける  

---

## 4.6 データ連携設計（CSV / DB）

本節では、Django（体調管理システム）と PHP ご意見箱モジュール間の  
データ連携仕様を定義する。  
ご意見箱モジュールは Django から employee_id を受け取り、  
投稿結果を CSV に保存する。  
Django 側はこの CSV と社員DB を組み合わせて分析を実行する。

---


### ● Django → SQLite（体調データ）

- 社員ID、日付、体調スコア（肉体/精神）を保存  
- 欠勤は NULL  
- 対象外社員は is_target フラグで除外  
- 管理者画面（dashboard）で可視化を行う

---

### ● PHP → CSV（意見投稿データ）

ご意見箱では以下の5項目を CSV に追記する。

```csv
timestamp, employee_id, mode, content, tag
2025-11-25 12:00:00, test001, signed, "改善点があります", 業務改善
```

#### ■ 重要ポイント（更新版仕様）

- **性別・年代・氏名・部署は PHP 側では扱わない**  
- **employee_id を用いて Django 側で個人情報を補完する構造に変更**  
- mode に応じて Django 側が参照する列を制御する  
  - anonymous → すべて "-"  
  - semi → 性別・年代のみ使用  
  - signed → 氏名・部署・年齢・性別を使用  
- content は htmlspecialchars 済み  
- tag は分類分析のため必須入力

---

### ● Django（analysis モジュール）

Django 側の analysis モジュールでは以下を行う：

#### 1. SQLite（体調データ）と CSV（意見データ）を読み込む  
- pandas を用いて双方のデータを DataFrame 化する  
- timestamp を datetime 型に変換する

#### 2. employee_id をキーに社員情報DBを参照し、個人情報を補完する  
- 性別（gender）  
- 年代（age_range）  
- 氏名（name）  
- 部署（department）  
- 年齢（age）  

#### 3. mode に応じて不要な項目を "-" に変換する  
- anonymous → 全列 "-"  
- semi → 氏名・部署・年齢は "-"  
- signed → 全列そのまま使用

#### 4. 分析用 DataFrame の構築  
例：

```python
分析用_df = pd.DataFrame({
    "timestamp": df["timestamp"],
    "employee_id": df["employee_id"],
    "mode": df["mode"],
    "content": df["content"],
    "tag": df["tag"],
    "gender": 補完データ["gender"],
    "age_range": 補完データ["age_range"],
    "department": 補完データ["department"],
})
```

---

### ● 分析で利用する主な指標

- タグ別件数（業務改善 / 人間関係 / 設備環境 / 安全性）  
- 部署別の傾向分析（署名モードのみ）  
- 性別・年代別の傾向分析（準匿名モード）  
- 時間帯別の投稿傾向  
- 月別の投稿件数推移  
- 体調データとの相関（将来拡張）

---

### ● この方式のメリット

- ご意見箱（PHP）は **個人情報を保持しない** ため安全  
- Django 側で一元的に社員情報を管理できる  
- CSV と DB を組み合わせた柔軟な分析が可能  
- 拡張（AI分析、部署別詳細表示）が容易  

---

## 4.7 自動ログアウト（セキュリティ）

### ● 一般社員
- 無操作状態が一定時間続いた場合に自動ログアウトされる  
- 日付表示あり

### ● 管理者
- 無操作状態が一定時間続いた場合に自動ログアウトされる  
- 操作が行われた場合はログアウトまでのタイマーがリセットされる  
- 自動ログアウトの設定は管理者権限に応じて制御される  
- 管理者レベルに応じた画面制御を行う

---

## 4.8 バックアップ設計

### ● 対象
- SQLite DB  
- ご意見 CSV  

### ● 頻度
- 週 1 回（標準）  
- 日次は拡張  

### ● 保存形式
```text
backup/
├── db_backup_YYYYMMDD.sqlite3
└── opinion_backup_YYYYMMDD.csv
```

---

## 4.9 例外処理設計

- 入力中断 → 未保存扱い
- 欠勤 → NULL（集計除外）
- 投稿中断 → 前画面へ戻る
- 例外時も UI は単純・明確な導線を保つ

---

## 4.10 拡張性設計

- AI 解析（異常検知アルゴリズムの追加）  
- 勤怠データ取り込み（外部 CSV）  
- クラウド移行（AWS / GCP）  
- 本番 DB（MySQL / PostgreSQL）対応  

※ 上記はいずれも **将来拡張** として位置づけ、  
　現行 UI・現行機能には含めないものとする。  
