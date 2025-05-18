from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey
from enum import Enum as PyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)

    posts: Mapped[list["Post"]] = relationship("Post", back_populates="poster", cascade="all, delete-orphan")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="author", cascade="all, delete-orphan")

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # No se incluye la contraseña por seguridad
        }

class Follower(db.Model):
    __tablename__ = "follower"

    user_from_id: Mapped[int] = mapped_column(ForeignKey('user.id'), primary_key=True)
    user_to_id: Mapped[int] = mapped_column(ForeignKey('user.id'), primary_key=True)

    user_from: Mapped["User"] = relationship("User", foreign_keys=[user_from_id])
    user_to: Mapped["User"] = relationship("User", foreign_keys=[user_to_id])

    def serialize(self):
        return {
            "user_from": self.user_from.serialize(),
            "user_to": self.user_to.serialize()
        }

class Post(db.Model):
    __tablename__ = "post"

    id: Mapped[int] = mapped_column(primary_key=True)
    poster_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)

    poster: Mapped["User"] = relationship("User", back_populates="posts")
    media_items: Mapped[list["Media"]] = relationship("Media", back_populates="post", cascade="all, delete-orphan")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="post", cascade="all, delete-orphan")

    def serialize(self):
        return {
            "post_id": self.id,
            "poster": self.poster.serialize(),
            "media_items": [media.serialize() for media in self.media_items],
            "comments": [comment.serialize() for comment in self.comments]
        }

class MediaType(PyEnum):
    Picture = "Picture"
    URL = "URL"
    Video = "Video"
    Text = "Text"

class Media(db.Model):
    __tablename__ = "media"

    media_id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[MediaType] = mapped_column(Enum(MediaType), nullable=False)
    url: Mapped[str] = mapped_column(unique=True, nullable=False)
    post_id: Mapped[int] = mapped_column(ForeignKey('post.id'), nullable=False)

    post: Mapped["Post"] = relationship("Post", back_populates="media_items")

    def serialize(self):
        return {
            "media_id": self.media_id,
            "type": self.type.value,
            "url": self.url,
            "post_id": self.post_id
        }

class Comment(db.Model):
    __tablename__ = "comment"

    id: Mapped[int] = mapped_column(primary_key=True)
    comment_text: Mapped[str] = mapped_column(nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    post_id: Mapped[int] = mapped_column(ForeignKey('post.id'), nullable=False)

    author: Mapped["User"] = relationship("User", back_populates="comments")
    post: Mapped["Post"] = relationship("Post", back_populates="comments")

    def serialize(self):
        return {
            "id": self.id,
            "comment_text": self.comment_text,
            "author": self.author.serialize(),
            "post_id": self.post_id
        }