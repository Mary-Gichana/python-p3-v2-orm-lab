from sqlite3 import Cursor
from __init__ import CURSOR, CONN

class Review:
    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        if not isinstance(year, int) or year < 2000:
            raise ValueError("Year must be an integer and >= 2000.")
        if not summary or len(summary.strip()) == 0:
            raise ValueError("Summary cannot be empty.")
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id  # Use the setter to validate

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        """Validate that the employee_id exists in the database."""
        sql = "SELECT id FROM employees WHERE id = ?"
        if not CURSOR.execute(sql, (value,)).fetchone():
            raise ValueError(f"Employee ID {value} does not exist.")
        self._employee_id = value

    # Other methods remain unchanged...


    @classmethod
    def create_table(cls):
        """Create the `reviews` table to persist Review instances."""
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employee(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """Drop the `reviews` table."""
        sql = "DROP TABLE IF EXISTS reviews;"
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """
        Persist the current Review object to the database.
        - Inserts a new row into the `reviews` table.
        - Updates the object's `id` attribute with the primary key of the new row.
        - Adds the object to the class-level dictionary `all`.
        """
        sql = "INSERT INTO reviews(year, summary, employee_id) VALUES (?, ?, ?)"
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
        self.id = CURSOR.lastrowid
        type(self).all[self.id] = self
        CONN.commit()

    @classmethod
    def create(cls, year, summary, employee_id):
        """
        Create a new Review instance and save it to the database.
        Return the new instance.
        """
        review = cls(year, summary, employee_id)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        """
        Create or update a Review instance from a database row.
        - If an instance with the same ID exists in `all`, update it.
        - Otherwise, create a new instance.
        """
        review = cls.all.get(row[0])

        if review:
            review.year = row[1]
            review.summary = row[2]
            review.employee_id = row[3]
        else:
            review = cls(row[1], row[2], row[3])
            review.id = row[0]
            cls.all[review.id] = review

        return review

    @classmethod
    def find_by_id(cls, id):
        """Find and return a Review instance by its ID."""
        sql = "SELECT * FROM reviews WHERE id = ?"
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None

    def update(self):
        """Update the database row corresponding to this Review instance."""
        sql = "UPDATE reviews SET year = ?, summary = ?, employee_id = ? WHERE id = ?"
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()

    def delete(self):
        """
        Delete this Review instance from the database and the class-level dictionary.
        Reset the `id` attribute to `None`.
        """
        sql = "DELETE FROM reviews WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        del type(self).all[self.id]
        self.id = None

    @classmethod
    def get_all(cls):
        """
        Retrieve all rows from the `reviews` table and return a list of Review instances.
        """
        sql = "SELECT * FROM reviews"
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]
