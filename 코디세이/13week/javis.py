import os
import wave
import csv
from datetime import datetime

import pyaudio
import speech_recognition as sr

record_dir = 'records'
# 시작할 때 폴더가 없으면 미리 한 번만 생성해둠 (파이썬 3.2+ 지원 기능)
os.makedirs(record_dir, exist_ok=True)

def record_audio(duration=5):
    rate, chunk = 44100, 1024
    p = pyaudio.PyAudio()
    
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=rate, input=True, frames_per_buffer=chunk)
    
    # for문을 한 줄(리스트 컴프리헨션)로 압축
    frames = [stream.read(chunk) for _ in range(0, int(rate / chunk * duration))]
    
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    file_path = os.path.join(record_dir, datetime.now().strftime('%Y%m%d-%H%M%S') + '.wav')
    
    # with문을 쓰면 마지막에 .close()를 안 써도 파이썬이 알아서 닫아줌
    with wave.open(file_path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
        
    print(f'녹음 완료: {file_path}')

def show_records(start, end):
    # 조건에 맞는 파일만 한 줄로 필터링
    files = [f for f in os.listdir(record_dir) if f.endswith('.wav') and start <= f.split('-')[0] <= end]
    print(f'{start}~{end} 녹음 파일: {files}')

def convert_speech_to_text():
    r = sr.Recognizer()
    wav_files = [f for f in os.listdir(record_dir) if f.endswith('.wav')]
    
    for f in wav_files:
        csv_path = os.path.join(record_dir, f.replace('.wav', '.csv'))
        
        if not os.path.exists(csv_path):
            try:
                with sr.AudioFile(os.path.join(record_dir, f)) as source:
                    text = r.recognize_google(r.record(source), language='ko-KR')
                    
                with open(csv_path, 'w', encoding='utf-8', newline='') as cf:
                    csv.writer(cf).writerow(['00:00', text])
            except Exception:
                pass # 인식 불가 등의 에러가 나면 그냥 조용히 넘어감

def search_keyword(keyword):
    csv_files = [f for f in os.listdir(record_dir) if f.endswith('.csv')]
    
    for f in csv_files:
        with open(os.path.join(record_dir, f), 'r', encoding='utf-8') as cf:
            for row in csv.reader(cf):
                if len(row) > 1 and keyword in row[1]:
                    print(f'[{f}] {row[0]} - {row[1]}')

if __name__ == '__main__':
    record_audio(duration=5)
    convert_speech_to_text()
    search_keyword('테스트')