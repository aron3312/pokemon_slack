# APP
SERVICE_NAME: str = "FastApi"
DEBUG: bool = False

# Database
DB_DSN = "sqlite+aiosqlite:///record.db"
DB_ECHO: bool = False
DB_POOL_SIZE: int = 5
DB_MAX_OVERFLOW: int = 0

# Pokemon settings
max_pokemons_num = 6
enemy_lv_range = 5
enemy_basic_exp = 15
HELP_MESSAGES = "====新手教學====\n  - 訓練家您好，新加入玩家可以先使用/create_player建立帳號，會自己抓取您的slack暱稱作為帳號。\n " \
                   "- 接著您可以使用/catch_first_pokemon獲得您的第一隻寶可夢 \n - 使用/check_my_pokemon可以查看目前手上寶可夢狀況" \
                   "\n - 使用/walk_around 可以進行遇怪，並且繼續使用/walk_around加上您要出戰的寶可夢id，並跟著提示的指令輸入相對應的動作代碼，即可完成捕捉或是打怪\n" \
                   "任何疑問歡迎提出！！祝您遊玩順利"
NO_ACCOUNT_MESSAGES = "請先建立玩家喔！"
