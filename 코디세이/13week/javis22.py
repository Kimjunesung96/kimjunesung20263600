import os
import csv
import time
from datetime import datetime

import soundcard as sc
import soundfile as sf
import whisper
import numpy as np


# 녹음 파일이 저장될 폴더 경로
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RECORD_DIR = os.path.join(SCRIPT_DIR, 'records')


def record_audio(duration=15):
    '''시스템 내부 소리를 캡처하여 records 폴더에 wav 파일로 저장한다.'''
    if not os.path.exists(RECORD_DIR):
        os.makedirs(RECORD_DIR)

    sample_rate = 44100

    default_speaker = sc.default_speaker()
    print(f'\n캡처 대상 스피커: {default_speaker.name}')

    loopback_mic = None
    for mic in sc.all_microphones(include_loopback=True):
        if str(default_speaker.id) in str(mic.id):
            loopback_mic = mic
            break

    if not loopback_mic:
        loopback_mic = sc.get_microphone(
            id=default_speaker.id,
            include_loopback=True
        )

    print('유튜브를 틀 시간을 드릴게요! 3초 뒤 녹음을 시작합니다...')
    for i in range(3, 0, -1):
        print(f'{i}...')
        time.sleep(1)

    print(f'[녹음 중] 시스템 오디오 녹음 중... ({duration}초)')

    with loopback_mic.recorder(samplerate=sample_rate) as recorder:
        audio_data = recorder.record(numframes=sample_rate * duration)

    print('녹음이 완료되었습니다.')

    max_vol = np.max(np.abs(audio_data))
    if max_vol < 0.01:
        print(f'\n[경고] 녹음된 볼륨이 너무 작습니다! (최대 볼륨: {max_vol:.5f})')
        print('   유튜브 소리가 파이썬으로 넘어오지 않고 정적만 녹음되었습니다.')
        print('   -> 윈도우 소리 설정에서 [오디오 향상] 기능을 끄거나 볼륨을 올려주세요.\n')

    now = datetime.now()
    file_name = now.strftime('%Y%m%d-%H%M%S') + '.wav'
    file_path = os.path.join(RECORD_DIR, file_name)

    # 모노 변환
    audio_data_mono = np.mean(audio_data, axis=1)

    # 표준 wav 포맷으로 저장
    sf.write(file_path, audio_data_mono, sample_rate, subtype='PCM_16')

    print(f'[완료] 녹음 파일 저장 완료: {file_path}')
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


def format_timestamp(seconds):
    '''초 단위 시간을 MM:SS 형식의 문자열로 변환한다.'''
    minutes = int(seconds) // 60
    secs = int(seconds) % 60
    return f'{minutes:02d}:{secs:02d}'


def convert_speech_to_text():
    '''records 폴더의 wav 파일을 Whisper AI로 변환해 csv 파일로 저장한다.'''
    if not os.path.exists(RECORD_DIR):
        print('저장된 폴더가 없습니다.')
        return

    print('\n[로딩] Whisper AI 두뇌를 불러오는 중입니다...')
    print('(최초 1회 다운로드로 인해 1~2분 정도 걸릴 수 있습니다!)')

    # Whisper 'base' 모델 로드 (가장 가볍고 속도가 빠름)
    model = whisper.load_model('base')
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
            # Whisper로 한국어 텍스트 추출 (구간별 시간 포함)
            result = model.transcribe(wav_path, language='ko')

            with open(csv_path, 'w', encoding='utf-8-sig', newline='') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(['시간', '인식된 텍스트'])

                for segment in result['segments']:
                    timestamp = format_timestamp(segment['start'])
                    text = segment['text'].strip()
                    writer.writerow([timestamp, text])

            print(f'  [완료] 변환 완료: {csv_path}')
            print(f'  [내용] 추출된 대사: {result["text"].strip()}')
            converted += 1

        except Exception as error:
            print(f'  [오류] STT 서비스 오류 ({file_name}): {error}')

    print(f'\n총 {converted}개 파일 변환 완료.')


def search_keyword(keyword):
    '''저장된 csv 파일에서 특정 키워드가 포함된 내용을 검색해 출력한다.'''
    if not os.path.exists(RECORD_DIR):
        print('저장된 폴더가 없습니다.')
        return

    print(f'\n[검색] "{keyword}" 검색 결과:')
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
                    print(f'  [{file_name}] {row[0]} -> {row[1]}')
                    found = True

    if not found:
        print(f'  "{keyword}"를 포함한 기록을 찾을 수 없습니다.')


if __name__ == '__main__':
    print('=' * 50)
    print('  JAVIS - Whisper 시스템 오디오 녹음기')
    print('=' * 50)

    # 1. 시스템 오디오 녹음 (15초)
    record_audio(duration=15)

    # 2. 녹음된 wav 파일 -> Whisper AI 변환
    convert_speech_to_text()

    # 3. 오늘 날짜 녹음 파일 목록 출력
    today = datetime.now().strftime('%Y%m%d')
    show_records(today, today)

    # 4. 키워드 검색 (사용자 입력)
    keyword = input('\n검색할 키워드를 입력하세요: ')
    search_keyword(keyword)