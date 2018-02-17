# Author Ondrej Barta
# ondrej@ondrej.it
# Copyright 2017


from django.contrib.auth import authenticate

from radicale.auth import BaseAuth


class Auth(BaseAuth):
    def is_authenticated2(self, login, username, password):
        user = authenticate(username=username, password=password)
        if user and user.is_active:
            is_valid = True
        else:
            is_valid = False

        return is_valid
