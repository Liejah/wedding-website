from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    send_from_directory
)

import json
import os
from functools import wraps
from werkzeug.utils import secure_filename


# =========================================================
# APP
# =========================================================

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "change-this-secret-key-before-production"
)


# =========================================================
# ADMIN LOGIN
# =========================================================

ADMIN_USERNAME = os.environ.get(
    "ADMIN_USERNAME",
    "Zyril Mae Aydinan"
)

ADMIN_PASSWORD = os.environ.get(
    "ADMIN_PASSWORD",
    "zyie010101"
)


# =========================================================
# DIRECTORIES
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads"
)

SETTINGS_FILE = os.path.join(
    BASE_DIR,
    "wedding_settings.json"
)

ALBUMS_FILE = os.path.join(
    BASE_DIR,
    "wedding_data.json"
)

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

app.config["MAX_CONTENT_LENGTH"] = (
    10 * 1024 * 1024
)


# =========================================================
# ALLOWED FILE TYPES
# =========================================================

ALLOWED_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp",
    "gif"
}


# =========================================================
# DEFAULT WEBSITE SETTINGS
# =========================================================

DEFAULT_SETTINGS = {

    "partner1": "Stevenson",

    "partner2": "Zyril Mae",

    "tagline":
        "Two hearts, one beautiful beginning.",

    "weddingDate":
        "December 12, 2026",

    "weddingTime":
        "4:00 PM",

    "venue":
        "The Rose Garden",

    "dressCode":
        "Formal",

    "rsvpEmail":
        "your@email.com",

    "rsvpMessage":
        "Please contact us to confirm your attendance.",

    "story1":
        "Our story began with a simple hello and grew into a love we want to celebrate with everyone we love.",

    "story2":
        "Now, we're beginning our next chapter together and we would love for you to be part of it.",

    "mainColor":
        "#D9A9A3"
}


# =========================================================
# DEFAULT ALBUMS
# =========================================================

DEFAULT_ALBUMS = {

    "features": [

        {
            "id": "our-day",
            "title": "OUR DAY",
            "subtitle": "The beginning of forever.",
            "description":
                "Beautiful moments from our special day.",
            "photos": []
        },

        {
            "id": "together",
            "title": "TOGETHER",
            "subtitle": "Every moment with you.",
            "description":
                "The memories we created together.",
            "photos": []
        },

        {
            "id": "forever",
            "title": "FOREVER",
            "subtitle": "Our love story continues.",
            "description":
                "The moments we will treasure forever.",
            "photos": []
        }

    ],

    "album": []
}


# =========================================================
# SETTINGS FUNCTIONS
# =========================================================

def save_settings(settings):

    with open(
        SETTINGS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            settings,
            file,
            indent=4,
            ensure_ascii=False
        )


def load_settings():

    if not os.path.exists(
        SETTINGS_FILE
    ):

        settings = DEFAULT_SETTINGS.copy()

        save_settings(settings)

        return settings

    try:

        with open(
            SETTINGS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            settings = json.load(file)

    except (
        json.JSONDecodeError,
        OSError
    ):

        settings = DEFAULT_SETTINGS.copy()

        save_settings(settings)

        return settings

    if not isinstance(
        settings,
        dict
    ):

        settings = DEFAULT_SETTINGS.copy()

        save_settings(settings)

        return settings

    changed = False

    for key, value in DEFAULT_SETTINGS.items():

        if key not in settings:

            settings[key] = value

            changed = True

    if changed:

        save_settings(settings)

    return settings


# =========================================================
# ALBUM FUNCTIONS
# =========================================================

def save_albums(data):

    with open(
        ALBUMS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


def load_albums():

    if not os.path.exists(
        ALBUMS_FILE
    ):

        data = DEFAULT_ALBUMS.copy()

        save_albums(data)

        return data

    try:

        with open(
            ALBUMS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

    except (
        json.JSONDecodeError,
        OSError
    ):

        data = DEFAULT_ALBUMS.copy()

        save_albums(data)

        return data

    if not isinstance(
        data,
        dict
    ):

        data = DEFAULT_ALBUMS.copy()

        save_albums(data)

        return data

    if "features" not in data:

        data["features"] = (
            DEFAULT_ALBUMS["features"]
        )

    if "album" not in data:

        data["album"] = []

    return data


# =========================================================
# FILE FUNCTIONS
# =========================================================

def allowed_file(filename):

    if not filename:
        return False

    if "." not in filename:
        return False

    extension = filename.rsplit(
        ".",
        1
    )[1].lower()

    return extension in ALLOWED_EXTENSIONS


# =========================================================
# ADMIN SECURITY
# =========================================================

def admin_required(function):

    @wraps(function)
    def wrapper(
        *args,
        **kwargs
    ):

        if not session.get(
            "admin_logged_in"
        ):

            return redirect(
                url_for("admin_login")
            )

        return function(
            *args,
            **kwargs
        )

    return wrapper


# =========================================================
# PUBLIC WEBSITE
# =========================================================

@app.route("/")
def home():

    settings = load_settings()

    data = load_albums()

    return render_template(
        "index.html",
        settings=settings,
        features=data["features"],
        album=data["album"]
    )


# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route(
    "/admin/login",
    methods=["GET", "POST"]
)
def admin_login():

    if session.get(
        "admin_logged_in"
    ):

        return redirect(
            url_for("admin")
        )

    error = None

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        if (
            username == ADMIN_USERNAME
            and
            password == ADMIN_PASSWORD
        ):

            session.clear()

            session["admin_logged_in"] = True

            session["admin_username"] = username

            return redirect(
                url_for("admin")
            )

        error = (
            "Incorrect username or password."
        )

    return render_template(
        "login.html",
        error=error
    )


# =========================================================
# ADMIN PANEL
# =========================================================

@app.route("/admin")
@admin_required
def admin():

    settings = load_settings()

    data = load_albums()

    return render_template(
        "admin.html",
        settings=settings,
        features=data["features"],
        album=data["album"]
    )


# =========================================================
# SAVE WEBSITE SETTINGS
# =========================================================

@app.route(
    "/admin/save",
    methods=["POST"]
)
@admin_required
def admin_save():

    settings = load_settings()

    fields = [

        "partner1",
        "partner2",
        "tagline",
        "weddingDate",
        "weddingTime",
        "venue",
        "dressCode",
        "rsvpEmail",
        "rsvpMessage",
        "story1",
        "story2",
        "mainColor"

    ]

    for field in fields:

        if field in request.form:

            settings[field] = request.form.get(
                field,
                ""
            ).strip()

    save_settings(settings)

    return redirect(
        url_for(
            "admin",
            saved="1"
        )
    )


# =========================================================
# UPLOAD PHOTO
# =========================================================

@app.route(
    "/admin/upload",
    methods=["POST"]
)
@admin_required
def admin_upload():

    photo = request.files.get(
        "photo"
    )

    destination = request.form.get(
        "destination",
        "album"
    )

    if photo is None:

        return redirect(
            url_for("admin")
        )

    if photo.filename == "":

        return redirect(
            url_for("admin")
        )

    if not allowed_file(
        photo.filename
    ):

        return redirect(
            url_for(
                "admin",
                error=(
                    "Only JPG, JPEG, PNG, WEBP "
                    "and GIF images are allowed."
                )
            )
        )

    filename = secure_filename(
        photo.filename
    )

    if not filename:

        return redirect(
            url_for(
                "admin",
                error="Invalid filename."
            )
        )

    base, extension = os.path.splitext(
        filename
    )

    counter = 1

    while os.path.exists(
        os.path.join(
            UPLOAD_FOLDER,
            filename
        )
    ):

        filename = (
            base
            + "_"
            + str(counter)
            + extension
        )

        counter += 1

    file_path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    try:

        photo.save(
            file_path
        )

    except OSError:

        return redirect(
            url_for(
                "admin",
                error="Could not upload photo."
            )
        )

    data = load_albums()

    if destination == "album":

        data["album"].append(
            filename
        )

    else:

        found = False

        for feature in data["features"]:

            if feature["id"] == destination:

                feature["photos"].append(
                    filename
                )

                found = True

                break

        if not found:

            data["album"].append(
                filename
            )

    save_albums(data)

    return redirect(
        url_for(
            "admin",
            uploaded="1"
        )
    )


# =========================================================
# DELETE PHOTO
# =========================================================

@app.route(
    "/admin/delete-photo",
    methods=["POST"]
)
@admin_required
def delete_photo():

    filename = request.form.get(
        "filename",
        ""
    ).strip()

    safe_filename = secure_filename(
        filename
    )

    if not safe_filename:

        return redirect(
            url_for("admin")
        )

    data = load_albums()

    data["album"] = [
        photo
        for photo in data["album"]
        if photo != safe_filename
    ]

    for feature in data["features"]:

        feature["photos"] = [

            photo
            for photo in feature["photos"]
            if photo != safe_filename

        ]

    save_albums(data)

    file_path = os.path.join(
        UPLOAD_FOLDER,
        safe_filename
    )

    if os.path.isfile(
        file_path
    ):

        try:

            os.remove(
                file_path
            )

        except OSError:

            pass

    return redirect(
        url_for("admin")
    )


# =========================================================
# DISPLAY PHOTO
# =========================================================

@app.route(
    "/uploads/<filename>"
)
def uploaded_file(
    filename
):

    safe_filename = secure_filename(
        filename
    )

    if not safe_filename:

        return redirect(
            url_for("home")
        )

    return send_from_directory(
        UPLOAD_FOLDER,
        safe_filename
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route(
    "/admin/logout"
)
def admin_logout():

    session.clear()

    return redirect(
        url_for("admin_login")
    )


# =========================================================
# FILE TOO LARGE
# =========================================================

@app.errorhandler(413)
def file_too_large(error):

    return redirect(
        url_for(
            "admin",
            error=(
                "Photo is too large. "
                "Maximum size is 10 MB."
            )
        )
    )


# =========================================================
# 404
# =========================================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "index.html",
        settings=load_settings(),
        features=load_albums()["features"],
        album=load_albums()["album"]
    ), 404


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )