from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

dog_links = [
    {
        "id": 1,
        "title": "30 Fun and Fascinating Dog Facts",
        "url": "https://www.akc.org/expert-advice/lifestyle/dog-facts/",
        "score": 10,
    },
    {
        "id": 2,
        "title": "Why Do Dogs Tilt Their Heads?",
        "url": "https://www.sciencefocus.com/nature/why-do-dogs-tilt-their-head-when-you-speak-to-them",
        "score": 5,
    },
    {
        "id": 3,
        "title": "r/dogs — top posts",
        "url": "https://www.reddit.com/r/dogs/",
        "score": 3,
    },
    {
        "id": 4,
        "title": "Basic Dog Training Guide",
        "url": "https://www.animalhumanesociety.org/resource/how-get-most-out-training-your-dog",
        "score": 2,
    },
    {
        "id": 5,
        "title": "The Dogist (photo stories)",
        "url": "https://thedogist.com/",
        "score": 1,
    },
]


# @app.get("/")
# def homepage():
#     return render_template("index.html", links=dog_links)


@app.route("/")
def homepage():
    # Sort links by score descending before rendering
    sorted_links = sorted(dog_links, key=lambda x: x["score"], reverse=True)
    return render_template("index.html", links=sorted_links)


@app.route("/vote/<int:link_id>/<action>")
def vote(link_id, action):
    for link in dog_links:
        if link["id"] == link_id:
            if action == "upvote":
                link["score"] += 1
            elif action == "downvote":
                link["score"] -= 1
            break

    return redirect(url_for("homepage"))


# if __name__ == "__main__":
#     app.run(debug=True)


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

        # Create new post
        new_id = max(link["id"] for link in dog_links) + 1 if dog_links else 1
        new_post = {
            "id": new_id,
            "title": title,
            "url": url,
            "score": 1,  # Default score
        }

        dog_links.append(new_post)
        return redirect(url_for("index"))

    # GET request - show the form
    return render_template("submit.html")
