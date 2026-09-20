"""
RT-019: Benchmarking Engine Tests.
"""
from benchmark.run import compute_wer, compute_cer, check_code_switch_preservation


def test_wer_identical():
    assert compute_wer("hello world", "hello world") == 0.0


def test_wer_completely_wrong():
    assert compute_wer("hello world", "foo bar") == 1.0


def test_wer_partial():
    wer = compute_wer("the cat sat on the mat", "the cat on the mat")
    assert 0.0 < wer < 1.0


def test_wer_empty_reference():
    assert compute_wer("", "some text") == 1.0
    assert compute_wer("", "") == 0.0


def test_cer_identical():
    assert compute_cer("hello", "hello") == 0.0


def test_cer_partial():
    cer = compute_cer("hello", "helo")
    assert 0.0 < cer < 1.0


def test_code_switch_preservation_preserved():
    ref = "mujhe ek coffee chahiye please"
    hyp = "mujhe ek coffee chahiye please"
    assert check_code_switch_preservation(ref, hyp) is True


def test_code_switch_preservation_lost():
    ref = "mujhe ek coffee chahiye please thank you"
    hyp = "मुझे एक कॉफी चाहिए"
    assert check_code_switch_preservation(ref, hyp) is False


def test_code_switch_no_latin():
    """No Latin tokens means nothing to check — should return True."""
    ref = "यह एक परीक्षण है"
    hyp = "यह एक परीक्षण है"
    assert check_code_switch_preservation(ref, hyp) is True
