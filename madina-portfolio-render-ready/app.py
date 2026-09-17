from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from pathlib import Path
import json
import sqlite3
import re
import smtplib
from config import Config
from email.message import EmailMessage

app = Flask(__name__)
app.config.from_object(Config)

BASE = Path(__file__).resolve().parent
PRODUCTS_FILE = BASE / "data" / "products.json"
BLOGS_FILE = BASE / "data" / "blogs.json"
DB_FILE = BASE / "database" / "app.db"


def load_json(path, key):
    try:
        return json.loads(path.read_text(encoding="utf-8")).get(key, [])
    except (OSError, json.JSONDecodeError):
        return []


def products():
    return load_json(PRODUCTS_FILE, "products")


def posts():
    return load_json(BLOGS_FILE, "posts")


def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def send_enquiry_email(name, phone, email, product, message):
    """Send a contact-form notification email when SMTP is configured."""

    recipient = app.config.get("NOTIFICATION_EMAIL", "").strip()
    username = app.config.get("SMTP_USERNAME", "").strip()
    password = app.config.get("SMTP_PASSWORD", "")

    if not recipient or not username or not password:
        app.logger.warning(
            "Email notification skipped: SMTP notification settings are not configured"
        )
        return False

    sender = app.config.get("SMTP_FROM", "").strip() or username

    subject = f"New Portfolio Enquiry - {name}"

    body = (
        "A new enquiry was submitted on the Madina portfolio website.\n\n"
        f"Name: {name}\n"
        f"Phone: {phone}\n"
        f"Email: {email or 'Not provided'}\n"
        f"Product: {product or 'Not specified'}\n\n"
        f"Message:\n{message}\n"
    )

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    if email:
        msg["Reply-To"] = email

    msg.set_content(body)

    try:
        with smtplib.SMTP(
            app.config.get("SMTP_HOST", "smtp.gmail.com"),
            app.config.get("SMTP_PORT", 587),
            timeout=15
        ) as smtp:

            smtp.starttls()
            smtp.login(username, password)
            smtp.send_message(msg)

            app.logger.info(
                "EMAIL SENT SUCCESSFULLY to %s",
                recipient
            )

        return True

    except (OSError, smtplib.SMTPException) as exc:
        app.logger.exception(
            "Could not send enquiry notification email: %s",
            exc
        )
        return False


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


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/products")
def product_list():
    items = products()
    categories = sorted(
        {p.get("category") for p in items if p.get("category")}
    )

    return render_template(
        "products.html",
        products=items,
        categories=categories
    )


@app.route("/products/<slug>")
def product_detail(slug):
    item = next(
        (p for p in products() if p.get("id") == slug),
        None
    )

    if not item:
        abort(404)

    return render_template(
        "product_detail.html",
        product=item
    )


@app.route("/wellness")
def wellness():
    return render_template("wellness.html")


@app.route("/blog")
def blog():
    return render_template(
        "blog.html",
        posts=posts(),
        categories=sorted(
            {p["category"] for p in posts() if p.get("category")}
        )
    )


@app.route("/blog/<slug>")
def blog_detail(slug):
    post = next(
        (p for p in posts() if p.get("slug") == slug),
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


@app.route("/faq")
def faq():
    return render_template("faq.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        product = request.form.get("product", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not phone or not message:
            return render_template(
                "contact.html",
                error="Please complete your name, phone and message."
            )

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
                error="We could not save your enquiry right now. Please try again or contact Madina on WhatsApp."
            )

        send_enquiry_email(
            name,
            phone,
            email,
            product,
            message
        )

        return render_template(
            "contact.html",
            success="Thank you! Your enquiry has been received. Madina will contact you soon."
        )

    return render_template("contact.html")


@app.route("/disclaimer")
def disclaimer():
    return render_template("disclaimer.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


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


@app.route("/robots.txt")
def robots():
    return (
        "User-agent: *\n"
        "Allow: /\n"
        "Sitemap: /sitemap.xml\n",
        200,
        {"Content-Type": "text/plain"}
    )


@app.errorhandler(404)
def not_found(e):
    return render_template(
        "base.html",
        title="Page Not Found",
        error_page=True
    ), 404


if __name__ == "__main__":
    app.run(debug=True)
