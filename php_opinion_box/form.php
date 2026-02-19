<?php
session_start();
if (!isset($_POST['employee_id'], $_POST['mode'])) {
    exit('不正なアクセスです');
}
$employee_id = $_POST['employee_id'];
$mode = $_POST['mode'];
$return_to = isset($_POST['return_to']) ? $_POST['return_to'] : ('http://' . $_SERVER['HTTP_HOST'] . '/login/');
$content = isset($_POST['content']) ? $_POST['content'] : '';
$tag = isset($_POST['tag']) ? $_POST['tag'] : '';
$valid_modes = ['anonymous', 'semi', 'signed'];
if (!in_array($mode, $valid_modes, true)) {
    exit('不正なモードです');
}
$_SESSION['can_post'] = true;
?>
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>入力画面</title>
    <link rel="stylesheet" href="css/style.css">
    <script src="js/validation.js"></script>
</head>
<body>
    <main class="card">
        <h1>入力画面</h1>
        <p class="sub">内容とタグを入力してください。</p>
        <form action="confirm.php" method="post" onsubmit="return validateForm();">
            <input type="hidden" name="employee_id" value="<?php echo htmlspecialchars($employee_id, ENT_QUOTES, 'UTF-8'); ?>">
            <input type="hidden" name="mode" value="<?php echo htmlspecialchars($mode, ENT_QUOTES, 'UTF-8'); ?>">
            <input type="hidden" name="return_to" value="<?php echo htmlspecialchars($return_to, ENT_QUOTES, 'UTF-8'); ?>">

            <div class="field">
                <label class="label">意見本文</label>
                <textarea name="content" rows="5" cols="40" required><?php echo htmlspecialchars($content, ENT_QUOTES, 'UTF-8'); ?></textarea>
            </div>

            <div class="field">
                <label class="label">タグ</label>
                <select name="tag" required>
                    <option value="">選択してください</option>
                    <option value="業務改善" <?php echo $tag === '業務改善' ? 'selected' : ''; ?>>業務改善</option>
                    <option value="人間関係" <?php echo $tag === '人間関係' ? 'selected' : ''; ?>>人間関係</option>
                    <option value="設備・環境" <?php echo $tag === '設備・環境' ? 'selected' : ''; ?>>設備・環境</option>
                    <option value="安全性" <?php echo $tag === '安全性' ? 'selected' : ''; ?>>安全性</option>
                    <option value="その他" <?php echo $tag === 'その他' ? 'selected' : ''; ?>>その他</option>
                </select>
            </div>

            <button class="btn" type="submit">確認</button>
        </form>
    </main>
</body>
</html>
