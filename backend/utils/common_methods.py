from auth_app.models import UserType
from rest_framework.utils.serializer_helpers import ReturnDict
from doctor_app.models import ClientStaffPermissions

def generate_serializer_error(errors):
    formated_error = ""
    if isinstance(errors, ReturnDict):
        return errors
    else:
        for key in errors:
            formated_error += (key+" - "+errors[key][0]) + \
                (", " if (list(errors)[-1] != key) else "")
        return formated_error

def verify_clientstaff_permissions(permissions):
    for p in permissions:
        if ClientStaffPermissions[p] == None:
            return False
    return True

def verify_admin(user):
    if user.usertype == UserType.ADMIN or user.usertype == UserType.ADMIN_STAFF:
        return True
    else:
        raise Exception("You don't have permission to perform this action.")
def get_client_staff_default_password(unit_name):
    return unit_name.replace(" ", "_").lower()+"@staff159827"