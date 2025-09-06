# 🎓 Smart Attendance & Productivity Suite

A comprehensive educational management system built with Streamlit, Firebase, and AI-powered face recognition technology. This platform automates attendance tracking, provides personalized student recommendations, and offers advanced analytics for educational institutions.

## 🌟 Features

### 🔐 Authentication System
- **Multi-role Authentication**: Separate login systems for students and faculty
- **Secure Registration**: User registration with role-based access control
- **Session Management**: Persistent login sessions with automatic redirects

### 👥 Student Management
- **Student Registration**: Bulk student registration with face recognition training
- **Profile Management**: Complete student profiles with academic records
- **Image Processing**: Advanced face detection and embedding generation for attendance

### 📊 Attendance System
- **Live Attendance**: Real-time face recognition-based attendance marking
- **Automated Detection**: AI-powered face detection using MTCNN and FaceNet
- **Attendance Analytics**: Comprehensive attendance reports and trends
- **Visual Reports**: Interactive charts and downloadable CSV reports

### 🎯 Personalized Learning
- **AI-Powered Suggestions**: Personalized study recommendations using Mistral AI
- **Progress Tracking**: Visual progress monitoring for student interests
- **Academic Analysis**: Performance-based suggestions and improvement plans
- **Daily Feedback**: Faculty feedback system for continuous improvement

### 📅 Schedule Management
- **Visual Timetables**: Interactive weekly schedule display
- **Faculty Check-in**: Period-wise faculty attendance tracking
- **Substitution Management**: Automatic substitution detection and logging
- **Real-time Updates**: Live schedule updates with faculty check-in status

### 📈 Analytics & Reports
- **Admin Dashboard**: Comprehensive analytics for administrators
- **Performance Metrics**: Student performance tracking and analysis
- **Attendance Trends**: Visual attendance patterns and insights
- **Export Functionality**: CSV export for all reports

## 🏗️ Project Structure

### Core Application Files

#### `main_dashboard.py`
- **Purpose**: Main faculty dashboard and entry point
- **Features**: 
  - Class management and student overview
  - Model training initiation
  - Integrated faculty tools in tabbed interface
  - Student registration with image upload and compression
- **Access**: Faculty and Admin only

#### `app/pages/auth.py`
- **Purpose**: Authentication and user management
- **Features**:
  - Multi-role login/signup (student/faculty)
  - Faculty check-in system with period validation
  - Student photo collection during registration
  - Session management and role-based redirects
- **Security**: Password-based authentication with role verification

### Student Features

#### `app/pages/student_dashboard.py`
- **Purpose**: Comprehensive student portal
- **Features**:
  - Personal profile with academic records
  - Real-time timetable with faculty check-in status
  - Attendance percentage calculation
  - Marks and feedback display
  - AI-powered personalized suggestions
  - Progress tracking dashboard
- **AI Integration**: Dynamic suggestions based on academic performance

#### `app/pages/visual_daily_planner.py`
- **Purpose**: Interactive daily schedule planner
- **Features**:
  - Visual Gantt chart for daily schedule
  - AI-powered free period suggestions
  - Task completion tracking
  - Progress monitoring
  - Real-time attendance integration
- **AI Features**: Mistral AI integration for personalized recommendations

#### `app/pages/suggestion_engine.py`
- **Purpose**: AI-powered recommendation system
- **Features**:
  - Academic performance analysis
  - Interest-based suggestions
  - Progress tracking with visual indicators
  - Task completion system
  - Dynamic suggestion generation
- **AI Technology**: Mistral AI API for personalized learning paths

### Faculty Features

#### `app/pages/faculty_checkin.py`
- **Purpose**: Faculty attendance and substitution management
- **Features**:
  - Period-wise check-in system
  - Automatic substitution detection
  - Schedule validation
  - Check-in history tracking
  - Manual check-in for administrative purposes
- **Validation**: Time-based period validation with schedule integration

#### `app/pages/marks_feedback.py`
- **Purpose**: Academic assessment management
- **Features**:
  - Marks and grades entry
  - Faculty feedback system
  - Subject-wise assessment tracking
  - Timestamp logging for all entries
- **Integration**: Direct integration with student records

#### `app/pages/daily_feedback.py`
- **Purpose**: Daily student feedback system
- **Features**:
  - Date-wise feedback entry
  - Faculty-specific feedback tracking
  - Student progress monitoring
- **Storage**: Firebase Firestore integration

#### `app/pages/faculty_student_records.py`
- **Purpose**: Comprehensive student record management
- **Features**:
  - Complete student profile viewing
  - Academic history display
  - Feedback compilation from multiple faculty
  - Image display with base64 decoding
- **Access Control**: Faculty-only access with subject filtering

### Administrative Features

#### `app/pages/admin_dashboard.py`
- **Purpose**: Administrative analytics and reporting
- **Features**:
  - Attendance trend analysis
  - Visual charts and graphs using Matplotlib/Seaborn
  - CSV export functionality
  - Date range filtering
  - Class-wise analytics
- **Visualization**: Interactive charts for attendance patterns

#### `app/pages/live_attendance.py`
- **Purpose**: Real-time attendance marking system
- **Features**:
  - Camera-based face recognition
  - Multi-face detection and identification
  - Visual annotation of detected faces
  - Automatic attendance logging
  - Unknown face detection
- **AI Technology**: MTCNN + InceptionResnetV1 for face recognition

#### `app/pages/student_registration.py`
- **Purpose**: Student enrollment system
- **Features**:
  - Bulk student registration
  - Image upload and compression
  - Duplicate prevention
  - Base64 image encoding
- **Validation**: Comprehensive input validation and error handling

### Backend Systems

#### `backend/model_training.py`
- **Purpose**: AI model training for face recognition
- **Features**:
  - Face detection and embedding extraction
  - Class-wise model training
  - Embedding storage using pickle
  - Debug visualization for training data
- **AI Models**: MTCNN for detection, InceptionResnetV1 for embeddings

#### `firebase/firebase_admin_init.py`
- **Purpose**: Firebase integration and configuration
- **Features**:
  - Firestore database connection
  - Firebase Storage integration
  - Environment variable configuration
  - Service account authentication
- **Security**: Secure credential management with environment variables

## 🛠️ Technology Stack

### Frontend
- **Streamlit**: Modern web application framework
- **Plotly**: Interactive data visualization
- **Matplotlib/Seaborn**: Statistical plotting
- **PIL (Pillow)**: Image processing and manipulation

### Backend & AI
- **Firebase Firestore**: NoSQL database for real-time data
- **Firebase Storage**: Cloud storage for images and files
- **PyTorch**: Deep learning framework
- **FaceNet-PyTorch**: Face recognition models (MTCNN, InceptionResnetV1)
- **Mistral AI**: Large language model for personalized recommendations

### Data Processing
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **Base64**: Image encoding/decoding
- **Pickle**: Model serialization

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- Firebase project with Firestore and Storage enabled
- Mistral AI API key

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd smart-attendance-suite
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Firebase Configuration**
   - Place your Firebase service account key in `firebase/`
   - Update the path in `firebase_admin_init.py`
   - Or set `FIREBASE_SERVICE_ACCOUNT_KEY` environment variable

4. **Environment Variables**
   ```bash
   # Create .env file
   FIREBASE_SERVICE_ACCOUNT_KEY=<your-service-account-json>
   MISTRAL_API_KEY=<your-mistral-api-key>
   ```

5. **Run the application**
   ```bash
   streamlit run main_dashboard.py
   ```

## 📱 Usage Guide

### For Students
1. **Registration**: Sign up with student role and upload 15 face images
2. **Dashboard**: View timetable, attendance, and academic records
3. **Daily Planner**: Get AI-powered suggestions for free periods
4. **Progress Tracking**: Monitor learning progress and completed tasks

### For Faculty
1. **Check-in**: Mark attendance for each period
2. **Student Management**: Add new students and manage records
3. **Assessment**: Enter marks, grades, and feedback
4. **Analytics**: View class performance and attendance trends

### For Administrators
1. **Dashboard**: Access comprehensive analytics
2. **Reports**: Generate and export attendance reports
3. **System Management**: Monitor overall system performance

## 🔒 Security Features

- **Role-based Access Control**: Separate interfaces for students and faculty
- **Session Management**: Secure login sessions with automatic timeouts
- **Data Validation**: Comprehensive input validation and sanitization
- **Image Security**: Secure image processing and storage
- **API Security**: Secure API key management for external services

## 📊 Database Schema

### Collections
- **users**: User authentication and profile data
- **students**: Student records with embedded face images
- **attendance**: Daily attendance records
- **schedules**: Class timetables and schedules
- **checkins**: Faculty check-in records
- **marks**: Student academic assessments
- **daily_feedback**: Faculty feedback records

## 🤖 AI Features

### Face Recognition
- **Detection**: MTCNN for accurate face detection
- **Recognition**: InceptionResnetV1 for face embeddings
- **Matching**: Euclidean distance-based face matching
- **Threshold**: Configurable similarity thresholds

### Personalized Recommendations
- **Academic Analysis**: Performance-based suggestions
- **Interest Matching**: Hobby and interest-based recommendations
- **Progress Tracking**: Visual progress monitoring
- **Task Management**: Completion tracking and rewards

## 🔧 Configuration

### Model Parameters
- **Face Detection Threshold**: Adjustable in `live_attendance.py`
- **Recognition Threshold**: Configurable similarity threshold (default: 0.9)
- **Image Compression**: Quality and size settings in registration

### API Configuration
- **Mistral AI**: Model selection and token limits
- **Firebase**: Database rules and security settings
- **Streamlit**: Page configuration and layout settings

## 📈 Performance Optimization

- **Image Compression**: Automatic image optimization for storage
- **Lazy Loading**: Efficient data loading strategies
- **Caching**: Streamlit caching for improved performance
- **Batch Processing**: Efficient bulk operations

## 🐛 Troubleshooting

### Common Issues
1. **Face Detection Fails**: Ensure good lighting and clear face images
2. **Firebase Connection**: Verify service account credentials
3. **Model Training**: Check image quality and format
4. **API Limits**: Monitor Mistral AI usage and quotas

### Debug Features
- **Training Visualization**: Debug face detection during training
- **Logging**: Comprehensive error logging throughout the application
- **Validation**: Input validation with user-friendly error messages

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Firebase**: For robust backend infrastructure
- **Streamlit**: For rapid web application development
- **PyTorch Community**: For excellent deep learning tools
- **Mistral AI**: For powerful language model capabilities

## 📞 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation for common solutions

---

**Built with ❤️ for educational institutions worldwide**