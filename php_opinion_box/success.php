<?php
$return_to = isset($_GET['return_to']) ? $_GET['return_to'] : ('http://' . $_SERVER['HTTP_HOST'] . '/login/');
?>
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>完了</title>
    <meta http-equiv="refresh" content="10;URL=<?php echo htmlspecialchars($return_to, ENT_QUOTES, 'UTF-8'); ?>">
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <main class="card">
        <h1>投稿が完了しました</h1>
        <p class="sub">10秒後にログイン画面へ戻ります。</p>
        <a class="link-btn" href="<?php echo htmlspecialchars($return_to, ENT_QUOTES, 'UTF-8'); ?>">ログイン画面へ戻る</a>
    </main>
</body>
</html>
