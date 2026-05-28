import soundcard as sc
import numpy as np
import time

def diagnose_audio():
    print("=" * 50)
    print("  🔍 JAVIS - 시스템 오디오 정밀 진단기")
    print("=" * 50)

    # 1. 현재 윈도우가 소리를 내보내고 있는 '기본 장치' 확인
    default_speaker = sc.default_speaker()
    print(f"\n현재 활성화된 스피커 : {default_speaker.name}")

    try:
        # 해당 스피커의 소리를 가로채는 루프백 마이크 연결
        mic = sc.get_microphone(id=default_speaker.name, include_loopback=True)
    except Exception as e:
        print(f"오류: 루프백 장치를 연결할 수 없습니다. ({e})")
        return

    print("\n🎧 유튜브나 음악을 지금 빵빵하게 틀어주세요!")
    for i in range(3, 0, -1):
        print(f" {i}초 뒤 주파수 측정을 시작합니다...")
        time.sleep(1)

    # 대괄호([]) 대신 소괄호(())를 사용하여 에러 원천 차단!
    test_rates = (44100, 48000)
    
    print("\n어떤 주파수(Hz)에서 소리가 정상적으로 잡히는지 테스트합니다...")
    
    for rate in test_rates:
        print(f"\n▶ {rate} Hz 로 2초간 소리 캡처 중...")
        try:
            with mic.recorder(samplerate=rate) as recorder:
                # 2초간 소리 녹음
                data = recorder.record(numframes=rate * 2)
                
                # 소리 크기(최대 진폭) 계산
                mono_data = np.mean(data, axis=1)
                max_vol = np.max(np.abs(mono_data))
                
                print(f"  - 감지된 소리 크기(볼륨): {max_vol:.5f}")
                
                # 볼륨이 0.001 이상이면 소리가 제대로 들어오고 있다는 뜻!
                if max_vol > 0.001:
                    print(f"  ✅ 띠링! 소리가 완벽하게 감지되었습니다!")
                    print(f"  🎯 정답 주파수: 네 컴퓨터는 지금 {rate} Hz 로 소리를 내고 있습니다.")
                else:
                    print(f"  ❌ 소리가 거의 0입니다. (이 주파수가 아니거나, 컴퓨터 볼륨이 너무 작습니다)")
                    
        except Exception as e:
            print(f"  ⚠️ {rate}Hz 측정 불가 (호환되지 않는 주파수): {e}")

    print("\n" + "=" * 50)
    print("진단이 끝났습니다. 정답 주파수를 확인하세요!")

if __name__ == '__main__':
    diagnose_audio()