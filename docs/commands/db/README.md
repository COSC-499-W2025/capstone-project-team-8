
# Database & Backend Docker Commands

## Start/Stop Containers
- **Start all containers (detached):**
	```powershell
	docker-compose up -d
	```
- **Stop all containers:**
	```powershell
	docker-compose down
	```

## Build Backend Image
- **Build backend container:**
	```powershell
	docker-compose build backend
	```

## Database Management
- **Flush (reset) database:**
	```powershell
	docker-compose exec backend python manage.py flush --no-input
	```


## Migrations
**When to run migrations:** After you change any Django model (add, remove, or edit fields/classes in `models.py`).
- **Make migrations (generate migration files):**
	```powershell
	docker-compose exec backend python manage.py makemigrations
	```
- **Apply migrations (update DB schema):**
	```powershell
	docker-compose exec backend python manage.py migrate
	```

**Tip:** Always run both commands after any model change to keep your database in sync with your code.

## Testing
- **Run all unit tests (unittest discover):**
	```powershell
	docker-compose exec backend python -m unittest discover -s /app/tests -p "test_*.py" -v
	```
- **Run a specific test file:**
	```powershell
	docker-compose exec backend python manage.py test tests.test_project_summary
	```

## MySQL Shell (optional)
- **Open MySQL shell in DB container:**
	```powershell
	docker-compose exec db mysql -u root -p
	```