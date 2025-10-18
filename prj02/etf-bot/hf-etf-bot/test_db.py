"""
Database verification script
데이터베이스 연결 및 기본 쿼리 테스트
"""

import sqlite3
import sys

def test_database():
    """데이터베이스 연결 및 기본 테스트"""

    print("="*60)
    print("ETF Database Verification Test")
    print("="*60)

    try:
        # 데이터베이스 연결
        print("\n1. Connecting to database...")
        conn = sqlite3.connect('etf_database.db')
        cursor = conn.cursor()
        print("   [OK] Database connected successfully")

        # 테이블 존재 확인
        print("\n2. Checking table existence...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"   [OK] Found {len(tables)} table(s): {[t[0] for t in tables]}")

        # ETFs 테이블 확인
        if ('ETFs',) not in tables:
            print("   [ERROR] ETFs table not found!")
            return False

        # 총 레코드 수
        print("\n3. Counting total ETF records...")
        cursor.execute("SELECT COUNT(*) FROM ETFs")
        count = cursor.fetchone()[0]
        print(f"   [OK] Total ETFs: {count}")

        if count == 0:
            print("   [WARNING] No ETF records found!")
            return False

        # 컬럼 정보
        print("\n4. Checking table schema...")
        cursor.execute("PRAGMA table_info(ETFs)")
        columns = cursor.fetchall()
        print(f"   [OK] Found {len(columns)} columns:")
        for col in columns:
            print(f"      - {col[1]} ({col[2]})")

        # 샘플 데이터
        print("\n5. Fetching sample data...")
        cursor.execute("""
            SELECT 종목코드, 종목명, 운용사, 수익률_최근1년, 순자산총액
            FROM ETFs
            WHERE 수익률_최근1년 IS NOT NULL
            LIMIT 3
        """)
        samples = cursor.fetchall()
        print(f"   [OK] Sample ETFs ({len(samples)} records):")
        for idx, row in enumerate(samples, 1):
            print(f"      {idx}. 종목코드: {row[0]}, 종목명: {row[1]}, 운용사: {row[2]}")

        # 운용사 통계
        print("\n6. Analyzing fund managers...")
        cursor.execute("SELECT COUNT(DISTINCT 운용사) FROM ETFs")
        manager_count = cursor.fetchone()[0]
        print(f"   [OK] Unique fund managers: {manager_count}")

        # 수익률 통계
        print("\n7. Analyzing returns...")
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                AVG(수익률_최근1년) as avg_return,
                MAX(수익률_최근1년) as max_return,
                MIN(수익률_최근1년) as min_return
            FROM ETFs
            WHERE 수익률_최근1년 IS NOT NULL
        """)
        stats = cursor.fetchone()
        print(f"   [OK] Return statistics:")
        print(f"      - ETFs with return data: {stats[0]}")
        print(f"      - Average return: {stats[1]:.2f}%" if stats[1] else "N/A")
        print(f"      - Max return: {stats[2]:.2f}%" if stats[2] else "N/A")
        print(f"      - Min return: {stats[3]:.2f}%" if stats[3] else "N/A")

        # 연결 종료
        conn.close()

        print("\n" + "="*60)
        print("All tests passed successfully!")
        print("="*60)
        return True

    except sqlite3.Error as e:
        print(f"\n[ERROR] SQLite error: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_database()
    sys.exit(0 if success else 1)
