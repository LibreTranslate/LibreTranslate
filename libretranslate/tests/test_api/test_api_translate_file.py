import io
import json


def test_api_translate_file(client):
    response = client.post("/translate_file", data={
        "source": "en",
        "target": "es",
        "file": (io.BytesIO(b"Hello world, this is a test."), "test.txt")
    }, content_type="multipart/form-data")

    response_json = json.loads(response.data)

    assert response.status_code == 200
    assert "translatedFileUrl" in response_json


def test_api_translate_file_and_download(client):
    response = client.post("/translate_file", data={
        "source": "en",
        "target": "es",
        "file": (io.BytesIO(b"Hello world, this is a test."), "test.txt")
    }, content_type="multipart/form-data")

    url = json.loads(response.data)["translatedFileUrl"]
    path = url[url.index("/download_file"):]

    download = client.get(path)

    assert download.status_code == 200
    assert len(download.data) > 0
    assert download.data != b"Hello world, this is a test."


def test_api_translate_file_missing_file(client):
    response = client.post("/translate_file", data={
        "source": "en",
        "target": "es"
    }, content_type="multipart/form-data")

    assert response.status_code == 400


def test_api_translate_file_missing_source(client):
    response = client.post("/translate_file", data={
        "target": "es",
        "file": (io.BytesIO(b"Hello"), "test.txt")
    }, content_type="multipart/form-data")

    response_json = json.loads(response.data)

    assert "error" in response_json
    assert response_json["error"] == "Invalid request: missing source parameter"
    assert response.status_code == 400


def test_api_translate_file_missing_target(client):
    response = client.post("/translate_file", data={
        "source": "en",
        "file": (io.BytesIO(b"Hello"), "test.txt")
    }, content_type="multipart/form-data")

    response_json = json.loads(response.data)

    assert "error" in response_json
    assert response_json["error"] == "Invalid request: missing target parameter"
    assert response.status_code == 400


def test_api_translate_file_unsupported_format(client):
    response = client.post("/translate_file", data={
        "source": "en",
        "target": "es",
        "file": (io.BytesIO(b"MZ\x90\x00"), "program.exe")
    }, content_type="multipart/form-data")

    response_json = json.loads(response.data)

    assert "error" in response_json
    assert response_json["error"] == "Invalid request: file format not supported"
    assert response.status_code == 400


def test_api_translate_file_unsupported_language(client):
    response = client.post("/translate_file", data={
        "source": "en",
        "target": "zz",
        "file": (io.BytesIO(b"Hello"), "test.txt")
    }, content_type="multipart/form-data")

    response_json = json.loads(response.data)

    assert "error" in response_json
    assert response_json["error"] == "zz is not supported"
    assert response.status_code == 400


def test_api_translate_file_disabled(client_factory):
    client = client_factory("--disable-files-translation")

    response = client.post("/translate_file", data={
        "source": "en",
        "target": "es",
        "file": (io.BytesIO(b"Hello"), "test.txt")
    }, content_type="multipart/form-data")

    assert response.status_code == 403


def test_api_download_file_disabled(client_factory):
    client = client_factory("--disable-files-translation")

    response = client.get("/download_file/anything.txt")

    assert response.status_code == 400
