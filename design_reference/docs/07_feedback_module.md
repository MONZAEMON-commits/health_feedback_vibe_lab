# 7. ご意見箱モジュール詳細設計（Feedback Module）

本章では、PHP で実装される「ご意見箱」機能の詳細仕様を定義する。  
本機能は **社員体調管理システムに付随するサブ機能** として位置づけられ、  
Django 本体とは独立して動作し、CSV を介して連携する。  

---

## 7.1 目的

- 社員が匿名・準匿名・署名のいずれかで自由に意見を投稿できる場を提供する  
- 投稿内容は **Django 側で分析・可視化するための入力データ** として活用される   
- 匿名性と利便性を両立した UI/UX を実現する  
- Django 側に余計な依存を持たせない（CSV 連携）

---

## 7.2 構成概要

```text
php_opinion_box/
├── index.php        ← 投稿形式選択
├── form.php         ← 入力画面
├── confirm.php      ← 確認画面
├── submit.php       ← CSV保存処理
├── success.php      ← 完了画面
├── css/style.css
├── js/validation.js
└── opinions/opinion_box.csv
```
（追記）

【Django との連携仕様（employee_id）】
- Django 側でログイン後に取得した employee_id を、
  `index.php?id=xxxxx` のように URL パラメータとして受け取る。
- 受け取った employee_id は form.php → confirm.php → submit.php と
  hidden フィールドで引き継ぎ、CSV の employee_id カラムとして保存する。
- **employee_id は識別子としてのみ使用し、個人情報は PHP 側では保持しない。**
- 
---

## 7.3 投稿形式選択（index.php）

### ● 7.3.1 選択肢
| 種類   | 内容                                     | 取得情報 |
| ------ | ---------------------------------------- | -------- |
| 匿名   | 完全匿名で投稿                           | 取得なし |
| 準匿名 | 投稿者を直接特定しない投稿               | 取得なし |
| 署名   | 識別子付き投稿（識別は Django 側で管理） | 取得なし |

### ● 7.3.2 表示仕様  
- 3つのボタン（匿名／準匿名／署名）を横並びまたは縦並びで表示  
- 押下すると説明モーダル（または説明画面）を表示  
- 「進む」ボタンで `form.php` へ遷移

---

## 7.4 入力画面（form.php）

### ● 入力項目（モードによって変化）

| 項目                    | 内容 |
| ----------------------- | ---- |
| 意見本文（content）     | ○    |
| タグ（カテゴリ）（tag） | ○    |

---

### ● タグ候補

- 業務改善  
- 人間関係  
- 設備・環境  
- 安全性  
- その他  

---

### ● 入力チェック仕様

- content は必須  
- content が空白のみの場合は JavaScript で送信不可  
- tag は必須  
- employee_id と mode は hidden で保持  
- content のエスケープは confirm.php で実施  

---

### ● JavaScript バリデーション

```html 
<script>
function validateForm() {
    const text = document.querySelector('textarea[name="content"]').value;
    if (text.trim().length === 0) {
        alert("内容が空白のみのため送信できません。");
        return false;
    }
    return true;
}
</script>
```

---

### ● form.php（抜粋）

```html
<form action="confirm.php" method="post" onsubmit="return validateForm();">
    <input type="hidden" name="employee_id" value="<?= $employee_id ?>">
    <input type="hidden" name="mode" value="<?= $mode ?>">

    <textarea name="content" rows="5" cols="40" required></textarea>

    <select name="tag" required>
        <option value="">選択してください</option>
        <option value="業務改善">業務改善</option>
        <option value="人間関係">人間関係</option>
        <option value="設備・環境">設備・環境</option>
        <option value="安全性">安全性</option>
        <option value="その他">その他</option>
    </select>

    <button type="submit">確認</button>
</form>
```

---

### ● 画面遷移仕様

1. index.php → mode / employee_id を POST して form.php へ  
2. form.php → content / tag を POST して confirm.php へ  
3. confirm.php → content をエスケープして表示  

---

## 7.5 確認画面（confirm.php）

### ● 表示内容
利用者が送信前に内容を確認するための画面を表示する。表示する項目は以下。

- 意見本文（content：エスケープ済み）
- 投稿形式（mode：匿名 / 準匿名 / 署名）
- タグ（カテゴリ：tag）

employee_id は内部識別用であり、画面には表示しない。

---

### ● エスケープ処理
confirm.php に遷移した直後に、content を htmlspecialchars によりエスケープし、安全な表示形式にする。

```php
$comment = htmlspecialchars($_POST['content'], ENT_QUOTES, 'UTF-8');
```

---

### ● mode の表示ラベル

| mode値    | 表示ラベル |
| --------- | ---------- |
| anonymous | 匿名       |
| semi      | 準匿名     |
| signed    | 署名       |

---

### ● hidden で保持する値
confirm.php から submit.php に渡す値は以下。

- employee_id  
- mode  
- content（エスケープ済み）  
- tag  

これらを hidden input として保持し、submit.php に POST する。

---

### ● 画面遷移仕様

#### ■ 戻るボタン
form.php に戻る。  
戻る際には以下の値を hidden として維持する。

- employee_id  
- mode  
- content（未エスケープ値）  
- tag  

#### ■ 送信ボタン
submit.php に POST し、CSV 書き込み処理へ進む。

---

### ● 確認画面の目的
- 利用者が最終内容を確認できる  
- XSS 防止のため、実際に保存される値（エスケープ後）を確認できる  
- 投稿モードとタグ選択の誤りを防止する

---

## 7.6 投稿処理（submit.php）

### ● 処理内容

submit.php は confirm.php から POST された値を受け取り、  
意見内容を CSV ファイルに 1 レコードとして追記保存する役割を持つ。

処理の流れは以下の通りとする。

1. POST データの取得  
2. timestamp の生成（submit.php 側で付与）  
3. CSV 行データの整形  
4. CSV ファイルへの追記保存  
5. 保存成功後、success.php へ遷移

---

### ● POST で受け取る値

confirm.php から submit.php に POST される値は以下とする。

- employee_id  
- mode  
- content（エスケープ済み）  
- tag  

※ 個人情報（性別・年代・部署・氏名）は Django 側で employee_id をキーとして補完する。  
　PHP 側では保持しない。

---

### ● timestamp の生成

submit.php 内で投稿時の timestamp を生成し、  
全レコードに付与する。

```php
$timestamp = date('Y-m-d H:i:s');
```

---

### ● CSV 書き込み仕様

CSV ファイルは以下のディレクトリに保存する。

php_opinion_box/opinions/opinion_box.csv

保存時の条件は次の通り。

- 文字コード：UTF-8（BOMなし）  
- 追記モード（a）で開く  
- fputcsv を用いて安全に書き込む  
- 書き込み前に配列を 1 レコード形式に整形する  

CSV レコード構造：

```csv
timestamp, employee_id, mode, content, tag
2025-11-25 10:00:00, test001, signed, "意見本文", "業務改善"
```

---

### ● エラー処理

- ファイルが開けない場合は保存処理を中止し、  
　「CSVファイルのオープンに失敗しました」と表示する。  

- 書き込みに失敗した場合は success.php には遷移せず、  
　エラーをその場で表示する。

---

### ● 遷移仕様

保存が正常に完了した場合：

- header("Location: success.php");  
- exit;  

により完了画面へ遷移する。

success.php では投稿完了メッセージを表示し、  
5秒後に Django 側のログイン画面へ自動遷移する。
can_post を要求し、処理後に false。
---

---

## 7.7 完了画面（success.php）

### ● 表示内容

submit.php による CSV 書き込み処理が正常に完了した場合、  
success.php を表示する。

画面に表示する内容は以下とする。

- 「投稿が完了しました」等の完了メッセージ
- 「5秒後にログイン画面へ戻ります」等の案内文
- 手動でログイン画面へ戻るためのリンク

---

### ● 自動遷移仕様

success.php では meta タグを用いて、5秒後に Django 側のログイン画面へ自動遷移する。

```html
<meta http-equiv="refresh" content="5;URL=http://localhost:8000/login/">
```

遷移先 URL は Django 開発環境のログイン URL とし、  
本番環境では適宜変更できるものとする。

---

### ● 手動戻りリンク

ユーザーが即時にログイン画面へ戻れるよう、  
画面内にログイン画面へのリンクを設置する。

```html
<a href="http://localhost:8000/login/">ログイン画面へ戻る</a>
```

---

### ● 画面遷移設計上の意図

- 投稿完了後に index.php に戻すと、employee_id（ログインユーザー情報）が失われるため、  
  ご意見箱の利用フローを一度終了し、必ず Django 側のログイン画面へ戻す。  
- ご意見箱は体調管理システムのサブ機能であり、  
  利用完了後はログイン画面を起点として再度システムを利用する設計とする。

---

## 7.8 セキュリティ対策

ご意見箱モジュール（PHP）は Django 本体とは独立して動作する構成であり、  
POST データを引き継ぐフロー上で発生しうる脅威に対して、  
本節では必要なセキュリティ対策を定義する。

---

### ● XSS（クロスサイトスクリプティング）対策

意見本文（content）はユーザーが自由入力できるため、  
confirm.php にて必ず htmlspecialchars によりエスケープ処理を行う。

```php
$comment = htmlspecialchars($_POST['content'], ENT_QUOTES, 'UTF-8');
```

※ submit.php では **エスケープ済みの値のみ** を受け取り、  
　そのまま CSV に保存することで XSS の混入を防ぐ。

---

### ● CSV インジェクション対策

Excel は以下の記号で始まる文字列を関数として解釈するため危険となる。

- =  
- +  
- -  
- @  

content または tag がこれらで始まる場合、  
先頭にシングルクォート（'）を付与して安全な文字列に変換する。

（必要に応じて submit.php 内で前処理を追加する）

---

### ● CSRF 対策（簡易）

本モジュールはログインセッションを保持せず、  
Django 側から employee_id を付与した形で遷移してくるため、  
一般的な CSRF トークン方式は採用しない。

代替方針として以下を採用する。

- form → confirm → submit の遷移はすべて **POST のみ許可**  
- 必須の hidden 値が揃っていない場合は **不正アクセス** として処理中断  
- 外部から submit.php に直接アクセスされても動作しない構造にする

---

### ● 必須 POST 値チェック（不正アクセス対策）

submit.php において、以下の値が揃っていない場合は  
不正アクセスとして即時終了する。

- employee_id  
- mode  
- content  
- tag  

```php
if (!isset($_POST['employee_id'], $_POST['mode'], $_POST['content'], $_POST['tag'])) {
    exit('不正なアクセスです');
}
```

このチェックにより、  
外部からの直接アクセスや欠損データによる異常保存を防ぐ。

---

### ● ディレクトリ・ファイルアクセス対策

CSV 保存先である opinions ディレクトリは  
Web から直接参照できない位置に置くか、  
Apache 使用時は .htaccess を配置してアクセス制御を行う。

```text
# .htaccess の例
Options -Indexes
```

---

### ● バリデーション（最低限の入力検証）

- content（意見本文）は空文字不可  
- 空白のみの入力も JavaScript + サーバー側の両方で拒否  
- tag（カテゴリ）は必須  
- employee_id と mode は hidden の欠損を許容しない

---

### ● 目的

- PHP 側のみで動作するモジュールに最低限の防御を実装し、全体の安全性を担保する  
- XSS・CSV インジェクション・不正アクセス・欠損データを防ぎ、  
  Django 側で利用可能な質の高い CSV を維持する  
- 独立構造でありながら、体調管理システムとの整合性と信頼性を確保する

---

## 7.9 例外処理

ご意見箱モジュールは POST データを段階的に引き継ぐ構造のため、  
値の欠損・異常入力・不正アクセスへの対策を本節で定義する。

---

### ● 必須項目の未入力（content／tag）

以下の項目が未入力の場合はエラー扱いとし、form.php に戻す。

- content（意見本文）
- tag（カテゴリ）

また、**空白のみの入力（例："   "）も無効** とし、  
サーバー側で trim を行って長さ 0 の場合はエラー扱いとする。

（JavaScript による事前チェックも併用するが、  
サーバー側でも必ず判定を行う。）

---

### ● hidden 値の欠損（employee_id／mode）

form → confirm → submit の POST 連携において、  
以下の値が 1 つでも欠損していた場合は **不正アクセス** と判断し、  
即時処理を中断する。

- employee_id  
- mode  
- content  
- tag  

```php
if (!isset($_POST['employee_id'], $_POST['mode'], $_POST['content'], $_POST['tag'])) {
    exit('不正なアクセスです');
}
```

欠損時は form.php に戻さず、その場で終了する。  
CSV 書き込みは行わない。

---

### ● mode の無効値（想定外値）

mode は以下の 3 種類のみを有効値とする。

- anonymous  
- semi  
- signed  

それ以外の値が渡された場合は不正データとみなし、  
処理を中断する。

---

### ● CSV 書き込み失敗時

fopen または fputcsv が失敗した場合は、  
以下の動作を行う。

- 「CSV 書き込みに失敗しました」等のエラーメッセージを表示  
- success.php には遷移しない  
- ユーザーに再入力を促す  
- ログ記録は必須とせず、管理者の手動確認を前提とする

---

### ● submit.php の直接アクセス（禁止）

submit.php に GET リクエストや直接 URL アクセスされた場合、  
必須の POST 値が揃わないため、  
不正アクセスとして即時終了する。

---

### ● 目的

- 連続した POST フローの中でデータ整合性を維持する  
- 欠損データ・異常データが CSV に保存されないようにする  
- Django 側で利用する分析データの品質を担保する  
- 不正アクセスや外部からの直接呼び出しを防ぐ


---

## 7.10 Django 側との連携仕様（読み込み処理）

ご意見箱モジュール（PHP）は Django 本体とは独立して動作し、  
CSV により投稿データを連携する。本節では、  
Django 側が CSV を読み込み、社員情報を補完し、  
分析用データとして再構築する仕様を定義する。

---

### ● CSV の構造（PHP 側で保存される形式）

```csv
timestamp, employee_id, mode, content, tag
2025-12-01 12:00:00, test001, signed, "設備改善をお願いします", 安全性
```

※ 性別・年代・氏名・部署などの個人情報は **CSV に含めない**。  
※ Django 側で employee_id をキーとして社員情報を DB から補完する。

---

### ● Django 側での基本処理フロー

1. PHP 側で作成された opinion_box.csv を pandas で読み込む  
2. timestamp を datetime 型へ変換  
3. employee_id をもとに Django の社員マスタを参照  
4. mode（anonymous / semi / signed）に応じて必要情報のみ補完  
5. 分析用 DataFrame を構築  
6. 管理者権限に応じて、閲覧可能な分析結果のみをダッシュボードへ渡す  

---

### ● pandas による CSV 読み込み

```python
import pandas as pd

df = pd.read_csv("php_opinion_box/opinions/opinion_box.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])
```

---

### ● Django 側での情報補完ロジック

employee_id をキーとして Django の DB（社員マスタ）を参照し、  
mode に応じて必要な情報のみ追加する。

#### ■ 匿名（anonymous）
- gender："-"
- age_range："-"
- department："-"
- name："-"

#### ■ 準匿名（semi）
- gender：社員マスタから取得  
- age_range：社員マスタから取得  
- name："-"
- department："-"

#### ■ 署名（signed）
- gender：取得  
- age_range：取得  
- department：取得  
- name：取得  

---

### ● 補完後の DataFrame 例

```python
analysis_df = pd.DataFrame({
    "timestamp": df["timestamp"],
    "employee_id": df["employee_id"],
    "mode": df["mode"],
    "content": df["content"],
    "tag": df["tag"],
    "gender":補完後データ["gender"],
    "age_range":補完後データ["age_range"],
    "department":補完後データ["department"],
    "name":補完後データ["name"],
})
```

※ mode に応じて不要な情報は "-" を設定する。

---

### ● 分析で利用する例

- タグ別投稿件数  
- 時間帯別投稿傾向  
- 部署別の意見傾向（署名時）  
- 性別・年代別の意見傾向（準匿名時）  
- 月次集計や年間推移のトレンド可視化  

---

### ● 目的

- PHP 側を「投稿最小限データの保持」に限定し、個人情報は Django 側で一元管理する  
- mode に応じた情報制御により、匿名性・準匿名性の境界を厳密に管理する  
- **匿名投稿の内容および詳細分析は管理者レベル2のみが閲覧可能とし、管理者レベル1では閲覧不可とする**  
- CSV → pandas → 社員マスタ補完 の流れにより、  
  信頼性の高い分析基盤を構築する

