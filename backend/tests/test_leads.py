"""Lead API tests: public submit, auth guarding, state machine, resume, email."""


def _submit(client, pdf_bytes, **overrides):
    data = {
        "first_name": overrides.get("first_name", "Jane"),
        "last_name": overrides.get("last_name", "Prospect"),
        "email": overrides.get("email", "jane@example.com"),
    }
    files = {
        "resume": (
            overrides.get("filename", "resume.pdf"),
            overrides.get("content", pdf_bytes),
            overrides.get("content_type", "application/pdf"),
        )
    }
    return client.post("/api/leads", data=data, files=files)


def test_public_submit_creates_pending_lead(client, pdf_bytes):
    res = _submit(client, pdf_bytes)
    assert res.status_code == 201
    body = res.json()
    assert body["state"] == "PENDING"
    assert body["email"] == "jane@example.com"
    assert body["resume_filename"] == "resume.pdf"


def test_submit_triggers_both_emails(client, pdf_bytes, sent_emails):
    _submit(client, pdf_bytes)
    assert len(sent_emails) == 1  # one send_lead_emails call (fires both messages)
    assert sent_emails[0]["email"] == "jane@example.com"


def test_submit_rejects_non_pdf(client, pdf_bytes):
    res = _submit(client, pdf_bytes, content_type="image/png", filename="x.png")
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "UNSUPPORTED_FILE_TYPE"


def test_submit_rejects_empty_file(client):
    res = client.post(
        "/api/leads",
        data={"first_name": "A", "last_name": "B", "email": "a@b.com"},
        files={"resume": ("empty.pdf", b"", "application/pdf")},
    )
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "EMPTY_FILE"


def test_submit_rejects_bad_email(client, pdf_bytes):
    res = _submit(client, pdf_bytes, email="not-an-email")
    assert res.status_code == 422


def test_submit_rejects_duplicate_email(client, pdf_bytes):
    first = _submit(client, pdf_bytes, email="dupe@example.com")
    assert first.status_code == 201
    second = _submit(client, pdf_bytes, email="dupe@example.com")
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "DUPLICATE_LEAD"


def test_list_requires_auth(client, pdf_bytes):
    _submit(client, pdf_bytes)
    assert client.get("/api/leads").status_code == 401


def test_list_returns_leads_with_auth(client, pdf_bytes, auth_headers):
    _submit(client, pdf_bytes)
    res = client.get("/api/leads", headers=auth_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["total"] == 1
    assert body["items"][0]["email"] == "jane@example.com"


def test_get_single_lead(client, pdf_bytes, auth_headers):
    lead_id = _submit(client, pdf_bytes).json()["id"]
    res = client.get(f"/api/leads/{lead_id}", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["id"] == lead_id


def test_get_missing_lead_404(client, auth_headers):
    res = client.get("/api/leads/does-not-exist", headers=auth_headers)
    assert res.status_code == 404
    assert res.json()["error"]["code"] == "LEAD_NOT_FOUND"


def test_state_transition_pending_to_reached_out(client, pdf_bytes, auth_headers):
    lead_id = _submit(client, pdf_bytes).json()["id"]
    res = client.patch(
        f"/api/leads/{lead_id}",
        json={"state": "REACHED_OUT"},
        headers=auth_headers,
    )
    assert res.status_code == 200
    assert res.json()["state"] == "REACHED_OUT"


def test_invalid_state_transition_rejected(client, pdf_bytes, auth_headers):
    lead_id = _submit(client, pdf_bytes).json()["id"]
    client.patch(
        f"/api/leads/{lead_id}", json={"state": "REACHED_OUT"}, headers=auth_headers
    )
    # REACHED_OUT -> PENDING is not allowed.
    res = client.patch(
        f"/api/leads/{lead_id}", json={"state": "PENDING"}, headers=auth_headers
    )
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "INVALID_STATE_TRANSITION"


def test_patch_requires_auth(client, pdf_bytes):
    lead_id = _submit(client, pdf_bytes).json()["id"]
    res = client.patch(f"/api/leads/{lead_id}", json={"state": "REACHED_OUT"})
    assert res.status_code == 401


def test_resume_download(client, pdf_bytes, auth_headers):
    lead_id = _submit(client, pdf_bytes).json()["id"]
    res = client.get(f"/api/leads/{lead_id}/resume", headers=auth_headers)
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert res.content == pdf_bytes


def test_resume_requires_auth(client, pdf_bytes):
    lead_id = _submit(client, pdf_bytes).json()["id"]
    assert client.get(f"/api/leads/{lead_id}/resume").status_code == 401
