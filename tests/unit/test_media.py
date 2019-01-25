from voicereader.extensions.media import allowed_file


def test_valid_file():
    allowed_extensions = set(['png', 'jpg', 'jpeg'])
    valid_file_name = 'valid.png'

    assert allowed_file(valid_file_name, allowed_extensions)


def test_invalid_file():
    allowed_extensions = set(['png', 'jpg', 'jpeg'])
    valid_file_name = 'valid.mp4'

    assert not allowed_file(valid_file_name, allowed_extensions)
