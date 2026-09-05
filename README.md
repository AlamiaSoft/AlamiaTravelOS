# AlamiaTravelOS - Odoo 19 Community Docker

A modular, enterprise-ready Docker setup for **Odoo 19.0 Community Edition** with PostgreSQL 17, optimized for local development and direct production deployment on **Hetzner Cloud** or **Oracle Cloud VPS**.

---

## 📁 Project Structure

```text
AlamiaTravelOS/
├── .env.example              # Environment variables template
├── .env                      # Local environment secrets (git-ignored)
├── .gitignore                # Git ignore rules
├── Dockerfile                # Custom Odoo 19 image with enterprise Python dependencies
├── docker-compose.yml        # Development Docker Compose stack
├── docker-compose.prod.yml   # Production Docker Compose stack
├── config/
│   ├── odoo.conf             # Odoo configuration (addons paths, proxy mode, limits)
│   └── nginx/
│       └── odoo.conf         # Production Nginx reverse proxy template (SSL + WebSockets)
├── custom_addons/            # In-house custom Odoo modules
├── third_party_addons/       # OCA and 3rd party community modules
├── scripts/
│   ├── manage.ps1            # Windows PowerShell management utility
│   ├── manage.sh             # Linux management helper
│   └── backup.sh             # PostgreSQL + filestore automated backup script
└── README.md                 # Complete documentation
```

---

## 🚀 Quick Start (Local Development)

### 1. Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
- Git.

### 2. Start the Stack

Using PowerShell (Windows):
```powershell
.\scripts\manage.ps1 up
```

Or using Docker Compose directly:
```bash
docker compose up -d
```

### 3. Access Odoo
Open your browser and navigate to:
👉 **[http://localhost:8069](http://localhost:8069)**

- **Master Password**: configured in `.env` (`admin` by default locally)
- Create your database and start developing!

---

## 🛠️ Management Commands

### Windows (PowerShell)
| Command | Action |
|---|---|
| `.\scripts\manage.ps1 up` | Start containers in background |
| `.\scripts\manage.ps1 down` | Stop and remove containers |
| `.\scripts\manage.ps1 restart` | Restart the Odoo web container |
| `.\scripts\manage.ps1 logs` | View live Odoo web logs |
| `.\scripts\manage.ps1 build` | Rebuild custom Docker image |
| `.\scripts\manage.ps1 scaffold <name>` | Generate boilerplate for a new custom addon |
| `.\scripts\manage.ps1 shell` | Open bash shell inside Odoo container |

### Linux / macOS / VPS
| Command | Action |
|---|---|
| `./scripts/manage.sh up` | Start local stack |
| `./scripts/manage.sh up:prod` | Start production stack |
| `./scripts/manage.sh down` | Stop containers |
| `./scripts/manage.sh logs` | View live logs |
| `./scripts/manage.sh scaffold <name>` | Scaffold a new module in `custom_addons` |

---

## 🧩 Developing Custom Addons

1. Generate a new module skeleton:
   ```powershell
   .\scripts\manage.ps1 scaffold travel_core
   ```
   This will create a new module under `custom_addons/travel_core`.
2. Edit your Python models, views, and security rules inside `custom_addons/travel_core`.
3. In Odoo Web UI:
   - Go to **Settings** > Activate **Developer Mode**.
   - Go to **Apps** > Click **Update Apps List**.
   - Search for your module and click **Install**.

---

## 🌐 Production Deployment Guide (Hetzner / Oracle Cloud VPS)

### 1. VPS Provisioning
- **Hetzner Cloud**: CX22 / CPX21 / CPX31 (Ubuntu 24.04 or Debian 12 recommended).
- **Oracle Cloud**: Always-Free Ampere A1 (ARM64) or E2.1.Micro / Standard x86 (Ubuntu 24.04).

### 2. Server Setup (Run on VPS)
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Docker & Docker Compose plugin
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER

# Log out and log back in to apply docker group
exit
```

### 3. Clone Repository & Configure Environment
```bash
git clone <your-repo-url> /opt/alamiatravelos
cd /opt/alamiatravelos

# Copy and configure production environment
cp .env.example .env
nano .env
```
> ⚠️ **Important in Production `.env`**:
> - Set strong passwords for `DB_PASSWORD` and `ODOO_ADMIN_PASSWORD`.
> - Set `DOMAIN=your-domain.com`.

### 4. Reverse Proxy & SSL (Nginx + Let's Encrypt)
Install Nginx and Certbot on the host:
```bash
sudo apt install -y nginx certbot python3-certbot-nginx

# Obtain SSL Certificate
sudo certbot --nginx -d travelos.yourcompany.com
```

Use the provided Nginx configuration template from `config/nginx/odoo.conf` and link it:
```bash
sudo cp config/nginx/odoo.conf /etc/nginx/sites-available/odoo.conf
# Replace 'travelos.example.com' with your actual domain in /etc/nginx/sites-available/odoo.conf
sudo ln -s /etc/nginx/sites-available/odoo.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5. Launch Production Stack
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

### 6. Automated Backup Setup (Cron Job)
Make the backup script executable and schedule a daily backup at 2:00 AM:
```bash
chmod +x scripts/backup.sh
crontab -e
```
Add the cron line:
```cron
0 2 * * * /opt/alamiatravelos/scripts/backup.sh >> /var/log/odoo_backup.log 2>&1
```

---

## 🔒 Security Best Practices
- Keep your master password `ODOO_ADMIN_PASSWORD` strictly private and strong.
- Do not expose port `5432` (PostgreSQL) publicly on the internet; keep it inside Docker internal network.
- Use `proxy_mode = True` in `odoo.conf` so client IP and SSL headers are accurately handled behind Nginx.
