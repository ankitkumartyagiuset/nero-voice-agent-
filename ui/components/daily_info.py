"""
Daily Information Panel Component for NERO HUD.
Displays Live System Clock, Calendar Date, Real Weather, and Live Tech News.
"""
from typing import Optional
from datetime import datetime
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt, QTimer
from .glass_panel import GlassPanel
from services.weather_service import get_weather_service
from services.news_service import get_news_service
from utils.helpers import get_current_time_str, get_current_date_str


class DailyInfoPanel(GlassPanel):
    """HUD Card displaying live real-time metrics, weather, and news."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(title="DAILY INFO", parent=parent)
        self.weather_service = get_weather_service()
        self.news_service = get_news_service()

        # 1. Live Digital Clock & Date
        clock_layout = QVBoxLayout()
        clock_layout.setSpacing(2)

        self._time_label = QLabel(get_current_time_str())
        self._time_label.setStyleSheet("font-size: 26px; font-weight: bold; color: #00f0ff; letter-spacing: 1px;")

        self._date_label = QLabel(get_current_date_str())
        self._date_label.setStyleSheet("font-size: 12px; color: #8fa3bf;")

        clock_layout.addWidget(self._time_label)
        clock_layout.addWidget(self._date_label)
        self.inner_layout.addLayout(clock_layout)

        # Separator
        self.inner_layout.addWidget(self._create_separator())

        # 2. Live Weather Widget
        weather_header = QLabel("LOCAL WEATHER")
        weather_header.setObjectName("SubtleLabel")
        self.inner_layout.addWidget(weather_header)

        self._weather_label = QLabel("Loading weather...")
        self._weather_label.setStyleSheet("font-size: 13px; color: #ffffff;")
        self.inner_layout.addWidget(self._weather_label)

        # Separator
        self.inner_layout.addWidget(self._create_separator())

        # 3. Live News Headlines Ticker
        news_header = QLabel("TECH NEWS HEADLINES")
        news_header.setObjectName("SubtleLabel")
        self.inner_layout.addWidget(news_header)

        self._news_label = QLabel("Fetching latest headlines...")
        self._news_label.setWordWrap(True)
        self._news_label.setStyleSheet("font-size: 11px; color: #8fa3bf; line-height: 1.3;")
        self.inner_layout.addWidget(self._news_label)

        self.inner_layout.addStretch()

        # Update Timers
        self._clock_timer = QTimer(self)
        self._clock_timer.setInterval(1000)
        self._clock_timer.timeout.connect(self._update_clock)
        self._clock_timer.start()

        self._info_timer = QTimer(self)
        self._info_timer.setInterval(180000) # 3 mins refresh
        self._info_timer.timeout.connect(self._fetch_external_data)
        self._info_timer.start()

        # Initial fetch
        QTimer.singleShot(100, self._fetch_external_data)

    def _create_separator(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: rgba(0, 240, 255, 0.15); height: 1px; border: none;")
        return line

    def _update_clock(self) -> None:
        self._time_label.setText(get_current_time_str())
        self._date_label.setText(get_current_date_str())

    def _fetch_external_data(self) -> None:
        # 1. Update weather
        wdata = self.weather_service.get_current_weather()
        if wdata.get("available", False):
            temp = wdata.get("temperature_c")
            cond = wdata.get("condition")
            city = wdata.get("city")
            self._weather_label.setText(f"🌡️ {temp}°C • {cond} ({city})")
        else:
            self._weather_label.setText("🌡️ Weather: Service offline")

        # 2. Update news
        news = self.news_service.get_latest_headlines(limit=2)
        if news:
            titles = [f"• {item['title']}" for item in news]
            self._news_label.setText("\n".join(titles))
        else:
            self._news_label.setText("• No news feed updates available.")
