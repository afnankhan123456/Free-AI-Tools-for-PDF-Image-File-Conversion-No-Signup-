import os
from flask import send_from_directory
import uuid
import threading
from flask import Flask, render_template, request, send_file, redirect, flash, jsonify
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from PIL import Image

from logic import (
    png_to_pdf_logic,
    jpg_to_pdf_logic,
    pdf_to_word_logic,
    word_to_pdf_logic,
    merge_pdf_logic,
    split_pdf_logic,
    compress_pdf_logic,
    rotate_pdf_logic,
    resize_pdf_logic,
    pdf_to_jpg_logic,
    image_resize_logic,
    base64_encoder_logic,
    json_formatter_logic,
    qr_generator_logic,
    word_counter_logic
)

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ======================================================
# 🔥 5MB MAX UPLOAD LIMIT (Global Limit for All Tools)
# ======================================================
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB

# ======================================================
# 🔥 ERROR HANDLER FOR FILE TOO LARGE
# ======================================================
@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    flash("File size exceeds 5MB limit. Please upload a smaller file.")
    return redirect(request.url)


UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["PROCESSED_FOLDER"] = PROCESSED_FOLDER

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

# ======================================================
# 🔥 HEAVY TOOL CONCURRENT LIMIT (MAX 3 USERS)
# Only for:
# - pdf_to_jpg
# - split_pdf
# ======================================================
heavy_tool_semaphore = threading.BoundedSemaphore(3)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ===============================
# HOME
# ===============================
@app.route("/")
def home():
    return render_template("home.html")
    
# ==== Google route add
@app.route("/google3e04282ea741df4b.html")
def google_verify():
    return send_from_directory("static", "google3e04282ea741df4b.html")

#=============
@app.route("/sitemap.xml")
def sitemap():
    pages = [
        "https://free-ai-tools-for-pdf-image-file.onrender.com/",
        "https://free-ai-tools-for-pdf-image-file.onrender.com/image-tools",
        "https://free-ai-tools-for-pdf-image-file.onrender.com/image-compressor",
        "https://free-ai-tools-for-pdf-image-file.onrender.com/image-resize",
        "https://free-ai-tools-for-pdf-image-file.onrender.com/pdf-tools",
        "https://free-ai-tools-for-pdf-image-file.onrender.com/png-to-pdf",
        "https://free-ai-tools-for-pdf-image-file.onrender.com/jpg-to-pdf",
        "https://free-ai-tools-for-pdf-image-file.onrender.com/pdf-to-word",
        "https://free-ai-tools-for-pdf-image-file.onrender.com/word-to-pdf",
        "https://free-ai-tools-for-pdf-image-file.onrender.com/pdf-to-jpg",
        "https://free-ai-tools-for-pdf-image-file.onrender.com/merge-pdf",
        "https://free-ai-tools-for-pdf-image-file.onrender.com/split-pdf",
        "https://free-ai-tools-for-pdf-image-file.onrender.com/compress-pdf",
        "https://free-ai-tools-for-pdf-image-file.onrender.com/rotate-pdf",
        "https://free-ai-tools-for-pdf-image-file.onrender.com/resize-pdf",
        "https://free-ai-tools-for-pdf-image-file.onrender.com/utility-tools",
        "https://free-ai-tools-for-pdf-image-file.onrender.com/word-counter",
        "https://free-ai-tools-for-pdf-image-file.onrender.com/qr-generator",
        "https://free-ai-tools-for-pdf-image-file.onrender.com/base64-encoder",
        "https://free-ai-tools-for-pdf-image-file.onrender.com/json-formatter"
    ]

    sitemap_xml = render_template("sitemap_template.xml", pages=pages)

    response = app.response_class(
        sitemap_xml,
        mimetype='application/xml'
    )

    return response

# ===============================
# CATEGORY PAGES
# ===============================
@app.route("/pdf-tools")
def pdf_tools():
    return render_template("pdf_tools/pdf_all_in_one.html")


@app.route("/image-tools")
def image_tools():
    return render_template("image_tools/image_tools.html")


@app.route("/utility-tools")
def utility_tools():
    return render_template("utility_tools/utility_tools.html")


# ===============================
# UTILITY TOOL ROUTES
# ===============================
@app.route("/base64-encoder", methods=["GET", "POST"])
def base64_encoder():
    result = None
    if request.method == "POST":
        result = base64_encoder_logic()
    return render_template("utility_tools/base64_encoder.html", result=result)


@app.route("/json-formatter", methods=["GET", "POST"])
def json_formatter():
    result = None
    error = None
    if request.method == "POST":
        try:
            result = json_formatter_logic()
        except Exception:
            error = "Invalid JSON format."
    return render_template("utility_tools/json_formatter.html", result=result, error=error)


@app.route("/qr-generator", methods=["GET", "POST"])
def qr_generator():
    if request.method == "POST":
        return qr_generator_logic(app)
    return render_template("utility_tools/qr_generator.html")


@app.route("/word-counter", methods=["GET", "POST"])
def word_counter():
    result = None
    if request.method == "POST":
        result = word_counter_logic()
    return render_template("utility_tools/word_counter.html", result=result)


# ===============================
# PDF TOOL PAGE ROUTES (GET)
# ===============================
@app.route("/png-to-pdf")
def png_to_pdf():
    return render_template("pdf_tools/png_to_pdf.html")


@app.route("/jpg-to-pdf", methods=["GET", "POST"])
def jpg_to_pdf():
    if request.method == "POST":
        from logic import jpg_to_pdf_logic
        return jpg_to_pdf_logic(app)
    return render_template("pdf_tools/jpg_to_pdf.html")


@app.route("/pdf-to-word")
def pdf_to_word():
    return render_template("pdf_tools/pdf_to_word.html")


@app.route("/word-to-pdf")
def word_to_pdf():
    return render_template("pdf_tools/word_to_pdf.html")


@app.route("/pdf-to-jpg")
def pdf_to_jpg():
    return render_template("pdf_tools/pdf_to_jpg.html")


@app.route("/merge-pdf")
def merge_pdf():
    return render_template("pdf_tools/merge_pdf.html")


@app.route("/split-pdf")
def split_pdf():
    return render_template("pdf_tools/split_pdf.html")


@app.route("/compress-pdf")
def compress_pdf():
    return render_template("pdf_tools/compress_pdf.html")


@app.route("/rotate-pdf")
def rotate_pdf():
    return render_template("pdf_tools/rotate_pdf.html")


@app.route("/resize-pdf")
def resize_pdf():
    return render_template("pdf_tools/resize_pdf.html")


# ===============================
# PDF TOOL ACTION ROUTES (POST)
# ===============================

@app.route("/png-to-pdf-action", methods=["POST"])
def png_to_pdf_action():
    return png_to_pdf_logic(app)


@app.route("/jpg-to-pdf-action", methods=["POST"])
def jpg_to_pdf_action():
    return jpg_to_pdf_logic(app)


@app.route("/pdf-to-word-action", methods=["POST"])
def pdf_to_word_action():
    return pdf_to_word_logic(app)


@app.route("/word-to-pdf-action", methods=["POST"])
def word_to_pdf_action():
    return word_to_pdf_logic(app)


# ======================================================
# 🔥 HEAVY TOOL 1: PDF TO JPG (LIMITED TO 3 USERS)
# ======================================================
@app.route("/pdf-to-jpg-action", methods=["POST"])
def pdf_to_jpg_action():
    if not heavy_tool_semaphore.acquire(blocking=False):
        return "Server busy. Please try again after few seconds."

    try:
        return pdf_to_jpg_logic(app)
    finally:
        heavy_tool_semaphore.release()


# ======================================================
# 🔥 HEAVY TOOL 2: SPLIT PDF (LIMITED TO 3 USERS)
# ======================================================
@app.route("/split-pdf-action", methods=["POST"])
def split_pdf_action():
    if not heavy_tool_semaphore.acquire(blocking=False):
        return "Server busy. Please try again after few seconds."

    try:
        return split_pdf_logic(app)
    finally:
        heavy_tool_semaphore.release()


@app.route("/merge-pdf-action", methods=["POST"])
def merge_pdf_action():
    return merge_pdf_logic(app)


@app.route("/compress-pdf-action", methods=["POST"])
def compress_pdf_action():
    return compress_pdf_logic(app)


@app.route("/rotate-pdf-action", methods=["POST"])
def rotate_pdf_action():
    return rotate_pdf_logic(app)


@app.route("/resize-pdf-action", methods=["POST"])
def resize_pdf_action():
    return resize_pdf_logic(app)


# ===============================
# IMAGE RESIZER
# ===============================
@app.route("/image-resize", methods=["GET", "POST"])
def image_resize():
    if request.method == "POST":
        return image_resize_logic(app)
    return render_template("image_tools/image_resize.html")


# ===============================
# IMAGE COMPRESSOR
# ===============================
@app.route("/image-compressor", methods=["GET", "POST"])
def image_compressor():

    if request.method == "POST":

        file = request.files.get("file")
        quality = request.form.get("quality", 60)

        if not file or file.filename == "":
            flash("No file selected")
            return redirect(request.url)

        if file and allowed_file(file.filename):

            unique_name = str(uuid.uuid4()) + "_" + secure_filename(file.filename)
            upload_path = os.path.join(UPLOAD_FOLDER, unique_name)
            file.save(upload_path)

            img = Image.open(upload_path)
            output_path = os.path.join(PROCESSED_FOLDER, unique_name)
            img.save(output_path, optimize=True, quality=int(quality))

            return send_file(output_path, as_attachment=True)

        else:
            flash("Invalid file type")
            return redirect(request.url)

    return render_template("image_tools/image_compress.html")


#=================================
from flask import send_from_directory

@app.route('/robots.txt')
def robots():
    return send_from_directory('static', 'robots.txt')

# =============== YANDEX ROUTE
@app.route('/yandex_3c01d903358ab76d.html')
def yandex_verify():
    return send_from_directory('.', 'yandex_3c01d903358ab76d.html')


# ===============================
# LOCAL RUN
# ===============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)



