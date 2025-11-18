# Test User Generation - Quick Reference Card

## 🚀 Quick Start (3 Commands)

```bash
# 1. Generate 100 students + 10 teachers
python backend/scripts/generate_test_users.py

# 2. View generated users
python backend/scripts/view_test_users.py

# 3. Start backend to test API
cd backend && python run.py
```

---

## 📊 What Gets Generated

| Type | Count | Email Domain | ID Format | Age Range |
|------|-------|--------------|-----------|-----------|
| Students | 100 | @student.edu | STU20241234 | 18-25 |
| Teachers | 10 | @faculty.edu | FAC12345 | 30-65 |

---

## 🔑 Default Passwords

- **Students:** `Student@123`
- **Teachers:** `Teacher@123`

---

## 📝 Student Fields

```
✅ name, email, roll_number
✅ department, year, semester
✅ phone, date_of_birth, profile_pic
✅ address (street, city, state, zip)
✅ emergency_contact (name, relationship, phone)
✅ enrolled_courses, total_points, badges
```

---

## 👨‍🏫 Teacher Fields

```
✅ name, email, employee_id
✅ department, designation, specializations
✅ phone, date_of_birth, profile_pic
✅ office (building, room, hours)
✅ education (degree, university, year)
✅ years_of_experience, courses_created
```

---

## 🖥️ Command-Line Tools

```bash
# View first 10 students
python backend/scripts/view_test_users.py students

# View first 10 teachers
python backend/scripts/view_test_users.py teachers

# View statistics
python backend/scripts/view_test_users.py stats

# View specific student
python backend/scripts/view_test_users.py student john.smith@student.edu

# Interactive menu
python backend/scripts/view_test_users.py
```

---

## 🌐 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/test-users/students` | GET | Get all students (paginated) |
| `/api/test-users/teachers` | GET | Get all teachers (paginated) |
| `/api/test-users/student/<id>` | GET | Get specific student |
| `/api/test-users/teacher/<id>` | GET | Get specific teacher |
| `/api/test-users/stats` | GET | Get statistics |
| `/api/test-users/search?q=john` | GET | Search users |
| `/api/test-users/departments` | GET | Get all departments |
| `/api/test-users/sample` | GET | Get sample users |

---

## 🧪 Quick API Test

```bash
# 1. Login (get token)
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@edunexa.com","password":"admin123"}'

# 2. Get students
curl -X GET http://localhost:5000/api/test-users/students?limit=5 \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. Get statistics
curl -X GET http://localhost:5000/api/test-users/stats \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 💾 MongoDB Queries

```javascript
// Count students
db.users.count({ role: "student", email: { $regex: "@student.edu$" } })

// Count teachers
db.users.count({ role: "teacher", email: { $regex: "@faculty.edu$" } })

// View sample students
db.users.find({ role: "student" }).limit(5)

// View sample teachers
db.users.find({ role: "teacher" }).limit(5)

// Students by department
db.users.aggregate([
  { $match: { role: "student" } },
  { $group: { _id: "$department", count: { $sum: 1 } } }
])
```

---

## 🎓 Viva Demo Script (5 Minutes)

### 1. Show Generation (1 min)
```bash
python backend/scripts/generate_test_users.py
```
**Say:** "This generates 100 students and 10 teachers with unique IDs and realistic data."

### 2. View in Database (1 min)
```bash
mongo edunexa_lms --eval "db.users.find({role:'student'}).limit(3)"
```
**Say:** "All data is stored directly in MongoDB, no static files."

### 3. View via Script (1 min)
```bash
python backend/scripts/view_test_users.py students
```
**Say:** "Command-line tools provide easy viewing and statistics."

### 4. Test API (1.5 min)
```bash
curl -X GET http://localhost:5000/api/test-users/stats \
  -H "Authorization: Bearer TOKEN"
```
**Say:** "RESTful API endpoints allow programmatic access with pagination and filtering."

### 5. Show Validation (0.5 min)
```bash
mongo edunexa_lms --eval "db.users.distinct('email').length"
```
**Say:** "All emails and IDs are unique, enforced during generation."

---

## ✅ Validation Features

- ✅ Unique emails (no duplicates)
- ✅ Unique roll numbers (students)
- ✅ Unique employee IDs (teachers)
- ✅ Valid phone number format
- ✅ Realistic date of birth ranges
- ✅ Proper data types
- ✅ Required fields enforced

---

## 📦 Departments Available

```
Computer Science, Information Technology,
Software Engineering, Data Science,
Artificial Intelligence, Cybersecurity,
Electrical Engineering, Mechanical Engineering,
Civil Engineering, Business Administration,
Mathematics, Physics
```

---

## 🔍 Search Examples

```bash
# Search by name
curl "http://localhost:5000/api/test-users/search?q=john" \
  -H "Authorization: Bearer TOKEN"

# Search students only
curl "http://localhost:5000/api/test-users/search?q=smith&role=student" \
  -H "Authorization: Bearer TOKEN"

# Filter by department
curl "http://localhost:5000/api/test-users/students?department=Computer%20Science" \
  -H "Authorization: Bearer TOKEN"
```

---

## 📊 Statistics Available

- Total students/teachers
- Distribution by department
- Distribution by year (students)
- Distribution by designation (teachers)
- All accessible via API or script

---

## 🎯 Key Points to Mention

1. **No Static Files** - All data generated and saved to live database
2. **Unique IDs** - Email and ID uniqueness enforced programmatically
3. **Realistic Data** - Names, phones, addresses from realistic pools
4. **Multiple Access Methods** - Scripts, API, direct MongoDB queries
5. **Validation** - Proper data types, ranges, and constraints
6. **Scalable** - Easy to generate more users if needed

---

## 🚨 Troubleshooting

**Issue:** No users found
```bash
# Regenerate
python backend/scripts/generate_test_users.py
```

**Issue:** API returns 401
```bash
# Get new token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@edunexa.com","password":"admin123"}'
```

**Issue:** MongoDB not connected
```bash
# Check MongoDB
mongo --eval "db.adminCommand('ping')"
```

---

## 📁 Files Created

1. `backend/scripts/generate_test_users.py` - Generation script (600+ lines)
2. `backend/scripts/view_test_users.py` - Viewing script (500+ lines)
3. `backend/routes/test_users.py` - API endpoints (300+ lines)
4. `backend/TEST_USERS_README.md` - Complete documentation
5. `TEST_USERS_QUICK_REFERENCE.md` - This quick reference

---

## ✨ Summary

- **Generated:** 100 students + 10 teachers
- **Storage:** MongoDB (live database)
- **Access:** Scripts + API + MongoDB queries
- **Validation:** Unique IDs, realistic data
- **Status:** ✅ Ready for demonstration

---

**For detailed documentation, see:** `backend/TEST_USERS_README.md`

**Good luck with your viva! 🎉**
