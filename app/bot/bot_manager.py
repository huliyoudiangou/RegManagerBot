import telebot
from config import settings
from app.utils.logger import logger
from app.bot.handlers import user_handlers, admin_handlers
from app.bot.core.bot_instance import bot
# 需要安装的模块：无
class BotManager:
    def __init__(self):
        self.bot = bot

        # 定义命令列表
        commands = [
            telebot.types.BotCommand("start", "简介"),
            telebot.types.BotCommand("help", "可用命令"),
            telebot.types.BotCommand("register", "注册用户 (需要提供用户名和密码)"),
            telebot.types.BotCommand("info", "查看个人信息"),
            telebot.types.BotCommand("deleteuser", "删除用户"),
            telebot.types.BotCommand("score", "查看我的积分"),
            telebot.types.BotCommand("checkin", "签到"),
            telebot.types.BotCommand("buyinvite", "购买邀请码"),
            telebot.types.BotCommand("reset_password", "重置密码"),
            telebot.types.BotCommand("give", "赠送积分"),
            telebot.types.BotCommand("bind", "绑定账号"),
            telebot.types.BotCommand("unbind", "解绑账号"),
            telebot.types.BotCommand("generate_code", "生成邀请码 (管理员)"),
            telebot.types.BotCommand("invite", "查看所有邀请码 (管理员)"),
            telebot.types.BotCommand("toggle_invite_code_system", "开启/关闭邀请码系统 (管理员)"),
            telebot.types.BotCommand("set_score", "设置用户积分 (管理员)"),
            telebot.types.BotCommand("get_score", "查看用户积分 (管理员)"),
            telebot.types.BotCommand("add_score", "增加用户积分 (管理员)"),
            telebot.types.BotCommand("reduce_score", "减少用户积分 (管理员)"),
            telebot.types.BotCommand("set_price", "设置积分价格 (管理员)"),
            telebot.types.BotCommand("userinfo", "获取用户信息 (管理员)"),
            telebot.types.BotCommand("userinfo_by_username", "通过用户名获取用户信息 (管理员)"),
            telebot.types.BotCommand("stats", "获取注册状态 (管理员)")
        ]
        # 设置Bot命令
        self.bot.set_my_commands(commands)

        # 注册路由
        bot.register_message_handler(user_handlers.start_command, commands=['start'])
        bot.register_message_handler(user_handlers.help_command, commands=['help'])
        bot.register_message_handler(user_handlers.register_command, commands=['register'])
        bot.register_message_handler(user_handlers.info_command, commands=['info'])
        bot.register_message_handler(user_handlers.delete_user_command, commands=['deleteuser'])
        bot.register_message_handler(user_handlers.score_command, commands=['score'])
        bot.register_message_handler(user_handlers.checkin_command, commands=['checkin'])
        bot.register_message_handler(user_handlers.buy_invite_code_command, commands=['buyinvite'])
        bot.register_message_handler(user_handlers.reset_password_command, commands=['reset_password'])
        bot.register_message_handler(user_handlers.give_score_command, commands=['give'])
        bot.register_message_handler(user_handlers.bind_command, commands=['bind'])
        bot.register_message_handler(user_handlers.unbind_command, commands=['unbind'])
    
         # 注册管理员命令处理函数
        bot.register_message_handler(admin_handlers.generate_invite_code_command, commands=['generate_code'])
        bot.register_message_handler(admin_handlers.get_all_invite_codes_command, commands=['invite'])
        bot.register_message_handler(admin_handlers.toggle_invite_code_system_command, commands=['toggle_invite_code_system'])
        bot.register_message_handler(admin_handlers.set_score_command, commands=['set_score'])
        bot.register_message_handler(admin_handlers.get_score_command, commands=['get_score', 'score'])
        bot.register_message_handler(admin_handlers.add_score_command, commands=['add_score'])
        bot.register_message_handler(admin_handlers.reduce_score_command, commands=['reduce_score'])
        bot.register_message_handler(admin_handlers.set_price_command, commands=['set_price'])
        bot.register_message_handler(admin_handlers.get_user_info_by_telegram_id_command, commands=['userinfo'])
        bot.register_message_handler(admin_handlers.get_user_info_by_username_command, commands=['userinfo_by_username'])
        bot.register_message_handler(admin_handlers.get_stats_command, commands=['stats'])

    def get_bot(self):
       return self.bot

def run_bot():
    """运行 Bot"""
    logger.info("Bot 启动")
    bot_manager = BotManager()
    bot = bot_manager.get_bot()
    bot.infinity_polling()

if __name__ == "__main__":
    run_bot()