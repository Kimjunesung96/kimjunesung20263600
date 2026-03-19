# Mission Log Analysis Report

## 1. 로그 개요

mission_computer_main.log 파일을 분석하여 사고 원인을 확인하였다.

## 2. 문제 발생 근처로그


2023-08-27 11:28:00,INFO,Touchdown confirmed. Rocket safely landed.
2023-08-27 11:30:00,INFO,Mission completed successfully. Recovery team dispatched.
2023-08-27 11:35:00,INFO,Oxygen tank unstable.
2023-08-27 11:40:00,INFO,Oxygen tank explosion.


## 3. 사고 원인 분석

로그를 분석한 결과 산소 탱크가 불안정한 상태가 된 이후 폭발이 발생하였다.

특히 `explosion` 로그가 기록되기 전에 산소 탱크 불안정 상태가 먼저 기록되어 있어 산소 탱크 문제가 사고의 원인으로 판단된다.

## 4. 결론

본 사고는 **Oxygen tank instability로 인한 폭발 사고**로 판단된다.