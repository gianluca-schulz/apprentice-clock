from uuid import uuid4

import pytest

REQUEST_2026 = {"date": "2026-11-26", "title": "Cooking", "description": "i am cooked"}
REQUEST_2025 = {"date": "2025-11-26", "title": "burning", "description": "i am burned"}
REQUEST_2027 = {"date": "2027-11-26", "title": "running", "description": "i ran away"}


def test_post_report_returns_201_and_the_report(client, auth_header, registered_user):
    response = client.post("/api/v1/reports", json=REQUEST_2026, headers=auth_header)
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == REQUEST_2026["title"]
    assert body["description"] == REQUEST_2026["description"]
    assert body["date"] == REQUEST_2026["date"]
    assert body["user_id"] == str(registered_user.id)
    assert "id" in body


def test_post_report_ignores_user_id_in_body(client, auth_header, registered_user):
    other_user_id = str(uuid4())
    response = client.post("/api/v1/reports", json={"user_id": other_user_id, **REQUEST_2026}, headers=auth_header)
    assert response.status_code == 201
    body = response.json()
    assert body["user_id"] == str(registered_user.id)
    assert "id" in body
    assert body["user_id"] != other_user_id


def test_post_report_twice_for_same_date_returns_409(client, auth_header):
    response = client.post("/api/v1/reports", json={**REQUEST_2026, "title": "something else"}, headers=auth_header)
    assert response.status_code == 201
    second_response = client.post("/api/v1/reports", json=REQUEST_2026, headers=auth_header)
    assert second_response.status_code == 409


@pytest.mark.parametrize(
    "json_dict",
    [
        ({"title": None, "date": "2026-11-26", "description": "testdescription"}),
        ({"title": "testtitle", "description": "testdescription"}),
        ({"title": "testtitle", "date": "invalid_date", "description": "testdescription"}),
        ({"title": "testtitle", "date": "2026-11-26", "description": None}),
    ],
)
def test_post_report_with_invalid_body_returns_422(client, auth_header, json_dict):
    response = client.post("/api/v1/reports", json=json_dict, headers=auth_header)
    assert response.status_code == 422


def test_only_date_gives_201(client, auth_header):
    response = client.post("/api/v1/reports", json={"date": REQUEST_2026["date"]}, headers=auth_header)
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == ""
    assert body["description"] == ""
    assert body["date"] == REQUEST_2026["date"]


@pytest.mark.parametrize(
    "method",
    [
        "post",
        "get",
    ],
)
def test_reports_without_token_return_401(client, method):
    response = client.request(method, "/api/v1/reports", json=REQUEST_2026)
    assert response.status_code == 401


def test_get_reports_returns_empty_list_without_reports(client, auth_header):
    response = client.get("/api/v1/reports", headers=auth_header)
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 0
    assert body == []


def test_get_reports_returns_newest_date_first(client, auth_header):
    response_2026 = client.post("/api/v1/reports", json=REQUEST_2026, headers=auth_header)
    assert response_2026.status_code == 201
    response_2025 = client.post("/api/v1/reports", json=REQUEST_2025, headers=auth_header)
    assert response_2025.status_code == 201
    response_2027 = client.post("/api/v1/reports", json=REQUEST_2027, headers=auth_header)
    assert response_2027.status_code == 201
    list_response = client.get("/api/v1/reports", headers=auth_header)
    assert list_response.status_code == 200
    body = list_response.json()
    assert len(body) == 3
    assert body[0]["date"] == "2027-11-26"
    assert body[1]["date"] == "2026-11-26"
    assert body[2]["date"] == "2025-11-26"


def test_get_reports_returns_only_own_reports(client, auth_header, second_auth_header):
    response = client.post("/api/v1/reports", json=REQUEST_2026, headers=auth_header)
    assert response.status_code == 201
    second_report_response = client.post("/api/v1/reports", json=REQUEST_2025, headers=second_auth_header)
    assert second_report_response.status_code == 201
    first_list_response = client.get("/api/v1/reports", headers=auth_header)
    second_list_response = client.get("/api/v1/reports", headers=second_auth_header)
    assert first_list_response.status_code == 200
    assert second_list_response.status_code == 200
    assert len(first_list_response.json()) == 1
    assert len(second_list_response.json()) == 1
    assert first_list_response.json()[0]["date"] == REQUEST_2026["date"]
    assert second_list_response.json()[0]["date"] == REQUEST_2025["date"]


def test_get_report_returns_200_and_the_report(client, auth_header, created_report):
    get_response = client.get(f"/api/v1/reports/{created_report['id']}", headers=auth_header)
    assert get_response.status_code == 200
    get_body = get_response.json()
    assert get_body["date"] == created_report["date"]
    assert get_body["description"] == created_report["description"]
    assert get_body["title"] == created_report["title"]
    assert get_body["id"] == created_report["id"]
    assert get_body["user_id"] == created_report["user_id"]


def test_get_report_of_another_user_returns_404(client, auth_header, second_auth_header, created_report):
    other_get_response = client.get(f"/api/v1/reports/{created_report['id']}", headers=second_auth_header)
    assert other_get_response.status_code == 404
    assert other_get_response.json()["detail"] == "report was not found"
    get_response = client.get(f"/api/v1/reports/{created_report['id']}", headers=auth_header)
    assert get_response.status_code == 200


def test_get_unknown_report_returns_404(client, auth_header, created_report):
    get_response = client.get(f"/api/v1/reports/{uuid4()}", headers=auth_header)
    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "report was not found"


def test_get_report_with_invalid_id_returns_422(client, auth_header):
    get_response = client.get("/api/v1/reports/abc", headers=auth_header)
    assert get_response.status_code == 422


def test_get_report_without_token_returns_401(client):
    get_response = client.get(f"/api/v1/reports/{uuid4()}")
    assert get_response.status_code == 401


def test_delete_report_returns_204_and_removes_it(client, created_report, auth_header):
    response = client.delete(f"/api/v1/reports/{created_report['id']}", headers=auth_header)
    assert response.status_code == 204
    assert response.content == b""
    get_response = client.get(f"/api/v1/reports/{created_report['id']}", headers=auth_header)
    assert get_response.status_code == 404
    list_response = client.get("/api/v1/reports", headers=auth_header)
    assert list_response.status_code == 200
    ids = [report["id"] for report in list_response.json()]
    assert created_report["id"] not in ids


def test_delete_report_of_another_user_returns_404(client, created_report, auth_header, second_auth_header):
    response = client.delete(f"/api/v1/reports/{created_report['id']}", headers=second_auth_header)
    assert response.status_code == 404
    get_response = client.get(f"/api/v1/reports/{created_report['id']}", headers=auth_header)
    assert get_response.status_code == 200


def test_delete_unknown_report_returns_404(client, created_report, auth_header):
    response = client.delete(f"/api/v1/reports/{uuid4()}", headers=auth_header)
    assert response.status_code == 404


def test_delete_report_without_token_returns_401(client):
    response = client.delete(f"/api/v1/reports/{uuid4()}")
    assert response.status_code == 401


def test_delete_report_with_invalid_id_returns_422(client, auth_header):
    response = client.delete("/api/v1/reports/abc", headers=auth_header)
    assert response.status_code == 422
