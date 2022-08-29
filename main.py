'''Testing SQLAlchemy'''
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import text

# Connect to an sqlite database using psyqlite API using an in-memory-only database.
engine = create_engine("sqlite+psyqlite:///:memory:", echo=True, future=True)

with engine.connect() as conn:
    result = conn.execute(text("select 'hello world'"))
    print(result.all())

# "commit as you go"
with engine.connect() as conn:
    conn.execute(text("CREATE TABLE some_table (x int, y int)"))
    conn.execute(
        text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
    )
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

# The Row objects themselves are intended to act like Python named tuples. Below we illustrate a variety of ways to access rows.

# Tuple
result = conn.execute(text("select x, y from some_table"))
for x, y in result:
    print(x)

# Integer Index
result = conn.execute(text("select x, y from some_table"))
for row in result:
    x = row[0]

# Attribute Name
result = conn.execute(text("select x, y from some_table"))
for row in result:
    y = row.y
    print(f"Row: {row.x} {y}")

# Mapping Access
result = conn.execute(text("select x, y from some_table"))
for dict_row in result.mappings():
    x = dict_row['x']
    y = dict_row['y']

# Sending Parameters
with engine.connect() as conn:
  result = conn.execute(
    text("SELECT x, y FROM some_table WHERE y > :y"),
    {"y": 2}
  )
  for row in result:
    print(f"x: {row.x} y:{row.y}")
