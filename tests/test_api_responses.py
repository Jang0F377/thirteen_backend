from thirteen_backend.utils.api_responses import format_error, format_success


def test_format_success_structure():
    content = {"foo": "bar"}
    meta = {"page": 1}
    result = format_success(content=content, meta=meta)

    assert result == {"status": "success", "data": content, "meta": meta}


def test_format_error_structure():
    error = "bad_request"
    message = "Something went wrong"
    result = format_error(error=error, message=message)

    assert result == {"status": "error", "error": error, "message": message}
