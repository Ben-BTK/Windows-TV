from windows_tv.onboarding import validate_display_name


def test_display_name_accepts_single_name_and_two_given_names():
    assert validate_display_name("Ben") == (True, "")
    assert validate_display_name("Maxi-Kai") == (True, "")
    assert validate_display_name("Ben Jason") == (True, "")


def test_display_name_rejects_three_names_and_invalid_punctuation():
    valid, _ = validate_display_name("Ben Jason Kai")
    assert not valid
    valid, _ = validate_display_name("Ben_123")
    assert not valid


def test_display_name_rejects_known_prohibited_examples():
    assert not validate_display_name("Adolf Hitler")[0]
    assert not validate_display_name("Heil Hitler")[0]


def test_display_name_requires_nonempty_value_and_limits_length():
    assert not validate_display_name("   ")[0]
    assert not validate_display_name("A" * 41)[0]
