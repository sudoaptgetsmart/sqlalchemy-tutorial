'''Testing SQLAlchemy'''
import sqlalchemy
from sqlalchemy import (Column, ForeignKey, Integer, MetaData, String, Table,
                        create_engine, text)
from sqlalchemy.orm import Session, declarative_base, relationship

# Connect to an sqlite database using an in-memory-only database.
engine = create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)

with engine.connect() as conn:
    result = conn.execute(text("select 'hello world'"))
    print(result.all())

# "commit as you go"
with engine.connect() as conn:
    conn.execute(text("CREATE TABLE some_table (x int, y int)"))
    conn.execute(
        text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
        [{"x": 1, "y": 1}, {"x": 2, "y": 4}]
    )
    conn.commit()
# "begin once"
with engine.begin() as conn:
    conn.execute(
        text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
        [{"x": 6, "y": 8}, {"x": 9, "y": 10}]
    )
# fetching rows
with engine.connect() as conn:
    result = conn.execute(text("SELECT x, y FROM some_table"))
    for row in result:
        print(f"x: {row.x} y: {row.y}")

# The Row objects themselves are intended to act like Python named tuples.
# Below we illustrate a variety of ways to access rows.

# # Tuple
# result = conn.execute(text("select x, y from some_table"))
# for x, y in result:
#     print(x)

# # Integer Index
# result = conn.execute(text("select x, y from some_table"))
# for row in result:
#     x = row[0]

# # Attribute Name
# result = conn.execute(text("select x, y from some_table"))
# for row in result:
#     y = row.y
#     print(f"Row: {row.x} {y}")

# # Mapping Access
# result = conn.execute(text("select x, y from some_table"))
# for dict_row in result.mappings():
#     x = dict_row['x']
#     y = dict_row['y']

# Sending Parameters
with engine.connect() as conn:
    result = conn.execute(
        text("SELECT x, y FROM some_table WHERE y > :y"),
        {"y": 2}
    )
    for row in result:
        print(f"x: {row.x} y:{row.y}")

# Sending Multiple Parameters
with engine.connect() as conn:
    conn.execute(
        text("INSERT INTO some_table (x,y) VALUES (:x, :y)"),
        [{"x": 11, "y": 12}, {"x": 13, "y": 14}]
    )
    conn.commit()

# Building Parameters with a Statement
stmt = text(
    "SELECT x, y FROM some_table WHERE y> :y ORDER by x, y").bindparams(y=6)
with engine.connect() as conn:
    result = conn.execute(stmt)
    for row in result:
        print(f"x: {row.x} y: {row.y}")

# Executing with an ORM Session
stmt = text(
    "SELECT x, y FROM some_table WHERE y > :y ORDER BY x, y").bindparams(y=6)
with Session(engine) as session:
    result = session.execute(stmt)
    for row in result:
        print(f"x: {row.x} y:{row.y}")

# Use the Session.commit() method for “commit as you go” behavior.
with Session(engine) as session:
    result = session.execute(
        text("UPDATE some_table SET y=:y WHERE x=:x"),
        [{"x": 9, "y": 11}, {"x": 13, "y": 15}]
    )
    session.commit()


# Setting up MetaData with Table objects
metadata_obj = MetaData()

user_table = Table(
    "user_account",
    metadata_obj,
    Column('id', Integer, primary_key=True),
    Column('name', String(30)),
    Column('fullname', String)
)

# Declaring Simple Constraints
address_table = Table(
    'address',
    metadata_obj,
    Column('id', Integer, primary_key=True),
    Column('user_id', ForeignKey('user_account.id'), nullable=False),
    Column('email_address', String, nullable=False)
)

# Emitting DDL to the Database
metadata_obj.create_all(engine)

# Defining Table Metadata with the ORM
Base = declarative_base()

# Declaring Mapped Classes


class User(Base):
    '''A class to represent a user.'''
    __tablename__ = 'user_account'

    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    fullname = Column(String)

    addresses = relationship("Address", back_populates="user")

    def __repr__(self):
        '''Returns the user's id, name, fullname.'''
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"


class Address(Base):
    '''A class to represent an address.'''
    __tablename__ = 'address'

    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('user_account.id'))

    user = relationship("User", back_populates="addresses")

    def __repr__(self):
        '''Returns user's address, email address.'''
        return f"Address(id={self.id!r}, email_address={self.email_address!r})"
