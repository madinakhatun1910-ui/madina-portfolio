from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from pathlib import Path
import json
import sqlite3
import os
import html
import resend

from config import Config


app = Flask(__name__)
app.config.from_object(Config)


# =========================================================
# PATHS
# =========================================================

BASE = Path(__file__).resolve().parent

PRODUCTS_FILE = BASE / "data" / "products.json"
BLOGS_FILE = BASE / "data" / "blogs.json"
DB_FILE = BASE / "database" / "app.db"


# =========================================================
# JSON HELPERS
# =========================================================

def load_json(path, key):
    try:
        return json.loads(
            path.read_text(encoding="utf-8")
        ).get(key, [])
    except (OSError, json.JSONDecodeError):
        return []


def products():
    return load_json(PRODUCTS_FILE, "products")


def posts():
    return load_json(BLOGS_FILE, "posts")


# =========================================================
# DATABASE
# =========================================================

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)

    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS enquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            product TEXT,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            status TEXT NOT NULL DEFAULT 'new'
                CHECK(status IN ('new','contacted','resolved'))
        )
    """)

    conn.commit()
    conn.close()


init_db()


# =========================================================
# RESEND EMAIL NOTIFICATION
# =========================================================

def send_enquiry_email(name, phone, email, product, message):
    """
    Send contact form notification using Resend API.
    """

    api_key = os.getenv("RESEND_API_KEY", "").strip()

    recipient = os.getenv(
        "MADINA_NOTIFICATION_EMAIL",
        "madinakhatun1910@gmail.com"
    ).strip()

    if not api_key:
        app.logger.warning(
            "Email notification skipped: RESEND_API_KEY is not configured"
        )
        return False

    if not recipient:
        app.logger.warning(
            "Email notification skipped: notification email is not configured"
        )
        return False

    try:
        # Set Resend API key
        resend.api_key = api_key

        # Escape user-submitted data before putting it into HTML
        safe_name = html.escape(name)
        safe_phone = html.escape(phone)
        safe_email = html.escape(email or "Not provided")
        safe_product = html.escape(product or "Not specified")
        safe_message = html.escape(message).replace("\n", "<br>")

        params = {
            "from": "onboarding@resend.dev",
            "to": [recipient],
            "subject": f"New Portfolio Enquiry - {name}",
            "html": f"""
                <div style="font-family: Arial, sans-serif; line-height: 1.6;">
                    <h2>New Portfolio Enquiry</h2>

                    <p>
                        <strong>Name:</strong>
                        {safe_name}
                    </p>

                    <p>
                        <strong>Phone:</strong>
                        {safe_phone}
                    </p>

                    <p>
                        <strong>Email:</strong>
                        {safe_email}
                    </p>

                    <p>
                        <strong>Product:</strong>
                        {safe_product}
                    </p>

                    <h3>Message</h3>

                    <p>
                        {safe_message}
                    </p>

                    <hr>

                    <p>
                        Sent from Madina Khatoon Portfolio Website.
                    </p>
                </div>
            """
        }

        result = resend.Emails.send(params)

        app.logger.info(
            "RESEND EMAIL SENT SUCCESSFULLY to %s: %s",
            recipient,
            result
        )

        return True

    except Exception as exc:
        app.logger.exception(
            "Could not send enquiry notification email via Resend: %s",
            exc
        )

        return False


# =========================================================
# GLOBAL SITE DATA
# =========================================================

@app.context_processor
def inject_globals():
    return {
        "site": {
            "name": "Madina Khatoon",
            "role": "Herbalife Independent Associate",
            "focus": "Nutrition & Wellness Guidance",
            "location": "Siwan, Bihar, India",
            "whatsapp": app.config["WHATSAPP_NUMBER"],
            "portrait_image": app.config["PORTRAIT_IMAGE"],
            "socials": app.config["SOCIALS"]
        }
    }


# =========================================================
# HOME
# =========================================================

@app.route("/")
def index():

    faqs = [
        (
            "Who is Madina Khatoon?",
            "Madina Khatoon is a Herbalife Independent Associate focused on nutrition and wellness guidance, based in Siwan, Bihar."
        ),
        (
            "What kind of guidance do you provide?",
            "General educational guidance around nutrition, wellness habits, healthy lifestyle topics and product information."
        ),
        (
            "Can I ask about a Herbalife product?",
            "Yes. You can ask for product information available in the supplied product documentation. Products are presented for information and guidance, not online purchase."
        ),
        (
            "Do you provide medical advice?",
            "No. The website provides general educational information and is not a substitute for advice from a qualified healthcare professional."
        ),
        (
            "Is online guidance available?",
            "Yes. Madina offers online guidance across India."
        ),
        (
            "How can I contact Madina?",
            "Use the enquiry form on this page or the WhatsApp button to start a conversation."
        ),
    ]

    wellness_topics = [
        (
            "01",
            "Nutrition",
            "Understand everyday food choices and balanced nutrition concepts in simple language."
        ),
        (
            "02",
            "Protein",
            "Learn the role of protein in a balanced diet and everyday nutrition awareness."
        ),
        (
            "03",
            "Fibre",
            "Explore fibre, food sources and why it is part of a balanced eating pattern."
        ),
        (
            "04",
            "Hydration",
            "Build awareness around regular fluid intake and everyday hydration habits."
        ),
        (
            "05",
            "Vitamins & Minerals",
            "A simple introduction to micronutrients and their place in nutrition."
        ),
        (
            "06",
            "Fitness",
            "General lifestyle education around movement and staying active."
        ),
        (
            "07",
            "Sleep",
            "Understand why consistent rest and healthy routines matter for wellbeing."
        ),
        (
            "08",
            "Healthy Lifestyle",
            "Practical awareness around sustainable everyday wellness habits."
        ),
    ]

    return render_template(
        "index.html",
        featured_products=products()[:6],
        featured_posts=posts()[:3],
        faqs=faqs,
        wellness_topics=wellness_topics,
        all_products=products()
    )


# =========================================================
# ABOUT
# =========================================================

@app.route("/about")
def about():
    return render_template("about.html")


# =========================================================
# PRODUCTS
# =========================================================

@app.route("/products")
def product_list():

    items = products()

    categories = sorted({
        p.get("category")
        for p in items
        if p.get("category")
    })

    return render_template(
        "products.html",
        products=items,
        categories=categories
    )


@app.route("/products/<slug>")
def product_detail(slug):

    item = next(
        (
            p for p in products()
            if p.get("id") == slug
        ),
        None
    )

    if not item:
        abort(404)

    return render_template(
        "product_detail.html",
        product=item
    )


# =========================================================
# WELLNESS
# =========================================================

@app.route("/wellness")
def wellness():
    return render_template("wellness.html")


# =========================================================
# BLOG
# =========================================================

@app.route("/blog")
def blog():

    blog_posts = posts()

    categories = sorted({
        p["category"]
        for p in blog_posts
        if p.get("category")
    })

    return render_template(
        "blog.html",
        posts=blog_posts,
        categories=categories
    )


@app.route("/blog/<slug>")
def blog_detail(slug):

    post = next(
        (
            p for p in posts()
            if p.get("slug") == slug
        ),
        None
    )

    if not post:
        abort(404)

    related = [
        p for p in posts()
        if p.get("slug") != slug
        and p.get("category") == post.get("category")
    ][:3]

    return render_template(
        "blog_detail.html",
        post=post,
        related=related
    )


# =========================================================
# FAQ
# =========================================================

@app.route("/faq")
def faq():
    return render_template("faq.html")


# =========================================================
# CONTACT
# =========================================================

@app.route("/contact", methods=["GET", "POST"])
def contact():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        product = request.form.get("product", "").strip()
        message = request.form.get("message", "").strip()

        # Required fields
        if not name or not phone or not message:
            return render_template(
                "contact.html",
                error="Please complete your name, phone and message."
            )

        # Length validation
        if (
            len(name) > 120
            or len(phone) > 40
            or len(email) > 160
            or len(product) > 180
            or len(message) > 3000
        ):
            return render_template(
                "contact.html",
                error="Please keep the submitted information within the allowed length."
            )

        # Save enquiry in database
        try:

            init_db()

            conn = get_db()

            conn.execute(
                """
                INSERT INTO enquiries
                (name, phone, email, product, message)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    name,
                    phone,
                    email,
                    product,
                    message
                )
            )

            conn.commit()
            conn.close()

        except sqlite3.Error:

            app.logger.exception(
                "Could not save enquiry to SQLite database"
            )

            return render_template(
                "contact.html",
                error=(
                    "We could not save your enquiry right now. "
                    "Please try again or contact Madina on WhatsApp."
                )
            )

        # Send email notification
        send_enquiry_email(
            name,
            phone,
            email,
            product,
            message
        )

        return render_template(
            "contact.html",
            success=(
                "Thank you! Your enquiry has been received. "
                "Madina will contact you soon."
            )
        )

    return render_template("contact.html")


# =========================================================
# DISCLAIMER
# =========================================================

@app.route("/disclaimer")
def disclaimer():
    return render_template("disclaimer.html")


# =========================================================
# PRIVACY
# =========================================================

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# =========================================================
# SITEMAP
# =========================================================

@app.route("/sitemap.xml")
def sitemap():

    urls = [
        url_for("index", _external=True),
        url_for("about", _external=True),
        url_for("product_list", _external=True),
        url_for("wellness", _external=True),
        url_for("blog", _external=True),
        url_for("faq", _external=True),
        url_for("contact", _external=True),
        url_for("disclaimer", _external=True),
        url_for("privacy", _external=True)
    ]

    urls += [
        url_for(
            "product_detail",
            slug=p["id"],
            _external=True
        )
        for p in products()
    ]

    urls += [
        url_for(
            "blog_detail",
            slug=p["slug"],
            _external=True
        )
        for p in posts()
    ]

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    )

    xml += "".join(
        f"<url><loc>{u}</loc></url>"
        for u in urls
    )

    xml += "</urlset>"

    return app.response_class(
        xml,
        mimetype="application/xml"
    )


# =========================================================
# ROBOTS.TXT
# =========================================================

@app.route("/robots.txt")
def robots():

    return (
        "User-agent: *\n"
        "Allow: /\n"
        "Sitemap: /sitemap.xml\n",
        200,
        {
            "Content-Type": "text/plain"
        }
    )


# =========================================================
# 404 ERROR
# =========================================================

@app.errorhandler(404)
def not_found(e):

    return render_template(
        "base.html",
        title="Page Not Found",
        error_page=True
    ), 404


# =========================================================
# LOCAL RUN
# =========================================================

if __name__ == "__main__":
    app.run(debug=True)
