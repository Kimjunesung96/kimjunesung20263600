import os
import csv
import time
from datetime import datetime

import soundcard as sc
import soundfile as sf
import speech_recognition as sr
import numpy as np


# 녹음 파일이 저장될 폴더 경로 (스크립트와 같은 위치에 records 폴더 생성)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RECORD_DIR = os.path.join(SCRIPT_DIR, 'records')


def list_audio_devices():
    '''사용 가능한 오디오 장치 목록을 출력한다.'''
    print('\n=== 사용 가능한 스피커/출력 장치 ===')
    for i, speaker in enumerate(sc.all_speakers()):
        print(f'  [{i}] {speaker.name}')

    print('\n=== 사용 가능한 마이크/입력 장치 ===')
    for i, mic in enumerate(sc.all_microphones(include_loopback=True)):
        print(f'  [{i}] {mic.name}')


def record_audio(duration=15):
    '''
    시스템 오디오(유튜브 등 PC에서 나오는 소리)를 루프백으로 녹음하고
    records 폴더에 wav 파일로 저장한다.
    '''
    if not os.path.exists(RECORD_DIR):
        os.makedirs(RECORD_DIR)
        print(f'폴더 생성: {RECORD_DIR}')

    # 48000으로 박자(Sample Rate) 고정!
    SAMPLE_RATE = 48000

    default_speaker = sc.default_speaker()
    print(f'\n캡처 대상 스피커: {default_speaker.name}')

    loopback_mic = sc.get_microphone(
        id=default_speaker.name,
        include_loopback=True
    )

    print(f'유튜브를 틀 시간을 드릴게요! 3초 뒤 녹음을 시작합니다...')
    for i in range(3, 0, -1):
        print(f'{i}...')
        time.sleep(1)

    print(f'🔴 시스템 오디오 녹음 중... ({duration}초)')

    with loopback_mic.recorder(samplerate=SAMPLE_RATE) as recorder:
        audio_data = recorder.record(numframes=SAMPLE_RATE * duration)

    print('녹음이 완료되었습니다.')

    now = datetime.now()
    file_name = now.strftime('%Y%m%d-%H%M%S') + '.wav'
    file_path = os.path.join(RECORD_DIR, file_name)

    # 구글 AI가 알아듣기 쉽게 소리를 모노(1채널)로 합치기
    audio_data_mono = np.mean(audio_data, axis=1)

    # 가장 핵심! subtype='PCM_16' 을 꼭 넣어야 구글 STT가 알아먹음
    sf.write(file_path, audio_data_mono, SAMPLE_RATE, subtype='PCM_16')

    print(f'✅ 녹음 파일 저장 완료!')
    print(f'   저장 경로: {file_path}')

    return file_path


def show_records(start_date, end_date):
    '''특정 날짜 범위(YYYYMMDD 문자열)에 해당하는 녹음 파일 목록을 출력한다.'''
    if not os.path.exists(RECORD_DIR):
        print('저장된 폴더가 없습니다.')
        return

    print(f'\n{start_date} 부터 {end_date} 까지의 녹음 파일:')
    found = False

    for file_name in sorted(os.listdir(RECORD_DIR)):
        if file_name.endswith('.wav'):
            date_part = file_name.split('-')[0]
            if start_date <= date_part <= end_date:
                full_path = os.path.join(RECORD_DIR, file_name)
                size_kb = os.path.getsize(full_path) / 1024
                print(f'  - {file_name}  ({size_kb:.1f} KB)')
                found = True

    if not found:
        print('  해당 날짜의 녹음 파일이 없습니다.')


def convert_speech_to_text():
    '''records 폴더의 wav 파일을 STT로 변환해 같은 이름의 csv 파일로 저장한다.'''
    if not os.path.exists(RECORD_DIR):
        print('저장된 폴더가 없습니다.')
        return

    recognizer = sr.Recognizer()
    converted = 0

    for file_name in sorted(os.listdir(RECORD_DIR)):
        if not file_name.endswith('.wav'):
            continue

        wav_path = os.path.join(RECORD_DIR, file_name)
        csv_path = os.path.join(RECORD_DIR, file_name.replace('.wav', '.csv'))

        if os.path.exists(csv_path):
            print(f'이미 변환됨 (건너뜀): {file_name}')
            continue

        print(f'변환 중: {file_name}')

        try:
            with sr.AudioFile(wav_path) as audio_source:
                audio_data = recognizer.record(audio_source)
                recognized_text = recognizer.recognize_google(
                    audio_data, language='ko-KR'
                )

            with open(csv_path, 'w', encoding='utf-8-sig', newline='') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(['시간', '인식된 텍스트'])
                writer.writerow(['00:00', recognized_text])

            print(f'  ✅ 변환 완료: {csv_path}')
            converted += 1

        except sr.UnknownValueError:
            print(f'  ⚠️ 음성을 인식할 수 없습니다: {file_name}')
        except sr.RequestError as error:
            print(f'  ❌ STT 서비스 오류 ({file_name}): {error}')

    print(f'\n총 {converted}개 파일 변환 완료.')


def search_keyword(keyword):
    '''저장된 csv 파일에서 특정 키워드가 포함된 내용을 검색해 출력한다.'''
    if not os.path.exists(RECORD_DIR):
        print('저장된 폴더가 없습니다.')
        return

    print(f'\n🔍 "{keyword}" 검색 결과:')
    found = False

    for file_name in sorted(os.listdir(RECORD_DIR)):
        if not file_name.endswith('.csv'):
            continue

        csv_path = os.path.join(RECORD_DIR, file_name)

        with open(csv_path, 'r', encoding='utf-8-sig') as csv_file:
            reader = csv.reader(csv_file)
            next(reader, None)  # 헤더 행 건너뜀

            for row in reader:
                if len(row) > 1 and keyword in row[1]:
                    print(f'  [{file_name}] {row[0]} → {row[1]}')
                    found = True

    if not found:
        print(f'  "{keyword}"를 포함한 기록을 찾을 수 없습니다.')


if __name__ == '__main__':
    print('=' * 50)
    print('  JAVIS - 시스템 오디오 녹음기')
    print('=' * 50)

    # 1. 시스템 오디오(유튜브 등) 녹음 (15초)
    record_audio(duration=15)

    # 2. 녹음된 wav 파일 → STT → csv 변환
    convert_speech_to_text()

    # 3. 오늘 날짜 녹음 파일 목록 출력
    today = datetime.now().strftime('%Y%m%d')
    show_records(today, today)

    # 4. 키워드 검색 예시
    search_keyword('린')