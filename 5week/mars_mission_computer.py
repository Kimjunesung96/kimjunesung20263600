# 파일명: mars_mission_computer.py

import random
from datetime import datetime


class DummySensor:
    '''화성 기지의 환경 데이터를 시뮬레이션하는 더미 센서 클래스'''

    def __init__(self):
        # 2번 과제: env_values 사전 객체 초기화
        self.env_values = {
            'mars_base_internal_temperature': 0,
            'mars_base_external_temperature': 0,
            'mars_base_internal_humidity': 0,
            'mars_base_external_illuminance': 0,
            'mars_base_internal_co2': 0,
            'mars_base_internal_oxygen': 0
        }

    # 실제 센서 하드웨어에서 값을 읽어오는 과정을 흉내 낸 내부 메서드들
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
        '''3번 과제: 각 '읽기' 메서드를 호출하여 실제 데이터처럼 업데이트'''
        self.env_values['mars_base_internal_temperature'] = self._read_internal_temp()
        self.env_values['mars_base_external_temperature'] = self._read_external_temp()
        self.env_values['mars_base_internal_humidity'] = self._read_internal_humidity()
        self.env_values['mars_base_external_illuminance'] = self._read_external_illuminance()
        self.env_values['mars_base_internal_co2'] = self._read_internal_co2()
        self.env_values['mars_base_internal_oxygen'] = self._read_internal_oxygen()

    def get_env(self):
        '''4번 & 보너스 과제: 환경 값을 반환하고 로그 파일에 기록'''
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 로그 데이터 구성 (작은따옴표 기본 사용, 딕셔너리 키는 부득이하게 큰따옴표 사용)
        log_entry = (
            f'{now}, '
            f'{self.env_values["mars_base_internal_temperature"]:.2f}, '
            f'{self.env_values["mars_base_external_temperature"]:.2f}, '
            f'{self.env_values["mars_base_internal_humidity"]:.2f}, '
            f'{self.env_values["mars_base_external_illuminance"]:.2f}, '
            f'{self.env_values["mars_base_internal_co2"]:.4f}, '
            f'{self.env_values["mars_base_internal_oxygen"]:.2f}\n'
        )
        
        # 로그 파일 저장
        with open('sensor_log.txt', 'a', encoding='utf-8') as f:
            f.write(log_entry)
            
        return self.env_values


# 5번 과제: ds 인스턴스 생성
ds = DummySensor()

# 6번 과제: 실행 및 결과 확인
ds.set_env()
current_env = ds.get_env()

# 출력부
print('--- [Mission Computer] 화성 기지 환경 모니터링 ---')
for key, value in current_env.items():
    print(f'{key}: {value:.2f}')
print('----------------------------------------------')
print('시스템: 센서 로그가 성공적으로 기록되었습니다.')