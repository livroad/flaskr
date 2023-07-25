// チェック間隔（ミリ秒）
const checkInterval = 15000; // 1分

// ログイン状態のフラグ
let isLoggedin = false;

// セッションの有効性をチェックする関数
function checkSessionValidity() {
    fetch('/check_session')
        .then(response => {
            if (response.status === 401) {
                // セッションが切れた場合、ページをリロードしてログアウト状態にする
                location.reload();
            }
        })
        .catch(error => console.error('Error:', error))
        .finally(() => {
            // チェック後は指定した間隔で再度チェックする
            setTimeout(checkSessionValidity, checkInterval);
        });
}

// ログイン状態の場合のみセッションの有効性を定期的にチェックを開始
fetch('/is_logged_in')
    .then(response => response.json())
    .then(data => {
        isLoggedin = data.is_logged_in;
        if (isLoggedin) {
            checkSessionValidity();
        }
    })
    .catch(error => console.error('Error:', error));
