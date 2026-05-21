import os
import wave
from datetime import datetime

import pyaudio

# 전역 변수로 폴더 경로 설정
record_dir = 'records'

def record_audio(duration=5):
    # 폴더가 없으면 생성
    if not os.path.exists(record_dir):
        os.makedirs(record_dir)

    chunk = 1024
    sample_format = pyaudio.paInt16
    channels = 1
    rate = 44100
    
    audio_interface = pyaudio.PyAudio()
    
    stream = audio_interface.open(
        format=sample_format,
        channels=channels,
        rate=rate,
        input=True,
        frames_per_buffer=chunk
    )
    
    print('마이크를 통해 음성 녹음을 시작합니다...')
    frames = []
    
    # 지정된 시간 동안 오디오 데이터를 읽어옴
    for _ in range(0, int(rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)
        
    print('녹음이 완료되었습니다.')
    
    stream.stop_stream()
    stream.close()
    audio_interface.terminate()
    
    # 년월일-시간분초 형태로 파일명 생성
    now = datetime.now()
    file_name = now.strftime('%Y%m%d-%H%M%S') + '.wav'
    file_path = os.path.join(record_dir, file_name)
    
    # wave 파일을 생성하여 녹음 데이터 저장
    wave_file = wave.open(file_path, 'wb')
    wave_file.setnchannels(channels)
    wave_file.setsampwidth(audio_interface.get_sample_size(sample_format))
    wave_file.setframerate(rate)
    wave_file.writeframes(b''.join(frames))
    wave_file.close()
    
    print(f'녹음 파일이 저장되었습니다: {file_path}')


def show_records(start_date, end_date):
    # 보너스 과제: 특정 범위의 날짜 조회
    if not os.path.exists(record_dir):
        print('저장된 폴더가 없습니다.')
        return
        
    print(f'\n{start_date} 부터 {end_date} 까지의 녹음 파일:')
    
    for file_name in os.listdir(record_dir):
        if file_name.endswith('.wav'):
            # 파일명에서 '년월일' 부분만 분리 (예: 20260521)
            date_part = file_name.split('-')[0]
            
            # YYYYMMDD 형태는 문자열 대소 비교(<=, >=)가 가능하므로 코드가 매우 단순해짐
            if start_date <= date_part <= end_date:
                print(f' - {file_name}')


if __name__ == '__main__':
    # 1. 5초간 음성 녹음
    record_audio(duration=5)
    
    # 2. 보너스 과제 확인 (오늘 날짜)
    today = datetime.now().strftime('%Y%m%d')
    show_records(today, today)