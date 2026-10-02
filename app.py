from flask import (
    Flask, render_template, request, redirect, url_for,
    session, send_from_directory, flash
)
import json
import os
from functools import wraps
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "stevenson-zyril-wedding-secret-key-change-this"
)

ADMIN_USERNAME = os.environ.get(
    "ADMIN_USERNAME",
    "Zyril Mae Aydinan"
)

ADMIN_PASSWORD = os.environ.get(
    "ADMIN_PASSWORD",
    "zyie010101"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(BASE_DIR, "wedding_settings.json")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ============================================================
# FILE TYPES
# ============================================================

IMAGE_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp",
    "gif"
}

AUDIO_EXTENSIONS = {
    "mp3",
    "wav",
    "ogg",
    "m4a",
    "aac",
    "webm"
}

# Maximum upload size: 30 MB
app.config["MAX_CONTENT_LENGTH"] = 30 * 1024 * 1024


# ============================================================
# DEFAULT WEBSITE SETTINGS
# ============================================================

DEFAULT_SETTINGS = {
    "partner1": "Stevenson",
    "partner2": "Zyril Mae",

    "tagline": "Join us as we begin forever together.",

    "weddingDate": "December 12, 2026",
    "weddingTime": "4:00 PM",

    "venue": "The Rose Garden",
    "dressCode": "Formal",

    "rsvpEmail": "your@email.com",
    "rsvpMessage": "Please contact us to confirm your attendance.",

    "story1": (
        "Our story began with a simple hello and grew into a love "
        "we want to celebrate with everyone we love."
    ),

    "story2": (
        "Now, we're beginning our next chapter together and we would "
        "love for you to be part of it."
    ),

      "mainColor": "#B97878",

    # --------------------------------------------------------
    # MUSIC
    # --------------------------------------------------------

    "music_enabled": False,
    "music_source": "upload",
    "music_url": "",
    "music_file": "",
    "music_volume": 0.35
}


# ============================================================
# SETTINGS
# ============================================================

def save_settings(settings):
    temporary = SETTINGS_FILE + ".tmp"

    with open(
        temporary,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            settings,
            file,
            indent=4,
            ensure_ascii=False
        )

    os.replace(
        temporary,
        SETTINGS_FILE
    )


def load_settings():

    if not os.path.exists(SETTINGS_FILE):

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
        OSError,
        json.JSONDecodeError,
        TypeError
    ):

        settings = DEFAULT_SETTINGS.copy()

    if not isinstance(settings, dict):

        settings = DEFAULT_SETTINGS.copy()

    changed = False

    # Add any missing settings without destroying
    # settings that already exist.

    for key, value in DEFAULT_SETTINGS.items():

        if key not in settings:

            settings[key] = value

            changed = True

    # Make sure volume is valid.

    try:

        settings["music_volume"] = max(
            0.0,
            min(
                1.0,
                float(
                    settings.get(
                        "music_volume",
                        0.35
                    )
                )
            )
        )

    except (
        TypeError,
        ValueError
    ):

        settings["music_volume"] = 0.35

        changed = True

    # Make sure music source is valid.

    if settings.get("music_source") not in {
        "upload",
        "url",
        "youtube",
        "spotify"
    }:

        settings["music_source"] = "upload"

        changed = True

    if changed:

        save_settings(settings)

    return settings


# ============================================================
# FILE HELPERS
# ============================================================

def allowed_file(
    filename,
    extensions
):

    if not filename or "." not in filename:

        return False

    return (
        filename.rsplit(
            ".",
            1
        )[1].lower()
        in extensions
    )


def unique_filename(original):

    filename = secure_filename(
        original
    )

    if not filename:

        return ""

    base, extension = os.path.splitext(
        filename
    )

    candidate = filename

    counter = 1

    while os.path.exists(
        os.path.join(
            UPLOAD_FOLDER,
            candidate
        )
    ):

        candidate = (
            f"{base}_{counter}{extension}"
        )

        counter += 1

    return candidate


def get_photos():

    try:

        return sorted(
            [
                name
                for name in os.listdir(
                    UPLOAD_FOLDER
                )
                if allowed_file(
                    name,
                    IMAGE_EXTENSIONS
                )
                and os.path.isfile(
                    os.path.join(
                        UPLOAD_FOLDER,
                        name
                    )
                )
            ],
            key=str.lower
        )

    except OSError:

        return []


# ============================================================
# ADMIN LOGIN PROTECTION
# ============================================================

def admin_required(function):

    @wraps(function)
    def decorated(
        *args,
        **kwargs
    ):

        if session.get(
            "admin_logged_in"
        ) is not True:

            return redirect(
                url_for("admin_login")
            )

        return function(
            *args,
            **kwargs
        )

    return decorated


# ============================================================
# PUBLIC WEBSITE
# ============================================================

@app.route("/")
def home():

    return render_template(
        "index.html",
        settings=load_settings(),
        photos=get_photos()
    )


# ============================================================
# ADMIN LOGIN
# ============================================================

@app.route(
    "/admin/login",
    methods=["GET", "POST"]
)
def admin_login():

    if session.get(
        "admin_logged_in"
    ) is True:

        return redirect(
            url_for("admin")
        )

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
            and password == ADMIN_PASSWORD
        ):

            session.clear()

            session["admin_logged_in"] = True

            session["admin_username"] = username

            flash(
                "Welcome to your wedding admin panel!",
                "success"
            )

            return redirect(
                url_for("admin")
            )

        flash(
            "Incorrect username or password.",
            "error"
        )

    return render_template(
        "login.html"
    )


# ============================================================
# ADMIN PANEL
# ============================================================

@app.route("/admin")
@admin_required
def admin():

    return render_template(
        "admin.html",
        settings=load_settings(),
        photos=get_photos()
    )


# ============================================================
# SAVE WEBSITE SETTINGS
# ============================================================

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

    # Validate color.

    color = settings.get(
        "mainColor",
        ""
    )

    if color and not (
        color.startswith("#")
        and len(color) in (4, 7)
    ):

        settings["mainColor"] = (
            DEFAULT_SETTINGS["mainColor"]
        )

    save_settings(settings)

    flash(
        "Website settings saved successfully!",
        "success"
    )

    return redirect(
        url_for("admin")
    )


# ============================================================
# BACKGROUND MUSIC
# ============================================================

@app.route(
    "/admin/music",
    methods=["POST"]
)
@admin_required
def admin_music():

    settings = load_settings()

    # --------------------------------------------------------
    # ENABLE / DISABLE MUSIC
    # --------------------------------------------------------

    settings["music_enabled"] = (
        request.form.get(
            "music_enabled"
        ) == "on"
    )

    # --------------------------------------------------------
    # MUSIC SOURCE
    # --------------------------------------------------------

    source = request.form.get(
        "music_source",
        "upload"
    )

    if source not in {
        "upload",
        "url",
        "youtube",
        "spotify"
    }:

        source = "upload"

    settings["music_source"] = source

    # --------------------------------------------------------
    # MUSIC URL
    # --------------------------------------------------------

    settings["music_url"] = request.form.get(
        "music_url",
        ""
    ).strip()

    # --------------------------------------------------------
    # VOLUME
    # --------------------------------------------------------

    try:

        volume = float(
            request.form.get(
                "music_volume",
                "0.35"
            )
        )

    except (
        TypeError,
        ValueError
    ):

        volume = 0.35

    settings["music_volume"] = max(
        0.0,
        min(
            1.0,
            volume
        )
    )

    # --------------------------------------------------------
    # UPLOAD MUSIC
    # --------------------------------------------------------

    audio = request.files.get(
        "music_file"
    )

    if audio and audio.filename:

        if not allowed_file(
            audio.filename,
            AUDIO_EXTENSIONS
        ):

            flash(
                "Unsupported music file. "
                "Use MP3, WAV, OGG, M4A, AAC, or WEBM.",
                "error"
            )

            return redirect(
                url_for("admin")
                + "#music"
            )

        filename = unique_filename(
            audio.filename
        )

        if not filename:

            flash(
                "Invalid music filename.",
                "error"
            )

            return redirect(
                url_for("admin")
                + "#music"
            )

        # Delete previous uploaded music.

        old_file = settings.get(
            "music_file",
            ""
        )

        if old_file:

            old_path = os.path.join(
                UPLOAD_FOLDER,
                os.path.basename(
                    old_file
                )
            )

            if os.path.isfile(
                old_path
            ):

                try:

                    os.remove(
                        old_path
                    )

                except OSError:

                    pass

        try:

            audio.save(
                os.path.join(
                    UPLOAD_FOLDER,
                    filename
                )
            )

        except OSError:

            flash(
                "There was a problem uploading the music file.",
                "error"
            )

            return redirect(
                url_for("admin")
                + "#music"
            )

        settings["music_file"] = filename

        # Automatically select uploaded music
        # when a new file is uploaded.

        settings["music_source"] = "upload"

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    source = settings.get(
        "music_source"
    )

    if (
        settings.get("music_enabled")
        and source == "upload"
        and not settings.get("music_file")
    ):

        flash(
            "Please upload a music file or select another music source.",
            "error"
        )

        return redirect(
            url_for("admin")
            + "#music"
        )

    if (
        settings.get("music_enabled")
        and source in {
            "url",
            "youtube",
            "spotify"
        }
        and not settings.get("music_url")
    ):

        flash(
            "Please enter a music URL.",
            "error"
        )

        return redirect(
            url_for("admin")
            + "#music"
        )

    save_settings(settings)

    flash(
        "Background music settings saved!",
        "success"
    )

    return redirect(
        url_for("admin")
        + "#music"
    )


# ============================================================
# REMOVE UPLOADED MUSIC
# ============================================================

@app.route(
    "/admin/music/remove",
    methods=["POST"]
)
@admin_required
def remove_music():

    settings = load_settings()

    old_file = settings.get(
        "music_file",
        ""
    )

    if old_file:

        path = os.path.join(
            UPLOAD_FOLDER,
            os.path.basename(
                old_file
            )
        )

        if os.path.isfile(path):

            try:

                os.remove(path)

            except OSError:

                pass

    settings["music_file"] = ""

    if settings.get(
        "music_source"
    ) == "upload":

        settings["music_source"] = "url"

    save_settings(settings)

    flash(
        "Uploaded wedding music removed.",
        "success"
    )

    return redirect(
        url_for("admin")
        + "#music"
    )


# ============================================================
# PHOTO UPLOAD
# ============================================================

@app.route(
    "/admin/upload",
    methods=["POST"]
)
@admin_required
def admin_upload():

    photo = request.files.get(
        "photo"
    )

    if not photo or not photo.filename:

        flash(
            "Please select a photo.",
            "error"
        )

        return redirect(
            url_for("admin")
        )

    if not allowed_file(
        photo.filename,
        IMAGE_EXTENSIONS
    ):

        flash(
            "Only JPG, JPEG, PNG, WEBP and GIF images are allowed.",
            "error"
        )

        return redirect(
            url_for("admin")
        )

    filename = unique_filename(
        photo.filename
    )

    if not filename:

        flash(
            "Invalid filename.",
            "error"
        )

        return redirect(
            url_for("admin")
        )

    try:

        photo.save(
            os.path.join(
                UPLOAD_FOLDER,
                filename
            )
        )

    except OSError:

        flash(
            "There was a problem uploading the photo.",
            "error"
        )

        return redirect(
            url_for("admin")
        )

    flash(
        f"Photo '{filename}' uploaded successfully!",
        "success"
    )

    return redirect(
        url_for("admin")
    )


# ============================================================
# SERVE UPLOADED FILES
# ============================================================

@app.route(
    "/uploads/<path:filename>"
)
def uploaded_file(filename):

    safe = secure_filename(
        os.path.basename(
            filename
        )
    )

    if not safe:

        return redirect(
            url_for("home")
        )

    return send_from_directory(
        UPLOAD_FOLDER,
        safe
    )


# ============================================================
# DELETE PHOTO
# ============================================================

@app.route(
    "/admin/delete-photo",
    methods=["POST"]
)
@admin_required
def delete_photo():

    filename = secure_filename(
        os.path.basename(
            request.form.get(
                "filename",
                ""
            ).strip()
        )
    )

    if not filename:

        flash(
            "Invalid filename.",
            "error"
        )

        return redirect(
            url_for("admin")
        )

    path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    if os.path.isfile(path):

        try:

            os.remove(path)

            flash(
                "Photo deleted successfully.",
                "success"
            )

        except OSError:

            flash(
                "Unable to delete the photo.",
                "error"
            )

    else:

        flash(
            "Photo not found.",
            "error"
        )

    return redirect(
        url_for("admin")
    )


# ============================================================
# LOG OUT
# ============================================================

@app.route(
    "/admin/logout"
)
def admin_logout():

    session.clear()

    return redirect(
        url_for("admin_login")
    )


# ============================================================
# FILE TOO LARGE
# ============================================================

@app.errorhandler(413)
def request_too_large(error):

    flash(
        "The uploaded file is too large. Maximum size is 30 MB.",
        "error"
    )

    return redirect(
        url_for("admin")
    )


# ============================================================
# 404
# ============================================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "index.html",
        settings=load_settings(),
        photos=get_photos()
    ), 404


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )

