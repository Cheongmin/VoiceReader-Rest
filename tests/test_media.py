from voicereader.extensions.media import allowed_file


def test_allowed_file():
    allowed_extensions = set(['png', 'jpg', 'jpeg'])
    allowed_filename = 'test.png'
    expected = True

    actual = allowed_file(allowed_filename, allowed_extensions)

    assert actual == expected


def test_not_allowed_file():
    allowed_extensions = set(['png', 'jpg', 'jpeg'])
    not_allowed_filename = 'test.mp4'
    expected = False

    actual = allowed_file(not_allowed_filename, allowed_extensions)

    assert actual == expected
