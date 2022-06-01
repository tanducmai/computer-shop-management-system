#!/usr/bin/python3
# -*- coding: utf-8 -*-

# =============================================================================
#
#        FILE:  user_management.py
#      AUTHOR:  Tan Duc Mai
#       EMAIL:  tan.duc.work@gmail.com
#     CREATED:  31-May-2022
# DESCRIPTION:  Stores every customer of the system, including the
#               authentication of their identity.
#   I hereby declare that I completed this work without any improper help
#   from a third party and without using any aids other than those cited.
#
# =============================================================================


# ------------------------------- Module Import -------------------------------
"""Stdlib"""
import hashlib
import random
import re

"""Third party"""
import icontract


# ------------------------------- Named Constant ------------------------------
# Original top-level domains
TLDs = {
    '.biz', '.com', '.edu', '.gov', '.info',
    '.int', '.mil', '.net', '.org',
}

COUNTRY_CODEs = {
    '.au', '.ca', '.cn', '.jp', '.uk', '.vn',
}


# ------------------------------ Class Definitions ----------------------------
class User:

    def __init__(self, username, email, password):
        # Create a new user object.
        # The password will be encrypted before storing.
        self.__is_logged_in = False
        self.__username = username
        self.__email = email
        self.__password = self.__encrypt_pw(password)

    @icontract.ensure(lambda result: isinstance(result, str))
    def __repr__(self):
        return self.__email

    @property
    def username(self):
        return self.__username

    @property
    def password(self):
        return self.__password

    @property
    def email(self):
        return self.__email

    @property
    def is_logged_in(self):
        return self.__is_logged_in

    @is_logged_in.setter
    @icontract.require(lambda boolean: isinstance(boolean, bool))
    @icontract.ensure(lambda result: result is None)
    def is_logged_in(self, boolean):
        self.__is_logged_in = boolean

    def check_password(self, password):
        # Return True if the password is valid for this user, False otherwise.
        encrypted = self.__encrypt_pw(password)
        return encrypted == self.__password

    def __encrypt_pw(self, password):
        # Encrypt the password with the username and return the sha digest.
        hash_string = self.__username + password
        hash_string = hash_string.encode('utf8')
        return hashlib.sha256(hash_string).hexdigest()


class AuthException(Exception):

    def __init__(self, message):
        super().__init__(message)


class UsernameAlreadyExists(AuthException):

    def __init__(self, username, user):
        super().__init__(
            repr(username) + ' already exists for ' + str(user) + '.\n'
        )


class EmailAlreadyExists(AuthException):

    def __init__(self, email, user):
        super().__init__(
            repr(email) + ' already exists for ' + str(user) + '.\n'
        )


class PasswordTooShort(AuthException):

    def __init__(self, password):
        super().__init__(repr(password) + ' is too short' + '.\n')


class InvalidUsername(AuthException):

    def __init__(self, username):
        super().__init__(repr(username) + ' does not exist' + '.\n')


class InvalidPassword(AuthException):

    def __init__(self, password):
        super().__init__(repr(password) + ' does not match' + '.\n')


class InvalidEmail(AuthException):

    def __init__(self, email):
        super().__init__(repr(email) + ' does not match' + '.\n')


class InappropriateEmail(AuthException):

    def __init__(self, email):
        super().__init__(
            'Your email ' + repr(email) + ' is not of a valid format:\n'
            "    '(string1)@(string2).(2+characters)'.\n"
            'Therefore, we generate a random one for you,')


class Authenticator:

    def __init__(self):
        """
        The initialization method creates an empty dictionary and assigns it
        to the attribute users.
        """
        self.__users = {}       # A dictionary of users coming to the store.
        self.__user_email = {}  # Each user is associated with only one email.

    @property
    def users(self):
        return self.__users

    @property
    def user_email(self):
        return self.__user_email

    def add_user(self, username, email, password):
        """
        Check two conditions for adding a user:
        1. Password length: If the password is smaller than 6 characters,
        then it should raise the PasswordTooShort exception.
        2. Username already exists: If the username already exists in the users
        dictionary, then an UsernameAlreadyExists exception should be raised.
        If both conditions hold, create a new instance of User with the new
        username and password and add it to the dictionary users with the key
        username.
        """
        if len(password) < 6:
            raise PasswordTooShort(password)
        elif username in self.__users:
            raise UsernameAlreadyExists(username, self.__users)
        else:
            valid_form = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
            if not re.fullmatch(valid_form, email):
                try:
                    raise InappropriateEmail(email)
                except InappropriateEmail as e:
                    print(e)
                    email = (username
                             + str(random.randint(100, 999))
                             + '@gmail'
                             + random.choice(tuple(TLDs))
                             + random.choice(tuple(COUNTRY_CODEs)))
                    print(f'    {repr(email)}')
            else:
                for stored_email in self.__user_email.values():
                    if email == stored_email:
                        raise EmailAlreadyExists(email, self.__users)
            self.__users[username] = User(username, email, password)
            self.__user_email[username] = email

    def login(self, username, password):
        """
        • Check if the username is included in the users dictionary. If it is
        not, then raise an InvalidUsername exception.
        • Check the password matches that user's password by calling that
        user's check_password() method. If it does not, then raise an
        InvalidPassword exception.
        • If both conditions hold then assign True to the attribute
        is_logged_in of the User object.
        """
        if username not in self.__users:
            raise InvalidUsername(username)
        elif not self.__users[username].check_password(password):
            raise InvalidPassword(password)
        else:
            self.__users[username].is_logged_in = True

    def logout(self, username, password):
        """Log user out of the system."""
        self.__users[username].is_logged_in = False

    def is_logged_in(self, username):
        if username in self.__users:
            return self.__users[username].is_logged_in
        return False


# ---------------------------------- Program ----------------------------------
if __name__ == '__main__':
    auth = Authenticator()

    try:
        auth.add_user('johnny', 'johnny121@gmail.com.au', 'johnnypassword')
        print(auth.is_logged_in('johnny'))
        auth.login('johnny', 'johnnypassword')
        print(auth.is_logged_in('johnny'))

        """Raise InvalidPassword exception."""
        # auth.add_user('susan', 'susan123@gmail.net', 'susanpassword')
        # auth.login('susan', '5U54N')

        """Raise UsernameAlreadyExists exception."""
        auth.add_user('johnny', 'johnny121@gmail.com.au', 'johnnypassword')
        auth.login('johnny', 'johnnypassword')
        print(auth.is_logged_in('johnny'))

        """Keep trying to add/validate new username/password."""
        valid = False
        while not valid:
            try:
                auth.add_user(input('Enter new username: '),
                              input('Enter new email: '),
                              input('Enter new password: '))
            except Exception as e1:
                print(e1)
            else:
                valid = True

    except Exception as e:
        print(e)