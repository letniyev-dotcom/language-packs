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
from aiogram.exceptions import TelegramAPIError
from aiogram.types.error_event import ErrorEvent

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
        "btn_manage": "управление",
        "cat_choice": "{0} выберите {1} язык",
        "cat_type_custom": "кастомный",
        "cat_type_global": "глобальный",
        "back": "назад",
        "install": "установить",
        "delete_admin": "🗑 удалить (админ)",
        "lang_view_title": "<b>название:</b> {0}",
        "lang_view_stats": "<b>переведено строк:</b> <code>{0}/{1}</code>",
        "lang_view_date": "<b>последнее обновление:</b> <code>{0}</code>",
        "lang_view_desc": "<b>описание:</b> <code>{0}</code>",
        "lang_view_footer": "для установки нажмите <b>установить</b> под этим сообщением и скопируйте содержимое файла",
        "file_sent": "файл отправлен ниже {0}",
        "to_menu": "в меню",
        "admin_panel_title": "<b>админ панель</b>\n\nздесь ты можешь управлять языками добавлять и создавать новый\nстатус: {0}",
        "btn_manage_langs": "управление языками",
        "btn_admins": "админы",
        "btn_categories": "категории",
        "btn_toggle_bot": "{0}",
        "manage_langs_title": "<b>управление языками</b>",
        "btn_create_new": "создать новый",
        "btn_add_string": "добавить строку",
        "btn_drafts": "черновики",
        "btn_strings": "строки",
        "admins_list_title": "<b>Список админов ({0}):</b>\nНажмите на админа для управления.",
        "admin_manage_user_title": "<b>Управление админом:</b>\nID: <code>{0}</code>",
        "btn_delete_admin_user": "🗑 удалить права админа",
        "btn_gen_invite": "создать приглашение",
        "invite_text": "<b>Одноразовая ссылка для нового админа:</b>\n<blockquote><code>{0}</code></blockquote>Перешлите её. После перехода он станет админом.",
        "lang_deleted": "Язык удален.",
        "admin_removed": "Админ {0} удален.",
        "access_denied": "У вас нет прав на это действие.",
        "wiz_step1": "<b>выберите категорию:</b>\n1 из 4",
        "wiz_step2": "<b>введите название:</b>\n2 из 4",
        "wiz_step3": "<b>добавьте описание</b>\n3 из 4",
        "wiz_step4": "создать с нуля? или загрузить готовый?",
        "wiz_btn_scratch": "создать новый",
        "wiz_btn_upload": "загрузить готовый",
        "wiz_upload_ask": "Отправьте .json, .lang или .rclang файл",
        "wiz_done": "язык добавлен",
        "trans_panel": "<b>панель переводчика</b>\n<blockquote><b>язык:</b> {0}\nпереведено {1} из {2}</blockquote>",
        "trans_publish": "✅ опубликовать",
        "trans_draft": "в черновики",
        "trans_next": "далее",
        "trans_apply": "применить",
        "lang_changed": "Язык изменен на Русский <tg-emoji emoji-id='5449408995691341691'>🇷🇺</tg-emoji>",
        "original_label": "Оригинал",
        "trans_label": "Перевод",
        "drafts_title": "<tg-emoji emoji-id='5373251851074415873'>📝</tg-emoji> черновики",
        "drafts_empty": "нет черновиков",
        "draft_view_title": "<b>название:</b> {0}",
        "btn_edit": "редактировать",
        "lang_updated": "язык обновлен",
        "action_cancelled": "действие отменено",
        "manage_strings_title": "управление строками для перевода",
        "strings_page_title": "управление строками",
        "strings_export_sent": "отправил файл ниже <tg-emoji emoji-id='5470177992950946662'>👇</tg-emoji>",
        "strings_imported": "импортировано {0} строк, все прошлые строки для перевода были удалены.",
        "assign_cat_remaining": "осталось {0} не отсортированных строк",
        "assign_cat_for": "выберите категорию для \n<blockquote>{0}</blockquote>\nзначение:\n<blockquote>{1}</blockquote>",
        "string_view_code": "код: {0}",
        "string_view_value": "перевод: {0}",
        "string_view_cat": "категория: {0}",
        "btn_delete": "удалить",
        "btn_change": "изменить",
        "select_category": "Выберите категорию:",
        "manage_categories_title": "управление категориями",
        "cat_view_title": "<b>название:</b> {0}",
        "cat_view_count": "строк в этой категории: {0}",
        "enter_name": "введите название:",
        "create_lang_unavailable": "пока недоступно...",
        "draft_sorting": "sorting",
        "cat_exists": "Категория уже существует",
        "cat_name_empty": "Имя категории не может быть пустым",
        "cat_key_invalid": "Неверный ключ категории"
    },
    "en": {
        "start_text": "Select bot language:", 
        "main_menu_text": "{0} <b>Recent Chats Fork</b> Language Catalog\n\nUse the buttons below to select a language or read the manual",
        "btn_custom": "custom",
        "btn_global": "global",
        "btn_manual": "manual",
        "btn_manage": "management",
        "cat_choice": "{0} select {1} language",
        "cat_type_custom": "custom",
        "cat_type_global": "global",
        "back": "back",
        "install": "install",
        "delete_admin": "🗑 delete (admin)",
        "lang_view_title": "<b>name:</b> {0}",
        "lang_view_stats": "<b>translated lines:</b> <code>{0}/{1}</code>",
        "lang_view_date": "<b>last update:</b> <code>{0}</code>",
        "lang_view_desc": "<b>description:</b> <code>{0}</code>",
        "lang_view_footer": "Press <b>install</b> below and copy the file content",
        "file_sent": "File sent below {0}",
        "to_menu": "main menu",
        "admin_panel_title": "<b>admin panel</b>\n\nManage languages, add new ones, or manage admins here.\nstatus: {0}",
        "btn_manage_langs": "manage languages",
        "btn_admins": "admins",
        "btn_categories": "categories",
        "btn_toggle_bot": "{0}",
        "manage_langs_title": "<b>manage languages</b>",
        "btn_create_new": "create new",
        "btn_add_string": "add string",
        "btn_drafts": "drafts",
        "btn_strings": "strings",
        "admins_list_title": "<b>Admin List ({0}):</b>\nClick on an admin to manage.",
        "admin_manage_user_title": "<b>Manage Admin:</b>\nID: <code>{0}</code>",
        "btn_delete_admin_user": "🗑 remove admin rights",
        "btn_gen_invite": "create invite",
        "invite_text": "<b>One-time link for new admin:</b>\n<blockquote><code>{0}</code></blockquote>Forward this. They will become admin upon clicking.",
        "lang_deleted": "Language deleted.",
        "admin_removed": "Admin {0} removed.",
        "access_denied": "Access denied.",
        "wiz_step1": "<b>select category:</b>\n1 of 4",
        "wiz_step2": "<b>enter name:</b>\n2 of 4",
        "wiz_step3": "<b>enter description:</b>\n3 of 4",
        "wiz_step4": "Create from scratch or upload existing?",
        "wiz_btn_scratch": "create new",
        "wiz_btn_upload": "upload file",
        "wiz_upload_ask": "Send .json, .lang or .rclang file",
        "wiz_done": "Language added",
        "trans_panel": "<b>translator panel</b>\n<blockquote><b>lang:</b> {0}\nprogress {1} of {2}</blockquote>",
        "trans_publish": "✅ publish",
        "trans_draft": "to drafts",
        "trans_next": "next",
        "trans_apply": "apply",
        "lang_changed": "Language changed to English <tg-emoji emoji-id='5202021044105257611'>🇺🇸</tg-emoji>",
        "original_label": "Original",
        "trans_label": "Trans",
        "drafts_title": "<tg-emoji emoji-id='5373251851074415873'>📝</tg-emoji> drafts",
        "drafts_empty": "no drafts",
        "draft_view_title": "<b>name:</b> {0}",
        "btn_edit": "edit",
        "lang_updated": "language updated",
        "action_cancelled": "action cancelled",
        "manage_strings_title": "manage strings for translation",
        "strings_page_title": "manage strings",
        "strings_export_sent": "sent file below <tg-emoji emoji-id='5470177992950946662'>👇</tg-emoji>",
        "strings_imported": "imported {0} strings, all previous strings for translation were deleted.",
        "assign_cat_remaining": "still remaining {0} strings without assigned categories",
        "assign_cat_for": "select category for \n<blockquote>{0}</blockquote>\nvalue:\n<blockquote>{1}</blockquote>",
        "string_view_code": "code: {0}",
        "string_view_value": "translation: {0}",
        "string_view_cat": "category: {0}",
        "btn_delete": "delete",
        "btn_change": "change",
        "select_category": "Select category:",
        "manage_categories_title": "manage categories",
        "cat_view_title": "<b>name:</b> {0}",
        "cat_view_count": "strings in this category: {0}",
        "enter_name": "enter name:",
        "create_lang_unavailable": "currently unavailable...",
        "draft_sorting": "sorting",
        "cat_exists": "Category already exists",
        "cat_name_empty": "Category name cannot be empty",
        "cat_key_invalid": "Invalid category key"
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
        "keys": ["extended_settings_hello", "general", "other", "footer", "clip_empty", "lang_applied", "lang_invalid", "err_open_channel", "deleted_account", "empty_list", "action_remove", "action_add", "chat_removed", "chat_added", "yes", "no", "lang_header", "lang_import_clip", "lang_reset", "lang_info", "catalog", "catalog_desc", "cancel"]
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
            "drafts": {},  # user_id: list of drafts
            "users": {}, # user_id: "ru" or "en"
            "invite_tokens": {},
            "base_template": BASE_TEMPLATE,
            "translation_categories": TRANSLATION_CATEGORIES,
            "bot_enabled": True
        }
        if not os.path.exists(self.filename):
            return default_data
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "languages" not in data: data["languages"] = []
                if "admins" not in data: data["admins"] = [MAIN_ADMIN_ID]
                if "drafts" not in data: data["drafts"] = {}
                if "users" not in data: data["users"] = {}
                if "invite_tokens" not in data: data["invite_tokens"] = {}
                if "base_template" not in data: data["base_template"] = BASE_TEMPLATE
                if "translation_categories" not in data: data["translation_categories"] = TRANSLATION_CATEGORIES
                if "bot_enabled" not in data: data["bot_enabled"] = True

                # Миграция: если drafts - список (старая версия), перевести в dict под MAIN_ADMIN_ID
                if isinstance(data.get("drafts"), list):
                    logger.warning("Migrating old drafts list to dict")
                    data["drafts"] = {MAIN_ADMIN_ID: data["drafts"]}

                # Конвертация ключей пользователей в int (JSON хранит ключи как str)
                data["users"] = {int(k): v for k, v in data["users"].items()}
                data["drafts"] = {int(k): v for k, v in data.get("drafts", {}).items()}
                return data
        except Exception as e:
            logger.error(f"Error loading DB: {e}")
            return default_data

    def save(self):
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                # При сохранении ключи словаря users станут строками, это норм для JSON
                json.dump(self.data, f, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving DB: {e}")

    def add_language(self, lang_data):
        if len(lang_data.get("content", {})) == 0:
            raise ValueError("Language content cannot be empty")
        self.data["languages"].append(lang_data)
        self.save()

    def remove_language(self, lang_id):
        self.data["languages"] = [l for l in self.data["languages"] if l["id"] != lang_id]
        self.save()

    def update_language(self, lang_id, updates):
        for l in self.data["languages"]:
            if l["id"] == lang_id:
                l.update(updates)
                break
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

    def add_draft(self, user_id, draft_data):
        if user_id not in self.data["drafts"]:
            self.data["drafts"][user_id] = []
        self.data["drafts"][user_id].append(draft_data)
        self.save()

    def get_drafts(self, user_id):
        return self.data["drafts"].get(user_id, [])

    def get_draft_by_id(self, draft_id, user_id):
        drafts = self.get_drafts(user_id)
        for d in drafts:
            if d["id"] == draft_id:
                return d
        return None

    def remove_draft(self, draft_id, user_id):
        drafts = self.get_drafts(user_id)
        self.data["drafts"][user_id] = [d for d in drafts if d["id"] != draft_id]
        self.save()

    def update_draft(self, draft_id, updates, user_id):
        drafts = self.get_drafts(user_id)
        for d in drafts:
            if d["id"] == draft_id:
                d.update(updates)
                break
        self.save()

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

    def add_invite_token(self, token):
        self.data["invite_tokens"][token] = True
        self.save()

    def remove_invite_token(self, token):
        if token in self.data["invite_tokens"]:
            del self.data["invite_tokens"][token]
            self.save()

    def check_invite_token(self, token):
        return token in self.data["invite_tokens"]

    def get_base_template(self):
        return self.data["base_template"]

    def update_base_template(self, new_template):
        self.data["base_template"] = new_template
        self.save()

    def get_translation_categories(self):
        return self.data["translation_categories"]

    def update_translation_categories(self, new_categories):
        self.data["translation_categories"] = new_categories
        self.save()

    def add_string_to_category(self, key, cat_key):
        categories = self.get_translation_categories()
        if cat_key in categories and key not in categories[cat_key]["keys"]:
            categories[cat_key]["keys"].append(key)
            self.update_translation_categories(categories)

    def remove_string_from_categories(self, key):
        categories = self.get_translation_categories()
        for cat in categories.values():
            if key in cat["keys"]:
                cat["keys"].remove(key)
        self.update_translation_categories(categories)

    def add_category(self, cat_key, name):
        categories = self.get_translation_categories()
        if cat_key not in categories:
            categories[cat_key] = {"name": name, "keys": []}
            self.update_translation_categories(categories)
            return True
        return False

    def remove_category(self, cat_key):
        categories = self.get_translation_categories()
        if cat_key in categories:
            del categories[cat_key]
            self.update_translation_categories(categories)

    def update_category_name(self, cat_key, new_name):
        categories = self.get_translation_categories()
        if cat_key in categories:
            categories[cat_key]["name"] = new_name
            self.update_translation_categories(categories)

    def toggle_bot_enabled(self):
        self.data["bot_enabled"] = not self.data["bot_enabled"]
        self.save()

    def is_bot_enabled(self):
        return self.data.get("bot_enabled", True)

    def get_sorting_draft(self, user_id):
        drafts = self.get_drafts(user_id)
        for d in drafts:
            if d.get("type") == "sorting":
                return d
        return None

    def save_sorting_draft(self, user_id, uncat_keys, uncat_index):
        self.remove_sorting_draft(user_id)
        sorting_draft = {
            "id": "sorting",
            "type": "sorting",
            "name": "сортировка",
            "uncat_keys": uncat_keys,
            "uncat_index": uncat_index
        }
        self.add_draft(user_id, sorting_draft)

    def remove_sorting_draft(self, user_id):
        drafts = self.get_drafts(user_id)
        self.data["drafts"][user_id] = [d for d in drafts if d.get("type") != "sorting"]
        self.save()

db = DB(DB_FILE)
BASE_TEMPLATE = db.get_base_template()
TRANSLATION_CATEGORIES = db.get_translation_categories()

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
EMOJI_CANCEL = get_tg_emoji("5260342697075416641", "❌")

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
    add_string_category = State()
    importing_strings = State()
    assigning_category = State()
    edit_string = State()
    add_cat_name = State()
    edit_cat_name = State()

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

def find_category_for_key(key):
    for cat_key, cat in TRANSLATION_CATEGORIES.items():
        if key in cat["keys"]:
            return cat["name"]
    return "None"

# ==========================================
# ГЛОБАЛЬНЫЙ ОБРАБОТЧИК ОШИБОК
# ==========================================
@dp.error()
async def errors_handler(event: ErrorEvent):
    logger.error(f"Exception: {event.exception}")
    if event.update.message:
        await event.update.message.answer("Произошла ошибка. Попробуйте позже.")
    return True

# ==========================================
# ХЕНДЛЕРЫ: СТАРТ, ЯЗЫК, КОМАНДЫ
# ==========================================

# НОВЫЕ КОМАНДЫ ДЛЯ СМЕНЫ ЯЗЫКА
@router.message(Command("ru"))
async def cmd_set_ru(message: types.Message):
    if not db.is_bot_enabled() and message.from_user.id not in db.get_admins():
        return
    db.set_user_lang(message.from_user.id, "ru")
    msg = await message.answer(TR("lang_changed", message.from_user.id))
    await asyncio.sleep(5)
    try:
        await msg.delete()
    except TelegramAPIError:
        pass
    await show_catalog_main(message)

@router.message(Command("en"))
async def cmd_set_en(message: types.Message):
    if not db.is_bot_enabled() and message.from_user.id not in db.get_admins():
        return
    db.set_user_lang(message.from_user.id, "en")
    msg = await message.answer(TR("lang_changed", message.from_user.id))
    await asyncio.sleep(5)
    try:
        await msg.delete()
    except TelegramAPIError:
        pass
    await show_catalog_main(message)

@router.message(Command("c", "cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    if not db.is_bot_enabled() and message.from_user.id not in db.get_admins():
        return
    current_state = await state.get_state()
    if current_state is None:
        return
    data = await state.get_data()
    if current_state == AdminStates.assigning_category:
        uncat_keys = data.get("uncat_keys")
        uncat_index = data.get("uncat_index")
        db.save_sorting_draft(message.from_user.id, uncat_keys, uncat_index)
    msg_id = data.get("msg_id")
    chat_id = message.chat.id
    uid = message.from_user.id
    await message.delete()
    if msg_id:
        try:
            await bot.edit_message_text(f"{EMOJI_CANCEL} {TR('action_cancelled', uid)}", chat_id=chat_id, message_id=msg_id)
            await asyncio.sleep(2)
            await admin_panel_logic(message, uid, is_edit=True, msg_id=msg_id)
        except TelegramAPIError:
            pass
    await state.clear()

@router.message(CommandStart())
async def cmd_start(message: types.Message, command: CommandObject):
    user_id = message.from_user.id
    if not db.is_bot_enabled() and user_id not in db.get_admins():
        return

    # 1. Проверка на инвайт админа
    args = command.args
    if args and args.startswith("admin_"):
        token = args.split("_")[1]
        if db.check_invite_token(token):
            db.add_admin(user_id)
            db.remove_invite_token(token)
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
    if not db.is_bot_enabled() and call.from_user.id not in db.get_admins():
        return
    lang_code = call.data.split("_")[2] # ru or en
    db.set_user_lang(call.from_user.id, lang_code)

    # После выбора языка сразу редактируем сообщение на главное меню
    await show_catalog_main(call.message, is_edit=True, user_id=call.from_user.id)

# ==========================================
# ХЕНДЛЕРЫ: КАТАЛОГ
# ==========================================

async def show_catalog_main(message: types.Message, is_edit=False, user_id=None, msg_id=None):
    if not user_id: user_id = message.chat.id # fallback if msg object differs

    text = TR("main_menu_text", user_id, EMOJI_CATALOG)

    kb = InlineKeyboardBuilder()
    kb.button(text=f"🎨 {TR('btn_custom', user_id)}", callback_data="cat_custom")
    kb.button(text=f"🌐 {TR('btn_global', user_id)}", callback_data="cat_global")
    kb.button(text=f"📖 {TR('btn_manual', user_id)}", url="https://t.me/huixplug")

    # Кнопка для админов
    if user_id in db.get_admins():
        kb.button(text=f"⚙️ {TR('btn_manage', user_id)}", callback_data="admin_entry")

    kb.adjust(2, 1, 1)

    if is_edit and msg_id:
        await bot.edit_message_text(text, chat_id=message.chat.id, message_id=msg_id, reply_markup=kb.as_markup())
    elif is_edit:
        await message.edit_text(text, reply_markup=kb.as_markup())
    else:
        await message.answer(text, reply_markup=kb.as_markup())

@router.callback_query(F.data.startswith("cat_"))
async def show_category(call: types.CallbackQuery):
    if not db.is_bot_enabled() and call.from_user.id not in db.get_admins():
        return
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
    if not db.is_bot_enabled() and call.from_user.id not in db.get_admins():
        return
    await show_catalog_main(call.message, is_edit=True, user_id=call.from_user.id)

# ------------------------------------
# ПРОСМОТР ЯЗЫКА
# ------------------------------------
@router.callback_query(F.data.startswith("view_lang_"))
async def view_language(call: types.CallbackQuery):
    if not db.is_bot_enabled() and call.from_user.id not in db.get_admins():
        return
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
    kb.button(text=f"🔧 {TR('install', uid)}", callback_data=f"install_{lang_id}")

    # Кнопки для админов
    if uid in db.get_admins():
        kb.button(text=f"🖊 {TR('btn_edit', uid)}", callback_data=f"edit_lang_{lang_id}")
        kb.button(text=TR("delete_admin", uid), callback_data=f"del_lang_{lang_id}")

    kb.button(text=f"⬅️ {TR('back', uid)}", callback_data=f"cat_{lang['type']}")
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
    if not db.is_bot_enabled() and call.from_user.id not in db.get_admins():
        return
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

@router.callback_query(F.data.startswith("edit_lang_"))
async def edit_language(call: types.CallbackQuery, state: FSMContext):
    uid = call.from_user.id
    if uid not in db.get_admins():
        await call.answer(TR("access_denied", uid), show_alert=True)
        return

    lang_id = call.data.split("_")[2]
    lang = db.get_language_by_id(lang_id)
    if not lang:
        await call.answer("Error", show_alert=True)
        return

    await state.set_state(AdminStates.translating_dashboard)
    await state.update_data(
        cat=lang["type"],
        name=lang["name"],
        desc=lang["description"],
        content=lang["content"],
        edit_id=lang_id,
        msg_id=call.message.message_id
    )
    await show_translation_dashboard(call, state)

# ==========================================
# АДМИН ПАНЕЛЬ
# ==========================================

@router.callback_query(F.data == "admin_entry")
async def admin_panel_callback(call: types.CallbackQuery):
    await admin_panel_logic(call.message, call.from_user.id, is_edit=True)

@router.message(Command("admin"))
async def admin_panel_command(message: types.Message):
    await admin_panel_logic(message, message.from_user.id, is_edit=False)

async def admin_panel_logic(message: types.Message, user_id, is_edit=False, msg_id=None):
    if user_id not in db.get_admins():
        return

    status = "включён" if db.is_bot_enabled() else "выключен"
    text = f"{EMOJI_ADMIN} " + TR("admin_panel_title", user_id, status)

    kb = InlineKeyboardBuilder()
    kb.button(text=f"🌐 {TR('btn_manage_langs', user_id)}", callback_data="admin_langs")
    if user_id == MAIN_ADMIN_ID:
        kb.button(text=f"👥 {TR('btn_admins', user_id)}", callback_data="admin_users_menu")
        kb.button(text=f"🗂 {TR('btn_categories', user_id)}", callback_data="adm_categories")
        toggle_text = "выключить" if db.is_bot_enabled() else "включить"
        kb.button(text=f"🔄 {TR('btn_toggle_bot', user_id, toggle_text)}", callback_data="toggle_bot")
    kb.button(text=f"⬅️ {TR('back', user_id)}", callback_data="main_menu")
    kb.adjust(1)

    if is_edit and msg_id:
        await bot.edit_message_text(text, chat_id=message.chat.id, message_id=msg_id, reply_markup=kb.as_markup())
    elif is_edit:
        await message.edit_text(text, reply_markup=kb.as_markup())
    else:
        await message.answer(text, reply_markup=kb.as_markup())

@router.callback_query(F.data == "toggle_bot")
async def toggle_bot_handler(call: types.CallbackQuery):
    uid = call.from_user.id
    if uid != MAIN_ADMIN_ID:
        return

    db.toggle_bot_enabled()
    await admin_panel_logic(call.message, uid, is_edit=True, msg_id=call.message.message_id)

@router.callback_query(F.data == "admin_back_main")
async def admin_back_handler(call: types.CallbackQuery):
    await admin_panel_logic(call.message, call.from_user.id, is_edit=True)

@router.callback_query(F.data == "admin_langs")
async def admin_manage_langs(call: types.CallbackQuery):
    uid = call.from_user.id
    text = f"{EMOJI_MANAGE} " + TR("manage_langs_title", uid)

    kb = InlineKeyboardBuilder()
    kb.button(text=f"➕ {TR('btn_create_new', uid)}", callback_data="adm_create_new")
    kb.button(text=f"📝 {TR('btn_drafts', uid)}", callback_data="adm_drafts")
    if uid == MAIN_ADMIN_ID:
        kb.button(text=f"🔤 {TR('btn_strings', uid)}", callback_data="adm_strings")
    kb.button(text=f"⬅️ {TR('back', uid)}", callback_data="admin_back_main")
    kb.adjust(1)

    await call.message.edit_text(text, reply_markup=kb.as_markup())

# ------------------------------------
# УПРАВЛЕНИЕ АДМИНАМИ
# ------------------------------------

@router.callback_query(F.data == "admin_users_menu")
async def admin_users_menu(call: types.CallbackQuery):
    uid = call.from_user.id
    admins = db.get_admins()
    if uid == MAIN_ADMIN_ID:
        admins = [a for a in admins if a != MAIN_ADMIN_ID]

    text = TR("admins_list_title", uid, len(admins))

    kb = InlineKeyboardBuilder()

    # Только главный админ может создавать приглашения
    if uid == MAIN_ADMIN_ID:
        kb.button(text=f"🔗 {TR('btn_gen_invite', uid)}", callback_data="adm_gen_invite")

    # Список админов 
    for aid in admins:
        if aid == MAIN_ADMIN_ID:
            btn_text = f"👑 {aid}"
            callback = "ignore"
        elif aid == uid:
            btn_text = f"👤 {aid} (You)"
            callback = "ignore"
        else:
            btn_text = f"👤 {aid}"
            callback = f"adm_view_{aid}"

        kb.button(text=btn_text, callback_data=callback)

    kb.button(text=f"⬅️ {TR('back', uid)}", callback_data="admin_back_main")
    kb.adjust(1)

    await call.message.edit_text(text, reply_markup=kb.as_markup())

@router.callback_query(F.data.startswith("adm_view_"))
async def admin_view_specific_user(call: types.CallbackQuery):
    uid = call.from_user.id
    target_id = call.data.split("_")[2]

    text = TR("admin_manage_user_title", uid, target_id)

    kb = InlineKeyboardBuilder()
    kb.button(text=TR("btn_delete_admin_user", uid), callback_data=f"adm_remove_{target_id}")
    kb.button(text=f"⬅️ {TR('back', uid)}", callback_data="admin_users_menu")
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
    db.add_invite_token(token)

    bot_info = await bot.get_me()
    link = f"https://t.me/{bot_info.username}?start=admin_{token}"

    text = TR("invite_text", uid, link)

    kb = InlineKeyboardBuilder()
    kb.button(text=f"⬅️ {TR('back', uid)}", callback_data="admin_users_menu")

    await call.message.edit_text(text, reply_markup=kb.as_markup())

# ------------------------------------
# УПРАВЛЕНИЕ КАТЕГОРИЯМИ
# ------------------------------------

async def adm_categories_menu(call_or_message: types.CallbackQuery | types.Message, state: FSMContext = None, edit_msg_id: Optional[int] = None):
    if isinstance(call_or_message, types.CallbackQuery):
        uid = call_or_message.from_user.id
        msg = call_or_message.message
        chat_id = msg.chat.id
        message_id = msg.message_id
    else:
        uid = call_or_message.from_user.id
        msg = call_or_message
        chat_id = msg.chat.id
        message_id = None  # Will use edit_msg_id if provided

    if uid != MAIN_ADMIN_ID:
        if isinstance(call_or_message, types.CallbackQuery):
            await call_or_message.answer(TR("access_denied", uid), show_alert=True)
        return

    text = f"{EMOJI_CATEGORY} {TR('manage_categories_title', uid)}"

    kb = InlineKeyboardBuilder()
    for cat_key in TRANSLATION_CATEGORIES:
        kb.button(text=TRANSLATION_CATEGORIES[cat_key]["name"], callback_data=f"view_cat_{cat_key}")
    kb.button(text=f"➕ создать", callback_data="add_new_cat")
    kb.button(text=f"⬅️ {TR('back', uid)}", callback_data="admin_back_main")
    kb.adjust(1)

    reply_markup = kb.as_markup()

    if edit_msg_id:
        await bot.edit_message_text(text, chat_id=chat_id, message_id=edit_msg_id, reply_markup=reply_markup)
    elif message_id:
        await bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=reply_markup)
    else:
        await msg.answer(text, reply_markup=reply_markup)

@router.callback_query(F.data == "adm_categories")
async def adm_categories_handler(call: types.CallbackQuery, state: FSMContext):
    await adm_categories_menu(call, state)

@router.callback_query(F.data.startswith("view_cat_"))
async def view_category_handler(call: types.CallbackQuery):
    uid = call.from_user.id
    cat_key = "_".join(call.data.split("_")[2:])
    cat = TRANSLATION_CATEGORIES.get(cat_key)
    if not cat:
        return

    text = TR("cat_view_title", uid, cat["name"]) + "\n" + TR("cat_view_count", uid, len(cat["keys"]))

    kb = InlineKeyboardBuilder()
    kb.button(text=f"🗑 {TR('btn_delete', uid)}", callback_data=f"del_cat_{cat_key}")
    kb.button(text=f"🖊 {TR('btn_change', uid)}", callback_data=f"edit_cat_{cat_key}")
    kb.button(text=f"⬅️ {TR('back', uid)}", callback_data="adm_categories")
    kb.adjust(1)

    await call.message.edit_text(text, reply_markup=kb.as_markup())

@router.callback_query(F.data.startswith("del_cat_"))
async def delete_category_handler(call: types.CallbackQuery):
    uid = call.from_user.id
    if uid != MAIN_ADMIN_ID:
        return

    cat_key = "_".join(call.data.split("_")[2:])
    db.remove_category(cat_key)
    global TRANSLATION_CATEGORIES
    TRANSLATION_CATEGORIES = db.get_translation_categories()
    await adm_categories_menu(call)

@router.callback_query(F.data.startswith("edit_cat_"))
async def edit_category_start(call: types.CallbackQuery, state: FSMContext):
    uid = call.from_user.id
    if uid != MAIN_ADMIN_ID:
        return

    cat_key = "_".join(call.data.split("_")[2:])
    await state.update_data(edit_cat_key=cat_key, msg_id=call.message.message_id)
    await call.message.edit_text(TR("enter_name", uid))
    await state.set_state(AdminStates.edit_cat_name)

@router.message(AdminStates.edit_cat_name)
async def edit_category_process(message: types.Message, state: FSMContext):
    uid = message.from_user.id
    data = await state.get_data()
    cat_key = data.get("edit_cat_key")
    msg_id = data.get("msg_id")
    new_name = message.text.strip()
    await message.delete()

    if not new_name:
        await bot.edit_message_text(TR("cat_name_empty", uid), chat_id=message.chat.id, message_id=msg_id)
        return

    db.update_category_name(cat_key, new_name)
    global TRANSLATION_CATEGORIES
    TRANSLATION_CATEGORIES = db.get_translation_categories()

    await state.clear()
    await adm_categories_menu(message, edit_msg_id=msg_id)

@router.callback_query(F.data == "add_new_cat")
async def add_category_start(call: types.CallbackQuery, state: FSMContext):
    uid = call.from_user.id
    if uid != MAIN_ADMIN_ID:
        return

    await call.message.edit_text(TR("enter_name", uid))
    await state.set_state(AdminStates.add_cat_name)
    await state.update_data(msg_id=call.message.message_id)

@router.message(AdminStates.add_cat_name)
async def add_category_process(message: types.Message, state: FSMContext):
    uid = message.from_user.id
    data = await state.get_data()
    msg_id = data.get("msg_id")
    name = message.text.strip()
    await message.delete()

    if not name:
        await bot.edit_message_text(TR("cat_name_empty", uid), chat_id=message.chat.id, message_id=msg_id)
        return

    cat_key = name.lower().replace(" ", "_")  # Simple key generation
    if not cat_key:
        await bot.edit_message_text(TR("cat_key_invalid", uid), chat_id=message.chat.id, message_id=msg_id)
        return

    added = db.add_category(cat_key, name)
    if not added:
        await bot.edit_message_text(TR("cat_exists", uid), chat_id=message.chat.id, message_id=msg_id)
        return

    global TRANSLATION_CATEGORIES
    TRANSLATION_CATEGORIES = db.get_translation_categories()

    await state.clear()
    await adm_categories_menu(message, edit_msg_id=msg_id)

# ------------------------------------
# УПРАВЛЕНИЕ СТРОКАМИ
# ------------------------------------

@router.callback_query(F.data == "adm_strings")
async def adm_strings_menu(call: types.CallbackQuery):
    uid = call.from_user.id
    if uid != MAIN_ADMIN_ID:
        await call.answer(TR("access_denied", uid), show_alert=True)
        return

    text = f"{EMOJI_DESC} {TR('manage_strings_title', uid)}"

    kb = InlineKeyboardBuilder()
    kb.button(text=f"👀 посмотреть все", callback_data="view_all_strings")
    kb.button(text=f"➕ добавить новую", callback_data="add_new_string")
    kb.button(text=f"📥 импорт", callback_data="import_strings")
    kb.button(text=f"📤 экспорт", callback_data="export_strings")
    kb.adjust(1, 1, 2)
    kb.button(text=f"⬅️ {TR('back', uid)}", callback_data="admin_langs")

    await call.message.edit_text(text, reply_markup=kb.as_markup())

@router.callback_query(F.data == "export_strings")
async def export_strings_handler(call: types.CallbackQuery):
    uid = call.from_user.id
    if uid != MAIN_ADMIN_ID:
        return

    content_str = json.dumps(BASE_TEMPLATE, ensure_ascii=False, indent=2)
    file_bytes = io.BytesIO(content_str.encode('utf-8'))
    file_input = BufferedInputFile(file_bytes.getvalue(), filename="base_template.txt")

    await call.message.edit_text(TR("strings_export_sent", uid))
    await call.message.answer_document(file_input)

@router.callback_query(F.data == "import_strings")
async def import_strings_start(call: types.CallbackQuery, state: FSMContext):
    uid = call.from_user.id
    if uid != MAIN_ADMIN_ID:
        return

    await call.message.edit_text("Отправьте .txt, .json, .lang или .rclang файл с JSON")
    await state.set_state(AdminStates.importing_strings)
    await state.update_data(msg_id=call.message.message_id)

@router.message(AdminStates.importing_strings, F.document)
async def import_strings_process(message: types.Message, state: FSMContext):
    uid = message.from_user.id
    if uid != MAIN_ADMIN_ID:
        return

    data = await state.get_data()
    msg_id = data.get("msg_id")

    file_id = message.document.file_id
    file_info = await bot.get_file(file_id)
    downloaded_file = await bot.download_file(file_info.file_path)

    try:
        new_template = json.load(downloaded_file)
        # Поддержка .rclang: игнорируем метаданные
        if 'lang_name' in new_template:
            new_template = {k: v for k, v in new_template.items() if k not in ['lang_name', 'author', 'description']}
        db.update_base_template(new_template)
        global BASE_TEMPLATE
        BASE_TEMPLATE = new_template

        # Clear categories keys
        categories = db.get_translation_categories()
        for cat in categories.values():
            cat["keys"] = []
        db.update_translation_categories(categories)
        global TRANSLATION_CATEGORIES
        TRANSLATION_CATEGORIES = categories

        await message.delete()

        uncat_keys = list(BASE_TEMPLATE.keys())
        if uncat_keys:
            await state.update_data(uncat_keys=uncat_keys, uncat_index=0)
            await show_assign_category(message, state)
        else:
            await admin_panel_logic(message, uid, is_edit=True, msg_id=msg_id)
            await state.clear()

    except json.JSONDecodeError:
        await message.delete()
        await bot.edit_message_text("Ошибка: Некорректный JSON", chat_id=message.chat.id, message_id=msg_id)
    except Exception as e:
        logger.error(e)
        await message.delete()
        await bot.edit_message_text("Ошибка импорта", chat_id=message.chat.id, message_id=msg_id)

async def show_assign_category(message_or_call, state: FSMContext):
    if isinstance(message_or_call, types.Message):
        uid = message_or_call.from_user.id
        chat_id = message_or_call.chat.id
        message_obj = message_or_call
    else:
        uid = message_or_call.from_user.id
        chat_id = message_or_call.message.chat.id
        message_obj = message_or_call.message

    data = await state.get_data()
    uncat_keys = data.get("uncat_keys", [])
    index = data.get("uncat_index", 0)
    msg_id = data.get("msg_id")

    if index >= len(uncat_keys):
        await state.clear()
        db.remove_sorting_draft(uid)
        await admin_panel_logic(message_obj, uid, is_edit=True, msg_id=msg_id)
        return

    remaining = len(uncat_keys) - index
    current_key = uncat_keys[index]

    text = TR("assign_cat_remaining", uid, remaining) + "\n" + TR("assign_cat_for", uid, current_key, BASE_TEMPLATE.get(current_key, ""))

    kb = InlineKeyboardBuilder()
    for cat_key in TRANSLATION_CATEGORIES:
        kb.button(text=TRANSLATION_CATEGORIES[cat_key]["name"], callback_data=f"assign_cat_{cat_key}")
    kb.adjust(1)

    await bot.edit_message_text(text, chat_id=chat_id, message_id=msg_id, reply_markup=kb.as_markup())
    await state.set_state(AdminStates.assigning_category)

@router.callback_query(F.data.startswith("assign_cat_"), AdminStates.assigning_category)
async def assign_category_handler(call: types.CallbackQuery, state: FSMContext):
    uid = call.from_user.id
    cat_key = "_".join(call.data.split("_")[2:])

    data = await state.get_data()
    uncat_keys = data.get("uncat_keys", [])
    index = data.get("uncat_index", 0)
    current_key = uncat_keys[index]

    db.add_string_to_category(current_key, cat_key)

    await state.update_data(uncat_index=index + 1)
    await show_assign_category(call, state)

@router.callback_query(F.data == "view_all_strings")
async def view_all_strings_handler(call: types.CallbackQuery, state: FSMContext):
    uid = call.from_user.id
    if uid != MAIN_ADMIN_ID:
        return

    await show_strings_page(call, 0)

async def show_strings_page(call_or_message, page):
    if isinstance(call_or_message, types.CallbackQuery):
        uid = call_or_message.from_user.id
        msg = call_or_message.message
    else:
        uid = call_or_message.from_user.id
        msg = call_or_message

    all_keys = sorted(list(BASE_TEMPLATE.keys()))
    per_page = 8
    total_pages = (len(all_keys) + per_page - 1) // per_page
    start = page * per_page
    end = start + per_page
    slice_keys = all_keys[start:end]

    text = f"{EMOJI_DESC} {TR('strings_page_title', uid)}\nстраница {page + 1} из {total_pages}\nна странице {len(slice_keys)} строк из {len(all_keys)}\nвыберите нужную:"

    kb = InlineKeyboardBuilder()
    for i in range(0, len(slice_keys), 2):
        row = []
        row.append(InlineKeyboardButton(text=slice_keys[i], callback_data=f"view_string_{slice_keys[i]}_{page}"))
        if i + 1 < len(slice_keys):
            row.append(InlineKeyboardButton(text=slice_keys[i+1], callback_data=f"view_string_{slice_keys[i+1]}_{page}"))
        kb.row(*row)

    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text="◀️", callback_data=f"strings_page_{page-1}"))
    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton(text="➡️", callback_data=f"strings_page_{page+1}"))
    if nav_row:
        kb.row(*nav_row)

    kb.button(text=f"⬅️ {TR('back', uid)}", callback_data="adm_strings")

    if isinstance(call_or_message, types.CallbackQuery):
        await msg.edit_text(text, reply_markup=kb.as_markup())
    else:
        await msg.answer(text, reply_markup=kb.as_markup())

@router.callback_query(F.data.startswith("strings_page_"))
async def strings_page_handler(call: types.CallbackQuery):
    page = int(call.data.split("_")[2])
    await show_strings_page(call, page)

@router.callback_query(F.data.startswith("view_string_"))
async def view_string_handler(call: types.CallbackQuery, state: FSMContext):
    parts = call.data.split("_")
    key = "_".join(parts[2:-1])  # because key may have _, last is page
    page = int(parts[-1])
    uid = call.from_user.id

    value = BASE_TEMPLATE.get(key, "???")
    cat_name = find_category_for_key(key)

    text = f"<b>код: {key}</b>\n<blockquote>перевод: {value}\nкатегория: {cat_name}</blockquote>"

    kb = InlineKeyboardBuilder()
    kb.button(text=f"🗑 {TR('btn_delete', uid)}", callback_data=f"delete_string_{key}_{page}")
    kb.button(text=f"🖊 {TR('btn_change', uid)}", callback_data=f"edit_string_{key}_{page}")
    kb.button(text=f"⬅️ {TR('back', uid)}", callback_data=f"strings_page_{page}")
    kb.adjust(1, 1)

    await call.message.edit_text(text, reply_markup=kb.as_markup())

@router.callback_query(F.data.startswith("delete_string_"))
async def delete_string_handler(call: types.CallbackQuery):
    parts = call.data.split("_")
    key = "_".join(parts[2:-1])
    page = int(parts[-1])
    uid = call.from_user.id

    if key in BASE_TEMPLATE:
        del BASE_TEMPLATE[key]
        db.update_base_template(BASE_TEMPLATE)
        db.remove_string_from_categories(key)
        await call.answer("Строка удалена", show_alert=True)
    await show_strings_page(call, page)

@router.callback_query(F.data.startswith("edit_string_"))
async def edit_string_start(call: types.CallbackQuery, state: FSMContext):
    parts = call.data.split("_")
    key = "_".join(parts[2:-1])
    page = int(parts[-1])
    uid = call.from_user.id

    await state.update_data(edit_key=key, strings_page=page)
    await call.message.edit_text("Введите новое значение для строки:")
    await state.set_state(AdminStates.edit_string)

@router.message(AdminStates.edit_string)
async def edit_string_process(message: types.Message, state: FSMContext):
    uid = message.from_user.id
    data = await state.get_data()
    key = data.get("edit_key")
    page = data.get("strings_page")
    new_value = message.text.strip()

    if key in BASE_TEMPLATE:
        BASE_TEMPLATE[key] = new_value
        db.update_base_template(BASE_TEMPLATE)

    await message.delete()
    await state.clear()
    await show_strings_page(message, page)

# --- ДОБАВЛЕНИЕ СТРОКИ ---
@router.callback_query(F.data == "add_new_string")
async def start_add_string(call: types.CallbackQuery, state: FSMContext):
    uid = call.from_user.id
    if uid != MAIN_ADMIN_ID:
        return

    await call.message.edit_text("Code:")
    await state.set_state(AdminStates.add_string_code)
    await state.update_data(msg_id=call.message.message_id)

@router.message(AdminStates.add_string_code)
async def process_string_code(message: types.Message, state: FSMContext):
    data = await state.get_data()
    msg_id = data.get("msg_id")
    code = message.text.strip()
    await message.delete()
    await bot.edit_message_text(f"Code: {code}\nValue:", chat_id=message.chat.id, message_id=msg_id)
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
    db.update_base_template(BASE_TEMPLATE)

    text = TR("select_category", message.from_user.id)
    kb = InlineKeyboardBuilder()
    for cat_key in TRANSLATION_CATEGORIES:
        kb.button(text=TRANSLATION_CATEGORIES[cat_key]["name"], callback_data=f"assign_new_cat_{cat_key}")
    kb.adjust(1)

    await bot.edit_message_text(text, chat_id=message.chat.id, message_id=msg_id, reply_markup=kb.as_markup())
    await state.set_state(AdminStates.add_string_category)

@router.callback_query(F.data.startswith("assign_new_cat_"), AdminStates.add_string_category)
async def assign_new_string_category(call: types.CallbackQuery, state: FSMContext):
    cat_key = "_".join(call.data.split("_")[3:])
    data = await state.get_data()
    new_key = data.get("new_key")

    db.add_string_to_category(new_key, cat_key)

    await call.answer("Строка добавлена", show_alert=True)
    await state.clear()
    await admin_manage_langs(call)

# --- WIZARD СОЗДАНИЯ ---

@router.callback_query(F.data == "adm_create_new")
async def wizard_step1_cat(call: types.CallbackQuery, state: FSMContext):
    uid = call.from_user.id
    if db.get_sorting_draft(uid):
        await call.answer(TR("create_lang_unavailable", uid), show_alert=True)
        return

    text = f"{EMOJI_CATEGORY} " + TR("wiz_step1", uid)
    kb = InlineKeyboardBuilder()
    kb.button(text=f"🎨 {TR('cat_type_custom', uid)}", callback_data="w_cat_custom")
    kb.button(text=f"🌐 {TR('cat_type_global', uid)}", callback_data="w_cat_global")
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
    kb.button(text=f"📄 {TR('wiz_btn_scratch', uid)}", callback_data="method_scratch")
    kb.button(text=f"📤 {TR('wiz_btn_upload', uid)}", callback_data="method_upload")
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
        file_data = json.load(downloaded_file)
        content = file_data
        name = data["name"]
        desc = data["desc"]
        # Поддержка .rclang: извлекаем метаданные
        if "lang_name" in content:
            name = content.pop("lang_name", name)
            author = content.pop("author", "")
            file_desc = content.pop("description", "")
            if file_desc:
                desc = file_desc if not desc else desc + "\n" + file_desc
            if author:
                desc += f"\nAuthor: {author}" if desc else f"Author: {author}"
            content = {k: v for k, v in content.items() if k not in ["lang_name", "author", "description"]}
    except json.JSONDecodeError:
        await message.delete()
        await bot.edit_message_text("JSON Error", chat_id=message.chat.id, message_id=msg_id)
        return
    except Exception as e:
        logger.error(e)
        await message.delete()
        await bot.edit_message_text("Error", chat_id=message.chat.id, message_id=msg_id)
        return

    await message.delete()

    new_lang = {
        "id": str(uuid.uuid4())[:8],
        "name": name,
        "description": desc,
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
        msg = call_or_message.message
    else:
        uid = call_or_message.from_user.id
        msg = call_or_message

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
    kb.button(text=TR("trans_draft", uid), callback_data="trans_draft")
    kb.adjust(1)

    msg_id = data.get("msg_id")
    if isinstance(call_or_message, types.CallbackQuery):
        await msg.edit_text(text, reply_markup=kb.as_markup())
    else:
        await bot.edit_message_text(text=text, chat_id=msg.chat.id, message_id=msg_id, reply_markup=kb.as_markup())

    await state.set_state(AdminStates.translating_dashboard)

@router.callback_query(F.data.startswith("trans_cat_"))
async def start_category_translation(call: types.CallbackQuery, state: FSMContext):
    cat_key = "_".join(call.data.split("_")[2:])
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
            f"{TR('original_label', uid)}:\n<blockquote>{original_text}</blockquote>\n"
            f"{TR('trans_label', uid)}:\n<blockquote>{current_translation}</blockquote>")

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
    uid = call.from_user.id
    data = await state.get_data()

    updates = {
        "content": data["content"],
        "date": datetime.now().strftime("%d.%m.%y")
    }

    if "edit_id" in data:
        db.update_language(data["edit_id"], updates)
        if "draft_id" in data:
            db.remove_draft(data["draft_id"], uid)
        await call.answer(TR("lang_updated", call.from_user.id), show_alert=True)
    else:
        new_lang = {
            "id": str(uuid.uuid4())[:8],
            "name": data["name"],
            "description": data["desc"],
            "type": data["cat"],
            "content": data["content"],
            "date": updates["date"],
            "author_id": call.from_user.id
        }
        db.add_language(new_lang)
        if "draft_id" in data:
            db.remove_draft(data["draft_id"], uid)
        await call.answer(TR("wiz_done", call.from_user.id), show_alert=True)

    kb = InlineKeyboardBuilder()
    kb.button(text=TR("to_menu", call.from_user.id), callback_data="admin_langs")

    await call.message.edit_text(
        text=f"{EMOJI_DONE} {TR('wiz_done' if 'edit_id' not in data else 'lang_updated', call.from_user.id)}",
        reply_markup=kb.as_markup()
    )
    await state.clear()

@router.callback_query(F.data == "trans_draft")
async def handle_trans_draft(call: types.CallbackQuery, state: FSMContext):
    uid = call.from_user.id
    data = await state.get_data()
    updates = {
        "content": data["content"],
        "date": datetime.now().strftime("%d.%m.%y")
    }
    if "draft_id" in data:
        db.update_draft(data["draft_id"], updates, uid)
        await call.answer("Сохранено в черновик", show_alert=True)
    else:
        new_draft = {
            "id": str(uuid.uuid4())[:8],
            "name": data["name"],
            "description": data["desc"],
            "type": data["cat"],
            "content": data["content"],
            "date": updates["date"],
            "author_id": uid
        }
        db.add_draft(uid, new_draft)
        await call.answer("Добавлено в черновики", show_alert=True)
    await state.clear()
    await admin_manage_langs(call)

@router.callback_query(F.data == "adm_drafts")
async def show_drafts(call: types.CallbackQuery):
    uid = call.from_user.id
    drafts = db.get_drafts(uid)

    if not drafts:
        text = TR("drafts_empty", uid)
    else:
        text = TR("drafts_title", uid)

    kb = InlineKeyboardBuilder()
    for draft in drafts:
        if draft.get("type") == "sorting":
            kb.button(text=f"📏 {TR('draft_sorting', uid)}", callback_data="resume_sorting")
        else:
            kb.button(text=draft["name"], callback_data=f"view_draft_{draft['id']}")
    kb.button(text=f"⬅️ {TR('back', uid)}", callback_data="admin_langs")
    kb.adjust(1)

    await call.message.edit_text(text, reply_markup=kb.as_markup())

@router.callback_query(F.data == "resume_sorting")
async def resume_sorting(call: types.CallbackQuery, state: FSMContext):
    uid = call.from_user.id
    sorting_draft = db.get_sorting_draft(uid)
    if sorting_draft:
        await state.update_data(uncat_keys=sorting_draft["uncat_keys"], uncat_index=sorting_draft["uncat_index"], msg_id=call.message.message_id)
        await show_assign_category(call, state)

@router.callback_query(F.data.startswith("view_draft_"))
async def view_draft(call: types.CallbackQuery):
    uid = call.from_user.id
    draft_id = call.data.split("_")[2]
    draft = db.get_draft_by_id(draft_id, uid)
    if not draft:
        await call.answer("Error")
        return

    total_keys = len(BASE_TEMPLATE)
    translated_keys = len(draft.get("content", {}))

    text = (
        f"{EMOJI_GLOBAL} " + TR("draft_view_title", uid, draft['name']) + "\n"
        f"<blockquote>" + TR("lang_view_stats", uid, translated_keys, total_keys) + "\n"
        + TR("lang_view_date", uid, draft.get('date', '...')) + "\n"
        + TR("lang_view_desc", uid, draft['description']) + "</blockquote>\n"
    )

    kb = InlineKeyboardBuilder()
    kb.button(text=TR("trans_publish", uid), callback_data=f"draft_publish_{draft_id}")
    kb.button(text=f"🖊 {TR('btn_edit', uid)}", callback_data=f"draft_edit_{draft_id}")
    kb.button(text=TR("delete_admin", uid), callback_data=f"draft_delete_{draft_id}")
    kb.button(text=f"⬅️ {TR('back', uid)}", callback_data="adm_drafts")
    kb.adjust(1)

    await call.message.edit_text(text, reply_markup=kb.as_markup())

@router.callback_query(F.data.startswith("draft_publish_"))
async def draft_publish(call: types.CallbackQuery):
    uid = call.from_user.id
    draft_id = call.data.split("_")[2]
    draft = db.get_draft_by_id(draft_id, uid)
    if draft:
        db.add_language(draft)
        db.remove_draft(draft_id, uid)
        await call.answer(TR("wiz_done", uid), show_alert=True)
        await admin_manage_langs(call)
    else:
        await call.answer("Error")

@router.callback_query(F.data.startswith("draft_delete_"))
async def draft_delete(call: types.CallbackQuery):
    uid = call.from_user.id
    draft_id = call.data.split("_")[2]
    db.remove_draft(draft_id, uid)
    await call.answer(TR("lang_deleted", uid), show_alert=True)
    await show_drafts(call)

@router.callback_query(F.data.startswith("draft_edit_"))
async def draft_edit(call: types.CallbackQuery, state: FSMContext):
    uid = call.from_user.id
    draft_id = call.data.split("_")[2]
    draft = db.get_draft_by_id(draft_id, uid)
    if not draft:
        return
    await state.set_state(AdminStates.translating_dashboard)
    await state.update_data(
        cat=draft["type"],
        name=draft["name"],
        desc=draft["description"],
        content=draft["content"],
        draft_id=draft_id,
        msg_id=call.message.message_id
    )
    await show_translation_dashboard(call, state)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass