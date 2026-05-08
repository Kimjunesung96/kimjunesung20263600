import random
import time
import json
from datetime import datetime


class DummySensor:
    """화성 기지의 환경 데이터를 시뮬레이션하는 더미 센서 클래스"""

    def __init__(self):
        self.env_values = {
            'mars_base_internal_temperature': 0,
            'mars_base_external_temperature': 0,
            'mars_base_internal_humidity': 0,
            'mars_base_external_illuminance': 0,
            'mars_base_internal_co2': 0,
            'mars_base_internal_oxygen': 0
        }

    def _read_internal_temp(self):
        return random.uniform(18, 30)

    def _read_external_temp(self):
        return random.uniform(0, 21)

    def _read_internal_humidity(self):
        return random.uniform(50, 60)

    def _read_external_illuminance(self):
        return random.uniform(500, 715)

    def _read_internal_co2(self):
        return random.uniform(0.02, 0.1)

    def _read_internal_oxygen(self):
        return random.uniform(4, 7)

    def set_env(self):
        self.env_values['mars_base_internal_temperature'] = self._read_internal_temp()
        self.env_values['mars_base_external_temperature'] = self._read_external_temp()
        self.env_values['mars_base_internal_humidity'] = self._read_internal_humidity()
        self.env_values['mars_base_external_illuminance'] = self._read_external_illuminance()
        self.env_values['mars_base_internal_co2'] = self._read_internal_co2()
        self.env_values['mars_base_internal_oxygen'] = self._read_internal_oxygen()

    def get_env(self):
        # 파일 저장을 위한 시간과 데이터 문자열 만들기
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = (
            f"{now}, "
            f"{self.env_values['mars_base_internal_temperature']:.2f}, "
            f"{self.env_values['mars_base_external_temperature']:.2f}, "
            f"{self.env_values['mars_base_internal_humidity']:.2f}, "
            f"{self.env_values['mars_base_external_illuminance']:.2f}, "
            f"{self.env_values['mars_base_internal_co2']:.4f}, "
            f"{self.env_values['mars_base_internal_oxygen']:.2f}\n"
        )
        
        # sensor_log.txt 파일에 차곡차곡 기록하기 (a 모드)
        with open('sensor_log.txt', 'a', encoding='utf-8') as f:
            f.write(log_entry)
            
        return self.env_values


class MissionComputer:
    """화성 기지 환경을 모니터링하고 제어하는 미션 컴퓨터 클래스"""

    def __init__(self):
        self.env_values = {}
        self.ds = DummySensor()
        self.history = []
        self.running = True

    def get_sensor_data(self):
        """1초마다 데이터를 출력하고 300초(5분)마다 평균을 계산"""
        print('미션 컴퓨터가 가동되었습니다. 1초마다 데이터를 수집합니다.')
        print('*** 시스템을 중단하려면 [Ctrl + C] 키를 누르세요 ***')
        start_time = time.time()
        
        while self.running:

            self.ds.set_env()
            self.env_values = self.ds.get_env()
            

            self.history.append(self.env_values.copy())


            print(f"\n[수집 시간: {datetime.now().strftime('%H:%M:%S')}]")
            print(json.dumps(self.env_values, indent=4))


            current_time = time.time()
            if current_time - start_time >= 300:
                self._display_average()
                start_time = time.time()
                self.history = []


            time.sleep(5)

    def _display_average(self):
        """5분간 쌓인 데이터의 평균을 계산하여 출력"""
        if not self.history:
            return

        print('\n' + '=' * 60)
        print('*** [REPORT] 5-Minute Environment Average ***')
        

        keys = self.history[0].keys()
        for key in keys:
            avg_val = sum(d[key] for d in self.history) / len(self.history)
            print(f'* {key}: {avg_val:.4f}')
        print('=' * 60 + '\n')

    def stop_system(self):
        self.running = False
        print('\nSystem stopped....')



RunComputer = MissionComputer()

if __name__ == '__main__':
    try:

        RunComputer.get_sensor_data()
    except KeyboardInterrupt:
        RunComputer.stop_system()
