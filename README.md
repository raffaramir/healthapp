# HEALTHAPP â€” Smart Healthcare Home Services Platform

A full-stack Django web application connecting **patients**, **doctors**, **lab technicians**, and **pharmacists** for at-home healthcare services, real-time consultations, and medication management.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 5.0 + Django REST Framework |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Real-time | Django Channels + WebSocket |
| Auth | Custom User model + JWT (DRF SimpleJWT) |
| UI | Django Templates + Custom CSS (Glassmorphism) |
| Async server | Daphne (ASGI) |

---

## Project Structure

```
healthapp/
â”œâ”€â”€ healthapp/          # Project config (settings, urls, asgi)
â”œâ”€â”€ apps/
â”‚   â”œâ”€â”€ accounts/       # Custom User model, auth, roles, signals
â”‚   â”œâ”€â”€ patients/       # PatientProfile, MedicationReminder, MedicalRecord
â”‚   â”œâ”€â”€ doctors/        # DoctorProfile
â”‚   â”œâ”€â”€ labs/           # LabProfile
â”‚   â”œâ”€â”€ pharmacy/       # PharmacistProfile, PharmacyProduct
â”‚   â”œâ”€â”€ services/       # ServiceRequest, Appointment, Review
â”‚   â”œâ”€â”€ chat/           # Conversation, ChatMessage, WebSocket consumer
â”‚   â”œâ”€â”€ notifications/  # Notification + medication reminder command
â”‚   â””â”€â”€ dashboard/      # Role-aware dashboards + admin panel
â”œâ”€â”€ templates/          # Django HTML templates (modern UI)
â”œâ”€â”€ static/
â”‚   â”œâ”€â”€ css/main.css    # Glassmorphism design system
â”‚   â””â”€â”€ js/main.js      # Theme toggle, WS chat, notifications
â”œâ”€â”€ media/              # User uploads (profiles, prescriptions, records)
â””â”€â”€ preview/            # Static HTML previews (no Django needed)
```

---

## Quick Start

### 1 â€” Clone / navigate to the project
```bash
cd "c:/Users/Admin/Desktop/projet santأ©/healthapp"
```

### 2 â€” Create and activate a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3 â€” Install dependencies
```bash
pip install -r requirements.txt
```

### 4 â€” Run database migrations
```bash
python manage.py migrate
```

### 5 â€” Seed sample data
```bash
python manage.py seed_data
```
This creates:
- 1 admin account
- 5 doctors, 2 labs, 2 pharmacists, 5 patients
- 10 service requests in various states
- Sample chat conversations
- Medication reminders

### 6 â€” Collect static files (optional for dev)
```bash
python manage.py collectstatic --noinput
```

### 7 â€” Run the development server
```bash
# Standard Django (HTTP only)
python manage.py runserver

# With WebSocket support (recommended)
daphne -b 0.0.0.0 -p 8000 healthapp.asgi:application
```

Open **http://127.0.0.1:8000** in your browser.

---

## Demo Accounts

| Role | Email | Password |
|---|---|---|
| Admin | admin@healthapp.local | Admin1234! |
| Patient | patient1@healthapp.local | Patient1234! |
| Doctor | dr.smith@healthapp.local | Doctor1234! |
| Lab Tech | lab.central@healthapp.local | Lab1234! |
| Pharmacist | pharma.medplus@healthapp.local | Pharma1234! |

---

## User Roles & Approval Flow

```
Register â†’ Pending approval â†’ Admin reviews â†’ Approved â†’ Full access
                                           â””â†’ Rejected â†’ Account locked
```

All non-admin accounts must be **approved by an admin** before they can access services.  
Admin can approve/reject from: **Dashboard â†’ Administration â†’ Users**

---

## Key Features

### Patients
- Request **doctor at home**, **lab at home**, **pharmacy order**, or **online consultation**
- Track request status in real time
- Upload / view **medical records**
- **Medication reminder** system with scheduled notifications
- Chat with doctors and pharmacists

### Doctors / Lab Techs / Pharmacists
- See incoming request queue
- Accept, start, and complete requests
- Add notes, estimated/final cost
- Chat with patients

### Admin
- Approve or reject any user account
- View analytics dashboard (users, requests, daily activity chart)
- Browse all service requests with status/type filters
- Read full system activity logs
- Access Django's built-in admin at `/admin/`

### Chat
- Real-time WebSocket messaging (via Django Channels)
- File and image attachments
- Unread message counters in the navbar

### Notifications
- In-app notification system (navbar bell icon)
- Automatic alerts on approval, request updates, messages
- Medication dose reminders via management command

---

## API Endpoints

| Endpoint | Description |
|---|---|
| `POST /api/v1/accounts/token/` | Obtain JWT access + refresh tokens |
| `POST /api/v1/accounts/token/refresh/` | Refresh JWT token |
| `GET /api/v1/accounts/me/` | Current user profile |
| `GET /api/v1/accounts/users/` | List users (admin only) |
| `POST /api/v1/accounts/approve/<id>/` | Approve user (admin only) |
| `POST /api/v1/accounts/reject/<id>/` | Reject user (admin only) |
| `GET /api/v1/services/requests/` | List service requests |
| `POST /api/v1/services/requests/` | Create service request |
| `POST /api/v1/services/requests/<id>/accept/` | Accept request (provider) |
| `GET /api/v1/chat/conversations/` | List conversations |
| `GET /api/v1/chat/messages/?conversation=<id>` | Get messages |
| `GET /api/v1/notifications/` | List notifications |

---

## WebSocket

Chat connects via:
```
ws://localhost:8000/ws/chat/<conversation_id>/
```
Handled by `apps/chat/consumers.py` â€” sends/receives JSON `{ body: "..." }`.

---

## Medication Reminder Dispatcher

Run this command on a schedule (cron / Task Scheduler) to fire reminders:
```bash
python manage.py dispatch_medication_reminders
```

Windows Task Scheduler example (every 5 minutes):
```
Program: C:\path\to\venv\Scripts\python.exe
Arguments: manage.py dispatch_medication_reminders
Start in: C:\Users\Admin\Desktop\projet santأ©\healthapp
```

---

## Mobile / PWA

HEALTHAPP installs as a **Progressive Web App** on Android, iOS, Windows, and macOS — no app store, no separate codebase.

**Endpoints** (served by Django):
- `/manifest.webmanifest` — app metadata, name, icons, theme color
- `/sw.js` — service worker (offline shell, asset caching, push hooks)
- `/offline/` — offline fallback page

**Install on a phone:**
1. Open the site over **HTTPS** (required by browsers — `localhost` also works for testing).
2. **Android (Chrome / Edge):** menu → *Install app* / *Add to Home screen*.
3. **iOS (Safari):** Share button → *Add to Home Screen*.
4. **Desktop (Chrome / Edge):** install icon in the URL bar.

**Regenerate icons** if you tweak the brand colors:
```bash
.venv\Scripts\python.exe scripts/gen_pwa_icons.py
```

> The service worker caches HTML (network-first), static assets (cache-first), and skips `/api/`, `/admin/`, and `/ws/`. Bump `VERSION` in [`templates/pwa/sw.js`](templates/pwa/sw.js) to force clients to refresh after a deploy.

---

## Production Checklist

- [ ] Set `DJANGO_SECRET_KEY` environment variable (long random string)
- [ ] Set `DJANGO_DEBUG=False`
- [ ] Set `USE_POSTGRES=True` and configure `DB_*` environment variables
- [ ] Set `ALLOWED_HOSTS` to your domain
- [ ] Configure Redis for channel layers (`CHANNEL_LAYERS` in settings)
- [ ] Configure real email backend (`EMAIL_BACKEND`)
- [ ] Run `collectstatic` and serve `/staticfiles/` via Nginx
- [ ] Use Gunicorn + Daphne behind Nginx for HTTP + WebSocket
- [ ] Set up SSL / HTTPS

---

## Environment Variables

```env
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
USE_POSTGRES=True
DB_NAME=healthapp
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
```

---

## UI Design System

| Token | Value |
|---|---|
| Primary | `#22C55E (bright green) |
| Secondary | `#16A34A (forest green) |
| Accent | `#10B981 (emerald green) |
| Background | `#060F0A` (dark navy) |
| Font | Inter (Google Fonts) |

Dark mode is the default. Toggle with the ًںŒ“ button in the topbar. Preference is saved to `localStorage`.

---

## License

MIT â€” built for educational and demonstration purposes.
