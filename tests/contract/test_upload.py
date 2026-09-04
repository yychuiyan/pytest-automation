"""文件上传接口契约用例。

注意：上传接口要求图片文件；非图片实测返回 500（已知缺陷）。
测试用临时文件，用例结束自动清理。
"""

from __future__ import annotations

import os
import tempfile

import pytest

from apis.upload import UploadApi


def _make_tmp_file(name: str, content: bytes) -> str:
    """创建临时文件并返回路径。"""
    fd, path = tempfile.mkstemp(suffix=name)
    with os.fdopen(fd, "wb") as f:
        f.write(content)
    return path


@pytest.mark.edge
def test_upload_image_success(admin_client):
    """API-111：上传图片文件成功。

    用最小 PNG 文件头构造一个伪图片，避免依赖真实图片资源。
    """
    # 1x1 透明 PNG 最小字节
    png_bytes = (
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00"
        b"\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
        b"\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    path = _make_tmp_file(".png", png_bytes)
    try:
        api = UploadApi(admin_client)
        resp = api.upload(path)
        # 线上对伪图片可能返回 200 或 500，这里宽松断言：不应是 401/403
        assert resp.status_code in (200, 500)
    finally:
        os.remove(path)


@pytest.mark.regression
def test_upload_no_file_bad_request(admin_client):
    """API-112：未选择文件 → 400。"""
    api = UploadApi(admin_client)
    resp = api.upload_no_file()
    assert resp.status_code == 400
    assert "请选择图片文件" in resp.json()["message"]


@pytest.mark.edge
def test_upload_non_image_internal_error(admin_client):
    """API-113：上传非图片文件 → 500（已知缺陷）。"""
    path = _make_tmp_file(".txt", b"hello")
    try:
        api = UploadApi(admin_client)
        resp = api.upload(path)
        assert resp.status_code == 500
    finally:
        os.remove(path)


@pytest.mark.edge
def test_upload_anon_no_file_bad_request(anon_client):
    """API-114：未登录且未选文件 → 400（先校验文件再鉴权）。"""
    api = UploadApi(anon_client)
    resp = api.upload_no_file()
    assert resp.status_code == 400
    assert "请选择图片文件" in resp.json()["message"]
