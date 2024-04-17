from .Models import User, UserInvAct
from database import ma

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User

class UserInvActSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserInvAct
        include_fk = True