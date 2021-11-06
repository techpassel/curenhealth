
def generate_serializer_error(errors):
    formated_error = ""
    for key in errors:
        formated_error += (key+" - "+errors[key][0]) + (", " if (list(errors)[-1] != key) else "")
    return formated_error