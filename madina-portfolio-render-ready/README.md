# Madina Khatoon — Premium Flask Portfolio

A personal-brand nutrition & wellness portfolio built with Flask, SQLite, HTML/CSS/JavaScript and Bootstrap 5.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

## Maintain product data

Edit `data/products.json`. Product pages and the catalogue load this JSON dynamically; products are not stored in SQLite.

The supplied product FAQ document was used as the source for the product FAQ content. Product information is not invented. Fields without source support are left empty.

## Maintain blog data

Edit `data/blogs.json` to add, edit or remove posts.

## WhatsApp

Change the WhatsApp number once in `config.py`, or set the `MADINA_WHATSAPP` environment variable. The Flask app reads this one configuration value and templates never contain the number.

The current value is a placeholder and MUST be replaced before deployment.

## Portrait and product images

Place images in `static/images/`.

For Madina's portrait, replace the placeholder in `templates/index.html` / `templates/about.html` with an image when ready.

For a product, set for example:

```json
"image": "images/product-name.jpg"
```

The product templates already handle empty image fields with an elegant placeholder.

## Enquiries

Contact submissions are stored in `database/app.db` in the `enquiries` table:
- id
- name
- phone
- email
- product
- message
- created_at
- status (`new`, `contacted`, `resolved`)

Products and blogs remain JSON files.

## Deployment notes

- Set a strong `MADINA_SECRET_KEY`.
- Set the real `MADINA_WHATSAPP`.
- Use HTTPS.
- Protect the SQLite file and server environment.
- Review privacy/data-retention requirements before collecting personal information publicly.
- Replace the portrait placeholder with Madina's own photo.
- Add real social URLs in `config.py`, or set `MADINA_INSTAGRAM`, `MADINA_YOUTUBE` and `MADINA_LINKEDIN` environment variables. For the portrait, set `PORTRAIT_IMAGE` in `config.py` or `MADINA_PORTRAIT` to a path such as `images/madina.jpg`.


## Hinglish / English mode

The site now includes a native three-way language switcher: **Hinglish (Original)**, **English**, and **Hindi (हिन्दी)**. The switcher uses local JSON catalogues in `static/translations/` and does not use Google Translate or any third-party translation overlay. The selected language is stored in browser `localStorage`, and the original supplied content remains the source data.


## Product images

Add product images to `static/images/products/`. The image filenames are intentionally short and fixed. For example, `fm1.jpg` is Formula 1 Nutritional Shake Mix. The complete mapping is in `static/images/products/README.txt`. You do not need to change HTML; just replace/add the matching JPG file.

## Language switch

The product information remains stored in the supplied JSON data. The header provides a native Hinglish / English / Hindi switcher. No external translation widget is used.

## Contact form email notifications

The contact form saves every enquiry to SQLite and can also send an email notification immediately after a successful submission. No email password is stored in the project.

For Gmail, use a Gmail App Password (not your normal Gmail password) and set these environment variables before starting Flask:

```bash
export MADINA_SMTP_HOST="smtp.gmail.com"
export MADINA_SMTP_PORT="587"
export MADINA_SMTP_USERNAME="your-gmail@gmail.com"
export MADINA_SMTP_PASSWORD="your-16-character-app-password"
export MADINA_NOTIFICATION_EMAIL="your-gmail@gmail.com"
export MADINA_SMTP_FROM="your-gmail@gmail.com"
python3 app.py
```

If SMTP variables are not configured, the form still works and enquiries are saved in `database/app.db`; only the email notification is skipped. The site never exposes SMTP credentials to visitors.
