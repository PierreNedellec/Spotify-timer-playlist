from solver import design_playlist
from playlist_generator import format_duration

def test_exact_target():
    ids, total = design_playlist([("a", 100), ("b", 200), ("c", 300)], 500)
    assert total == 500 and sorted(ids) == ["b", "c"]

def test_no_duplicates():
    ids, _ = design_playlist([(str(i), 180 + i) for i in range(50)], 1800)
    assert len(ids) == len(set(ids))

def test_impossible_target_returns_closest():
    ids, total = design_playlist([("a", 100)], 1000)
    assert total == 100

def test_format_duration():
    assert format_duration(3360) == "56:00"
    assert format_duration(67) == "1:07"