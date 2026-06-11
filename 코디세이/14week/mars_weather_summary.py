import csv
import pymysql


class MySQLHelper:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            charset='utf8mb4'
        )

    def execute_insert(self, query, args=()):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, args)
            self.connection.commit()
        except Exception as e:
            print(f"쿼리 실행 중 오류 발생: {e}")
            self.connection.rollback()

    def fetch_all(self, query, args=()):
        with self.connection.cursor() as cursor:
            cursor.execute(query, args)
            return cursor.fetchall()

    def count_rows(self):
        result = self.fetch_all('SELECT COUNT(*) FROM mars_weather')
        return result[0][0]

    def search_by_date(self, keyword):
        return self.fetch_all(
            'SELECT * FROM mars_weather WHERE mars_date LIKE %s',
            (f'%{keyword}%',)
        )

    def search_by_temp_range(self, min_temp, max_temp):
        return self.fetch_all(
            'SELECT * FROM mars_weather WHERE temp BETWEEN %s AND %s',
            (min_temp, max_temp)
        )

    def search_by_storm(self, storm):
        return self.fetch_all(
            'SELECT * FROM mars_weather WHERE storm = %s',
            (storm,)
        )

    def close(self):
        if self.connection:
            self.connection.close()


def insert_mode(db_helper, csv_file_path):
    print('데이터가 없습니다. CSV 파일을 읽어 데이터를 입력합니다...')

    insert_query = (
        'INSERT INTO mars_weather (mars_date, temp, storm) '
        'VALUES (%s, %s, %s)'
    )

    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        next(csv_reader, None)

        for row in csv_reader:
            if len(row) >= 4:
                mars_date = row[1]
                temp = int(float(row[2]))
                storm = int(row[3])
                db_helper.execute_insert(insert_query, (mars_date, temp, storm))

    print('데이터 입력이 완료되었습니다.')


def search_mode(db_helper):
    print('데이터가 존재합니다. 검색 모드로 전환합니다.')
    print()

    while True:
        print('---- 검색 메뉴 ----')
        print('1. 날짜로 검색')
        print('2. 온도 범위로 검색')
        print('3. 모래 폭풍 여부로 검색')
        print('4. 전체 조회')
        print('0. 종료')
        choice = input('선택: ').strip()

        if choice == '1':
            keyword = input('날짜 키워드 입력 (예: 2024-01): ').strip()
            rows = db_helper.search_by_date(keyword)
        elif choice == '2':
            min_temp = int(input('최소 온도: ').strip())
            max_temp = int(input('최대 온도: ').strip())
            rows = db_helper.search_by_temp_range(min_temp, max_temp)
        elif choice == '3':
            storm_input = input('모래 폭풍 여부 (1: 있음 / 0: 없음): ').strip()
            rows = db_helper.search_by_storm(int(storm_input))
        elif choice == '4':
            rows = db_helper.fetch_all('SELECT * FROM mars_weather')
        elif choice == '0':
            print('프로그램을 종료합니다.')
            break
        else:
            print('올바른 번호를 입력해 주세요.')
            continue

        print(f'검색 결과: {len(rows)}건')
        for row in rows:
            print(row)
        print()


def main():
    db_host = 'localhost'
    db_user = 'root'
    db_password = '//'
    db_database = 'testdb'

    csv_file_path = 'mars_weathers_data.CSV'

    db_helper = MySQLHelper(db_host, db_user, db_password, db_database)

    if db_helper.count_rows() == 0:
        insert_mode(db_helper, csv_file_path)
    else:
        search_mode(db_helper)

    db_helper.close()


if __name__ == '__main__':
    main()
