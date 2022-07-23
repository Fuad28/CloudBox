"""Blueprint specific helper functions. Global helper functions can be found in services"""

import  validators
from cloudbox.models import User


def email(email_str):
    print(email_str)
    """Return email_str if valid, raise an exception in other case."""
    if validators.email(email_str):
        return email_str
    
    elif email_str== "":
        raise ValueError("email of the user is required")

    elif len(User.query.filter(email= email_str)) > 0:
        raise ValueError(f'Email {email_str} exists already')

    else:
        raise ValueError(f'{email_str} is not a valid email')
