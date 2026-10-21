import pytest
import sqlite3
from app import app

@pytest.fixture
def client(tmp_path):
    test_db_path = tmp_path / "test.db"
    app.config["DATABASE"] = str(test_db_path)
    app.config["TESTING"] = True

    # 读取 schema.sql 并直接在临时库里建表
    with open("schema.sql", "r", encoding="utf-8") as f:
        schema_sql = f.read()
    
    conn = sqlite3.connect(test_db_path)
    conn.executescript(schema_sql)
    # 插入一条测试用的演示数据，保证详情页能查到
    conn.execute("INSERT INTO tickets (title, room, status, description) VALUES ('演示工单', 'A101', 'open', '测试描述')")
    conn.commit()
    conn.close()

    with app.test_client() as c:
        yield c
