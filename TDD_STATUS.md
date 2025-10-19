# Test-Driven Development (TDD) - MySQL Database Tests

## Current Status: Testing MySQL Connection ✅

Simple tests to verify MySQL database is working with Django.

---

## Tests Written

✅ **test_create_user_in_database** - Creates a user and saves to MySQL  
✅ **test_create_multiple_users** - Creates multiple users and verifies count

---

## What These Tests Do

1. Create users with Django's User model
2. Save them to MySQL database (in Docker)
3. Verify they were saved (check for database ID)
4. Retrieve them from database
5. Count total users

---

## Run the Tests

```bash
# Make sure Docker is running
docker compose up -d

# Run tests
docker compose exec backend python manage.py test ../../tests
```

**Expected Result:** Tests should PASS ✅ (User model already exists)

---

## Why This Matters

These tests verify:
- ✅ MySQL connection works
- ✅ Django can talk to MySQL
- ✅ Data is being saved to database
- ✅ Database queries work
- ✅ Your setup is correct

---

## Next Steps

After these pass, we can:
1. Create custom models (Artifact, Project, etc.)
2. Add TDD tests for those models
3. Build out the application

Ready to commit! 🚀
