"""
Models entity for the all website, the main objects are Site, Author and Post
"""

from constant.constant import db_string
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, LargeBinary
from datetime import datetime
import sys
sys.path.append('../../commandLine')


Base = declarative_base()


class Site(Base):
    """
    Site entity Model
    """
    __tablename__ = 'site'
    id = Column(Integer, primary_key=True)
    domain = Column(String(245), unique=False, nullable=False)
    name = Column(String(245), unique=False, nullable=False)
    template = Column(String(245), unique=False, nullable=False)
    added = Column(DateTime, nullable=False,
                   default=datetime.utcnow)
    description = Column(Text(), unique=False, nullable=False)

    variables = relationship("SiteVar")
    authors = relationship("Author")
    posts = relationship("Post")

    def __repr__(self):
        """
        Return representation of the object
        :return:
        """
        return f"<{self.id}>"

    def readable(self):
        """
        Get readable instance of the File
        :return:
        """
        return dict(
            id=self.id,
            domain=self.domain,
            name=self.name,
            template=self.template,
            description=self.description
        )


class SiteVar(Base):
    __tablename__ = 'site_var'
    """
    Site variable model
    """
    id = Column(Integer, primary_key=True)
    site = Column(Integer, ForeignKey("site.id"))
    key = Column(String(245), unique=False, nullable=False)
    value = Column(Text(), unique=False, nullable=False)

    def __repr__(self):
        """
        Return representation of the object
        :return:
        """
        return f"<{self.key}>"

    def readable(self):
        """
        Get readable instance of the File
        :return:
        """
        return dict(
            key=self.key,
            data=self.value
        )


class Author(Base):
    """
    Author entity model
    """
    __tablename__ = 'author'
    id = Column(Integer, primary_key=True)
    site = Column(Integer, ForeignKey("site.id"))
    name = Column(String(245), unique=False, nullable=False)
    age = Column(Integer, unique=False, nullable=False)
    profession = Column(String(245), unique=False, nullable=False)
    bio = Column(Text(), unique=False, nullable=False)
    image = Column(LargeBinary(), unique=False, nullable=False)
    # posts = relationship("Post")
   # posts = relationship("Post", back_populates="author")

    def __repr__(self):
        """
        Return representation of the object
        :return:
        """
        return f"<{self.name}>"

    def readable(self):
        """
        Get readable instance of the File
        :return:
        """
        return dict(
            id=self.id,
            name=self.name,
            age=self.age,
            profession=self.profession,
            bio=self.bio,
            image=self.image
        )


class Post(Base):
    """
    Post entity Model
    """
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True)
    site = Column(Integer, ForeignKey("site.id"))
    name = Column(String(245), unique=False, nullable=False)
    title = Column(String(245), unique=False, nullable=False)
    seo = Column(String(245), unique=False, nullable=False)
    text = Column(Text, unique=False, nullable=False)
    uri = Column(String(245), unique=False, nullable=False)
    posted = Column(String(245), unique=False, nullable=False)
    author = Column(Integer, ForeignKey("author.id"))
    image = Column(LargeBinary(), unique=False, nullable=True)

    # author = relationship("Author", back_populates="posts")

    def __repr__(self):
        """
        Return representation of the object
        :return:
        """
        return f"<{self.name}>"

    def readable(self):
        """
        Get readable instance of the File
        :return:
        """
        return dict(
            id=self.id,
            name=self.name,
            uri=self.uri,
            title=self.title,
            text=self.text,
            posted=self.posted.replace("T", " "),
            author=self.author,
            image=self.image,
            seo=self.seo
        )


engine = create_engine(db_string)
Base.metadata.create_all(bind=engine)
