import csv
import pymysql


class MySQLHelper:

    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None

    def connect(self):
        self.connection = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            charset="utf8mb4",
        )
        self.cursor = self.connection.cursor()

    def infer_data_types(self, csv_file_path, headers):
        """CSV 데이터를 분석하여 각 열의 최적의 데이터 타입을 추론하는 함수"""
        # 각 컬럼별로 발견된 데이터 타입을 기록할 딕셔너리 초기화
        # 기본값은 최상위 타입인 'INT'로 시작해서 조건에 따라 FLOAT -> VARCHAR로 업그레이드됨
        col_types = {header: "INT" for header in headers}

        with open(csv_file_path, mode="r", encoding="utf-8") as file:
            csv_reader = csv.reader(file)
            next(csv_reader, None)  # 헤더 스킵

            for row in csv_reader:
                for idx, value in enumerate(row):
                    if idx >= len(headers):
                        break
                    header = headers[idx]
                    val_str = value.strip()

                    # 비어있는 값은 패스
                    if not val_str:
                        continue

                    # 이미 해당 컬럼이 VARCHAR(문자열)로 판정났다면 더 검사할 필요 없음
                    if col_types[header] == "VARCHAR":
                        诚ontinue

                    # 1. 정수형(INT)인지 확인
                    try:
                        int(val_str)
                        continue  # 정수 맞으면 다음 데이터로
                    except ValueError:
                        pass

                    # 2. 실수형(FLOAT)인지 확인
                    try:
                        float(val_str)
                        col_types[header] = "FLOAT"  # FLOAT으로 업그레이드
                        continue
                    except ValueError:
                        pass

                    # 3. 둘 다 아니면 문자열(VARCHAR)로 확정
                    col_types[header] = "VARCHAR"

        return col_types

    def create_table_auto_type(self, table_name, csv_file_path):
        """CSV의 헤더와 데이터 타입을 분석하여 자동으로 테이블을 생성하는 메서드"""
        try:
            with open(csv_file_path, mode="r", encoding="utf-8") as file:
                csv_reader = csv.reader(file)
                headers = [h.strip() for h in next(csv_reader, None)]

            if not headers:
                print("[오류] CSV 파일이 비어있습니다.")
                return None

            # 데이터 타입을 동적으로 분석
            print("[시스템] CSV 데이터 타입을 분석 중입니다...")
            inferred_types = self.infer_data_types(csv_file_path, headers)

            # SQL 구문 조립
            column_definitions = []
            for header in headers:
                data_type = inferred_types[header]

                # 추론된 타입에 따라 실제 SQL 타입 매핑
                if data_type == "INT":
                    sql_type = "INT NULL"
                elif data_type == "FLOAT":
                    sql_type = "FLOAT NULL"
                else:
                    sql_type = "VARCHAR(255) NULL"

                column_definitions.append(f"`{header}` {sql_type}")

            columns_str = ", ".join(column_definitions)
            query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                {columns_str}
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """

            self.cursor.execute(query)
            self.connection.commit()
            print(
                f"[시스템] 분석 완료! '{table_name}' 테이블이 자동으로 맞춤 생성되었습니다."
            )
            print(f" -> 분석된 속성: {inferred_types}")
            return headers

        except Exception as e:
            print(f"[오류] 동적 테이블 생성 실패: {e}")
            return None

    def execute_insert(self, query, args=()):
        try:
            self.cursor.execute(query, args)
            self.connection.commit()
        except Exception as e:
            print(f"쿼리 실행 중 오류 발생: {e}")
            self.connection.rollback()

    def count_rows(self, table_name):
        try:
            self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            return self.cursor.fetchone()[0]
        except Exception:
            return 0

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()


def insert_mode_dynamic(db_helper, table_name, csv_file_path, headers):
    print("[시스템] 테이블에 데이터가 없어 CSV 입력을 시작합니다...")

    with open(csv_file_path, mode="r", encoding="utf-8") as file:
        csv_reader = csv.reader(file)
        next(csv_reader, None)  # 헤더 스킵

        placeholders = ", ".join(["%s"] * len(headers))
        columns = ", ".join([f"`{h}`" for h in headers])
        insert_query = (
            f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        )

        for row in csv_reader:
            if len(row) == len(headers):
                # 데이터가 비어있으면 None(DB에서는 NULL)으로 치환하여 삽입
                processed_row = [
                    val.strip() if val.strip() else None for val in row
                ]
                db_helper.execute_insert(insert_query, tuple(processed_row))

    print("[시스템] 모든 데이터가 알맞은 타입으로 변환되어 저장되었습니다.")


def main():
    db_host = "localhost"
    db_user = "root"
    db_password = "//"
    db_database = "testdb"

    table_name = "mars_weather"
    csv_file_path = "mars_weathers_data.CSV"

    db_helper = MySQLHelper(db_host, db_user, db_password, db_database)

    try:
        db_helper.connect()

        # 1. 헤더도 읽고, 데이터 타입도 전수 조사해서 알아서 테이블 생성하기
        headers = db_helper.create_table_auto_type(table_name, csv_file_path)

        if headers:
            # 2. 데이터 유무 확인 후 마이그레이션
            row_count = db_helper.count_rows(table_name)

            if row_count == 0:
                insert_mode_dynamic(
                    db_helper, table_name, csv_file_path, headers
                )
            else:
                print(
                    f"[시스템] 이미 데이터가 존재합니다. (총 {row_count}건)"
                )

    except Exception as e:
        print(f"[오류] 메인 로직 실행 중 에러: {e}")
    finally:
        db_helper.close()


if __name__ == "__main__":
    main()