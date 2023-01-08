from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, type, nickname, password, usrimg):
        self.id = id
        self.type = type
        self.nickname = nickname 
        self.password = password
        self.usrimg = usrimg