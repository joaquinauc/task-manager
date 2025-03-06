from typing import Optional

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

import sqlalchemy as sa
import sqlalchemy.orm as so

from app import db, login

class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                                unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,
                                             unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    tasks: so.WriteOnlyMapped['Task'] = so.relationship(back_populates='author')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Task(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(40))
    body: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    due_date: so.Mapped[Optional[str]] = so.mapped_column(sa.String(20))
    progress: so.Mapped[Optional[int]] = so.mapped_column()
    priority: so.Mapped[Optional[int]] = so.mapped_column()
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),index=True)
    author: so.Mapped[User] = so.relationship(back_populates='tasks')


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
