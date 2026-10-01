
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
    "ADMIN_PASSWORD"
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

    # -----------------------------------------------------
    # BASIC INFORMATION
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # COLORS
    # -----------------------------------------------------

    "mainColor":
        "#D9A9A3",

    "backgroundStyle":
        "cream",


    # -----------------------------------------------------
    # TYPOGRAPHY
    # -----------------------------------------------------

    "headingFont":
        "Cormorant Garamond",

    "bodyFont":
        "Montserrat",


    # -----------------------------------------------------
    # EFFECTS
    # -----------------------------------------------------

    "petals":
        True,

    "lightbox":
        True,

    "animations":
        True,


    # -----------------------------------------------------
    # SECTION VISIBILITY
    # -----------------------------------------------------

    "showHero":
        True,

    "showStory":
        True,

    "showDetails":
        True,

    "showFeatures":
        True,

    "showAlbum":
        True,

    "showRSVP":
        True,

    "showFooter":
        True,


    # -----------------------------------------------------
    # HERO
    # -----------------------------------------------------

    "heroTitle":
        "We're Getting Married",

    "heroSubtitle":
        "Join us as we begin forever together.",


    # -----------------------------------------------------
    # STORY SECTION
    # -----------------------------------------------------

    "storyTitle":
        "Our Story",

    "storySubtitle":
        "A little piece of our journey together.",


    # -----------------------------------------------------
    # DETAILS SECTION
    # -----------------------------------------------------

    "detailsTitle":
        "Wedding Details",

    "detailsSubtitle":
        "Everything you need to know about our special day.",


    # -----------------------------------------------------
    # FEATURES SECTION
    # -----------------------------------------------------

    "featuresTitle":
        "Our Memories",

    "featuresSubtitle":
        "Moments that made our story beautiful.",


    # -----------------------------------------------------
    # ALBUM SECTION
    # -----------------------------------------------------

    "albumTitle":
        "The Album",

    "albumSubtitle":
        "A collection of memories we will treasure forever.",


    # -----------------------------------------------------
    # RSVP SECTION
    # -----------------------------------------------------

    "rsvpTitle":
        "Will You Join Us?",

    "rsvpSubtitle":
        "We would love to celebrate this special day with you.",


    # -----------------------------------------------------
    # FOOTER
    # -----------------------------------------------------

    "footerText":
        "With love, Stevenson & Zyril Mae",

    "footerCopyright":
        "© 2026 Stevenson & Zyril Mae"
}


# =========================================================
# DEFAULT FEATURE ALBUMS
# =========================================================

DEFAULT_ALBUMS = {

    "features": [

        {
            "id": "our-day",

            "title": "OUR DAY",

            "subtitle":
                "The beginning of forever.",

            "description":
                "Beautiful moments from our special day.",

            "photos": []
        },

        {
            "id": "together",

            "title": "TOGETHER",

            "subtitle":
                "Every moment with you.",

            "description":
                "The memories we created together.",

            "photos": []
        },

        {
            "id": "forever",

            "title": "FOREVER",

            "subtitle":
                "Our love story continues.",

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

    temporary_file = SETTINGS_FILE + ".tmp"

    try:

        with open(
            temporary_file,
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
            temporary_file,
            SETTINGS_FILE
        )

    except OSError as error:

        print(
            f"Error saving settings: {error}"
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
        OSError,
        TypeError
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

    temporary_file = ALBUMS_FILE + ".tmp"

    try:

        with open(
            temporary_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )

        os.replace(
            temporary_file,
            ALBUMS_FILE
        )

    except OSError as error:

        print(
            f"Error saving albums: {error}"
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
        OSError,
        TypeError
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

        data["features"] = []

    if "album" not in data:

        data["album"] = []

    # Make sure all default features exist
    existing_ids = {
        feature.get("id")
        for feature in data["features"]
        if isinstance(feature, dict)
    }

    for default_feature in DEFAULT_ALBUMS["features"]:

        if default_feature["id"] not in existing_ids:

            data["features"].append(
                default_feature.copy()
            )

    # Make sure every feature has photos
    for feature in data["features"]:

        if "photos" not in feature:

            feature["photos"] = []

        if "title" not in feature:

            feature["title"] = ""

        if "subtitle" not in feature:

            feature["subtitle"] = ""

        if "description" not in feature:

            feature["description"] = ""

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
# SAVE ALL WEBSITE SETTINGS
# =========================================================

@app.route(
    "/admin/save",
    methods=["POST"]
)
@admin_required
def admin_save():

    settings = load_settings()

    # =====================================================
    # TEXT SETTINGS
    # =====================================================

    text_fields = [
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
        "mainColor",

        # Design
        "backgroundStyle",
        "headingFont",
        "bodyFont",

        # Hero
        "heroTitle",
        "heroSubtitle",

        # Story
        "storyTitle",
        "storySubtitle",

        # Details
        "detailsTitle",
        "detailsSubtitle",

        # Features
        "featuresTitle",
        "featuresSubtitle",

        # Album
        "albumTitle",
        "albumSubtitle",

        # RSVP
        "rsvpTitle",
        "rsvpSubtitle",

        # Footer
        "footerText",
        "footerCopyright"
    ]

    for field in text_fields:

        if field in request.form:

            settings[field] = request.form.get(
                field,
                ""
            ).strip()


    # =====================================================
    # WEBSITE SECTION VISIBILITY
    # =====================================================

    visibility_fields = [
        "showHero",
        "showStory",
        "showDetails",
        "showFeatures",
        "showAlbum",
        "showRSVP",
        "showFooter"
    ]

    for field in visibility_fields:

        settings[field] = (
            field in request.form
        )


    # =====================================================
    # WEBSITE EFFECTS
    # =====================================================

    effect_fields = [
        "petals",
        "lightbox",
        "animations"
    ]

    for field in effect_fields:

        settings[field] = (
            field in request.form
        )


    # =====================================================
    # VALIDATE BACKGROUND
    # =====================================================

    allowed_backgrounds = [
        "cream",
        "white",
        "rose"
    ]

    if settings.get(
        "backgroundStyle"
    ) not in allowed_backgrounds:

        settings["backgroundStyle"] = "cream"


    # =====================================================
    # VALIDATE HEADING FONT
    # =====================================================

    allowed_heading_fonts = [
        "Cormorant Garamond",
        "Georgia",
        "Times New Roman"
    ]

    if settings.get(
        "headingFont"
    ) not in allowed_heading_fonts:

        settings["headingFont"] = (
            "Cormorant Garamond"
        )


    # =====================================================
    # VALIDATE BODY FONT
    # =====================================================

    allowed_body_fonts = [
        "Montserrat",
        "Arial",
        "Georgia"
    ]

    if settings.get(
        "bodyFont"
    ) not in allowed_body_fonts:

        settings["bodyFont"] = "Montserrat"


    # =====================================================
    # VALIDATE MAIN COLOR
    # =====================================================

    main_color = settings.get(
        "mainColor",
        "#D9A9A3"
    ).strip()

    valid_color = False

    if main_color.startswith("#"):

        if len(main_color) in (4, 7):

            try:

                int(
                    main_color[1:],
                    16
                )

                valid_color = True

            except ValueError:

                valid_color = False


    if not valid_color:

        settings["mainColor"] = "#D9A9A3"


    # =====================================================
    # SAVE EVERYTHING
    # =====================================================

    save_settings(settings)


    # =====================================================
    # RETURN TO ADMIN
    # =====================================================

    return redirect(
        url_for(
            "admin",
            saved="1"
        )
    )



# =========================================================
# SAVE FEATURE SETTINGS
# =========================================================

@app.route(
    "/admin/save-feature",
    methods=["POST"]
)
@admin_required
def save_feature():

    feature_id = request.form.get(
        "feature_id",
        ""
    ).strip()

    if not feature_id:

        return redirect(
            url_for("admin")
        )

    data = load_albums()

    for feature in data["features"]:

        if feature.get("id") == feature_id:

            feature["title"] = request.form.get(
                "title",
                feature.get("title", "")
            ).strip()

            feature["subtitle"] = request.form.get(
                "subtitle",
                feature.get("subtitle", "")
            ).strip()

            feature["description"] = request.form.get(
                "description",
                feature.get("description", "")
            ).strip()

            break

    save_albums(data)

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
    ).strip()


    if photo is None:

        return redirect(
            url_for(
                "admin",
                error="Please select a photo."
            )
        )


    if photo.filename == "":

        return redirect(
            url_for(
                "admin",
                error="Please select a photo."
            )
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


    # -----------------------------------------------------
    # PREVENT DUPLICATE FILENAMES
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # SAVE FILE
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # ASSIGN PHOTO
    # -----------------------------------------------------

    data = load_albums()


    if destination == "album":

        data["album"].append(
            filename
        )

    else:

        found = False

        for feature in data["features"]:

            if feature.get("id") == destination:

                feature.setdefault(
                    "photos",
                    []
                )

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


    # Remove from general album

    data["album"] = [

        photo

        for photo in data["album"]

        if photo != safe_filename
    ]


    # Remove from feature albums

    for feature in data["features"]:

        feature["photos"] = [

            photo

            for photo in feature.get(
                "photos",
                []
            )

            if photo != safe_filename
        ]


    save_albums(data)


    # Delete physical file

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

    data = load_albums()

    return render_template(
        "index.html",
        settings=load_settings(),
        features=data["features"],
        album=data["album"]
    ), 404


# =========================================================
# START SERVER
# =========================================================

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
