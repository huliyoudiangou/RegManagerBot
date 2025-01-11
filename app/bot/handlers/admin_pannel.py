from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.bot.core.bot_instance import bot
from app.bot.validators import admin_required
from app.bot.handlers.admin_handlers import (
    get_user_info_by_telegram_id_command,
    get_user_info_by_username_command,
    get_user_info_in_server_command,
    set_score_command,
    add_score_command,
    reduce_score_command,
    get_score_command,
    get_score_chart_command,
    generate_invite_code_command,
    generate_renew_codes_command,
    get_all_invite_codes_command,
    get_unused_invite_codes_command,
    get_unused_renew_codes_command,
    toggle_invite_code_system_command,
    set_price_command,
    get_stats_command,
    toggle_expired_user_clean_command,
    get_expired_users_command,
    get_expiring_users_command,
    clean_expired_users_command,
    random_give_score_by_checkin_time_command,
    add_random_score_command,
    toggle_clean_msg_system_command
)

def create_admin_panel():
    """创建管理面板"""
    markup = InlineKeyboardMarkup()
    markup.row_width = 4
    markup.add(
        InlineKeyboardButton("用户管理", callback_data="admin_user_management"),
        InlineKeyboardButton("邀请码管理", callback_data="admin_invite_management"),
        InlineKeyboardButton("积分管理", callback_data="admin_score_management"),
        InlineKeyboardButton("状态管理", callback_data="admin_status_management")
    )
    return markup

def create_user_management_panel():
    """创建用户管理面板"""
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("获取用户信息 (Telegram ID)", callback_data="admin_get_user_info_by_id"),
        InlineKeyboardButton("获取用户信息 (用户名)", callback_data="admin_get_user_info_by_username"),
        InlineKeyboardButton("获取服务器用户信息", callback_data="admin_get_user_info_in_server"),
        InlineKeyboardButton("返回主菜单", callback_data="admin_main_menu")
    )
    return markup

def create_invite_management_panel():
    """创建邀请码管理面板"""
    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(
        InlineKeyboardButton("生成邀请码", callback_data="admin_generate_invite_code"),
        InlineKeyboardButton("生成续期码", callback_data="admin_generate_renew_code"),
        InlineKeyboardButton("查看所有邀请码", callback_data="admin_get_all_invite_codes"),
        InlineKeyboardButton("查看未使用邀请码", callback_data="admin_get_unused_invite_codes"),
        InlineKeyboardButton("查看未使用续期码", callback_data="admin_get_unused_renew_codes"),
        InlineKeyboardButton("设置邀请码价格", callback_data="admin_set_invite_price"),
        InlineKeyboardButton("返回主菜单", callback_data="admin_main_menu")
    )
    return markup

def create_score_management_panel():
    """创建积分管理面板"""
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("设置用户积分", callback_data="admin_set_score"),
        InlineKeyboardButton("增加用户积分", callback_data="admin_add_score"),
        InlineKeyboardButton("减少用户积分", callback_data="admin_reduce_score"),
        InlineKeyboardButton("查看用户积分", callback_data="admin_get_score"),
        InlineKeyboardButton("积分排行榜", callback_data="admin_get_score_chart"),
        InlineKeyboardButton("随机增加积分 (签到时间)", callback_data="admin_random_give_score_by_checkin_time"),
        InlineKeyboardButton("随机增加积分 (注册时间)", callback_data="admin_add_random_score"),
        InlineKeyboardButton("返回主菜单", callback_data="admin_main_menu")
    )
    return markup

def create_status_management_panel():
    """创建状态管理面板"""
    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(
        InlineKeyboardButton("获取统计信息", callback_data="admin_get_stats"),
        InlineKeyboardButton("开启/关闭邀请码系统", callback_data="admin_toggle_invite_code_system"),
        InlineKeyboardButton("开启/关闭清理系统", callback_data="admin_toggle_expired_user_clean"),
        InlineKeyboardButton("获取过期用户", callback_data="admin_get_expired_users"),
        InlineKeyboardButton("获取即将过期用户", callback_data="admin_get_expiring_users"),
        InlineKeyboardButton("清理过期用户", callback_data="admin_clean_expired_users"),
        InlineKeyboardButton("开启/关闭消息清理", callback_data="admin_toggle_clean_msg_system"),
        InlineKeyboardButton("返回主菜单", callback_data="admin_main_menu")
    )
    return markup

@bot.message_handler(commands=['admin'])
@admin_required
def admin_panel_command(message):
    """显示管理面板"""
    bot.send_message(message.chat.id, "请选择管理模块：", reply_markup=create_admin_panel(), delay=None)

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_'))
def admin_panel_callback(call):
    """处理管理面板回调"""
    chat_id = call.message.chat.id
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("取消输入", callback_data="user_cancel")
    )
    match call.data:
        case "admin_main_menu":
            bot.edit_message_text("请选择管理模块：", chat_id, call.message.message_id, reply_markup=create_admin_panel())
        case "admin_user_management":
            bot.edit_message_text("用户管理：", chat_id, call.message.message_id, reply_markup=create_user_management_panel())
        case "admin_invite_management":
            bot.edit_message_text("邀请码管理：", chat_id, call.message.message_id, reply_markup=create_invite_management_panel())
        case "admin_score_management":
            bot.edit_message_text("积分管理：", chat_id, call.message.message_id, reply_markup=create_score_management_panel())
        case "admin_status_management":
            bot.edit_message_text("状态管理：", chat_id, call.message.message_id, reply_markup=create_status_management_panel())
        case "admin_get_user_info_by_id":
            bot.send_message(chat_id, "请输入用户 Telegram ID：<30S未输入自动退出>", reply_markup=markup, delay=30)
            bot.register_next_step_handler(call.message, get_user_info_by_telegram_id_command)
        case "admin_get_user_info_by_username":
            bot.send_message(chat_id, "请输入用户名：<30S未输入自动退出>", reply_markup=markup, delay=30)
            bot.register_next_step_handler(call.message, get_user_info_by_username_command)
        case "admin_get_user_info_in_server":
            bot.send_message(chat_id, "请输入用户名：<30S未输入自动退出>", reply_markup=markup, delay=30)
            bot.register_next_step_handler(call.message, get_user_info_in_server_command)
        case "admin_generate_invite_code":
            bot.send_message(chat_id, "请输入要生成的邀请码数量：<30S未输入自动退出>", reply_markup=markup, delay=30)
            bot.register_next_step_handler(call.message, generate_invite_code_command)
        case "admin_generate_renew_code":
            bot.send_message(chat_id, "请输入续期天数和生成数量（格式：天数 数量）：<30S未输入自动退出>", reply_markup=markup, delay=30)
            bot.register_next_step_handler(call.message, generate_renew_codes_command)
        case "admin_get_all_invite_codes":
            get_all_invite_codes_command(call.message)
        case "admin_get_unused_invite_codes":
            get_unused_invite_codes_command(call.message)
        case "admin_get_unused_renew_codes":
            get_unused_renew_codes_command(call.message)
        case "admin_set_invite_price":
            bot.send_message(chat_id, "请输入邀请码价格：<30S未输入自动退出>", reply_markup=markup, delay=30)
            bot.register_next_step_handler(call.message, set_price_command)
        case "admin_set_score":
            bot.send_message(chat_id, "请输入用户 Telegram ID 和积分数（格式：ID 积分）：<30S未输入自动退出>", reply_markup=markup, delay=30)
            bot.register_next_step_handler(call.message, set_score_command)
        case "admin_add_score":
            bot.send_message(chat_id, "请输入用户 Telegram ID 和积分数（格式：ID 积分）：<30S未输入自动退出>", reply_markup=markup, delay=30)
            bot.register_next_step_handler(call.message, add_score_command)
        case "admin_reduce_score":
            bot.send_message(chat_id, "请输入用户 Telegram ID 和积分数（格式：ID 积分）：<30S未输入自动退出>", reply_markup=markup, delay=30)
            bot.register_next_step_handler(call.message, reduce_score_command)
        case "admin_get_score":
            bot.send_message(chat_id, "请输入用户 Telegram ID：<30S未输入自动退出>", reply_markup=markup, delay=30)
            bot.register_next_step_handler(call.message, get_score_command)
        case "admin_get_score_chart":
            bot.send_message(chat_id, "请输入要显示的排行榜用户数量（默认10）：<30S未输入自动退出>", reply_markup=markup, delay=30)
            bot.register_next_step_handler(call.message, get_score_chart_command)
        case "admin_random_give_score_by_checkin_time":
            bot.send_message(chat_id, "请输入签到时间范围和最大积分数（格式：范围 最大积分）：<30S未输入自动退出>", reply_markup=markup, delay=30)
            bot.register_next_step_handler(call.message, random_give_score_by_checkin_time_command)
        case "admin_add_random_score":
            bot.send_message(chat_id, "请输入注册时间范围和最大积分数（格式：开始时间 结束时间 最大积分）：<30S未输入自动退出>", reply_markup=markup, delay=30)
            bot.register_next_step_handler(call.message, add_random_score_command)
        case "admin_get_stats":
            get_stats_command(call.message)
        case "admin_toggle_invite_code_system":
            toggle_invite_code_system_command(call.message)
        case "admin_toggle_expired_user_clean":
            toggle_expired_user_clean_command(call.message)
        case "admin_get_expired_users":
            get_expired_users_command(call.message)
        case "admin_get_expiring_users":
            get_expiring_users_command(call.message)
        case "admin_clean_expired_users":
            clean_expired_users_command(call.message)
        case "admin_toggle_clean_msg_system":
            toggle_clean_msg_system_command(call.message)
        case _:
            bot.send_message(chat_id, "未知操作，请重试！")

@bot.callback_query_handler(func=lambda call: call.data == "user_cancel")
def user_cancel_callback(call):
    """处理用户取消回调"""
    chat_id = call.message.chat.id
    bot.clear_step_handler(call.message)
    bot.send_message(chat_id, "已取消操作！")