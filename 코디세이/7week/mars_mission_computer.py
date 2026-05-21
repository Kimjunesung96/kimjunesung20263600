import random
import time
import json
import platform
from datetime import datetime

# 외부 라이브러리 예외 처리 (미션 조건)
try:
    import psutil
except ImportError:
    psutil = None
    print('경고: psutil 라이브러리가 없습니다. 명령창에 pip install psutil 을 입력하세요.')


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
        # 보너스 과제: 세팅 파일 불러오기
        self.settings = self._load_settings()

    def _load_settings(self):
        """setting.txt 파일을 읽어 출력 항목을 설정합니다."""
        default_settings = {
            'os': True,
            'os_version': True,
            'cpu_type': True,
            'cpu_cores': True,
            'memory_size': True,
            'cpu_usage': True,
            'memory_usage': True
        }
        try:
            with open('setting.txt', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # 파일이 없으면 기본 설정으로 자동 생성
            with open('setting.txt', 'w', encoding='utf-8') as f:
                json.dump(default_settings, f, indent=4)
            return default_settings
        except Exception as e:
            print(f'설정 파일 읽기 오류: {e}')
            return default_settings

    def get_mission_computer_info(self):
        """1번 과제: 시스템 정보를 수집하고 JSON으로 출력"""
        info = {}
        try:
            if self.settings.get('os'):
                info['os'] = platform.system()
            if self.settings.get('os_version'):
                info['os_version'] = platform.release()
            if self.settings.get('cpu_type'):
                info['cpu_type'] = platform.processor()
            
            if psutil:
                if self.settings.get('cpu_cores'):
                    info['cpu_cores'] = psutil.cpu_count(logical=False)
                if self.settings.get('memory_size'):
                    # 메모리를 기가바이트(GB) 단위로 변환
                    info['memory_size'] = round(psutil.virtual_memory().total / (1024 ** 3), 2)
        except Exception as e:
            print(f'시스템 정보 수집 중 오류 발생: {e}')
            
        print('\n=== 미션 컴퓨터 시스템 정보 ===')
        print(json.dumps(info, indent=4))
        return info

    def get_mission_computer_load(self):
        """2번 과제: 시스템 실시간 부하를 수집하고 JSON으로 출력"""
        load_info = {}
        try:
            if psutil:
                if self.settings.get('cpu_usage'):
                    # 1초 동안 측정한 CPU 사용률
                    load_info['cpu_usage'] = psutil.cpu_percent(interval=1)
                if self.settings.get('memory_usage'):
                    load_info['memory_usage'] = psutil.virtual_memory().percent
            else:
                load_info['error'] = 'psutil 라이브러리가 필요합니다.'
        except Exception as e:
            print(f'시스템 부하 수집 중 오류 발생: {e}')

        print('\n=== 미션 컴퓨터 실시간 부하 상태 ===')
        print(json.dumps(load_info, indent=4))
        return load_info

    def get_sensor_data(self):
        """이전 주차 과제: 환경 센서 데이터 수집 루프"""
        print('\n미션 컴퓨터가 가동되었습니다. 5초마다 데이터를 수집합니다.')
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
        print('\nSytem stoped….')


# 5번 과제: runComputer 인스턴스화
runComputer = MissionComputer()

if __name__ == '__main__':
    try:
        # 6번 과제: 정보 및 부하 출력 메소드 호출
        runComputer.get_mission_computer_info()
        runComputer.get_mission_computer_load()
        
        # 센서 데이터 수집 루프 실행 (원하지 않으시면 주석 처리 하시면 됩니다)
        runComputer.get_sensor_data()
    except KeyboardInterrupt:
        runComputer.stop_system()
