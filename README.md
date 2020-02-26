# Whogoodbonbon - 誰好棒棒

一個簡單的 telegram 群組內計分 bot

### 使用方式

1. 對想要加分 / 扣分的人發的訊息回覆，然後輸入 +10、-10 之類的數字即可。
2. 不可對自己加分，但是可以對自己扣分
3. 加減分不可以超過 100，否則視為灌水
4. `/score` 顯示自己分數，如果回覆別人則是顯示對方分數
5. `/list_score` 顯示所有人分數

### 安裝

使用 [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)

`pip install python-telegram-bot --upgrade`

取得 token 後替代 `bot.py` 的 token，直接執行 `bot.py` 即可

需要在 `@botfather` 那邊開啟 Allow Groups 跟關閉 Group Privacy 否則無法使用。

資料計算使用智障的 `score.json` (´・ω・｀)