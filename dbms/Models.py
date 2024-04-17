from database import db, ma

class User(db.Model):
  __tablename__ = 'user'
  uid = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(120), nullable=True, unique=True)
  password = db.Column(db.String(128))
  name = db.Column(db.String(50), nullable=False)
  picture = db.Column(db.String(128))
  lineId = db.Column(db.String(128), nullable=True, unique=True)

  userInvAct = db.relationship("UserInvAct", uselist=False, back_populates="user")

  def __init__(self, email, password, name, picture, lineId):
    self.email = email
    self.password = password
    self.name = name
    self.picture = picture
    self.lineId = lineId

class UserInvAct(db.Model):
  __tablename__ = 'user_inv_act'
  actId = db.Column(db.Integer, primary_key=True)
  totalAssets = db.Column(db.Integer)
  stopLossPoint = db.Column(db.Integer)

  uid = db.Column(db.Integer, db.ForeignKey('user.uid'), nullable=False)
  user = db.relationship("User", back_populates="userInvAct")

  def __init__(self, totalAssets, stopLossPoint, uid):
    self.totalAssets = totalAssets
    self.stopLossPoint = stopLossPoint
    self.uid = uid
