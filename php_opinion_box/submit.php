<?php
session_start();
if (!isset($_POST['employee_id'], $_POST['mode'], $_POST['content'], $_POST['tag'])) {
    exit('不正なアクセスです');
}
if (empty($_SESSION['can_post'])) {
    exit('不正なアクセスです');
}

$employee_id = $_POST['employee_id'];
$mode = $_POST['mode'];
$content = $_POST['content'];
$tag = $_POST['tag'];

$valid_modes = ['anonymous', 'semi', 'signed'];
if (!in_array($mode, $valid_modes, true)) {
    exit('不正なモードです');
}

if (trim($content) === '' || trim($tag) === '') {
    exit('必須項目が未入力です');
}

function escape_csv_injection($value) {
    if ($value === '') {
        return $value;
    }
    $first = $value[0];
    if ($first === '=' || $first === '+' || $first === '-' || $first === '@') {
        return "'" . $value;
    }
    return $value;
}

$content = escape_csv_injection($content);
$tag = escape_csv_injection($tag);

$timestamp = date('Y-m-d H:i:s');
$file_path = __DIR__ . '/opinions/opinion_box.csv';

$fp = fopen($file_path, 'a');
if ($fp === false) {
    echo 'CSVファイルのオープンに失敗しました';
    exit;
}

flock($fp, LOCK_EX);
$result = fputcsv($fp, [$timestamp, $employee_id, $mode, $content, $tag]);
flock($fp, LOCK_UN);
fclose($fp);

if ($result === false) {
    echo 'CSV 書き込みに失敗しました';
    exit;
}

$_SESSION['can_post'] = false;
header('Location: success.php');
exit;
?>
