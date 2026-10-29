from datejar.security import hash_password, verify_password

PASSWORD = "Going on dates is fun"
WRONG_PASSWORD = "Jam in a jar"


def test_verify_accepts_correct_password():
    hashed_password = hash_password(PASSWORD)

    assert verify_password(hashed_password, PASSWORD) is True


def test_verify_rejects_wrong_password():
    hashed_password = hash_password(PASSWORD)

    assert verify_password(hashed_password, WRONG_PASSWORD) is False


def test_same_password_gives_different_hashes():
    hashed_password_1 = hash_password(PASSWORD)
    hashed_password_2 = hash_password(PASSWORD)

    assert hashed_password_1 != hashed_password_2
    assert verify_password(hashed_password_1, PASSWORD) is True
    assert verify_password(hashed_password_2, PASSWORD) is True


def test_hash_is_argon2id_and_hides_password():
    hashed_password = hash_password(PASSWORD)

    assert PASSWORD not in hashed_password
    assert hashed_password.startswith("$argon2id$") is True
