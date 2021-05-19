# class RolesUsers(Base):
#     __tablename__ = "roles_users"
#
#     id = Column(Integer, primary_key=True)
#     user_id = Column("user_id", Integer, ForeignKey("users.id"))
#     role_id = Column("role_id", Integer, ForeignKey("roles.id"))
#
#
# class Role(Base, RoleMixin):
#     __tablename__ = "roles"
#
#     id = Column(Integer, primary_key=True)
#     name = Column(String(80), unique=True)
#     description = Column(String(255))
#
#
# class User(Base, UserMixin):
#     __tablename__ = "users"
#
#     id = Column(Integer, primary_key=True)
#     email = Column(String(255), unique=True)
#     password = Column(String(255))
#     active = Column(Boolean())
#     confirmed_at = Column(DateTime())
#     roles = relationship("Role", secondary="roles_users", backref=backref("users", lazy="dynamic"))
#
#     last_login_at = Column(String(255))
#     current_login_at = Column(String(255))
#     last_login_ip = Column(String(255))
#     current_login_ip = Column(String(255))
#     login_count = Column(Integer)
