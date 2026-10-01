from tempo.services.extraction import _remove_repeated_headers_and_footers, _reorder_page


def _block(name: str, x: float, y: float, width: float = 0.3) -> dict:
    return {"id": name, "text": name, "bbox": {"x": x, "y": y, "width": width, "height": 0.04}, "readingOrder": 0}


def test_two_column_reading_order_reads_left_column_before_right():
    blocks = [_block("right-1", 0.58, 0.2), _block("left-2", 0.08, 0.4), _block("left-1", 0.08, 0.2), _block("right-2", 0.58, 0.4)]
    _reorder_page(blocks)
    assert [block["id"] for block in blocks] == ["left-1", "left-2", "right-1", "right-2"]


def test_repeated_headers_are_removed_without_removing_body_text():
    pages = [
        {"blocks": [_block("Conference 2026", 0.1, 0.03), _block("page-one-method", 0.1, 0.3)]},
        {"blocks": [_block("Conference 2026", 0.1, 0.03), _block("page-two-results", 0.1, 0.3)]},
    ]
    _remove_repeated_headers_and_footers(pages)
    assert [[block["id"] for block in page["blocks"]] for page in pages] == [["page-one-method"], ["page-two-results"]]
