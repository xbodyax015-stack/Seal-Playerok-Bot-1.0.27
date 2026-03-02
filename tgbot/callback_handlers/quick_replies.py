from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from settings import Settings as sett
from .. import callback_datas as calls
from ..templates.quick_replies import (
    settings_quick_replies_text, settings_quick_replies_kb, 
    quick_reply_select_kb, quick_reply_delete_kb,
    quick_reply_edit_kb
)
from ..templates.main import do_action_text, back_kb
from ..states.quick_replies import QuickReplyStates
from ..helpful import get_playerok_bot

router = Router()


@router.callback_query(calls.QuickReplyAction.filter(F.action == "add"))
async def callback_add_quick_reply(callback: CallbackQuery, state: FSMContext):
    """Активирует режим добавления новой заготовки"""
    await state.set_state(QuickReplyStates.waiting_for_name)
    await callback.message.edit_text(
        do_action_text("📝 <b>Введите название заготовки:</b>\n\n<i>Например: Приветствие, Спасибо, Ожидание</i>"),
        reply_markup=back_kb(calls.SettingsNavigation(to="quick_replies").pack()),
        parse_mode="HTML"
    )
    await callback.answer()


# Message handlers перенесены в tgbot/handlers/states_quick_replies.py


@router.callback_query(calls.QuickReplyAction.filter(F.action == "edit"))
async def callback_edit_quick_reply_select(callback: CallbackQuery, state: FSMContext):
    """Показывает список заготовок для редактирования"""
    quick_replies = sett.get("quick_replies")
    if not quick_replies:
        await callback.answer("❌ Нет заготовок для редактирования", show_alert=True)
        return
    
    await callback.message.edit_text(
        do_action_text("✏️ <b>Выберите заготовку для редактирования:</b>"),
        reply_markup=quick_reply_edit_kb(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(calls.QuickReplyAction.filter(F.action == "confirm_edit"))
async def callback_confirm_edit_quick_reply(callback: CallbackQuery, callback_data: calls.QuickReplyAction, state: FSMContext):
    """Активирует режим редактирования заготовки"""
    await state.update_data(reply_name=callback_data.reply_name)
    await state.set_state(QuickReplyStates.editing_text)
    
    quick_replies = sett.get("quick_replies")
    current_text = quick_replies.get(callback_data.reply_name, "")
    
    await callback.message.edit_text(
        do_action_text(f"✏️ <b>Редактирование заготовки '{callback_data.reply_name}'</b>\n\n<b>Текущий текст:</b>\n{current_text}\n\n📝 <b>Введите новый текст:</b>"),
        reply_markup=back_kb(calls.SettingsNavigation(to="quick_replies").pack()),
        parse_mode="HTML"
    )
    await callback.answer()


# Message handler для editing_text перенесён в tgbot/handlers/states_quick_replies.py


@router.callback_query(calls.QuickReplyAction.filter(F.action == "delete"))
async def callback_delete_quick_reply_select(callback: CallbackQuery, state: FSMContext):
    """Показывает список заготовок для удаления"""
    quick_replies = sett.get("quick_replies")
    if not quick_replies:
        await callback.answer("❌ Нет заготовок для удаления", show_alert=True)
        return
    
    await callback.message.edit_text(
        do_action_text("🗑 <b>Выберите заготовку для удаления:</b>"),
        reply_markup=quick_reply_delete_kb(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(calls.QuickReplyAction.filter(F.action == "confirm_delete"))
async def callback_confirm_delete_quick_reply(callback: CallbackQuery, callback_data: calls.QuickReplyAction, state: FSMContext):
    """Удаляет выбранную заготовку"""
    quick_replies = sett.get("quick_replies")
    if callback_data.reply_name in quick_replies:
        del quick_replies[callback_data.reply_name]
        sett.set("quick_replies", quick_replies)
        await callback.answer(f"✅ Заготовка '{callback_data.reply_name}' удалена!", show_alert=True)
    else:
        await callback.answer("❌ Заготовка не найдена", show_alert=True)
    
    await callback.message.edit_text(
        settings_quick_replies_text(),
        reply_markup=settings_quick_replies_kb(),
        parse_mode="HTML"
    )


@router.callback_query(calls.RememberUsername.filter(F.do == "quick_reply"))
async def callback_show_quick_replies(callback: CallbackQuery, callback_data: calls.RememberUsername, state: FSMContext):
    """Показывает список заготовок для отправки пользователю"""
    quick_replies = sett.get("quick_replies")
    if not quick_replies:
        await callback.answer("❌ Нет заготовок. Создайте их в настройках бота.", show_alert=True)
        return
    
    await callback.message.edit_text(
        do_action_text(f"📋 <b>Выберите заготовку для отправки пользователю {callback_data.name}:</b>"),
        reply_markup=quick_reply_select_kb(callback_data.name),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(calls.QuickReplySelect.filter())
async def callback_send_quick_reply(callback: CallbackQuery, callback_data: calls.QuickReplySelect, state: FSMContext):
    """Отправляет выбранную заготовку пользователю"""
    quick_replies = sett.get("quick_replies")
    reply_text = quick_replies.get(callback_data.reply_name)
    
    if not reply_text:
        await callback.answer("❌ Заготовка не найдена", show_alert=True)
        return
    
    try:
        playerok_bot = get_playerok_bot()
        # Получаем чат по username и отправляем сообщение
        chat = playerok_bot.account.get_chat_by_username(callback_data.username)
        if not chat:
            await callback.answer(f"❌ Чат с пользователем {callback_data.username} не найден", show_alert=True)
            return
        playerok_bot.send_message(chat.id, reply_text)
        await callback.answer(f"✅ Отправлено пользователю {callback_data.username}", show_alert=True)
        await callback.message.edit_text(
            f"✅ Сообщение отправлено пользователю <b>{callback_data.username}</b>\n\n"
            f"<b>Заготовка:</b> {callback_data.reply_name}\n"
            f"<b>Текст:</b>\n{reply_text}", 
            parse_mode="HTML"
        )
    except Exception as e:
        await callback.answer(f"❌ Ошибка отправки: {str(e)}", show_alert=True)
