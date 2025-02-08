from app.utils.logger import logger
from config import settings
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from app.bot.core.bot_instance import bot
from app.bot.validators import chat_type_required, user_status_required
from app.bot.handlers.user_handlers import (
    register_user_command,
    reg_score_user_command,
    delete_user_command,
    use_invite_code_command,
    use_renew_code_command,
    buy_invite_code_command,
    info_command,
    score_command,
    checkin_command,
    bind_command,
    unbind_command,
    help_command
)


def create_user_panel():
    """创建用户面板"""
    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(
        InlineKeyboardButton("地址", callback_data="user_help"),
        InlineKeyboardButton("注册", callback_data="user_register"),
        InlineKeyboardButton("积分用户注册", callback_data="user_reg_score"),
        InlineKeyboardButton("使用邀请码", callback_data="user_use_code"),
        InlineKeyboardButton("购买邀请码", callback_data="user_buyinvite"),
        InlineKeyboardButton("使用续期码", callback_data="user_use_renew_code"),
        InlineKeyboardButton("签到", callback_data="user_checkin"),
        InlineKeyboardButton("积分", callback_data="user_score"),
        InlineKeyboardButton("个人信息", callback_data="user_info"),
        InlineKeyboardButton("绑定/换绑", callback_data="user_bind"),
        InlineKeyboardButton("解绑", callback_data="user_unbind"),
        InlineKeyboardButton("删除用户", callback_data="user_delete"),
        InlineKeyboardButton("进群链接", url="https://t.me/navidrom_talk"),
        InlineKeyboardButton("频道链接", url="https://t.me/navidrom_notify"),
        InlineKeyboardButton("使用教程", url="https://makifx.com/1278.html"),
        InlineKeyboardButton("没有想听的歌？投稿/求歌", url="https://t.me/MaycyBot")
    )
    return markup


def create_input_markup():
    """创建输入键盘，包含取消和回到主菜单的按钮"""
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("取消输入", callback_data="user_cancel"),
        InlineKeyboardButton("回到主菜单", callback_data="panel_user")
    )
    return markup


@bot.callback_query_handler(func=lambda call: call.data == "user_cancel")
def user_cancel_callback(call):
    """处理用户取消回调"""
    chat_id = call.message.chat.id
    bot.clear_step_handler(call.message)
    bot.answer_callback_query(call.id, "已取消输入")
    bot.delete_message(chat_id, call.message.message_id)


@bot.callback_query_handler(func=lambda call: call.data == "panel_user")
def user_panel(call):
    """处理用户回到主菜单"""
    chat_id = call.message.chat.id
    bot.edit_message_text("请选择管理模块：", chat_id, call.message.message_id, reply_markup=create_user_panel(),
                          delay=None)
    bot.answer_callback_query(call.id, "显示主菜单")


@bot.message_handler(commands=['start'])
@chat_type_required(not_chat_type=["group", "supergroup"])
@user_status_required()
def start_panel_command(message):
    """显示用户面板"""
    telegram_id = message.from_user.id
    chat_id = message.chat.id
    user_name = message.from_user.username
    bot.delete_message(message.chat.id, message.message_id)
    # bot.send_message(message.chat.id, "请选择操作：", reply_markup=create_user_panel(), delay=None)
    img_url = "https://i.imgur.com/jci9UJm.jpeg"
    resp = f"*倾听音乐，享受生活！欢迎 {user_name} 来到音海拾贝！*\n"
    bot.send_photo(chat_id, img_url, resp, reply_markup=create_user_panel(), parse_mode="Markdown")


@bot.callback_query_handler(func=lambda call: call.data.startswith('user_'))
@user_status_required()
def user_panel_callback(call):
    """处理用户面板回调"""
    chat_id = call.message.chat.id
    markup = create_input_markup()
    mock_message = Message(
        message_id=call.message.message_id,
        from_user=call.from_user,
        date=call.message.date,
        chat=call.message.chat,
        content_type='text',
        options={},
        json_string=''
    )
    mock_message.text = f"/{call.data}"  # 设置模拟的命令文本

    match call.data:
        case "user_register":
            if not settings.INVITE_CODE_SYSTEM_ENABLED:
                bot.delete_message(chat_id, call.message.message_id)
                bot.send_message(chat_id, "请输入用户名和密码（格式：用户名 密码）：<30S未输入自动退出>",
                                 reply_markup=markup, delay=30)
                bot.register_next_step_handler(call.message, register_user_command)
            else:
                bot.answer_callback_query(call.id, "注册已关闭，请用邀请码注册！", show_alert=True)
                # bot.send_message(chat_id, "注册已关闭，请用邀请码注册！")
        case "user_use_code":
            bot.answer_callback_query(call.id)
            bot.delete_message(chat_id, call.message.message_id)
            bot.send_message(chat_id, "请输入邀请码（格式：邀请码）：<30S未输入自动退出>", reply_markup=markup, delay=30)
            bot.register_next_step_handler(call.message, use_invite_code_command)
        case "user_reg_score":
            bot.answer_callback_query(call.id)
            logger.info(f"用户积分注册：{call.message.chat.id}")
            reg_score_user_command(mock_message)
        case "user_use_renew_code":
            bot.answer_callback_query(call.id)
            bot.delete_message(chat_id, call.message.message_id)
            bot.send_message(chat_id, "请输入续期码：<30S未输入自动退出>", reply_markup=markup, delay=30)
            bot.register_next_step_handler(call.message, use_renew_code_command)
        case "user_delete":
            bot.answer_callback_query(call.id)
            delete_user_command(mock_message)
        case "user_buyinvite":
            bot.answer_callback_query(call.id)
            buy_invite_code_command(mock_message)
        case "user_info":
            bot.answer_callback_query(call.id)
            info_command(mock_message)
        case "user_score":
            bot.answer_callback_query(call.id)
            score_command(mock_message)
        case "user_checkin":
            bot.answer_callback_query(call.id)
            checkin_command(mock_message)
        case "user_bind":
            bot.answer_callback_query(call.id)
            bot.delete_message(chat_id, call.message.message_id)
            bot.send_message(chat_id, "请输入用户名和密码（格式：用户名 密码）：<30S未输入自动退出>",
                             reply_markup=markup, delay=30)
            bot.register_next_step_handler(call.message, bind_command)
        case "user_unbind":
            bot.answer_callback_query(call.id)
            unbind_command(mock_message)
        case "user_help":
            bot.answer_callback_query(call.id)
            help_command(mock_message)
        case _:
            bot.answer_callback_query(call.id, "未知操作，请重试！", show_alert=True)


@bot.callback_query_handler(func=lambda call: call.data == "user_cancel")
def user_cancel_callback(call):
    """处理用户取消回调"""
    bot.answer_callback_query(call.id, "已取消操作！")
    chat_id = call.message.chat.id
    bot.clear_step_handler(call.message)
    bot.send_message(chat_id, "已取消操作！")
