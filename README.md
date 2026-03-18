# Burnette Phone Store - Django E-commerce Application

A full-featured Django e-commerce website for Burnette Phone Store in Tanzania, featuring user authentication, shopping cart, admin management, media uploads, search functionality, and more.

## Features

### Core Functionality
- **Product Management**: Display products with images/videos, prices, and descriptions
- **Search**: Real-time product search with Q objects
- **Request System**: Customer product requests with discount calculation, delivery options, and payment methods
- **Admin Panel**: Custom admin dashboard for managing products, updates, requests, and site settings
- **Media Handling**: Image and video uploads with lazy loading for performance
- **Responsive Design**: Bootstrap 5 with mobile-first approach, animations, and back-to-top button

### User Features
- **User Authentication**: Login, register, logout with Django auth and Google OAuth
- **Shopping Cart**: Add/remove products, update quantities, view cart summary
- **User Profiles**: Store additional user details (phone, address, etc.)
- **Dynamic Content**: Updates/news section with media support

### Technical Features
- **Caching**: LocMem cache with middleware for performance
- **Security**: CSRF protection, secure headers, input validation
- **SEO & Analytics**: Meta tags, Open Graph, Google Analytics placeholder, sitemap.xml, robots.txt
- **Email Notifications**: Console backend for request submissions, notifications to admins
- **Database**: MySQL with models for Product, Update, Request, Cart, SiteSettings, UserProfile, etc.

### Admin Features
- **Dashboard**: Overview of products, updates, requests with status filtering
- **CRUD Operations**: Full create/read/update/delete for all models
- **User Management**: Manage registered users and their profiles
- **Cart Management**: View and manage user carts
- **Settings Management**: Site-wide settings like logo, theme, contact info

## Tech Stack

- **Backend**: Django 6.0.3
- **Frontend**: Bootstrap 5.3.2, Font Awesome, Custom CSS
- **Database**: MySQL
- **Media**: Django file storage with Pillow for image handling
- **Environment**: Python 3.13, Virtual environment

## Installation & Setup

1. **Clone/Setup Workspace**:
   ```bash
   git clone <repo-url>
   cd burnette-phone-store
   ```

2. **Create Virtual Environment**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup**:
   - Ensure MySQL is running
   - Update `burnette_store/settings.py` with your MySQL credentials
   - Run migrations:
     ```bash
     python manage.py makemigrations
     python manage.py migrate
     ```

5. **Populate Data** (optional):
   ```bash
   python populate.py
   ```

6. **Run Server**:
   ```bash
   python manage.py runserver
   ```
   Visit `http://127.0.0.1:8000`

## Usage

### Public Access
- Browse products, search, view updates
- Submit product requests with delivery/payment options
- Register/login to access cart features

### User Features
- Login/Register via navbar links
- Add products to cart, view/update cart
- Proceed to checkout (integrates with request form)

### Admin Access
- Visit `/admin/login/` or tap logo 5 times on home page
- Username: `hudhaifa`, Password: `123`
- Manage all content, view requests, update settings

## Project Structure

```
burnette-phone-store/
├── burnette_store/          # Django project settings
│   ├── settings.py         # App configs, DB, caching, security
│   ├── urls.py             # Main URL routing
│   └── wsgi.py
├── store/                   # Main app
│   ├── models.py           # Product, Cart, Request, etc.
│   ├── views.py            # Home, products, auth, cart views
│   ├── urls.py             # App URL patterns
│   ├── tests.py            # Unit tests
│   └── admin.py            # Admin configurations
├── templates/               # HTML templates
│   ├── base.html           # Base template with navbar/footer
│   ├── home.html           # Homepage with hero/video
│   ├── products.html       # Product grid with search
│   ├── login.html          # User login
│   ├── register.html       # User registration
│   ├── cart.html           # Shopping cart
│   └── sitemap.xml         # SEO sitemap
├── static/                  # CSS, JS, images
│   ├── css/styles.css      # Custom styles/animations
│   ├── js/app.js           # JavaScript functionality
│   └── robots.txt          # SEO robots file
├── media/                   # Uploaded files
└── README.md
```

## Testing

Run tests with:
```bash
python manage.py test store
```

Includes tests for models (Product, Cart) and views (home, products, cart access control).

## Deployment Notes

- **Static Files**: Use `python manage.py collectstatic` for production
- **Media Files**: Configure cloud storage (e.g., AWS S3) for uploads
- **Security**: Set `DEBUG=False`, use HTTPS, configure allowed hosts
- **Performance**: Enable CDN for static/media files, database indexing
- **Analytics**: Replace `GA_MEASUREMENT_ID` with actual Google Analytics ID

## Google OAuth Setup

To enable Google login:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials (Client ID and Secret)
5. Add authorized redirect URIs: `http://127.0.0.1:8000/accounts/google/login/callback/`
6. In Django admin, go to Social Applications and add:
   - Provider: Google
   - Name: Google
   - Client ID: Your Client ID
   - Secret Key: Your Secret
   - Sites: Add your site (e.g., example.com)

## Email Notifications

The system sends email notifications to `cleysir54@gmail.com` and `hudhaifabashiru@gmail.com` for:
- New user registrations
- New cart items added
- New product requests submitted

Configure `EMAIL_BACKEND` in settings for production email sending.

## Admin Credentials

- **Username**: `hudhaifa`
- **Password**: `123`
- **Email**: `hudhaifabashiru@gmail.com`
- **Phone**: `0626905105`

## License

This project is for educational/commercial use by Burnette Phone Store.
