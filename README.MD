# Pokemon Slack

### usage

---

<pre>python main.py</pre>

<pre>
endpoint:
create_player [method: post] [body:{"user_name":<玩家姓名>}]
catch_first_pokemon [method:post] [body:{"user_name":<玩家姓名>}]
check_my_pokemon [method:post] [body:{"user_name":<玩家姓名>}]
walk_around [method:post] [body:{"user_name":<玩家姓名>}]
</pre>


### 如何協作

slack api request 基本上包含的格式就是 user_name (slack的使用者帳號，也就是本遊戲的帳號)

因此可以透過這個名字，去串聯資料庫中不同的資訊

我會負責的部分：
- 回合制戰鬥或捕捉
- 每日活動

目前其他需要的功能：
- 寶可夢技能系統
    - hint:db創一個skill table去串聯現有神奇寶貝
- 經驗值系統
    - 不同怪物的經驗值，以及等級的比例(新的經驗值表)
- 進化的串聯
    - hint:check目前怪獸等級，並且提供進化的串聯(創一個新表去定義進化)
    

我再開給大家上傳權限，可以先在本機去作業，到時候再上傳到不同branch，但應該會由我這邊去審核pull request並且update到server版本上

感謝！

任何其他問題歡迎在issue上提出