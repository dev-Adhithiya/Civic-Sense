# Civic Issue Reporter 

AI-powered issue detection for managing and monitoring civic infrastructure complaints with a comprehensive admin dashboard.

## 📋 Features

### Admin Dashboard
- **Real-time Statistics**: Track total complaints, pending issues, in-progress tasks, and resolution rates
- **Complaint Management**: View, edit, and update complaint statuses
- **Advanced Filtering**: Filter by status, severity, and search by ID or location
- **Visual Analytics**: Interactive charts showing issue distribution
- **Activity Feed**: Monitor recent complaint submissions
- **Data Export**: Export all complaints to CSV format
- **Auto-refresh**: Dashboard updates every 30 seconds

### API Features
- Image analysis using Google Gemini Vision AI
- Automatic issue detection (Potholes, Garbage, Water Leakage, Drains, Streetlights)
- Severity scoring (1-10 scale)
- Authority assignment based on issue type
- Complaint tracking with unique IDs
- RESTful API endpoints for admin operations

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Google Gemini API key
- Modern web browser

### Installation

1. **Clone or extract the project files**

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**

Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

To get a Gemini API key:
- Visit https://makersuite.google.com/app/apikey
- Sign in with your Google account
- Click "Create API Key"
- Copy the key to your `.env` file

4. **Start the server**
```bash
python main.py
```

The API will start on `http://localhost:8000`

5. **Open the Admin Dashboard**

Open `admin.html` in your web browser, or navigate to:
```
http://localhost:8000/admin.html
```

## 📂 Project Structure

```
civic-issue-reporter/
├── main.py                 # FastAPI backend with admin endpoints
├── vision_analyzer.py      # AI image analysis module
├── schemas.py             # Data models and schemas
├── requirements.txt       # Python dependencies
├── index.html            # User-facing complaint submission form
├── admin.html            # Admin dashboard interface
└── .env                  # Environment variables (create this)
```

## 🔌 API Endpoints

### Public Endpoints

#### Submit Complaint
```http
POST /analyze
Content-Type: multipart/form-data

Parameters:
- file: Image file (JPG, PNG, etc.)
- location: Location string

Response: AnalysisResponse with complaint details
```

#### Health Check
```http
GET /health

Response: API health status
```

### Admin Endpoints

#### Get All Complaints
```http
GET /admin/complaints?status=<status>&severity=<severity>&limit=<limit>

Query Parameters:
- status: Filter by status (Pending, In Progress, Resolved)
- severity: Filter by severity (Low, Medium, High)
- limit: Maximum results (default: 100)

Response: List of complaints with metadata
```

#### Get Specific Complaint
```http
GET /admin/complaints/{complaint_id}

Response: Detailed complaint information
```

#### Update Complaint Status
```http
PUT /admin/complaints/{complaint_id}/status?status=<new_status>

Query Parameters:
- status: New status (Pending, In Progress, Resolved)

Response: Updated complaint details
```

#### Delete Complaint
```http
DELETE /admin/complaints/{complaint_id}

Response: Deletion confirmation
```

#### Get Statistics
```http
GET /admin/statistics

Response: Dashboard statistics including:
- Total complaints
- Status breakdown
- Severity distribution
- Issue type counts
- Resolution rate
```

#### Export Data
```http
GET /admin/export

Response: JSON export of all complaints
```

## 💻 Admin Dashboard Usage

### Dashboard Overview
1. **Header**: Shows API status, refresh button, and export functionality
2. **Statistics Cards**: Real-time metrics for complaints
3. **Complaints Table**: Searchable, filterable list of all complaints
4. **Issue Distribution Chart**: Visual breakdown of issue types
5. **Recent Activity**: Timeline of latest complaint submissions

### Managing Complaints

#### Viewing Details
1. Click "View" button on any complaint
2. Modal shows complete complaint information
3. Update status directly from the modal

#### Updating Status
1. Click "Edit" button on any complaint
2. Choose new status (1-Pending, 2-In Progress, 3-Resolved)
3. Confirm to update

#### Filtering Complaints
- Use dropdown filters for Status and Severity
- Use search box to find by ID or location
- Filters work in combination

#### Exporting Data
1. Click "Export Data" button in header
2. CSV file downloads automatically
3. Includes all complaint details

### Auto-Refresh
- Dashboard refreshes every 30 seconds automatically
- Manual refresh available via Refresh button
- Green dot indicates API is online

## 🎨 Issue Detection

The system automatically detects and categorizes:

| Issue Type | Authority | Common Severity |
|------------|-----------|----------------|
| Pothole | Public Works Department | Medium-High |
| Garbage Overflow | Sanitation Department | Medium |
| Water Leakage | Water Board | High |
| Open Drain | Public Works Department | High |
| Streetlight Issue | Electrical Department | Low-Medium |

## 📊 Severity Scoring

Severity is calculated based on:
- Issue type
- Description keywords (large, deep, major, etc.)
- Visual analysis from AI

| Score | Level | Description |
|-------|-------|-------------|
| 1-3 | Low | Minor issues, routine maintenance |
| 4-7 | Medium | Moderate issues, priority attention |
| 8-10 | High | Critical issues, immediate action needed |

## 🔧 Configuration

### API Settings
Edit in `main.py`:
- `host`: Server host (default: 0.0.0.0)
- `port`: Server port (default: 8000)
- `reload`: Auto-reload on code changes

### Dashboard Settings
Edit in `admin.html`:
- `API_BASE_URL`: Backend API URL (default: http://localhost:8000)
- Auto-refresh interval (default: 30 seconds)

### CORS Settings
For production, update allowed origins in `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Update this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🗄️ Data Storage

**Current**: In-memory storage (data resets on server restart)

**For Production**: Replace with database
1. Add database dependency (PostgreSQL, MongoDB, etc.)
2. Replace `complaints_db = []` with database connection
3. Update CRUD operations to use database queries

Example with SQLAlchemy:
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://user:password@localhost/civic_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
```

## 🔒 Security Recommendations

For production deployment:
1. Add authentication for admin endpoints
2. Implement rate limiting
3. Add HTTPS/SSL certificates
4. Restrict CORS origins
5. Add input validation and sanitization
6. Implement user roles and permissions
7. Add audit logging
8. Secure API keys using secrets management

## 🐛 Troubleshooting

### API Not Connecting
- Check if server is running (`python main.py`)
- Verify `API_BASE_URL` in admin.html matches server address
- Check browser console for errors
- Ensure no firewall blocking port 8000

### No Complaints Showing
- Submit a test complaint via index.html first
- Check API is responding: visit http://localhost:8000/health
- Verify Gemini API key is configured correctly

### Image Analysis Failing
- Verify GEMINI_API_KEY in .env file
- Check image file size (max 10MB)
- Ensure image is valid format (JPG, PNG)
- Check Google AI Studio quota limits

## 📱 Browser Compatibility

Tested and working on:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 🤝 Contributing

To extend the dashboard:
1. Add new API endpoints in `main.py`
2. Update frontend JavaScript in `admin.html`
3. Add corresponding UI elements
4. Test with various complaint scenarios

## 📄 License

This project is provided as-is for educational and municipal use.

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation
3. Check browser console for errors
4. Verify all dependencies are installed

## 🎯 Future Enhancements

Potential improvements:
- User authentication and authorization
- Real-time notifications
- Map visualization of complaints
- Mobile app integration
- Email notifications to authorities
- Advanced analytics and reporting
- Multi-language support
- Offline mode
- Image storage and retrieval
- Automated status updates based on workflows

---

**Note**: This system uses in-memory storage. For production use, implement a proper database solution and add authentication/authorization.
