from auth_app.models import UserType


def generate_serializer_error(errors):
    formated_error = ""
    for key in errors:
        formated_error += (key+" - "+errors[key][0]) + (", " if (list(errors)[-1] != key) else "")
    return formated_error


def verify_admin(user):
    if user.usertype == UserType.SUPERADMIN or user.usertype == UserType.SUPERADMIN_STAFF:
        return True
    else:
        raise Exception("You don't have permission to perform this action.")