import sqlite3

from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
DATABASE = "reddit.db"


def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Create posts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            score INTEGER NOT NULL DEFAULT 1,
            hidden INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Check if we need to seed initial data
    cursor.execute("SELECT COUNT(*) FROM posts")
    count = cursor.fetchone()[0]

    if count == 0:
        # Seed with initial dog links
        initial_posts = [
            (
                "30 Fun and Fascinating Dog Facts",
                "https://www.akc.org/expert-advice/lifestyle/dog-facts/",
                10,
                0,
            ),
            (
                "Why Do Dogs Tilt Their Heads?",
                "https://www.sciencefocus.com/nature/why-do-dogs-tilt-their-head-when-you-speak-to-them",
                5,
                0,
            ),
            ("r/dogs — top posts", "https://www.reddit.com/r/dogs/", 3, 0),
            (
                "Basic Dog Training Guide",
                "https://www.animalhumanesociety.org/resource/how-get-most-out-training-your-dog",
                2,
                0,
            ),
            ("The Dogist (photo stories)", "https://thedogist.com/", 1, 0),
        ]

        cursor.executemany(
            """
            INSERT INTO posts (title, url, score, hidden)
            VALUES (?, ?, ?, ?)
        """,
            initial_posts,
        )

    conn.commit()
    conn.close()


def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn


def get_all_posts():
    """Get all posts from database"""
    conn = get_db_connection()
    posts = conn.execute("SELECT * FROM posts ORDER BY created_at").fetchall()
    conn.close()
    return posts


@app.route("/")
def homepage():
    # Get non-hidden posts sorted by score descending
    conn = get_db_connection()
    non_hidden_posts = conn.execute(
        "SELECT * FROM posts WHERE hidden = 0 ORDER BY score DESC"
    ).fetchall()

    # Get hidden posts sorted by score descending
    hidden_posts = conn.execute(
        "SELECT * FROM posts WHERE hidden = 1 ORDER BY score DESC"
    ).fetchall()
    conn.close()

    return render_template(
        "index.html", links=non_hidden_posts, hidden_links=hidden_posts
    )


@app.route("/vote/<int:link_id>/<action>")
def vote(link_id, action):
    conn = get_db_connection()

    if action == "upvote":
        conn.execute("UPDATE posts SET score = score + 1 WHERE id = ?", (link_id,))
    elif action == "downvote":
        conn.execute("UPDATE posts SET score = score - 1 WHERE id = ?", (link_id,))

    conn.commit()
    conn.close()
    return redirect(url_for("homepage"))


@app.route("/hide/<int:link_id>")
def hide_post(link_id):
    conn = get_db_connection()

    # Toggle hidden status
    conn.execute("UPDATE posts SET hidden = NOT hidden WHERE id = ?", (link_id,))

    conn.commit()
    conn.close()
    return redirect(url_for("homepage"))


@app.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        url = request.form.get("url", "").strip()

        # Basic validation
        if not title:
            return "Error: Title cannot be empty", 400
        if not url.startswith("http"):
            return "Error: URL must start with http", 400

        # Insert new post into database
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO posts (title, url, score, hidden) VALUES (?, ?, 1, 0)",
            (title, url),
        )
        conn.commit()
        conn.close()

        return redirect(url_for("homepage"))

    # GET request - show the form
    return render_template("submit.html")


# Initialize database when app starts
init_db()

if __name__ == "__main__":
    app.run(debug=True)
