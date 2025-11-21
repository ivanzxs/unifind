# Campus Lost & Found System

A web-based portal where students can post lost or found items, browse, claim, and track items inside the school campus. The system features a claim verification system, anonymous posting, campus map integration, and a reputation points system.

## ✨ Features

- **User Authentication**: Register/login with school email and student ID
- **Report Lost/Found Items**: Post items with photos, descriptions, location, and category
- **Claim Verification System**: Finders set verification questions that claimants must answer
- **Anonymous Posting**: Option to post items anonymously
- **Campus Map Integration**: Pin exact locations using Leaflet.js interactive maps
- **Reputation Points System**: Earn points for returning items (displayed in profile)
- **Notifications**: Real-time notifications for claims and item matches
- **Admin Moderation**: Staff can approve/reject posts and manage users
- **Auto-Archive**: Items not claimed after 30 days are automatically archived
- **Browse & Search**: Filter items by type, category, and search keywords

## 🎨 Design

- **Color Scheme**: Strict use of Yellow (#ecb80d) and Vivid Azure (#08598b)
- **UI Framework**: Pure CSS with Django Templates (no Bootstrap)
- **Modern & Clean**: Student-friendly interface focused on trust and simplicity

## 🛠 Tech Stack

- **Backend**: Django 5.2.7
- **Frontend**: Django Templates + Pure CSS + JavaScript
- **Database**: SQLite (development) / PostgreSQL (production)
- **Maps**: Leaflet.js
- **Charts**: Chart.js (for admin reports)
- **API**: Django Rest Framework (optional)

## 📦 Installation

### Prerequisites

- Python 3.8+
- pip

### Setup Steps

1. **Navigate to project directory**:
   ```powershell
   cd "c:\Users\nazrey builders corp\Desktop\university find"
   ```

2. **Activate virtual environment**:
   ```powershell
   .\.venv\Scripts\Activate
   ```

3. **Run migrations** (if not already done):
   ```powershell
   python manage.py migrate
   ```

4. **Create a superuser** (for admin access):
   ```powershell
   python manage.py createsuperuser
   ```
   Follow the prompts to set username, email, student_id, and password.

5. **Run the development server**:
   ```powershell
   python manage.py runserver
   ```

6. **Access the application**:
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## 📁 Project Structure

```
campus_lostfound/          # Main project settings
├── settings.py            # Django configuration
├── urls.py                # Root URL routing
└── wsgi.py                # WSGI application

users/                     # User authentication & profiles
├── models.py              # Custom User model with student_id & reputation
├── forms.py               # Registration & login forms
├── views.py               # Auth views
└── admin.py               # User admin configuration

items/                     # Lost & found items
├── models.py              # Item model (type, category, location, etc.)
├── forms.py               # Item posting forms
├── views.py               # Item CRUD & browsing
└── admin.py               # Item admin

claims/                    # Claim system
├── models.py              # Claim model with verification
├── forms.py               # Claim submission form
├── views.py               # Claim & review logic
└── admin.py               # Claims admin

notifications/             # Notification system
├── models.py              # Notification model
├── views.py               # Notification views
└── admin.py               # Notifications admin

dashboard/                 # Main dashboard
├── views.py               # Landing & student dashboard
└── urls.py                # Dashboard routing

templates/                 # HTML templates
├── base.html              # Base template with navbar
├── users/                 # Auth templates
├── items/                 # Item templates
├── claims/                # Claim templates
└── dashboard/             # Dashboard templates

static/                    # Static files
└── css/
    └── style.css          # Main stylesheet

media/                     # User uploads (item images)
```

## 🗄 Database Models

### User
- `student_id` (unique)
- `reputation_points` (integer, default 0)
- Inherits from Django's AbstractUser

### Item
- `user` (ForeignKey to User)
- `type` (lost/found)
- `category` (ID, Gadget, Book, Clothing, Keys, Wallet, Others)
- `description` (text)
- `image` (optional)
- `location_text` (string)
- `location_lat`, `location_lng` (coordinates)
- `verification_question` (for found items)
- `is_anonymous` (boolean)
- `status` (pending/claimed/unclaimed/archived)
- `created_at` (timestamp)

### Claim
- `item` (ForeignKey to Item)
- `claimant` (ForeignKey to User)
- `answer_text` (verification answer)
- `status` (pending/approved/rejected)
- `created_at` (timestamp)

### Notification
- `user` (ForeignKey to User)
- `message` (text)
- `is_read` (boolean)
- `created_at` (timestamp)

## 🚀 Usage

### For Students

1. **Register**: Create an account with your school email and student ID
2. **Report Lost Item**: Post details, photo, and last seen location
3. **Report Found Item**: Post details, photo, location found, and set a verification question
4. **Browse Items**: Search and filter lost/found items
5. **Claim Item**: Answer the verification question to claim a found item
6. **Dashboard**: View your items, claims, and notifications
7. **Earn Points**: Get 10 reputation points for each successful return

### For Admin/Staff

1. **Login to Admin**: http://127.0.0.1:8000/admin/
2. **Moderate Posts**: Approve or reject item posts
3. **Manage Users**: View, edit, or ban user accounts
4. **Review Claims**: Monitor claim activity
5. **Generate Reports**: View statistics on lost/found/claimed items

## 🔧 Configuration

### Email Settings (for notifications)
Edit `campus_lostfound/settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

### Map Default Location
Edit `templates/items/post_item.html` line 113:
```javascript
const map = L.map('map').setView([YOUR_LAT, YOUR_LNG], 15);
```

## 📝 TODO / Future Enhancements

- [ ] Implement auto-archive scheduled task (Django Celery)
- [ ] Add Chart.js reports for admin dashboard
- [ ] Email notifications for claims
- [ ] SMS notifications integration
- [ ] Mobile app (React Native)
- [ ] Advanced search with filters
- [ ] Item matching algorithm (suggest matches)
- [ ] Export reports to PDF/Excel
- [ ] Multi-language support

## 🤝 Contributing

This is a school project. For improvements or bug reports, please contact the development team.

## 📄 License

This project is for educational purposes.

## 👥 Credits

Developed for campus lost and found management.

---

**Color Palette**:
- Primary: #08598b (Vivid Azure)
- Secondary: #ecb80d (Yellow)
