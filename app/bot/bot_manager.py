# Bot 管理模块
import telebot
from config import settings
from app.utils.logger import logger
from app.bot.handlers import user_handlers, admin_handlers
from app.bot.core.bot_instance import bot
# 需要安装的模块：无

# bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)

# 注册用户命令处理函数
bot.register_message_handler(user_handlers.register_command, commands=['register'])
# bot.register_message_handler(user_handlers.start_command, commands=['start'])
# bot.register_message_handler(user_handlers.info_command, commands=['info'])
bot.register_message_handler(user_handlers.delete_user_command, commands=['deleteuser'])
bot.register_message_handler(user_handlers.score_command, commands=['score']) # 注册查询积分命令
bot.register_message_handler(user_handlers.checkin_command, commands=['checkin']) # 注册签到命令
bot.register_message_handler(user_handlers.buy_invite_code_command, commands=['buyinvite']) # 注册购买邀请码命令

# 注册管理员命令处理函数
bot.register_message_handler(admin_handlers.generate_invite_code_command, commands=['generate_code'])
bot.register_message_handler(admin_handlers.get_all_invite_codes_command, commands=['invite'])
bot.register_message_handler(admin_handlers.toggle_invite_code_system_command, commands=['toggle_invite_code_system'])
bot.register_message_handler(admin_handlers.set_score_command, commands=['set_score']) # 注册设置积分命令
bot.register_message_handler(admin_handlers.get_score_command, commands=['get_score', 'score']) # 注册查看积分命令
bot.register_message_handler(admin_handlers.add_score_command, commands=['add_score']) # 注册增加积分命令
bot.register_message_handler(admin_handlers.reduce_score_command, commands=['reduce_score']) # 注册减少积分命令

def run_bot():
    """运行 Bot"""
    logger.info("Bot 启动")
    bot.infinity_polling()

if __name__ == "__main__":
    run_bot()