import asyncio
import logging
import json
import os
import io
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# ==========================================
# КОНФИГУРАЦИЯ
# ==========================================
TOKEN = "8365296454:AAFEZahhInOwtRv6RoHcRCX5ioSm-5G3G9o"
# Главный админ (Босс) - только он может добавлять/удалять других админов
MAIN_ADMIN_ID = 8274761521 
DB_FILE = "languages_db.json"

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(
    token=TOKEN, 
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

# Временное хранилище для инвайт-токенов
INVITE_TOKENS = {}

# ==========================================
# ЛОКАЛИЗАЦИЯ БОТА (ИНТЕРФЕЙС)
# ==========================================

BOT_STRINGS = {
    "ru": {
        # ИСПРАВЛЕНО: Убраны дублирующиеся эмодзи перед тегом
        "start_text": "<tg-emoji emoji-id='5449408995691341691'>🇷🇺</tg-emoji> выберите язык бота:\n<tg-emoji emoji-id='5202021044105257611'>🇺🇸</tg-emoji> select the language of the bot:",
        "main_menu_text": "{0} каталог языков для плагина <b>Recent Chats Fork</b>\n\nиспользуйте кнопки ниже чтобы выбрать язык или ознакомиться с инструкцией",
        "btn_custom": "кастомные",
        "btn_global": "глобальные",
        "btn_manual": "инструкция",
        "btn_manage": "⚙️ Управление",
        "cat_choice": "{0} выберите {1} язык",
        "cat_type_custom": "кастомный",
        "cat_type_global": "глобальный",
        "back": "назад",
        "install": "установить",
        "delete_admin": "🗑 Удалить (Админ)",
        "lang_view_title": "<b>название:</b> {0}",
        "lang_view_stats": "<b>переведено строк:</b> <code>{0}/{1}</code>",
        "lang_view_date": "<b>последнее обновление:</b> <code>{0}</code>",
        "lang_view_desc": "<b>описание:</b> <code>{0}</code>",
        "lang_view_footer": "для установки нажмите <b>установить</b> под этим сообщением и скопируйте содержимое файла",
        "file_sent": "файл отправлен ниже {0}",
        "to_menu": "в меню",
        "admin_panel_title": "<b>админ панель</b>\n\nздесь ты можешь управлять языками добавлять и создавать новый",
        "btn_manage_langs": "управление языками",
        "btn_admins": "админы",
        "manage_langs_title": "<b>управление языками</b>",
        "btn_create_new": "создать новый",
        "btn_add_string": "добавить строку",
        "admins_list_title": "<b>Список админов ({0}):</b>\nНажмите на админа для управления.",
        "admin_manage_user_title": "<b>Управление админом:</b>\nID: <code>{0}</code>",
        "btn_delete_admin_user": "🗑 Удалить права админа",
        "btn_gen_invite": "создать приглашение",
        "invite_text": "<b>Одноразовая ссылка для нового админа:</b>\n<code>{0}</code>\n\nПерешлите её. После перехода он станет админом.",
        "lang_deleted": "Язык удален.",
        "admin_removed": "Админ {0} удален.",
        "access_denied": "У вас нет прав на это действие.",
        "wiz_step1": "<b>выберите категорию:</b>\n1 из 4",
        "wiz_step2": "<b>введите название:</b>\n2 из 4",
        "wiz_step3": "<b>добавьте описание</b>\n3 из 4",
        "wiz_step4": "создать с нуля? или загрузить готовый?",
        "wiz_btn_scratch": "создать новый",
        "wiz_btn_upload": "загрузить готовый",
        "wiz_upload_ask": "Отправьте .json или .lang файл",
        "wiz_done": "язык добавлен",
        "trans_panel": "<b>панель переводчика</b>\n<blockquote><b>язык:</b> {0}\nпереведено {1} из {2}</blockquote>",
        "trans_publish": "✅ опубликовать",
        "trans_next": "далее",
        "trans_apply": "применить",
        "lang_changed": "Язык изменен на Русский 🇷🇺"
    },
    "en": {
        "start_text": "Select bot language:", 
        "main_menu_text": "{0} <b>Recent Chats Fork</b> Language Catalog\n\nUse the buttons below to select a language or read the manual",
        "btn_custom": "Custom",
        "btn_global": "Global",
        "btn_manual": "Manual",
        "btn_manage": "⚙️ Management",
        "cat_choice": "{0} select {1} language",
        "cat_type_custom": "custom",
        "cat_type_global": "global",
        "back": "Back",
        "install": "Install",
        "delete_admin": "🗑 Delete (Admin)",
        "lang_view_title": "<b>Name:</b> {0}",
        "lang_view_stats": "<b>Translated lines:</b> <code>{0}/{1}</code>",
        "lang_view_date": "<b>Last update:</b> <code>{0}</code>",
        "lang_view_desc": "<b>Description:</b> <code>{0}</code>",
        "lang_view_footer": "Press <b>Install</b> below and copy the file content",
        "file_sent": "File sent below {0}",
        "to_menu": "Main Menu",
        "admin_panel_title": "<b>Admin Panel</b>\n\nManage languages, add new ones, or manage admins here.",
        "btn_manage_langs": "Manage Languages",
        "btn_admins": "Admins",
        "manage_langs_title": "<b>Manage Languages</b>",
        "btn_create_new": "Create New",
        "btn_add_string": "Add String",
        "admins_list_title": "<b>Admin List ({0}):</b>\nClick on an admin to manage.",
        "admin_manage_user_title": "<b>Manage Admin:</b>\nID: <code>{0}</code>",
        "btn_delete_admin_user": "🗑 Remove Admin Rights",
        "btn_gen_invite": "Create Invite",
        "invite_text": "<b>One-time link for new admin:</b>\n<code>{0}</code>\n\nForward this. They will become admin upon clicking.",
        "lang_deleted": "Language deleted.",
        "admin_removed": "Admin {0} removed.",
        "access_denied": "Access denied.",
        "wiz_step1": "<b>Select Category:</b>\n1 of 4",
        "wiz_step2": "<b>Enter Name:</b>\n2 of 4",
        "wiz_step3": "<b>Enter Description:</b>\n3 of 4",
        "wiz_step4": "Create from scratch or upload existing?",
        "wiz_btn_scratch": "Create New",
        "wiz_btn_upload": "Upload File",
        "wiz_upload_ask": "Send .json or .lang file",
        "wiz_done": "Language added",
        "trans_panel": "<b>Translator Panel</b>\n<blockquote><b>Lang:</b> {0}\nProgress {1} of {2}</blockquote>",
        "trans_publish": "✅ Publish",
        "trans_next": "Next",
        "trans_apply": "Apply",
        "lang_changed": "Language changed to English 🇺🇸"
    }
}

# ==========================================
# БАЗОВЫЙ ШАБЛОН (ДЛЯ ПЛАГИНА)
# ==========================================
BASE_TEMPLATE = {
    "extended_settings_hello": "Привет, {0}!",
    "general": "Общие",
    "other": "Другое",
    "footer": "v{0} | автор оригинального плагина - @oodze...",
    "clip_empty": "Буфер обмена пуст",
    "lang_applied": "Языковой пакет применен!",
    "lang_invalid": "Ошибка: Некорректный JSON",
    "err_open_channel": "Не удалось открыть канал",
    "deleted_account": "Deleted Account",
    "empty_list": "Список выбранных чатов пуст",
    "action_remove": "Удалить этот чат",
    "action_add": "Добавить этот чат",
    "chat_removed": "Чат удален из списка",
    "chat_added": "Чат добавлен в список",
    "yes": "Да",
    "no": "Нет",
    "menu_filters": "Фильтры чатов",
    "menu_appearance": "Внешний вид",
    "menu_advanced": "Тонкая настройка",
    "menu_updates": "Обновления",
    "menu_language": "Языковые пакеты",
    "lang_header": "Настройка языка",
    "lang_import_clip": "Применить из буфера",
    "lang_reset": "Сбросить (Русский)",
    "lang_info": "Скопируйте JSON с языковым пакетом...",
    "catalog": "Каталог | Catalog",
    "catalog_desc": "Там можно скачать любой язык...",
    "filters_mode_header": "Выборочный режим",
    "filter_only_selected": "Только выбранные чаты",
    "setup_list": "Настроить список",
    "filter_desc": "Если включено, будут отображаться только чаты...",
    "filter_show_header": "Какие чаты показывать?",
    "filter_users": "Личные сообщения",
    "filter_groups": "Группы",
    "filter_channels": "Каналы",
    "filter_bots": "Боты",
    "wl_params": "Параметры",
    "wl_btn": "Быстрая кнопка",
    "wl_btn_desc": "Показывать быструю кнопку добавления...",
    "wl_chats_header": "Выбранные чаты",
    "search_placeholder": "Поиск...",
    "add_placeholder": "Добавить (username или ID)",
    "add_action": "Добавить в список",
    "list_empty_text": "Список пуст.",
    "nothing_found": "Ничего не найдено",
    "clear_list": "Очистить список",
    "wl_info": "Только эти чаты будут отображаться...",
    "err_enter_id": "Введите username или ID",
    "err_invalid_username": "Неверный формат username",
    "err_invalid_id": "Неверный ID или username",
    "added_success": "Добавлено в список",
    "delete_title": "Удаление",
    "delete_confirm": "Удалить",
    "deleted_success": "Удалено из списка",
    "clear_title": "Очистка",
    "clear_confirm": "Очистить список избранных чатов?",
    "list_cleared": "Список очищен",
    "display_header": "Внешний вид списка",
    "max_chats": "Макс. количество чатов",
    "show_pinned": "Закреплённые сверху",
    "hide_muted": "Скрыть замьюченные",
    "show_unread": "Только непрочитанные",
    "anim_header": "Анимации",
    "anim_menu": "Меню",
    "anim_scale": "Масштаб",
    "anim_alpha": "Прозрачность",
    "anim_slide": "Сдвиг снизу",
    "anim_menu_desc": "Определяет, как появляется само окно...",
    "anim_list": "Список",
    "anim_list_cascade_bot": "Каскад снизу",
    "anim_list_cascade_side": "Каскад сбоку",
    "anim_list_scale": "Масштаб и появление",
    "anim_list_desc": "Определяет, как появляются строки...",
    "adv_header": "Параметры кнопки и меню",
    "enable": "Включить",
    "pop_w": "Ширина меню (dp)",
    "pop_x": "Отступ меню X (dp)",
    "pop_y": "Отступ меню Y (dp)",
    "btn_y": "Позиция кнопки Y (dp)",
    "btn_x": "Позиция кнопки X (dp)",
    "btn_w": "Ширина кнопки (dp)",
    "btn_h": "Высота кнопки (dp)",
    "bg_alpha": "Прозрачность фона (0-255)",
    "adv_desc": "Включите настройку, чтобы изменить координаты.",
    "updates_header": "Обновления",
    "auto_upd": "Автообновления",
    "check_upd": "Проверить обновления",
    "other_ver": "Другие версии",
    "upd_err_check": "Не удалось проверить обновления",
    "upd_latest": "У вас актуальная версия",
    "upd_err_hash": "Несовпадение хеша",
    "upd_checking": "Идёт проверка обновлений...",
    "upd_avail": "Доступно обновление",
    "upd_new_ver": "Вышла новая версия",
    "upd_cur_ver": "Текущая",
    "upd_what_do": "Что делать?",
    "upd_btn": "Обновить",
    "upd_changelog": "Что изменилось?",
    "cancel": "Отмена",
    "upd_success": "Обновлено до",
    "restart_needed": "Перезапустите клиент!",
    "upd_failed": "Не удалось обновить плагин",
    "backups_header": "Другие версии",
    "backups_empty": "Нет других версий",
    "ver": "Версия",
    "backups_hint": "Нажми - восстановить версию...",
    "restore_title": "Откат",
    "restore_confirm": "Восстановить версию из",
    "restore_desc": "Текущая версия будет сохранена как бэкап.",
    "restore_success": "Версия восстановлена!",
    "restore_failed": "Не удалось восстановить версию",
    "del_backup_title": "Удаление бэкапа",
    "del_backup_confirm": "Удалить",
    "forever": "навсегда",
    "backup_deleted": "Бэкап удалён",
    "file_not_found": "Файл не найден",
    "del_backup_failed": "Не удалось удалить бэкап"
}

TRANSLATION_CATEGORIES = {
    "filters": {
        "name": "Фильтры чатов",
        "keys": ["menu_filters", "filters_mode_header", "filter_only_selected", "setup_list", "filter_desc", "filter_show_header", "filter_users", "filter_groups", "filter_channels", "filter_bots", "wl_params", "wl_btn", "wl_btn_desc", "wl_chats_header", "search_placeholder", "add_placeholder", "add_action", "list_empty_text", "nothing_found", "clear_list", "wl_info", "err_enter_id", "err_invalid_username", "err_invalid_id", "added_success", "delete_title", "delete_confirm", "deleted_success", "clear_title", "clear_confirm", "list_cleared"]
    },
    "appearance": {
        "name": "Внешний вид",
        "keys": ["menu_appearance", "display_header", "max_chats", "show_pinned", "hide_muted", "show_unread", "anim_header", "anim_menu", "anim_scale", "anim_alpha", "anim_slide", "anim_menu_desc", "anim_list", "anim_list_cascade_bot", "anim_list_cascade_side", "anim_list_scale", "anim_list_desc"]
    },
    "advanced": {
        "name": "Тонкая настройка",
        "keys": ["menu_advanced", "adv_header", "enable", "pop_w", "pop_x", "pop_y", "btn_y", "btn_x", "btn_w", "btn_h", "bg_alpha", "adv_desc"]
    },
    "updates": {
        "name": "Обновления",
        "keys": ["menu_updates", "updates_header", "auto_upd", "check_upd", "other_ver", "upd_err_check", "upd_latest", "upd_err_hash", "upd_checking", "upd_avail", "upd_new_ver", "upd_cur_ver", "upd_what_do", "upd_btn", "upd_changelog", "upd_success", "restart_needed", "upd_failed", "backups_header", "backups_empty", "ver", "backups_hint", "restore_title", "restore_confirm", "restore_desc", "restore_success", "restore_failed", "del_backup_title", "del_backup_confirm", "forever", "backup_deleted", "file_not_found", "del_backup_failed"]
    },
    "general": {
        "name": "Другое",
        "keys": ["extended_settings_hello", "extended_settings_subtitle", "general", "other", "footer", "clip_empty", "lang_applied", "lang_invalid", "err_open_channel", "deleted_account", "empty_list", "action_remove", "action_add", "chat_removed", "chat_added", "yes", "no", "lang_header", "lang_import_clip", "lang_reset", "lang_info", "catalog", "catalog_desc", "cancel"]
    }
}

# ==========================================
# КЛАСС БД
# ==========================================

class DB:
    def __init__(self, filename):
        self.filename = filename
        self.data = self._load()

    def _load(self):
        default_data = {
            "languages": [], 
            "admins": [MAIN_ADMIN_ID],
            "users": {} # user_id: "ru" or "en"
        }
        if not os.path.exists(self.filename):
            return default_data
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "languages" not in data: data["languages"] = []
                if "admins" not in data: data["admins"] = [MAIN_ADMIN_ID]
                if "users" not in data: data["users"] = {}
                # Конвертация ключей пользователей в int (JSON хранит ключи как str)
                data["users"] = {int(k): v for k, v in data["users"].items()}
                return data
        except Exception:
            return default_data

    def save(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            # При сохранении ключи словаря users станут строками, это норм для JSON
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def add_language(self, lang_data):
        self.data["languages"].append(lang_data)
        self.save()
    
    def remove_language(self, lang_id):
        self.data["languages"] = [l for l in self.data["languages"] if l["id"] != lang_id]
        self.save()

    def get_languages(self, lang_type=None):
        if lang_type:
            return [l for l in self.data["languages"] if l.get("type") == lang_type]
        return self.data["languages"]

    def get_language_by_id(self, lang_id):
        for l in self.data["languages"]:
            if l["id"] == lang_id:
                return l
        return None

    def get_admins(self):
        return self.data.get("admins", [MAIN_ADMIN_ID])

    def add_admin(self, user_id):
        if user_id not in self.data["admins"]:
            self.data["admins"].append(user_id)
            self.save()
            return True
        return False
    
    def remove_admin(self, user_id):
        if user_id in self.data["admins"] and user_id != MAIN_ADMIN_ID:
            self.data["admins"].remove(user_id)
            self.save()
            return True
        return False

    def set_user_lang(self, user_id, lang_code):
        self.data["users"][user_id] = lang_code
        self.save()

    def get_user_lang(self, user_id):
        return self.data["users"].get(user_id, None)

db = DB(DB_FILE)

# ==========================================
# ЭМОДЗИ И УТИЛИТЫ
# ==========================================

def get_tg_emoji(emoji_id, fallback):
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'

EMOJI_CATALOG = get_tg_emoji("5294233717072497688", "🐱")
EMOJI_CUSTOM = get_tg_emoji("5431456208487716895", "🎨")
EMOJI_GLOBAL = get_tg_emoji("5397753673130463064", "🌏")
EMOJI_FILE = get_tg_emoji("5470177992950946662", "👇")
EMOJI_ADMIN = get_tg_emoji("5931546553868095844", "🔨")
EMOJI_MANAGE = get_tg_emoji("5879585266426973039", "🌐")
EMOJI_CATEGORY = get_tg_emoji("5431736674147114227", "🗂")
EMOJI_EDIT = get_tg_emoji("5985774024968379294", "🖊")
EMOJI_DESC = get_tg_emoji("6006038041448156880", "📝")
EMOJI_THINK = get_tg_emoji("5370724846936267183", "🤔")
EMOJI_TRANSLATE = get_tg_emoji("5373141891321699086", "😎")
EMOJI_DONE = get_tg_emoji("5294233717072497688", "🐱")

class AdminStates(StatesGroup):
    creating_cat = State()
    creating_name = State()
    creating_desc = State()
    creating_method = State()
    uploading_file = State()
    translating_dashboard = State()
    translating_input = State()
    add_string_code = State()
    add_string_value = State()

# Функция получения текста
def TR(key, user_id, *args):
    lang = db.get_user_lang(user_id) or "ru"
    text = BOT_STRINGS.get(lang, BOT_STRINGS["ru"]).get(key, key)
    if args:
        try:
            return text.format(*args)
        except:
            return text
    return text

# ==========================================
# ХЕНДЛЕРЫ: СТАРТ, ЯЗЫК, КОМАНДЫ
# ==========================================

# НОВЫЕ КОМАНДЫ ДЛЯ СМЕНЫ ЯЗЫКА
@router.message(Command("ru"))
async def cmd_set_ru(message: types.Message):
    db.set_user_lang(message.from_user.id, "ru")
    await message.answer(TR("lang_changed", message.from_user.id))
    await show_catalog_main(message)

@router.message(Command("en"))
async def cmd_set_en(message: types.Message):
    db.set_user_lang(message.from_user.id, "en")
    await message.answer(TR("lang_changed", message.from_user.id))
    await show_catalog_main(message)


@router.message(CommandStart())
async def cmd_start(message: types.Message, command: CommandObject):
    user_id = message.from_user.id
    
    # 1. Проверка на инвайт админа
    args = command.args
    if args and args.startswith("admin_"):
        token = args.split("_")[1]
        if token in INVITE_TOKENS:
            db.add_admin(user_id)
            del INVITE_TOKENS[token]
            await message.answer(f"{EMOJI_ADMIN} <b>Доступ получен!</b>")
            # После успешного инвайта показываем выбор языка, если его нет
            if not db.get_user_lang(user_id):
                await show_lang_selection(message)
            else:
                await show_catalog_main(message)
            return
        else:
            await message.answer("Ссылка недействительна.")
            return

    # 2. Проверка: выбран ли язык бота
    if not db.get_user_lang(user_id):
        await show_lang_selection(message)
    else:
        await show_catalog_main(message)

async def show_lang_selection(message: types.Message):
    # Текст из конфига (смешанный RU/EN)
    text = BOT_STRINGS["ru"]["start_text"]
    
    kb = InlineKeyboardBuilder()
    kb.button(text="🇷🇺 Русский", callback_data="set_bot_ru")
    kb.button(text="🇺🇸 English", callback_data="set_bot_en")
    kb.adjust(2)
    
    await message.answer(text, reply_markup=kb.as_markup())

@router.callback_query(F.data.startswith("set_bot_"))
async def set_bot_language(call: types.CallbackQuery):
    lang_code = call.data.split("_")[2] # ru or en
    db.set_user_lang(call.from_user.id, lang_code)
    
    # После выбора языка сразу редактируем сообщение на главное меню
    await show_catalog_main(call.message, is_edit=True, user_id=call.from_user.id)

# ==========================================
# ХЕНДЛЕРЫ: КАТАЛОГ
# ==========================================

async def show_catalog_main(message: types.Message, is_edit=False, user_id=None):
    if not user_id: user_id = message.chat.id # fallback if msg object differs
    
    text = TR("main_menu_text", user_id, EMOJI_CATALOG)
    
    kb = InlineKeyboardBuilder()
    kb.button(text=TR("btn_custom", user_id), callback_data="cat_custom")
    kb.button(text=TR("btn_global", user_id), callback_data="cat_global")
    kb.button(text=TR("btn_manual", user_id), url="https://t.me/huixplug")
    
    # Кнопка для админов
    if user_id in db.get_admins():
        kb.button(text=TR("btn_manage", user_id), callback_data="admin_entry")

    kb.adjust(2, 1, 1)

    if is_edit:
        await message.edit_text(text, reply_markup=kb.as_markup())
    else:
        await message.answer(text, reply_markup=kb.as_markup())

@router.callback_query(F.data.startswith("cat_"))
async def show_category(call: types.CallbackQuery):
    uid = call.from_user.id
    cat_type = call.data.split("_")[1]
    
    emoji = EMOJI_CUSTOM if cat_type == "custom" else EMOJI_GLOBAL
    cat_name = TR(f"cat_type_{cat_type}", uid)
    
    text = TR("cat_choice", uid, emoji, cat_name)
    
    langs = db.get_languages(cat_type)
    
    kb = InlineKeyboardBuilder()
    for lang in langs:
        kb.button(text=lang["name"], callback_data=f"view_lang_{lang['id']}")
    kb.button(text=TR("back", uid), callback_data="main_menu")
    kb.adjust(1)
    
    await call.message.edit_text(text, reply_markup=kb.as_markup())

@router.callback_query(F.data == "main_menu")
async def back_to_main(call: types.CallbackQuery):
    await show_catalog_main(call.message, is_edit=True, user_id=call.from_user.id)

# ------------------------------------
# ПРОСМОТР ЯЗЫКА
# ------------------------------------
@router.callback_query(F.data.startswith("view_lang_"))
async def view_language(call: types.CallbackQuery):
    uid = call.from_user.id
    lang_id = call.data.split("_")[2]
    lang = db.get_language_by_id(lang_id)
    
    if not lang:
        await call.answer("Error", show_alert=True)
        return

    total_keys = len(BASE_TEMPLATE)
    translated_keys = len(lang.get("content", {}))
    
    text = (
        f"{EMOJI_GLOBAL} " + TR("lang_view_title", uid, lang['name']) + "\n"
        f"<blockquote>" + TR("lang_view_stats", uid, translated_keys, total_keys) + "\n"
        + TR("lang_view_date", uid, lang.get('date', '...')) + "\n"
        + TR("lang_view_desc", uid, lang['description']) + "</blockquote>\n"
        + TR("lang_view_footer", uid)
    )
    
    kb = InlineKeyboardBuilder()
    kb.button(text=TR("install", uid), callback_data=f"install_{lang_id}")
    
    # Кнопка удаления для админов
    if uid in db.get_admins():
        kb.button(text=TR("delete_admin", uid), callback_data=f"del_lang_{lang_id}")

    kb.button(text=TR("back", uid), callback_data=f"cat_{lang['type']}")
    kb.adjust(1)
    
    await call.message.edit_text(text, reply_markup=kb.as_markup())

@router.callback_query(F.data.startswith("del_lang_"))
async def admin_delete_language(call: types.CallbackQuery):
    uid = call.from_user.id
    if uid not in db.get_admins():
        return
        
    lang_id = call.data.split("_")[2]
    db.remove_language(lang_id)
    
    await call.answer(TR("lang_deleted", uid), show_alert=True)
    await show_catalog_main(call.message, is_edit=True, user_id=uid)

@router.callback_query(F.data.startswith("install_"))
async def install_language(call: types.CallbackQuery):
    uid = call.from_user.id
    lang_id = call.data.split("_")[1]
    lang = db.get_language_by_id(lang_id)
    
    if not lang:
        return

    content_str = json.dumps(lang["content"], ensure_ascii=False, indent=2)
    file_bytes = io.BytesIO(content_str.encode('utf-8'))
    file_input = BufferedInputFile(file_bytes.getvalue(), filename=f"{lang['name']}.txt")
    
    await call.message.edit_text(TR("file_sent", uid, EMOJI_FILE))
    await call.message.answer_document(file_input)
    
    kb = InlineKeyboardBuilder()
    kb.button(text=TR("to_menu", uid), callback_data="main_menu")
    await call.message.answer(TR("to_menu", uid), reply_markup=kb.as_markup())

# ==========================================
# АДМИН ПАНЕЛЬ
# ==========================================

@router.callback_query(F.data == "admin_entry")
async def admin_panel_callback(call: types.CallbackQuery):
    await admin_panel_logic(call.message, call.from_user.id, is_edit=True)

@router.message(Command("admin"))
async def admin_panel_command(message: types.Message):
    await admin_panel_logic(message, message.from_user.id, is_edit=False)

async def admin_panel_logic(message: types.Message, user_id, is_edit=False):
    if user_id not in db.get_admins():
        return

    text = f"{EMOJI_ADMIN} " + TR("admin_panel_title", user_id)
    
    kb = InlineKeyboardBuilder()
    kb.button(text=TR("btn_manage_langs", user_id), callback_data="admin_langs")
    kb.button(text=TR("btn_admins", user_id), callback_data="admin_users_menu")
    kb.button(text=TR("back", user_id), callback_data="main_menu")
    kb.adjust(1)
    
    if is_edit:
        await message.edit_text(text, reply_markup=kb.as_markup())
    else:
        await message.answer(text, reply_markup=kb.as_markup())

@router.callback_query(F.data == "admin_back_main")
async def admin_back_handler(call: types.CallbackQuery):
    await admin_panel_logic(call.message, call.from_user.id, is_edit=True)

@router.callback_query(F.data == "admin_langs")
async def admin_manage_langs(call: types.CallbackQuery):
    uid = call.from_user.id
    text = f"{EMOJI_MANAGE} " + TR("manage_langs_title", uid)
    
    kb = InlineKeyboardBuilder()
    kb.button(text=TR("btn_create_new", uid), callback_data="adm_create_new")
    kb.button(text=TR("btn_add_string", uid), callback_data="adm_add_string")
    kb.button(text=TR("back", uid), callback_data="admin_back_main")
    kb.adjust(1)
    
    await call.message.edit_text(text, reply_markup=kb.as_markup())

# ------------------------------------
# УПРАВЛЕНИЕ АДМИНАМИ (ИЗМЕНЕНО)
# ------------------------------------

@router.callback_query(F.data == "admin_users_menu")
async def admin_users_menu(call: types.CallbackQuery):
    uid = call.from_user.id
    admins = db.get_admins()
    
    text = TR("admins_list_title", uid, len(admins))
    
    kb = InlineKeyboardBuilder()
    
    # Только главный админ может создавать приглашения
    if uid == MAIN_ADMIN_ID:
        kb.button(text=TR("btn_gen_invite", uid), callback_data="adm_gen_invite")
    
    # Список админов 
    for aid in admins:
        if aid == MAIN_ADMIN_ID:
            btn_text = f"👑 {aid}"
            callback = "ignore"
        elif aid == uid:
            btn_text = f"👤 {aid} (Вы)"
            callback = "ignore"
        else:
            # Открываем меню управления админом
            btn_text = f"👤 {aid}"
            callback = f"adm_view_{aid}"
        
        kb.button(text=btn_text, callback_data=callback)

    kb.button(text=TR("back", uid), callback_data="admin_back_main")
    kb.adjust(1)
    
    await call.message.edit_text(text, reply_markup=kb.as_markup())

# ПРОСМОТР АДМИНА И УДАЛЕНИЕ
@router.callback_query(F.data.startswith("adm_view_"))
async def admin_view_specific_user(call: types.CallbackQuery):
    uid = call.from_user.id
    target_id = call.data.split("_")[2]
    
    text = TR("admin_manage_user_title", uid, target_id)
    
    kb = InlineKeyboardBuilder()
    kb.button(text=TR("btn_delete_admin_user", uid), callback_data=f"adm_remove_{target_id}")
    kb.button(text=TR("back", uid), callback_data="admin_users_menu")
    kb.adjust(1)
    
    await call.message.edit_text(text, reply_markup=kb.as_markup())

@router.callback_query(F.data.startswith("adm_remove_"))
async def remove_admin_handler(call: types.CallbackQuery):
    uid = call.from_user.id
    target_id = int(call.data.split("_")[2])
    
    # Проверка безопасности: только главный может удалять
    if uid != MAIN_ADMIN_ID:
        await call.answer(TR("access_denied", uid), show_alert=True)
        return

    if db.remove_admin(target_id):
        await call.answer(TR("admin_removed", uid, target_id), show_alert=True)
        await admin_users_menu(call) # Возврат в список
    else:
        await call.answer("Error", show_alert=True)

@router.callback_query(F.data == "adm_gen_invite")
async def generate_admin_invite(call: types.CallbackQuery):
    uid = call.from_user.id
    
    # Еще одна проверка
    if uid != MAIN_ADMIN_ID:
        await call.answer(TR("access_denied", uid), show_alert=True)
        return

    token = str(uuid.uuid4())[:10]
    INVITE_TOKENS[token] = True
    
    bot_info = await bot.get_me()
    link = f"https://t.me/{bot_info.username}?start=admin_{token}"
    
    text = TR("invite_text", uid, link)
    
    kb = InlineKeyboardBuilder()
    kb.button(text=TR("back", uid), callback_data="admin_users_menu")
    
    await call.message.edit_text(text, reply_markup=kb.as_markup())

# --- ДОБАВЛЕНИЕ СТРОКИ ---
@router.callback_query(F.data == "adm_add_string")
async def start_add_string(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Code:")
    await state.set_state(AdminStates.add_string_code)
    await state.update_data(msg_id=call.message.message_id)

@router.message(AdminStates.add_string_code)
async def process_string_code(message: types.Message, state: FSMContext):
    data = await state.get_data()
    msg_id = data.get("msg_id")
    code = message.text.strip()
    await message.delete()
    await bot.edit_message_text(f"Code: {code}\nTranslation:", chat_id=message.chat.id, message_id=msg_id)
    await state.update_data(new_key=code)
    await state.set_state(AdminStates.add_string_value)

@router.message(AdminStates.add_string_value)
async def process_string_value(message: types.Message, state: FSMContext):
    data = await state.get_data()
    msg_id = data.get("msg_id")
    new_key = data.get("new_key")
    value = message.text.strip()
    await message.delete()
    
    BASE_TEMPLATE[new_key] = value
    
    if new_key not in TRANSLATION_CATEGORIES["general"]["keys"]:
        TRANSLATION_CATEGORIES["general"]["keys"].append(new_key)
    
    kb = InlineKeyboardBuilder()
    kb.button(text="save", callback_data="save_new_string")
    await bot.edit_message_text(f"Added:\n{new_key} = {value}", chat_id=message.chat.id, message_id=msg_id, reply_markup=kb.as_markup())

@router.callback_query(F.data == "save_new_string")
async def save_new_string_finish(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await admin_manage_langs(call)

# --- WIZARD СОЗДАНИЯ ---

@router.callback_query(F.data == "adm_create_new")
async def wizard_step1_cat(call: types.CallbackQuery, state: FSMContext):
    uid = call.from_user.id
    text = f"{EMOJI_CATEGORY} " + TR("wiz_step1", uid)
    kb = InlineKeyboardBuilder()
    kb.button(text=TR("cat_type_custom", uid), callback_data="w_cat_custom")
    kb.button(text=TR("cat_type_global", uid), callback_data="w_cat_global")
    kb.adjust(2)
    
    await call.message.edit_text(text, reply_markup=kb.as_markup())
    await state.set_state(AdminStates.creating_cat)
    await state.update_data(msg_id=call.message.message_id)

@router.callback_query(F.data.startswith("w_cat_"))
async def wizard_step2_name_ask(call: types.CallbackQuery, state: FSMContext):
    uid = call.from_user.id
    cat = call.data.split("_")[2]
    await state.update_data(cat=cat)
    
    text = f"{EMOJI_EDIT} " + TR("wiz_step2", uid)
    await call.message.edit_text(text)
    await state.set_state(AdminStates.creating_name)

@router.message(AdminStates.creating_name)
async def wizard_step2_name_proc(message: types.Message, state: FSMContext):
    data = await state.get_data()
    msg_id = data.get("msg_id")
    name = message.text
    await message.delete()
    await state.update_data(name=name)
    
    text = f"{EMOJI_DESC} " + TR("wiz_step3", message.from_user.id)
    await bot.edit_message_text(chat_id=message.chat.id, message_id=msg_id, text=text)
    await state.set_state(AdminStates.creating_desc)

@router.message(AdminStates.creating_desc)
async def wizard_step3_desc_proc(message: types.Message, state: FSMContext):
    uid = message.from_user.id
    data = await state.get_data()
    msg_id = data.get("msg_id")
    desc = message.text
    await message.delete()
    await state.update_data(desc=desc)
    
    text = f"{EMOJI_THINK} " + TR("wiz_step4", uid)
    kb = InlineKeyboardBuilder()
    kb.button(text=TR("wiz_btn_scratch", uid), callback_data="method_scratch")
    kb.button(text=TR("wiz_btn_upload", uid), callback_data="method_upload")
    kb.adjust(1)
    
    await bot.edit_message_text(chat_id=message.chat.id, message_id=msg_id, text=text, reply_markup=kb.as_markup())
    await state.set_state(AdminStates.creating_method)

# --- UPLOAD ---
@router.callback_query(F.data == "method_upload")
async def wizard_upload_ask(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(TR("wiz_upload_ask", call.from_user.id))
    await state.set_state(AdminStates.uploading_file)

@router.message(AdminStates.uploading_file, F.document)
async def wizard_upload_proc(message: types.Message, state: FSMContext):
    data = await state.get_data()
    msg_id = data.get("msg_id")
    
    file_id = message.document.file_id
    file_info = await bot.get_file(file_id)
    downloaded_file = await bot.download_file(file_info.file_path)
    
    try:
        content = json.load(downloaded_file)
    except Exception:
        await message.delete()
        await bot.edit_message_text("JSON Error", chat_id=message.chat.id, message_id=msg_id)
        return

    await message.delete()
    
    new_lang = {
        "id": str(uuid.uuid4())[:8],
        "name": data["name"],
        "description": data["desc"],
        "type": data["cat"],
        "content": content,
        "date": datetime.now().strftime("%d.%m.%y"),
        "author_id": message.from_user.id
    }
    db.add_language(new_lang)
    
    kb = InlineKeyboardBuilder()
    kb.button(text=TR("to_menu", message.from_user.id), callback_data="admin_langs")
    
    await bot.edit_message_text(
        text=f"{EMOJI_DONE} " + TR("wiz_done", message.from_user.id),
        chat_id=message.chat.id,
        message_id=msg_id,
        reply_markup=kb.as_markup()
    )
    await state.clear()

# --- TRANSLATOR ---
@router.callback_query(F.data == "method_scratch")
async def wizard_scratch_start(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(content={}) 
    await show_translation_dashboard(call, state)

async def show_translation_dashboard(call_or_message, state: FSMContext):
    data = await state.get_data()
    # Проверка, откуда пришел вызов
    if isinstance(call_or_message, types.CallbackQuery):
        uid = call_or_message.from_user.id
    else:
        uid = call_or_message.chat.id # Fallback
        
    content = data.get("content", {})
    name = data.get("name")
    
    total_completed = len(content)
    total_all = len(BASE_TEMPLATE)
    
    text = f"{EMOJI_TRANSLATE} " + TR("trans_panel", uid, name, total_completed, total_all)
    
    kb = InlineKeyboardBuilder()
    for cat_key, cat_val in TRANSLATION_CATEGORIES.items():
        keys_in_cat = cat_val["keys"]
        count_cat_all = len(keys_in_cat)
        count_cat_done = sum(1 for k in keys_in_cat if k in content)
        kb.button(text=f"{cat_val['name']} {count_cat_done} • {count_cat_all}", callback_data=f"trans_cat_{cat_key}")
        
    kb.button(text=TR("trans_publish", uid), callback_data="trans_publish")
    kb.adjust(1)
    
    msg_id = data.get("msg_id")
    if isinstance(call_or_message, types.CallbackQuery):
        await call_or_message.message.edit_text(text, reply_markup=kb.as_markup())
    else:
        await bot.edit_message_text(text=text, chat_id=call_or_message.chat.id, message_id=msg_id, reply_markup=kb.as_markup())

    await state.set_state(AdminStates.translating_dashboard)

@router.callback_query(F.data.startswith("trans_cat_"))
async def start_category_translation(call: types.CallbackQuery, state: FSMContext):
    cat_key = call.data.split("_")[2]
    cat_keys_list = TRANSLATION_CATEGORIES[cat_key]["keys"]
    await state.update_data(current_cat_keys=cat_keys_list, current_key_index=0, current_cat_key=cat_key)
    await show_next_key_translation(call, state)

async def show_next_key_translation(call_or_obj, state: FSMContext):
    data = await state.get_data()
    keys = data.get("current_cat_keys")
    index = data.get("current_key_index")
    content = data.get("content", {})
    
    # Определяем UID
    if isinstance(call_or_obj, types.CallbackQuery):
        uid = call_or_obj.from_user.id
        msg_obj = call_or_obj.message
    else:
        uid = call_or_obj.from_user.id
        msg_obj = call_or_obj
        
    if index >= len(keys):
        await show_translation_dashboard(call_or_obj, state)
        return

    current_key = keys[index]
    original_text = BASE_TEMPLATE.get(current_key, "???")
    current_translation = content.get(current_key, "---")
    
    text = (f"<b>{index + 1} / {len(keys)}</b>\n"
            f"Original:\n<blockquote>{original_text}</blockquote>\n"
            f"Trans:\n<blockquote>{current_translation}</blockquote>")
    
    kb = InlineKeyboardBuilder()
    kb.button(text=TR("trans_next", uid), callback_data="trans_next")
    kb.button(text=TR("trans_apply", uid), callback_data="trans_apply_cat")
    kb.adjust(2)
    
    msg_id = data.get("msg_id")
    if isinstance(call_or_obj, types.CallbackQuery):
        await msg_obj.edit_text(text, reply_markup=kb.as_markup())
    else:
        await bot.edit_message_text(text=text, chat_id=msg_obj.chat.id, message_id=msg_id, reply_markup=kb.as_markup())
        
    await state.set_state(AdminStates.translating_input)

@router.message(AdminStates.translating_input)
async def process_translation_input(message: types.Message, state: FSMContext):
    data = await state.get_data()
    keys = data.get("current_cat_keys")
    index = data.get("current_key_index")
    current_key = keys[index]
    content = data.get("content", {})
    
    content[current_key] = message.text
    await message.delete()
    
    await state.update_data(content=content)
    await show_next_key_translation(message, state)

@router.callback_query(F.data == "trans_next")
async def translation_next_key(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    index = data.get("current_key_index")
    await state.update_data(current_key_index=index + 1)
    await show_next_key_translation(call, state)

@router.callback_query(F.data == "trans_apply_cat")
async def translation_apply_category(call: types.CallbackQuery, state: FSMContext):
    await show_translation_dashboard(call, state)

@router.callback_query(F.data == "trans_publish")
async def finish_translation_publish(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    new_lang = {
        "id": str(uuid.uuid4())[:8],
        "name": data["name"],
        "description": data["desc"],
        "type": data["cat"],
        "content": data["content"],
        "date": datetime.now().strftime("%d.%m.%y"),
        "author_id": call.from_user.id
    }
    db.add_language(new_lang)
    
    kb = InlineKeyboardBuilder()
    kb.button(text=TR("to_menu", call.from_user.id), callback_data="admin_langs")
    
    await call.message.edit_text(
        text=f"{EMOJI_DONE} {TR('wiz_done', call.from_user.id)}",
        reply_markup=kb.as_markup()
    )
    await state.clear()

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
