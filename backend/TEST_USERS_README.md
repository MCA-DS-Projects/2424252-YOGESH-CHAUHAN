# Test User Generation System - README

## Overview

This system generates 100 unique students and 10 unique teachers with realistic data and saves them directly to MongoDB. It includes scripts for generation, viewing, and API endpoints for retrieval.

## Features

✅ **Realistic Data Generation**
- Unique names from pool of 100+ first and last names
- Unique email addresses (@student.edu, @faculty.edu)
- Unique IDs (roll numbers for students, employee IDs for teachers)
- Realistic phone numbers, addresses, dates of birth
- Avatar URLs generated automatically
- Department, year, semester, specializations
- Emergency contacts, office information, education details

✅ **Data Validation**
- Email uniqueness enforced
- ID uniqueness enforced (roll numbers, employee IDs)
- Proper date ranges (students 18-25, teachers 30-65)
- Valid phone number format
- Proper data types and structure

✅ **Database Integration**
- Direct MongoDB insertion
- No static files or hard-coded data
- Proper indexing and validation
- Secure password hashing

✅ **Retrieval Tools**
- Command-line viewer script
- Interactive menu
- REST API endpoints
- Export to CSV functionality

---

## Quick Start (5 Minutes)

### Step 1: Generate Users

```bash
python backend/scripts/generate_test_users.py
```

This will:
- Generate 100 unique students
- Generate 10 unique teachers
- Save directly to MongoDB
- Display sample data

**Output:**
```
✅ Connected to MongoDB
✅ Generated 100 students
✅ Generated 10 teachers
✅ Inserted 100 students
✅ Inserted 10 teachers
```

### Step 2: View Users

```bash
# Interactive menu
python backend/scripts/view_test_users.py

# Quick view (first 10 students)
python backend/scripts/view_test_users.py students

# Quick view (first 10 teachers)
python backend/scripts/view_test_users.py teachers

# View statistics
python backend/scripts/view_test_users.py stats
```

### Step 3: Test API Endpoints

```bash
# Start backend
cd backend
python run.py

# In another terminal, test endpoints
# (Login first to get token)

# Get all students
curl -X GET http://localhost:5000/api/test-users/students \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get all teachers
curl -X GET http://localhost:5000/api/test-users/teachers \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get statistics
curl -X GET http://localhost:5000/api/test-users/stats \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Generated Data Structure

### Student Record

```json
{
  "_id": "ObjectId",
  "name": "John Smith",
  "email": "john.smith@student.edu",
  "password": "hashed_password",
  "role": "student",
  "roll_number": "STU20241234",
  "department": "Computer Science",
  "year": "2nd Year",
  "semester": "Fall 2024",
  "phone": "+1-555-123-4567",
  "profile_pic": "https://ui-avatars.com/api/?name=John+Smith&background=random&size=200",
  "date_of_birth": "2003-05-15T00:00:00Z",
  "enrolled_courses": [],
  "completed_courses": [],
  "total_points": 250,
  "badges": [],
  "created_at": "2024-11-17T10:00:00Z",
  "updated_at": "2024-11-17T10:00:00Z",
  "is_active": true,
  "address": {
    "street": "123 Main St",
    "city": "New York",
    "state": "NY",
    "zip_code": "10001"
  },
  "emergency_contact": {
    "name": "Jane Smith",
    "relationship": "Parent",
    "phone": "+1-555-987-6543"
  }
}
```

### Teacher Record

```json
{
  "_id": "ObjectId",
  "name": "Dr. Sarah Johnson",
  "email": "sarah.johnson@faculty.edu",
  "password": "hashed_password",
  "role": "teacher",
  "employee_id": "FAC12345",
  "department": "Computer Science",
  "designation": "Associate Professor",
  "specializations": ["Machine Learning", "Deep Learning", "Neural Networks"],
  "phone": "+1-555-234-5678",
  "profile_pic": "https://ui-avatars.com/api/?name=Dr.+Sarah+Johnson&background=random&size=200",
  "date_of_birth": "1980-08-20T00:00:00Z",
  "courses_created": [],
  "created_at": "2024-11-17T10:00:00Z",
  "updated_at": "2024-11-17T10:00:00Z",
  "is_active": true,
  "office": {
    "building": "Engineering",
    "room": "305",
    "hours": "Mon-Fri 9:00 AM - 5:00 PM"
  },
  "education": {
    "highest_degree": "Ph.D.",
    "university": "MIT",
    "year": 2010
  },
  "years_of_experience": 15
}
```

---

## Scripts

### 1. Generate Test Users

**File:** `backend/scripts/generate_test_users.py`

**Usage:**
```bash
python backend/scripts/generate_test_users.py
```

**Features:**
- Generates 100 students and 10 teachers
- Ensures unique emails and IDs
- Realistic data from predefined pools
- Direct MongoDB insertion
- Shows sample data after generation
- Prompts before overwriting existing data

**Default Passwords:**
- Students: `Student@123`
- Teachers: `Teacher@123`

### 2. View Test Users

**File:** `backend/scripts/view_test_users.py`

**Usage:**

**Interactive Menu:**
```bash
python backend/scripts/view_test_users.py
```

**Command Line:**
```bash
# View first 10 students
python backend/scripts/view_test_users.py students

# View first 10 teachers
python backend/scripts/view_test_users.py teachers

# View statistics
python backend/scripts/view_test_users.py stats

# View specific student
python backend/scripts/view_test_users.py student john.smith@student.edu

# View specific teacher
python backend/scripts/view_test_users.py teacher sarah.johnson@faculty.edu
```

**Features:**
- Interactive menu with 10 options
- Table-formatted output
- Detailed user information
- Statistics and distributions
- Export to CSV
- Search by email

---

## API Endpoints

All endpoints require JWT authentication.

### 1. Get All Students

```http
GET /api/test-users/students
Authorization: Bearer <token>
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Results per page (default: 20)
- `department` (optional): Filter by department
- `year` (optional): Filter by year

**Response:**
```json
{
  "students": [...],
  "total": 100,
  "page": 1,
  "limit": 20,
  "total_pages": 5
}
```

### 2. Get All Teachers

```http
GET /api/test-users/teachers
Authorization: Bearer <token>
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Results per page (default: 20)
- `department` (optional): Filter by department

**Response:**
```json
{
  "teachers": [...],
  "total": 10,
  "page": 1,
  "limit": 20,
  "total_pages": 1
}
```

### 3. Get Student by ID

```http
GET /api/test-users/student/<student_id>
Authorization: Bearer <token>
```

**Response:**
```json
{
  "student": { ... }
}
```

### 4. Get Teacher by ID

```http
GET /api/test-users/teacher/<teacher_id>
Authorization: Bearer <token>
```

**Response:**
```json
{
  "teacher": { ... }
}
```

### 5. Get Statistics

```http
GET /api/test-users/stats
Authorization: Bearer <token>
```

**Response:**
```json
{
  "total_students": 100,
  "total_teachers": 10,
  "student_by_department": [...],
  "student_by_year": [...],
  "teacher_by_department": [...],
  "teacher_by_designation": [...]
}
```

### 6. Search Users

```http
GET /api/test-users/search?q=john&role=student
Authorization: Bearer <token>
```

**Query Parameters:**
- `q` (required): Search query (name or email)
- `role` (optional): Filter by role (student, teacher)
- `limit` (optional): Max results (default: 20)

**Response:**
```json
{
  "results": [...],
  "count": 5,
  "query": "john"
}
```

### 7. Get Departments

```http
GET /api/test-users/departments
Authorization: Bearer <token>
```

**Response:**
```json
{
  "departments": [
    "Computer Science",
    "Information Technology",
    ...
  ]
}
```

### 8. Get Sample Users

```http
GET /api/test-users/sample
Authorization: Bearer <token>
```

**Response:**
```json
{
  "sample_students": [5 students],
  "sample_teachers": [3 teachers]
}
```

---

## Viva Demonstration (10 Minutes)

### Preparation (2 minutes)
1. Ensure MongoDB is running
2. Generate test users if not already done
3. Start backend server
4. Have MongoDB Compass open
5. Have Postman or terminal ready

### Demo Script

**1. Show Generation (2 min)**

```bash
# Show the generation script
cat backend/scripts/generate_test_users.py | head -50

# Run generation (if not already done)
python backend/scripts/generate_test_users.py
```

**Explain:**
- Generates 100 students and 10 teachers
- Unique emails and IDs enforced
- Realistic data from predefined pools
- Direct MongoDB insertion

**2. View in Database (2 min)**

```bash
# Open MongoDB Compass
# Show users collection
# Filter: { "email": { "$regex": "@student.edu$" } }
# Show sample records
```

**Explain:**
- All data stored in MongoDB
- No static files
- Proper structure and validation

**3. View via Script (2 min)**

```bash
# View students
python backend/scripts/view_test_users.py students

# View statistics
python backend/scripts/view_test_users.py stats

# View detailed student
python backend/scripts/view_test_users.py student <email>
```

**Explain:**
- Command-line tools for viewing
- Table-formatted output
- Detailed information available

**4. Test API Endpoints (3 min)**

```bash
# Login to get token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@edunexa.com","password":"admin123"}'

# Get students
curl -X GET http://localhost:5000/api/test-users/students?limit=5 \
  -H "Authorization: Bearer TOKEN"

# Get teachers
curl -X GET http://localhost:5000/api/test-users/teachers \
  -H "Authorization: Bearer TOKEN"

# Get statistics
curl -X GET http://localhost:5000/api/test-users/stats \
  -H "Authorization: Bearer TOKEN"

# Search users
curl -X GET "http://localhost:5000/api/test-users/search?q=john" \
  -H "Authorization: Bearer TOKEN"
```

**Explain:**
- RESTful API endpoints
- Pagination support
- Filtering and search
- Statistics and aggregations

**5. Show Data Validation (1 min)**

```bash
# Show unique emails
mongo edunexa_lms --eval "db.users.find({email: {$regex: '@student.edu$'}}, {email: 1}).limit(10)"

# Show unique roll numbers
mongo edunexa_lms --eval "db.users.find({role: 'student'}, {roll_number: 1}).limit(10)"

# Show unique employee IDs
mongo edunexa_lms --eval "db.users.find({role: 'teacher'}, {employee_id: 1})"
```

**Explain:**
- All emails are unique
- All IDs are unique
- Proper validation enforced

---

## Testing Checklist

### Generation Tests
- [ ] Run generation script
- [ ] Verify 100 students created
- [ ] Verify 10 teachers created
- [ ] Check for unique emails
- [ ] Check for unique IDs
- [ ] Verify realistic data

### Viewing Tests
- [ ] View students via script
- [ ] View teachers via script
- [ ] View statistics
- [ ] View detailed student
- [ ] View detailed teacher
- [ ] Export to CSV

### API Tests
- [ ] GET /api/test-users/students
- [ ] GET /api/test-users/teachers
- [ ] GET /api/test-users/student/<id>
- [ ] GET /api/test-users/teacher/<id>
- [ ] GET /api/test-users/stats
- [ ] GET /api/test-users/search
- [ ] GET /api/test-users/departments
- [ ] GET /api/test-users/sample

### Database Tests
- [ ] Check users collection in MongoDB
- [ ] Verify data structure
- [ ] Check for duplicates
- [ ] Verify indexes
- [ ] Test queries

---

## Database Queries

### View All Students
```javascript
db.users.find({ role: "student", email: { $regex: "@student.edu$" } }).limit(10)
```

### View All Teachers
```javascript
db.users.find({ role: "teacher", email: { $regex: "@faculty.edu$" } }).limit(10)
```

### Count Students
```javascript
db.users.count({ role: "student", email: { $regex: "@student.edu$" } })
```

### Count Teachers
```javascript
db.users.count({ role: "teacher", email: { $regex: "@faculty.edu$" } })
```

### Students by Department
```javascript
db.users.aggregate([
  { $match: { role: "student", email: { $regex: "@student.edu$" } } },
  { $group: { _id: "$department", count: { $sum: 1 } } },
  { $sort: { count: -1 } }
])
```

### Teachers by Department
```javascript
db.users.aggregate([
  { $match: { role: "teacher", email: { $regex: "@faculty.edu$" } } },
  { $group: { _id: "$department", count: { $sum: 1 } } },
  { $sort: { count: -1 } }
])
```

### Check for Duplicate Emails
```javascript
db.users.aggregate([
  { $group: { _id: "$email", count: { $sum: 1 } } },
  { $match: { count: { $gt: 1 } } }
])
```

### Check for Duplicate Roll Numbers
```javascript
db.users.aggregate([
  { $match: { role: "student" } },
  { $group: { _id: "$roll_number", count: { $sum: 1 } } },
  { $match: { count: { $gt: 1 } } }
])
```

---

## Troubleshooting

### Issue: Generation Script Fails

**Solution:**
```bash
# Check MongoDB connection
mongo --eval "db.adminCommand('ping')"

# Check .env file
cat backend/.env | grep MONGO_URI

# Try connecting manually
mongo mongodb://localhost:27017/edunexa_lms
```

### Issue: No Users Found

**Solution:**
```bash
# Check if users were generated
mongo edunexa_lms --eval "db.users.count({email: {$regex: '@student.edu$'}})"

# Regenerate if needed
python backend/scripts/generate_test_users.py
```

### Issue: API Endpoints Return 401

**Solution:**
```bash
# Login to get valid token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@edunexa.com","password":"admin123"}'

# Use the returned token in Authorization header
```

### Issue: Duplicate Key Error

**Solution:**
```bash
# Delete existing test users
mongo edunexa_lms --eval "db.users.deleteMany({email: {$regex: '@(student|faculty).edu$'}})"

# Regenerate
python backend/scripts/generate_test_users.py
```

---

## Data Pools

### Departments
- Computer Science
- Information Technology
- Software Engineering
- Data Science
- Artificial Intelligence
- Cybersecurity
- Electrical Engineering
- Mechanical Engineering
- Civil Engineering
- Business Administration
- Mathematics
- Physics

### Student Years
- 1st Year
- 2nd Year
- 3rd Year
- 4th Year

### Teacher Designations
- Professor
- Associate Professor
- Assistant Professor
- Senior Lecturer
- Lecturer
- Instructor

### Specializations (Teachers)
- Machine Learning, Deep Learning, Neural Networks
- Web Development, Mobile Development, Cloud Computing
- Database Systems, Data Mining, Big Data
- Network Security, Cryptography, Ethical Hacking
- Software Architecture, Design Patterns, Agile Methodologies
- Computer Vision, Natural Language Processing, Robotics
- Algorithms, Data Structures, Computational Theory
- Operating Systems, Distributed Systems, Parallel Computing

---

## Key Points for Viva

**Technical Implementation:**
- Direct MongoDB insertion (no static files)
- Unique constraint enforcement
- Realistic data generation
- Proper validation and error handling

**Data Quality:**
- 100+ unique first/last names
- Unique emails and IDs
- Realistic phone numbers and addresses
- Proper date ranges for age groups
- Avatar URLs auto-generated

**Retrieval Methods:**
- Command-line scripts
- Interactive menu
- REST API endpoints
- MongoDB queries
- CSV export

**Demonstration:**
- Show generation process
- View in database
- Use command-line tools
- Test API endpoints
- Show data validation

---

## Files Created

1. `backend/scripts/generate_test_users.py` - Generation script
2. `backend/scripts/view_test_users.py` - Viewing script
3. `backend/routes/test_users.py` - API endpoints
4. `backend/TEST_USERS_README.md` - This documentation

---

## Summary

✅ **100 unique students generated**
✅ **10 unique teachers generated**
✅ **All data saved to MongoDB**
✅ **Unique IDs enforced**
✅ **Realistic data with validation**
✅ **Command-line viewing tools**
✅ **REST API endpoints**
✅ **Ready for viva demonstration**

---

**Status:** ✅ Complete and Ready for Demonstration
**Total Records:** 110 (100 students + 10 teachers)
**Storage:** MongoDB (live database)
**Retrieval:** Scripts + API endpoints
