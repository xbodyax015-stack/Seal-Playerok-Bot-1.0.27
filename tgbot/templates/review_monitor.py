"""Templates для раздела мониторинга отзывов"""

import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett
from .. import callback_datas as calls


def review_monitor_text():
    """Текст главной страницы мониторинга отзывов"""
    config = sett.get("config")
    review_config = config.get("playerok", {}).get("review_monitoring", {})
    messages = sett.get("messages")
    msg_data = messages.get("new_review_response", {})
    
    enabled = review_config.get("enabled", False)
    # wait_days = review_config.get("wait_days", 7)
    wait_minutes = review_config.get('wait_minutes', 10)
    check_interval = review_config.get("check_interval", 120)
    
    msg_enabled = msg_data.get("enabled", False)
    text_lines = msg_data.get("text", [])
    current_text = "\n".join(text_lines) if text_lines else "<i>Текст не задан</i>"
    
    status_icon = "🟢" if enabled else "🔴"
    status_text = "Включен" if enabled else "Выключен"
    
    msg_status_icon = "🟢" if msg_enabled else "🔴"
    msg_status_text = "Включено" if msg_enabled else "Выключено"
    
    # Получаем статистику
    try:
        from plbot.review_monitor import get_monitoring_stats
        stats = get_monitoring_stats()
        total_deals = stats["total"]
        deals_info = f"\n\n📊 <b>Сделок в мониторинге:</b> {total_deals} шт."
        # if total_deals > 0:
        #
        #     for deal in stats["deals"][:5]:  # Показываем только первые 5
        #         deals_info += f"\n • Сделка #{deal['deal_id']}: {deal['user']} ({deal['days_elapsed']} дн.)"
        #     if total_deals > 5:
        #         deals_info += f"\n   <i>... и ещё {total_deals - 5}</i>"
        # else:
        #     deals_info = "\n\n📊 <b>Сделки в мониторинге:</b> нет"
    except:
        deals_info = ""
    
    txt = textwrap.dedent(f"""
⭐ <b>Мониторинг отзывов</b>

Эта функция автоматически отслеживает подтверждённые сделки и отправляет сообщение покупателю после того, как он оставит отзыв.

<b>Статус мониторинга:</b> {status_icon} {status_text}
<b>Время ожидания отзыва:</b> {wait_minutes} минут.
<b>Интервал проверки:</b> {check_interval} секунд.

<b>Автоответ при получении отзыва:</b> {msg_status_icon} {msg_status_text}

<b>Текущее сообщение:</b>
<code>{current_text}</code>{deals_info}

Используйте кнопки ниже для управления ↓
""")
    return txt


def review_monitor_kb():
    """Клавиатура главной страницы мониторинга отзывов"""
    config = sett.get("config")
    review_config = config.get("playerok", {}).get("review_monitoring", {})
    
    enabled = review_config.get("enabled", False)
    
    monitor_toggle_text = "🟢 Мониторинг включён" if enabled else "🔴 Мониторинг выключен"

    rows = [
        [InlineKeyboardButton(
            text=monitor_toggle_text, 
            callback_data=calls.ReviewMonitorToggle().pack()
        )],
        [InlineKeyboardButton(
            text="⏱️ Изменить время ожидания", 
            callback_data=calls.ReviewMonitorAction(action="set_interval").pack()
        )],
        [InlineKeyboardButton(
            text="⚙️ Автоответ на отзывы", 
            callback_data=calls.SettingsNavigation(to="autoresponse_review").pack()
        )],
        [InlineKeyboardButton(
            text="⬅️ Назад в меню", 
            callback_data=calls.MenuPagination(page=0).pack()
        )]
    ]
    
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb
