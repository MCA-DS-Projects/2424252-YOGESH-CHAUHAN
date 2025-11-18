# How to Remove Mock/Seed Data from Database

## Problem Identified

Mock/seed data is appearing in the teacher dashboard, specifically these courses:
- **Introduction to Machine Learning**
- **Data Science Fundamentals**
- **Advanced Python Programming**
- **Web Development with React**

These courses were created by the `seed_sample_data.py` script and need to be removed.

## Quick Solution

### Step 1: Identify Mock Data

First, check what mock data exists in your database:

```bash
python backend/scripts/identify_mock_data.py
```

This will show you:
- All seed users (teacher01@datams.edu, student01@datams.edu, etc.)
- All seed courses
- Related enrollments, assignments, and submissions
- Whether you have any real data that should be preserved

### Step 2: Preview Cleanup (Dry Run)

See what will be deleted without actually deleting:

```bash
python backend/scripts/cleanup_seed_data.py
```

This runs in **dry run mode** and shows you exactly what will be removed.

### Step 3: Clean Up Mock Data

When you're ready to delete the mock data:

```bash
python backend/scripts/cleanup_seed_data.py --confirm
```

You'll be asked to type `DELETE` to confirm. This will remove:
- ✅ All seed users
- ✅ All seed courses
- ✅ All related enrollments
- ✅ All related assignments
- ✅ All related submissions
- ✅ All related materials

### Step 4: Verify Cleanup

After cleanup, verify the data is gone:

```bash
python backend/scripts/identify_mock_data.py
```

You should see: "✅ No seed/mock data found in database!"

## Detailed Explanation

### What is Seed Data?

Seed data is test/sample data created by the `seed_sample_data.py` script for development and testing. It includes:

**Users:**
- `teacher01@datams.edu` - Dr. Seema Singh
- `teacher02@datams.edu` - Prof. Anil Mehta
- `student01@datams.edu` - Ravi Kumar
- `student02@datams.edu` - Priya Sharma
- `student03@datams.edu` - Aman Verma
- `superadmin@datams.edu` - Super Admin

**Courses:**
- Introduction to Machine Learning (by teacher01)
- Data Science Fundamentals (by teacher01)
- Advanced Python Programming (by teacher02)
- Web Development with React (by teacher02)

### Why is it Appearing?

The seed script was run manually at some point, which inserted this data into your MongoDB database. The teacher dashboard correctly loads data from the database, so it's showing these seed courses.

### Is This a Bug?

**No!** The teacher dashboard is working correctly. It's loading real data from the database. The issue is that seed/test data was inserted into the production database.

### How to Prevent This?

1. **Never run seed scripts on production database**
2. **Use separate databases for development and production**
3. **Add environment checks to seed scripts**

## Alternative: Manual Cleanup

If you prefer to manually remove specific courses:

### Using MongoDB Shell

```bash
# Connect to MongoDB
mongosh mongodb://localhost:27017/edunexa_lms

# Find seed courses
db.courses.find({title: {$in: [
  "Introduction to Machine Learning",
  "Data Science Fundamentals",
  "Advanced Python Programming",
  "Web Development with React"
]}})

# Delete specific course (replace with actual course ID)
db.courses.deleteOne({_id: ObjectId("course_id_here")})

# Delete all seed courses
db.courses.deleteMany({title: {$in: [
  "Introduction to Machine Learning",
  "Data Science Fundamentals",
  "Advanced Python Programming",
  "Web Development with React"
]}})
```

### Using Python Script

```python
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/edunexa_lms')
db = client.edunexa_lms

# Delete seed courses
result = db.courses.delete_many({
    'title': {
        '$in': [
            'Introduction to Machine Learning',
            'Data Science Fundamentals',
            'Advanced Python Programming',
            'Web Development with React'
        ]
    }
})

print(f"Deleted {result.deleted_count} courses")
```

## Safety Checks

### Before Cleanup

1. **Backup your database:**
   ```bash
   mongodump --db edunexa_lms --out backup_$(date +%Y%m%d)
   ```

2. **Check for real data:**
   ```bash
   python backend/scripts/identify_mock_data.py
   ```
   
   Look for the "Real Data Check" section to see if you have any real users/courses.

3. **Review what will be deleted:**
   ```bash
   python backend/scripts/cleanup_seed_data.py
   ```
   
   This shows exactly what will be removed.

### After Cleanup

1. **Verify cleanup:**
   ```bash
   python backend/scripts/identify_mock_data.py
   ```

2. **Check teacher dashboard:**
   - Login as a real teacher
   - Dashboard should show only real courses
   - No "Introduction to Machine Learning" or similar seed courses

3. **Test creating a new course:**
   - Create a test course
   - Verify it appears in dashboard
   - Delete the test course

## Troubleshooting

### Issue: Script says "No seed data found" but I still see mock courses

**Solution:**
The courses might have different titles or be created by different teachers. Check manually:

```bash
# List all courses
mongosh mongodb://localhost:27017/edunexa_lms
db.courses.find({}, {title: 1, teacher_id: 1})

# List all teachers
db.users.find({role: 'teacher'}, {name: 1, email: 1})
```

### Issue: I have real data mixed with seed data

**Solution:**
1. Don't use the automated cleanup script
2. Manually identify seed courses by title or teacher email
3. Delete only those specific courses
4. Keep real user data intact

### Issue: Cleanup script fails with error

**Solution:**
1. Check MongoDB is running
2. Check connection string in `.env` file
3. Check you have write permissions
4. Review error message and stack trace

### Issue: After cleanup, dashboard is empty

**Solution:**
This is expected if you only had seed data. Now:
1. Create a real teacher account
2. Login as teacher
3. Create real courses
4. Dashboard will show your real courses

## Best Practices

### For Development

1. **Use separate databases:**
   ```
   Development: mongodb://localhost:27017/edunexa_lms_dev
   Production: mongodb://localhost:27017/edunexa_lms
   ```

2. **Add environment checks to seed scripts:**
   ```python
   if os.getenv('ENVIRONMENT') == 'production':
       print("❌ Cannot run seed script in production!")
       sys.exit(1)
   ```

3. **Use Docker for isolated environments:**
   ```yaml
   services:
     mongodb-dev:
       image: mongo:latest
       ports:
         - "27017:27017"
   ```

### For Production

1. **Never run seed scripts**
2. **Use real user registration**
3. **Create courses through UI**
4. **Regular database backups**
5. **Monitor for test data**

## Summary

**The teacher dashboard is working correctly!** It's showing real data from the database. The issue is that seed/test data was inserted into the database.

**Solution:**
1. Run `python backend/scripts/identify_mock_data.py` to see what's there
2. Run `python backend/scripts/cleanup_seed_data.py --confirm` to remove it
3. Verify with `python backend/scripts/identify_mock_data.py` again

**Prevention:**
- Don't run seed scripts on production database
- Use separate dev/prod databases
- Create real data through the UI

---

**Need Help?**
- Check the scripts in `backend/scripts/`
- Review MongoDB data directly with `mongosh`
- Contact system administrator
