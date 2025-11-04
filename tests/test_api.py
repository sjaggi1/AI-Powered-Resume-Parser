"""
API Integration Tests
Tests all major API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app
import io


# Create test client
client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check_success(self):
        """Test successful health check"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data
        assert "services" in data
    
    def test_health_check_structure(self):
        """Test health check response structure"""
        response = client.get("/api/v1/health")
        data = response.json()
        
        assert "services" in data
        assert "database" in data["services"]
        assert "ai_service" in data["services"]


class TestResumeUpload:
    """Test resume upload and parsing"""
    
    def test_upload_txt_resume(self):
        """Test uploading a text resume"""
        # Create sample resume content
        resume_content = """
        John Doe
        john.doe@example.com | +1-555-123-4567
        San Francisco, CA
        
        EXPERIENCE
        Senior Software Engineer | Tech Corp | 2020-2024
        - Developed microservices architecture
        - Led team of 5 developers
        - Improved system performance by 40%
        
        EDUCATION
        Bachelor of Science in Computer Science
        University of California | 2018
        
        SKILLS
        Python, JavaScript, AWS, Docker, PostgreSQL
        """
        
        files = {
            "file": ("test_resume.txt", resume_content.encode(), "text/plain")
        }
        
        response = client.post("/api/v1/resumes/upload", files=files)
        
        # Should return 202 Accepted (processing started)
        assert response.status_code == 202
        
        data = response.json()
        assert "id" in data
        assert data["status"] in ["processing", "completed"]
        assert "message" in data
    
    def test_upload_without_file(self):
        """Test upload endpoint without file"""
        response = client.post("/api/v1/resumes/upload")
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_upload_unsupported_format(self):
        """Test uploading unsupported file format"""
        files = {
            "file": ("test.xlsx", b"fake content", "application/vnd.ms-excel")
        }
        
        response = client.post("/api/v1/resumes/upload", files=files)
        assert response.status_code == 415  # Unsupported Media Type


class TestResumeRetrieval:
    """Test resume data retrieval"""
    
    @pytest.fixture
    def uploaded_resume_id(self):
        """Fixture to upload a resume and return its ID"""
        resume_content = """
        Jane Smith
        jane.smith@example.com
        
        EXPERIENCE
        Data Scientist | Analytics Co | 2019-2024
        - Built ML models for customer segmentation
        - Improved prediction accuracy by 25%
        
        SKILLS
        Python, R, TensorFlow, SQL
        """
        
        files = {
            "file": ("jane_resume.txt", resume_content.encode(), "text/plain")
        }
        
        response = client.post("/api/v1/resumes/upload", files=files)
        return response.json()["id"]
    
    def test_get_resume_success(self, uploaded_resume_id):
        """Test retrieving a resume by ID"""
        response = client.get(f"/api/v1/resumes/{uploaded_resume_id}")
        
        # Should be 200 if completed, or 202 if still processing
        assert response.status_code in [200, 202]
        
        data = response.json()
        assert "id" in data
        
        if response.status_code == 200:
            assert "personalInfo" in data or "metadata" in data
    
    def test_get_nonexistent_resume(self):
        """Test retrieving non-existent resume"""
        response = client.get("/api/v1/resumes/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404
        
        data = response.json()
        assert "error" in data
    
    def test_get_processing_status(self, uploaded_resume_id):
        """Test getting processing status"""
        response = client.get(f"/api/v1/resumes/{uploaded_resume_id}/status")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert "status" in data
        assert data["status"] in ["processing", "completed", "failed"]


class TestJobMatching:
    """Test resume-job matching functionality"""
    
    @pytest.fixture
    def uploaded_resume_id(self):
        """Upload a test resume"""
        resume_content = """
        Alex Johnson
        alex.j@email.com | +1-555-999-8888
        
        EXPERIENCE
        Senior Software Engineer | TechStart | 2018-2024
        - Built scalable microservices with Python and Docker
        - Led AWS migration project
        - Mentored junior developers
        
        EDUCATION
        MS Computer Science | Stanford University | 2018
        BS Computer Science | UC Berkeley | 2016
        
        SKILLS
        Python, JavaScript, AWS, Docker, Kubernetes, PostgreSQL, React
        
        CERTIFICATIONS
        AWS Certified Solutions Architect
        """
        
        files = {
            "file": ("alex_resume.txt", resume_content.encode(), "text/plain")
        }
        
        response = client.post("/api/v1/resumes/upload", files=files)
        return response.json()["id"]
    
    def test_job_matching_success(self, uploaded_resume_id):
        """Test successful job matching"""
        job_description = {
            "jobDescription": {
                "title": "Senior Software Engineer",
                "company": "Tech Innovation Corp",
                "description": "We are seeking a skilled engineer...",
                "requirements": {
                    "required": [
                        "5+ years of experience",
                        "Python expertise",
                        "AWS experience"
                    ],
                    "preferred": [
                        "Docker/Kubernetes",
                        "Leadership experience"
                    ]
                },
                "skills": {
                    "required": ["Python", "AWS", "Docker"],
                    "preferred": ["Kubernetes", "React"]
                }
            },
            "options": {
                "includeExplanation": True,
                "detailedBreakdown": True
            }
        }
        
        response = client.post(
            f"/api/v1/resumes/{uploaded_resume_id}/match",
            json=job_description
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert "matchId" in data
        assert "matchingResults" in data
        assert "overallScore" in data["matchingResults"]
        assert 0 <= data["matchingResults"]["overallScore"] <= 100
    
    def test_job_matching_nonexistent_resume(self):
        """Test job matching with non-existent resume"""
        job_description = {
            "jobDescription": {
                "title": "Engineer",
                "description": "Test",
                "requirements": {"required": ["Test"]},
                "skills": {"required": ["Test"]}
            }
        }
        
        response = client.post(
            "/api/v1/resumes/00000000-0000-0000-0000-000000000000/match",
            json=job_description
        )
        
        assert response.status_code == 404


class TestAnalytics:
    """Test analytics endpoints"""
    
    def test_market_analytics(self):
        """Test market analytics endpoint"""
        response = client.get("/api/v1/analytics/market")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "topSkills" in data
        assert "salaryTrends" in data
        assert "industryDistribution" in data
    
    def test_market_analytics_with_filters(self):
        """Test market analytics with filters"""
        response = client.get(
            "/api/v1/analytics/market",
            params={"timeframe": "30d", "industry": "technology"}
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["timeframe"] == "30d"


class TestErrorHandling:
    """Test error handling"""
    
    def test_404_not_found(self):
        """Test 404 error handling"""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    def test_invalid_json(self):
        """Test invalid JSON handling"""
        response = client.post(
            "/api/v1/resumes/test-id/match",
            data="invalid json"
        )
        assert response.status_code in [400, 422]


# Run tests with: pytest tests/test_api.py -v