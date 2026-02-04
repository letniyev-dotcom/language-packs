import time
import threading
from typing import Optional

from base_plugin import BasePlugin
from android_utils import run_on_ui_thread, log
from client_utils import get_last_fragment
from hook_utils import find_class

# UI Components
from ui.settings import Header, Text, Selector, Switch, Divider, Input
from ui.bulletin import BulletinHelper

# Android Imports
from android.graphics import Color, Typeface, android_graphics
from android.widget import TextView, FrameLayout
from android.view import Gravity, ViewGroup, View
from org.telegram.messenger import AndroidUtilities

# --- METADATA ---
__id__ = "fps_counter_pro"
__name__ = "FPS Counter Pro"
__description__ = "FPS монитор (Fixed Visuals)"
__author__ = "User & Gemini"
__version__ = "2.1.0"
__icon__ = "msg_stats"
min_version = "12.0.0"


class FPSPlugin(BasePlugin):
    def init(self):
        super().init()
        self.text_view: Optional[TextView] = None
        # Переменные для логики
        self.last_time = 0
        self.frame_count = 0
        self.current_fps = 0
        self.min_fps = 999
        self.max_fps = 0
        self.fps_history = []
        self.is_enabled = False
        self.is_visible = False
        self.measurement_thread = None
        self.stop_measurement = False
        
    def create_settings(self):
        return [
            Header("Основное"),
            Switch("enabled", "Включить счетчик", False, self._toggle_enabled, icon="msg_stats"),
            Divider(),
            Header("Внешний вид"),
            Selector("position", "Позиция", 1, ["Верх-Лево", "Верх-Право", "Низ-Лево", "Низ-Право"], self._update_layout_params, icon="msg_location"),
            Selector("text_size", "Размер текста", 1, ["Маленький", "Средний", "Большой"], self._update_style, icon="msg_fontsize"),
            Selector("color_mode", "Цвет текста", 0, ["Авто (светофор)", "Белый", "Зеленый", "Яркий"], self._update_style, icon="msg_palette"),
            Switch("show_bg", "Фон подложки", True, self._update_style, icon="msg_background"),
            Input("bg_alpha", "Прозрачность фона (0-255)", "100"),
            Divider(),
            Text("Тест (3 сек)", lambda v: self._run_test()),
            Text("Сброс статистики", lambda v: self._reset_stats(), red=True),
        ]

    def on_plugin_load(self):
        self.is_enabled = self.get_setting("enabled", False)
        if self.is_enabled:
            # Ждем немного, пока Activity полностью загрузится
            run_on_ui_thread(self._show_counter, delay=1.0)
        return True

    def on_plugin_unload(self):
        self._hide_counter()

    def _toggle_enabled(self, val=None):
        self.is_enabled = not self.is_enabled if val is None else val
        self.set_setting("enabled", self.is_enabled)
        if self.is_enabled:
            self._show_counter()
        else:
            self._hide_counter()

    def _show_counter(self):
        if self.is_visible: return
        
        def _create():
            try:
                activity = self._get_activity()
                if not activity: return

                # 1. Создаем TextView
                self.text_view = TextView(activity)
                self.text_view.setText("FPS: Init...")
                self.text_view.setTypeface(Typeface.MONOSPACE, Typeface.BOLD)
                
                # 2. Важно: Elevation поднимает View над остальными слоями Telegram
                self.text_view.setElevation(AndroidUtilities.dp(10)) 
                
                # 3. Настройка отступов внутри плашки
                pad = AndroidUtilities.dp(6)
                self.text_view.setPadding(pad, pad // 2, pad, pad // 2)

                # 4. Формируем LayoutParams для наложения
                params = FrameLayout.LayoutParams(
                    FrameLayout.LayoutParams.WRAP_CONTENT,
                    FrameLayout.LayoutParams.WRAP_CONTENT
                )
                
                # 5. Используем addContentView - это добавляет View на самый верхний слой окна Activity
                activity.addContentView(self.text_view, params)
                
                self.is_visible = True
                self._update_style()
                self._update_layout_params()
                self._start_thread()
                
            except Exception as e:
                log(f"FPS Error: {e}")

        run_on_ui_thread(_create)

    def _hide_counter(self):
        self.stop_measurement = True
        if not self.is_visible: return
        
        def _remove():
            try:
                if self.text_view and self.text_view.getParent():
                    # Приводим родителя к ViewGroup для удаления
                    parent = self.text_view.getParent()
                    parent.removeView(self.text_view)
                self.text_view = None
                self.is_visible = False
            except Exception as e:
                log(f"Hide error: {e}")
                
        run_on_ui_thread(_remove)

    def _update_layout_params(self, *args):
        """Обновление позиции на экране"""
        if not self.text_view: return
        
        def _apply():
            try:
                params = self.text_view.getLayoutParams()
                pos = self.get_setting("position", 1)
                margin = AndroidUtilities.dp(10)
                # Отступ сверху для статусбара (примерно 24dp + запас)
                status_bar = AndroidUtilities.dp(35) 

                params.setMargins(0, 0, 0, 0)
                
                if pos == 0: # TL
                    params.gravity = Gravity.TOP | Gravity.LEFT
                    params.leftMargin = margin
                    params.topMargin = status_bar
                elif pos == 1: # TR
                    params.gravity = Gravity.TOP | Gravity.RIGHT
                    params.rightMargin = margin
                    params.topMargin = status_bar
                elif pos == 2: # BL
                    params.gravity = Gravity.BOTTOM | Gravity.LEFT
                    params.leftMargin = margin
                    params.bottomMargin = margin + AndroidUtilities.dp(50) # +50 чтобы не перекрывать ввод
                elif pos == 3: # BR
                    params.gravity = Gravity.BOTTOM | Gravity.RIGHT
                    params.rightMargin = margin
                    params.bottomMargin = margin + AndroidUtilities.dp(50)

                self.text_view.setLayoutParams(params)
                self.text_view.requestLayout()
            except: pass
            
        run_on_ui_thread(_apply)

    def _update_style(self, *args):
        """Обновление цветов и шрифтов"""
        if not self.text_view: return
        
        def _apply():
            try:
                # Размер
                sizes = [12, 14, 16]
                s_idx = self.get_setting("text_size", 1)
                self.text_view.setTextSize(sizes[s_idx])
                
                # Фон (объединили bg и textview)
                if self.get_setting("show_bg", True):
                    alpha = int(self.get_setting("bg_alpha", "100"))
                    # Черный фон с альфа-каналом
                    self.text_view.setBackgroundColor(Color.argb(min(255, max(0, alpha)), 0, 0, 0))
                    # Скругляем углы (необязательно, но красиво) через GradientDrawable можно, но пока просто цвет
                else:
                    self.text_view.setBackgroundColor(Color.TRANSPARENT)

            except: pass
        run_on_ui_thread(_apply)

    def _start_thread(self):
        if self.measurement_thread and self.measurement_thread.is_alive(): return
        self.stop_measurement = False
        self.measurement_thread = threading.Thread(target=self._loop, daemon=True)
        self.measurement_thread.start()

    def _loop(self):
        last_t = time.time()
        frames = 0
        
        while not self.stop_measurement:
            cur_t = time.time()
            dt = cur_t - last_t
            
            if dt >= 1.0: # Обновляем раз в секунду
                fps = frames / dt
                self.current_fps = fps
                frames = 0
                last_t = cur_t
                self._update_text()
            
            frames += 1
            # Очень короткий слип, чтобы не плавить процессор, но считать "кадры" цикла
            time.sleep(0.001)

    def _update_text(self):
        if not self.text_view: return
        
        fps = int(self.current_fps)
        mode = self.get_setting("color_mode", 0)
        
        def _ui():
            try:
                self.text_view.setText(f"FPS: {fps}")
                
                # Цвет текста
                color = Color.WHITE
                if mode == 0: # Авто
                    if fps > 50: color = Color.GREEN
                    elif fps > 30: color = Color.YELLOW
                    else: color = Color.RED
                elif mode == 2: color = Color.GREEN
                elif mode == 3: color = 0xFFFF00FF # Purple/Bright
                
                self.text_view.setTextColor(color)
            except: pass
            
        run_on_ui_thread(_ui)

    def _get_activity(self):
        try:
            # Способ 1: Через фрагмент
            frag = get_last_fragment()
            if frag: return frag.getParentActivity()
            
            # Способ 2: LaunchActivity
            act = find_class("org.telegram.ui.LaunchActivity").instance
            if act: return act
        except: pass
        return None

    def _reset_stats(self):
        self.min_fps = 999
        self.max_fps = 0
        BulletinHelper.show_success("Сброшено")

    def _run_test(self):
        BulletinHelper.show_info("Тест запущен...")
        # Просто нагрузка
        def _t():
            time.sleep(3)
            run_on_ui_thread(lambda: BulletinHelper.show_success("Тест завершен"))
        threading.Thread(target=_t).start()

plugin_instance = FPSPlugin()