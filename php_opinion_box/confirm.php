<?php
session_start();
if (!isset($_POST['employee_id'], $_POST['mode'], $_POST['content'], $_POST['tag'])) {
    exit('不正なアクセスです');
}
$employee_id = $_POST['employee_id'];
$mode = $_POST['mode'];
$return_to = isset($_POST['return_to']) ? $_POST['return_to'] : ('http://' . $_SERVER['HTTP_HOST'] . '/login/');
$content_raw = $_POST['content'];
$tag = $_POST['tag'];

$valid_modes = ['anonymous', 'semi', 'signed'];
if (!in_array($mode, $valid_modes, true)) {
    exit('不正なモードです');
}

$content = htmlspecialchars($content_raw, ENT_QUOTES, 'UTF-8');
$mode_label = [
    'anonymous' => '匿名',
    'semi' => '準匿名',
    'signed' => '署名',
][$mode];
?>
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>確認画面</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <main class="card">
        <h1>確認画面</h1>
        <p class="sub">内容に問題がなければ送信してください。</p>
        <div class="item">
            <p class="item-title">投稿形式</p>
            <p class="item-value"><?php echo $mode_label; ?></p>
        </div>
        <div class="item">
            <p class="item-title">タグ</p>
            <p class="item-value"><?php echo htmlspecialchars($tag, ENT_QUOTES, 'UTF-8'); ?></p>
        </div>
        <div class="item">
            <p class="item-title">内容</p>
            <p class="item-value"><?php echo $content; ?></p>
        </div>

        <div class="row">
            <form method="post" action="form.php">
                <input type="hidden" name="employee_id" value="<?php echo htmlspecialchars($employee_id, ENT_QUOTES, 'UTF-8'); ?>">
                <input type="hidden" name="mode" value="<?php echo htmlspecialchars($mode, ENT_QUOTES, 'UTF-8'); ?>">
                <input type="hidden" name="return_to" value="<?php echo htmlspecialchars($return_to, ENT_QUOTES, 'UTF-8'); ?>">
                <input type="hidden" name="content" value="<?php echo htmlspecialchars($content_raw, ENT_QUOTES, 'UTF-8'); ?>">
                <input type="hidden" name="tag" value="<?php echo htmlspecialchars($tag, ENT_QUOTES, 'UTF-8'); ?>">
                <button class="btn-outline" type="submit">戻る</button>
            </form>

            <form method="post" action="submit.php">
                <input type="hidden" name="employee_id" value="<?php echo htmlspecialchars($employee_id, ENT_QUOTES, 'UTF-8'); ?>">
                <input type="hidden" name="mode" value="<?php echo htmlspecialchars($mode, ENT_QUOTES, 'UTF-8'); ?>">
                <input type="hidden" name="return_to" value="<?php echo htmlspecialchars($return_to, ENT_QUOTES, 'UTF-8'); ?>">
                <input type="hidden" name="content" value="<?php echo htmlspecialchars($content, ENT_QUOTES, 'UTF-8'); ?>">
                <input type="hidden" name="tag" value="<?php echo htmlspecialchars($tag, ENT_QUOTES, 'UTF-8'); ?>">
                <button class="btn" type="submit">送信</button>
            </form>
        </div>
    </main>
</body>
</html>
