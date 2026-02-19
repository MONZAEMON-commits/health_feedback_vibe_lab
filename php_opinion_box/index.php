<?php
session_start();
$employee_id = isset($_GET['id']) ? $_GET['id'] : '';
if ($employee_id === '') {
    echo 'employee_id が必要です。';
    exit;
}
$return_to = isset($_GET['return_to']) ? $_GET['return_to'] : '';
if ($return_to === '') {
    $return_to = 'http://' . $_SERVER['HTTP_HOST'] . '/login/';
}
?>
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>投稿形式選択</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <main class="card">
        <h1>投稿形式選択</h1>
        <p class="sub">投稿形式を選んで次へ進んでください。</p>
        <form method="post" action="form.php">
            <input type="hidden" name="employee_id" value="<?php echo htmlspecialchars($employee_id, ENT_QUOTES, 'UTF-8'); ?>">
            <input type="hidden" name="return_to" value="<?php echo htmlspecialchars($return_to, ENT_QUOTES, 'UTF-8'); ?>">
            <div class="mode-list">
                <label class="mode-option"><input type="radio" name="mode" value="anonymous" required> 匿名</label>
                <label class="mode-option"><input type="radio" name="mode" value="semi" required> 準匿名</label>
                <label class="mode-option"><input type="radio" name="mode" value="signed" required> 署名</label>
            </div>
            <button class="btn" type="submit">進む</button>
        </form>
    </main>
</body>
</html>
