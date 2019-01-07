def allowed_file(file_name, allowed_extensions):
    return '.' in file_name and \
           file_name.rsplit('.', 1)[1].lower() in allowed_extensions
