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
    "music_volume": 0.35,

    # Featured photo albums
    "featured_albums": [],

    # Permanent OUR STORY photo
    "story_photo": ""
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
# ============================================================
# FEATURED PHOTO ALBUMS
# ============================================================

@app.route(
    "/admin/featured/create",
    methods=["POST"]
)
@admin_required
def create_featured_album():

    settings = load_settings()

    albums = settings.get(
        "featured_albums",
        []
    )

    title = request.form.get(
        "title",
        ""
    ).strip()

    if not title:
        flash(
            "Please enter a featured album name.",
            "error"
        )
        return redirect(
            url_for("admin") + "#featured"
        )

    album_id = secure_filename(title).lower()

    if not album_id:
        flash(
            "Invalid featured album name.",
            "error"
        )
        return redirect(
            url_for("admin") + "#featured"
        )

    existing_ids = {
        album.get("id")
        for album in albums
    }

    base_id = album_id
    counter = 2

    while album_id in existing_ids:
        album_id = f"{base_id}-{counter}"
        counter += 1

    albums.append({
        "id": album_id,
        "title": title,
        "photos": []
    })

    settings["featured_albums"] = albums

    save_settings(settings)

    flash(
        f"Featured album '{title}' created!",
        "success"
    )

    return redirect(
        url_for("admin") + "#featured"
    )


@app.route(
    "/admin/featured/rename",
    methods=["POST"]
)
@admin_required
def rename_featured_album():

    settings = load_settings()

    albums = settings.get(
        "featured_albums",
        []
    )

    album_id = request.form.get(
        "album_id",
        ""
    ).strip()

    title = request.form.get(
        "title",
        ""
    ).strip()

    if not album_id or not title:
        flash(
            "Please enter an album name.",
            "error"
        )
        return redirect(
            url_for("admin") + "#featured"
        )

    album = next(
        (
            album
            for album in albums
            if album.get("id") == album_id
        ),
        None
    )

    if not album:
        flash(
            "Featured album not found.",
            "error"
        )
        return redirect(
            url_for("admin") + "#featured"
        )

    album["title"] = title

    settings["featured_albums"] = albums

    save_settings(settings)

    flash(
        "Featured album name updated!",
        "success"
    )

    return redirect(
        url_for("admin") + "#featured"
    )


@app.route(
    "/admin/featured/upload",
    methods=["POST"]
)
@admin_required
def upload_featured_photo():

    settings = load_settings()

    albums = settings.get(
        "featured_albums",
        []
    )

    album_id = request.form.get(
        "album_id",
        ""
    ).strip()

    album = next(
        (
            album
            for album in albums
            if album.get("id") == album_id
        ),
        None
    )

    if not album:
        flash(
            "Featured album not found.",
            "error"
        )
        return redirect(
            url_for("admin") + "#featured"
        )

    photo = request.files.get(
        "featured_photo"
    )

    if not photo or not photo.filename:
        flash(
            "Please select a photo.",
            "error"
        )
        return redirect(
            url_for("admin") + "#featured"
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
            url_for("admin") + "#featured"
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
            url_for("admin") + "#featured"
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
            "There was a problem uploading the featured photo.",
            "error"
        )

        return redirect(
            url_for("admin") + "#featured"
        )

    album.setdefault(
        "photos",
        []
    ).append(filename)

    settings["featured_albums"] = albums

    save_settings(settings)

    flash(
        "Featured photo added!",
        "success"
    )

    return redirect(
        url_for("admin") + "#featured"
    )


@app.route(
    "/admin/featured/delete-photo",
    methods=["POST"]
)
@admin_required
def delete_featured_photo():

    settings = load_settings()

    albums = settings.get(
        "featured_albums",
        []
    )

    album_id = request.form.get(
        "album_id",
        ""
    ).strip()

    filename = secure_filename(
        os.path.basename(
            request.form.get(
                "filename",
                ""
            ).strip()
        )
    )

    album = next(
        (
            album
            for album in albums
            if album.get("id") == album_id
        ),
        None
    )

    if not album or not filename:
        flash(
            "Featured photo not found.",
            "error"
        )
        return redirect(
            url_for("admin") + "#featured"
        )

    if filename in album.get(
        "photos",
        []
    ):
        album["photos"].remove(
            filename
        )

    path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    if os.path.isfile(path):

        try:
            os.remove(path)
        except OSError:
            pass

    settings["featured_albums"] = albums

    save_settings(settings)

    flash(
        "Featured photo deleted.",
        "success"
    )

    return redirect(
        url_for("admin") + "#featured"
    )


@app.route(
    "/admin/featured/delete",
    methods=["POST"]
)
@admin_required
def delete_featured_album():

    settings = load_settings()

    albums = settings.get(
        "featured_albums",
        []
    )

    album_id = request.form.get(
        "album_id",
        ""
    ).strip()

    album = next(
        (
            album
            for album in albums
            if album.get("id") == album_id
        ),
        None
    )

    if not album:
        flash(
            "Featured album not found.",
            "error"
        )
        return redirect(
            url_for("admin") + "#featured"
        )

    for filename in album.get(
        "photos",
        []
    ):

        safe_filename = secure_filename(
            os.path.basename(filename)
        )

        if not safe_filename:
            continue

        path = os.path.join(
            UPLOAD_FOLDER,
            safe_filename
        )

        if os.path.isfile(path):

            try:
                os.remove(path)
            except OSError:
                pass

    settings["featured_albums"] = [
        item
        for item in albums
        if item.get("id") != album_id
    ]

    save_settings(settings)

    flash(
        "Featured album deleted.",
        "success"
    )

    return redirect(
        url_for("admin") + "#featured"
    )


# ============================================================

# ============================================================
# OUR STORY PHOTO
# ============================================================

@app.route(
    "/admin/story-photo",
    methods=["POST"]
)
@admin_required
def admin_story_photo():

    settings = load_settings()

    photo = request.files.get(
        "story_photo"
    )

    if not photo or not photo.filename:

        flash(
            "Please select a story photo.",
            "error"
        )

        return redirect(
            url_for("admin") + "#story-photo"
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
            url_for("admin") + "#story-photo"
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
            url_for("admin") + "#story-photo"
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
            "There was a problem uploading the story photo.",
            "error"
        )

        return redirect(
            url_for("admin") + "#story-photo"
        )

    old_photo = settings.get(
        "story_photo",
        ""
    )

    settings["story_photo"] = filename

    save_settings(settings)

    # Remove the previous dedicated story photo.
    # Do not remove it if it is also being used elsewhere.
    if old_photo and old_photo != filename:

        still_used = False

        if old_photo in settings.get("featured_albums", []):
            still_used = True

        for album in settings.get(
            "featured_albums",
            []
        ):

            if old_photo in album.get(
                "photos",
                []
            ):
                still_used = True
                break

        if not still_used:

            old_path = os.path.join(
                UPLOAD_FOLDER,
                secure_filename(
                    os.path.basename(old_photo)
                )
            )

            if os.path.isfile(old_path):

                try:
                    os.remove(old_path)
                except OSError:
                    pass

    flash(
        "OUR STORY photo changed successfully!",
        "success"
    )

    return redirect(
        url_for("admin") + "#story-photo"
    )


# PHOTO UPLOAD
# ============================================================

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
