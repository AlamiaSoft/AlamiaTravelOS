<#
.SYNOPSIS
    Management helper script for AlamiaTravelOS (Odoo 19 Community Docker) on Windows.

.EXAMPLE
    .\scripts\manage.ps1 up
    .\scripts\manage.ps1 down
    .\scripts\manage.ps1 restart
    .\scripts\manage.ps1 logs
    .\scripts\manage.ps1 scaffold travel_core
#>

param (
    [Parameter(Position=0, Mandatory=$true)]
    [ValidateSet("up", "down", "restart", "logs", "build", "ps", "shell", "scaffold", "update-module", "help")]
    [string]$Command,

    [Parameter(Position=1, Mandatory=$false)]
    [string]$Arg1
)

$ErrorActionPreference = "Stop"

switch ($Command) {
    "up" {
        Write-Host "Starting AlamiaTravelOS containers..." -ForegroundColor Green
        docker compose up -d
        Write-Host "Odoo 19 is running at: http://localhost:8069" -ForegroundColor Cyan
    }
    "down" {
        Write-Host "Stopping AlamiaTravelOS containers..." -ForegroundColor Yellow
        docker compose down
    }
    "restart" {
        Write-Host "Restarting Odoo service..." -ForegroundColor Yellow
        docker compose restart web
    }
    "logs" {
        if ($Arg1) {
            docker compose logs -f $Arg1
        } else {
            docker compose logs -f web
        }
    }
    "build" {
        Write-Host "Rebuilding Odoo custom image..." -ForegroundColor Green
        docker compose build --no-cache
    }
    "ps" {
        docker compose ps
    }
    "shell" {
        Write-Host "Opening shell inside Odoo container..." -ForegroundColor Green
        docker compose exec -it web bash
    }
    "scaffold" {
        if (-not $Arg1) {
            Write-Error "Please specify module name. Example: .\scripts\manage.ps1 scaffold travel_management"
        }
        Write-Host "Scaffolding new module: $Arg1 in custom_addons..." -ForegroundColor Green
        docker compose exec -u root web odoo scaffold $Arg1 /mnt/extra-addons
        Write-Host "Module created at custom_addons/$Arg1" -ForegroundColor Cyan
    }
    "update-module" {
        if (-not $Arg1) {
            Write-Error "Please specify module name. Example: .\scripts\manage.ps1 update-module travel_management"
        }
        Write-Host "Updating module: $Arg1..." -ForegroundColor Green
        docker compose exec web odoo -u $Arg1 --stop-after-init
    }
    "help" {
        Write-Host "Available commands:" -ForegroundColor Cyan
        Write-Host "  up             - Start docker containers in background"
        Write-Host "  down           - Stop and remove containers"
        Write-Host "  restart        - Restart the Odoo web container"
        Write-Host "  logs [service] - View live logs (default: web)"
        Write-Host "  build          - Rebuild Docker image"
        Write-Host "  ps             - Show container status"
        Write-Host "  shell          - Open bash shell in Odoo container"
        Write-Host "  scaffold <name>- Create new Odoo addon boilerplate"
        Write-Host "  update-module  - Upgrade a specific module in database"
    }
}
