"""Sanity tests for the SoundStorm web backend."""


def test_true():
    """Baseline: pytest is configured and running."""
    assert True


def test_scales_dict():
    """SCALES covers all 12 chromatic roots."""
    from backend.main import SCALES
    assert len(SCALES) == 12
    for key, intervals in SCALES.items():
        assert len(intervals) == 7, f"{key} scale should have 7 intervals"


def test_chords_dict():
    """CHORDS entries are valid interval lists."""
    from backend.main import CHORDS
    assert len(CHORDS) >= 6
    for name, intervals in CHORDS.items():
        assert len(intervals) >= 3, f"{name} chord needs at least 3 notes"
        assert all(isinstance(i, int) for i in intervals)


def test_audio_to_base64_roundtrip():
    """audio_to_base64 produces a valid base64-encoded WAV."""
    import base64
    from pydub import AudioSegment
    from pydub.generators import Sine
    from backend.main import audio_to_base64

    tone = Sine(440).to_audio_segment(duration=100)
    result = audio_to_base64(tone)
    decoded = base64.b64decode(result)
    # WAV files start with the RIFF header
    assert decoded[:4] == b"RIFF"
