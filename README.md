# Weather Server

Сервер прогноза погоды для Домодедово и Тушино.

## Что показывает
- Туман (visibility < 1000 м)
- Гроза (weather_code 95/96/99)
- Осадки (precipitation > 0)

## Запуск
pip install flask requests
python server.py

## Адреса
- http://localhost:5000/forecast/tushino — таблица
- http://localhost:5000/api/tushino — JSON
- http://localhost:5000/compare — сравнение станций