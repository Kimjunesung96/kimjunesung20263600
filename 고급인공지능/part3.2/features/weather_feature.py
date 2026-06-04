import requests
from datetime import datetime


# ---------------------------------------------------------
# ⛅ 날씨 엔진
# ---------------------------------------------------------
class WeatherFeature:
    WMO_MAP = {
        0:  ("☀️",  "맑음"),
        1:  ("🌤️", "대체로 맑음"),
        2:  ("⛅",  "구름조금"),
        3:  ("☁️",  "흐림"),
        45: ("🌫️", "안개"),
        48: ("🌫️", "안개"),
        51: ("🌧️", "가벼운 이슬비"),
        53: ("🌧️", "이슬비"),
        55: ("🌧️", "강한 이슬비"),
        61: ("☔",  "가벼운 비"),
        63: ("☔",  "비"),
        65: ("☔",  "강한 비"),
        71: ("❄️",  "가벼운 눈"),
        73: ("❄️",  "눈"),
        75: ("❄️",  "강한 눈"),
        95: ("⛈️",  "천둥번개"),
    }

    @staticmethod
    def get_weather_briefing(location="서울"):
        try:
            url = (
                "https://api.open-meteo.com/v1/forecast"
                "?latitude=37.566&longitude=126.978"
                "&current_weather=true"
                "&hourly=temperature_2m,precipitation_probability,weathercode"
                "&timezone=Asia%2FSeoul"
            )
            data = requests.get(url, timeout=5).json()

            cur      = data.get("current_weather", {})
            cur_temp = cur.get("temperature", 0)
            cur_code = cur.get("weathercode", 0)

            now_hour = datetime.now().hour
            hours    = data["hourly"]["time"]
            temps    = data["hourly"]["temperature_2m"]
            codes    = data["hourly"]["weathercode"]
            rains    = data["hourly"]["precipitation_probability"]

            # 현재 시간 강수 확률
            cur_rain = 0
            for i, t in enumerate(hours):
                if int(t[11:13]) == now_hour:
                    cur_rain = rains[i]
                    break

            icon, status = WeatherFeature.WMO_MAP.get(cur_code, ("⛅", "알 수 없음"))
            briefing_text = f"🌡 현재 {location}: {status} {cur_temp}°C (강수 {cur_rain}%)\n\n"
            will_rain = cur_rain >= 40 or "비" in status or "눈" in status or "소나기" in status

            count = 0
            for i, t in enumerate(hours):
                h = int(t[11:13])
                if h <= now_hour:
                    continue

                wicon, wstatus = WeatherFeature.WMO_MAP.get(codes[i], ("⛅", "?"))
                briefing_text += f"▪ {h}시: {round(temps[i])}°C {wicon} {wstatus} (강수 {rains[i]}%)\n"

                if rains[i] >= 40 or "비" in wstatus or "눈" in wstatus:
                    will_rain = True

                count += 1
                if count >= 6:
                    break

            if will_rain:
                icon = "☔"
                briefing_text += "\n💡 비/눈 올 가능성 있어요! 우산 챙기세요!"

            return icon, briefing_text

        except Exception:
            return "⛅", "날씨 정보를 불러오지 못했습니다."