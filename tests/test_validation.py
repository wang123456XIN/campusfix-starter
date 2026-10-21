import pytest
from app import validate_ticket, app

def test_title_too_long():
    error = validate_ticket("A" * 21, "A101")
    assert error == "标题不能超过20个字符"
def test_post_title_too_long():
    client = app.test_client()
    resp = client.post("/tickets/new", data={
        "title": "A" * 21,
        "room": "A区101",
        "description": "测试",
    })
    assert resp.status_code == 400
    assert "标题不能超过20个字符" in resp.data.decode()

@pytest.mark.parametrize("title,expected", [
    ("正常标题", 200),      # 有效类代表值
    ("A" * 19, 200),       # 边界内
    ("A" * 20, 200),       # 恰好上限
    ("A" * 21, 400),       # 越界
    ("A" * 100, 400),      # 无效类代表值
])
def test_title_boundary(client, title, expected):
    resp = client.post("/tickets/new", data={
        "title": title, "room": "A区101", "description": "测试",
    }, follow_redirects=True)  
    assert resp.status_code == expected