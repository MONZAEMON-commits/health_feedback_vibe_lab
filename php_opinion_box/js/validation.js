function validateForm() {
    var text = document.querySelector('textarea[name="content"]').value;
    if (text.trim().length === 0) {
        alert("内容が空白のみのため送信できません。");
        return false;
    }
    return true;
}
