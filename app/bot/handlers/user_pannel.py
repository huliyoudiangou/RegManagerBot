from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.bot.core.bot_instance import bot
from app.bot.handlers.user_handlers import (
    register_user_command,
    reg_score_user_command,
    update_user_command,
    use_invite_code_command,
    use_renew_code_command,
    buy_invite_code_command,
    info_command,
    score_command,
    checkin_command,
    bind_command,
    unbind_command
)

def create_user_panel():
    """创建用户面板"""
    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(
        InlineKeyboardButton("注册", callback_data="user_register"),
        InlineKeyboardButton("邀请码注册", callback_data="user_use_code"),
        InlineKeyboardButton("更新用户", callback_data="user_update"),
        InlineKeyboardButton("使用续期码", callback_data="user_use_renew_code"),
        InlineKeyboardButton("购买邀请码", callback_data="user_buyinvite"),
        InlineKeyboardButton("个人信息", callback_data="user_info"),
        InlineKeyboardButton("积分", callback_data="user_score"),
        InlineKeyboardButton("签到", callback_data="user_checkin"),
        InlineKeyboardButton("绑定", callback_data="user_bind"),
        InlineKeyboardButton("解绑", callback_data="user_unbind")
    )
    return markup

@bot.message_handler(commands=['start'])
def start_panel_command(message):
    """显示用户面板"""
    bot.send_message(message.chat.id, "请选择操作：", reply_markup=create_user_panel(), delay=None)

@bot.callback_query_handler(func=lambda call: call.data.startswith('user_'))
def user_panel_callback(call):
    """处理用户面板回调"""
    chat_id = call.message.chat.id
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("取消输入", callback_data="user_cancel")
    )
    match call.data:
        case "user_register":
            bot.send_message(chat_id, "请输入用户名和密码（格式：用户名 密码）：<30S未输入自动退出>", reply_markup=markup, delay=30)
            bot.register_next_step_handler(call.message, register_user_command)
        case "user_use_code":
            bot.send_message(chat_id, "请输入邀请码（格式：邀请码）：<30S未输入自动退出>", reply_markup=markup, delay=30)
            bot.register_next_step_handler(call.message, use_invite_code_command)
        case "user_use_renew_code":
            bot.send_message(chat_id, "请输入续期码：<30S未输入自动退出>", reply_markup=markup, delay=30)
            bot.register_next_step_handler(call.message, use_renew_code_command)
        case "user_update":
            bot.send_message(chat_id, "请输入用户名和密码（格式：用户名 密码）：<30S未输入自动退出>", reply_markup=markup, delay=30)
            bot.register_next_step_handler(call.message, update_user_command)
        case "user_buyinvite":
            buy_invite_code_command(call.message)
        case "user_info":
            info_command(call.message)
        case "user_score":
            score_command(call.message)
        case "user_checkin":
            checkin_command(call.message)
        case "user_bind":
            bot.send_message(chat_id, "请输入用户名和用户 ID（格式：用户名 用户ID）：<30S未输入自动退出>", reply_markup=markup, delay=30)
            bot.register_next_step_handler(call.message, bind_command)
        case "user_unbind":
            unbind_command(call.message)
        case _:
            bot.send_message(chat_id, "未知操作，请重试！")

@bot.callback_query_handler(func=lambda call: call.data == "user_cancel")
def user_cancel_callback(call):
    """处理用户取消回调"""
    chat_id = call.message.chat.id
    bot.clear_step_handler(call.message)
    bot.send_message(chat_id, "已取消操作！")
