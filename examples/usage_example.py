"""
Complete Usage Example
Demonstrates how to use the Resume Parser API
"""

import requests
import json
import time
from pathlib import Path


# API Base URL
BASE_URL = "http://localhost:8000/api/v1"


def check_health():
    """Check if the API is healthy"""
    print("🔍 Checking API health...")
    response = requests.get(f"{BASE_URL}/health")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API is healthy (v{data['version']})")
        print(f"   Services: {data['services']}")
        return True
    else:
        print(f"❌ API is not healthy: {response.status_code}")
        return False


def upload_resume(file_path, options=None):
    """Upload and parse a resume"""
    print(f"\n📤 Uploading resume: {file_path}")
    
    # Prepare file
    files = {
        'file': (Path(file_path).name, open(file_path, 'rb'))
    }
    
    # Prepare options
    data = {}
    if options:
        data['options'] = json.dumps(options)
    
    # Upload
    response = requests.post(
        f"{BASE_URL}/resumes/upload",
        files=files,
        data=data
    )
    
    if response.status_code in [200, 202]:
        result = response.json()
        resume_id = result['id']
        print(f"✅ Resume uploaded successfully")
        print(f"   Resume ID: {resume_id}")
        print(f"   Status: {result['status']}")
        return resume_id
    else:
        print(f"❌ Upload failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return None


def get_resume_data(resume_id, max_wait=30):
    """Get parsed resume data (with polling if still processing)"""
    print(f"\n📥 Retrieving resume data...")
    
    waited = 0
    while waited < max_wait:
        response = requests.get(f"{BASE_URL}/resumes/{resume_id}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Resume data retrieved successfully")
            
            # Display key information
            if 'personalInfo' in data:
                print("\n👤 Personal Information:")
                name = data['personalInfo'].get('name', {}).get('full', 'N/A')
                email = data['personalInfo'].get('contact', {}).get('email', 'N/A')
                print(f"   Name: {name}")
                print(f"   Email: {email}")
            
            if 'experience' in data:
                print(f"\n💼 Work Experience: {len(data['experience'])} positions")
                for exp in data['experience'][:2]:  # Show first 2
                    print(f"   - {exp.get('title')} at {exp.get('company')}")
            
            if 'education' in data:
                print(f"\n🎓 Education: {len(data['education'])} entries")
                for edu in data['education'][:2]:
                    print(f"   - {edu.get('degree')} in {edu.get('field')}")
            
            if 'skills' in data:
                print("\n🔧 Skills:")
                technical = data['skills'].get('technical', [])
                if technical:
                    for category in technical[:2]:
                        print(f"   {category.get('category')}: {', '.join(category.get('items', [])[:5])}")
            
            if 'aiEnhancements' in data:
                print("\n🤖 AI Insights:")
                enhancements = data['aiEnhancements']
                print(f"   Quality Score: {enhancements.get('qualityScore', 'N/A')}/100")
                print(f"   Career Level: {enhancements.get('careerLevel', 'N/A')}")
            
            return data
            
        elif response.status_code == 202:
            print("⏳ Still processing... waiting 2 seconds")
            time.sleep(2)
            waited += 2
        else:
            print(f"❌ Failed to retrieve data: {response.status_code}")
            return None
    
    print("⚠️  Timeout waiting for resume processing")
    return None


def match_with_job(resume_id, job_description):
    """Match resume with a job description"""
    print(f"\n🎯 Matching resume with job: {job_description['jobDescription']['title']}")
    
    response = requests.post(
        f"{BASE_URL}/resumes/{resume_id}/match",
        json=job_description
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Job matching completed")
        
        matching = result['matchingResults']
        print(f"\n📊 Match Results:")
        print(f"   Overall Score: {matching['overallScore']}/100")
        print(f"   Confidence: {matching['confidence']:.2%}")
        print(f"   Recommendation: {matching['recommendation']}")
        
        if 'categoryScores' in matching:
            print("\n   Category Scores:")
            for category, scores in matching['categoryScores'].items():
                print(f"   - {category}: {scores.get('score', 'N/A')}/100")
        
        if 'strengthAreas' in matching:
            print("\n   💪 Strength Areas:")
            for strength in matching['strengthAreas'][:3]:
                print(f"   - {strength}")
        
        if 'gapAnalysis' in matching:
            gaps = matching['gapAnalysis']
            if gaps.get('criticalGaps'):
                print("\n   ⚠️  Critical Gaps:")
                for gap in gaps['criticalGaps'][:2]:
                    print(f"   - {gap.get('missing')}: {gap.get('suggestion', '')}")
        
        return result
    else:
        print(f"❌ Job matching failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return None


def get_analytics(resume_id):
    """Get resume analytics"""
    print(f"\n📈 Fetching analytics...")
    
    response = requests.get(f"{BASE_URL}/analytics/resume/{resume_id}")
    
    if response.status_code == 200:
        analytics = response.json()
        print("✅ Analytics retrieved")
        
        print(f"\n   Quality Score: {analytics.get('qualityScore', 'N/A')}/100")
        print(f"   Completeness: {analytics.get('completenessScore', 'N/A')}/100")
        print(f"   Career Level: {analytics.get('careerLevel', 'N/A')}")
        
        if 'salaryEstimate' in analytics:
            salary = analytics['salaryEstimate']
            print(f"   Salary Range: ${salary.get('min', 0):,} - ${salary.get('max', 0):,} {salary.get('currency', 'USD')}")
        
        if 'improvementSuggestions' in analytics:
            print("\n   💡 Suggestions:")
            for suggestion in analytics['improvementSuggestions'][:3]:
                print(f"   - {suggestion}")
        
        return analytics
    else:
        print(f"❌ Failed to get analytics: {response.status_code}")
        return None


def main():
    """Main example workflow"""
    print("=" * 60)
    print("AI-Powered Resume Parser - Usage Example")
    print("=" * 60)
    
    # Step 1: Check health
    if not check_health():
        print("\n⚠️  API is not available. Please start the server.")
        return
    
    # Step 2: Upload resume
    # You can replace this with your own resume file
    resume_file = "sample_resumes/sample_resume.txt"
    
    if not Path(resume_file).exists():
        # Create a sample resume if it doesn't exist
        print("\n📝 Creating sample resume...")
        Path("sample_resumes").mkdir(exist_ok=True)
        
        sample_content = """
John Developer
john.dev@email.com | +1-555-100-2000 | San Francisco, CA

PROFESSIONAL SUMMARY
Experienced software engineer with 6+ years of expertise in full-stack development, 
cloud architecture, and team leadership.

WORK EXPERIENCE

Senior Software Engineer | Tech Innovations Inc | 2020-Present
- Architected and deployed microservices infrastructure serving 1M+ users
- Led team of 5 developers in Agile environment
- Improved application performance by 60% through optimization
- Technologies: Python, React, AWS, Docker, Kubernetes

Software Engineer | Digital Solutions Co | 2018-2020
- Developed RESTful APIs and web applications
- Implemented CI/CD pipelines reducing deployment time by 40%
- Collaborated with cross-functional teams on product features
- Technologies: JavaScript, Node.js, PostgreSQL, Redis

EDUCATION

Master of Science in Computer Science
Stanford University | 2018 | GPA: 3.8

Bachelor of Science in Computer Science  
UC Berkeley | 2016 | GPA: 3.7

SKILLS

Programming: Python, JavaScript, TypeScript, Java, Go
Frameworks: React, Django, FastAPI, Node.js, Express
Cloud & DevOps: AWS, Docker, Kubernetes, Terraform, Jenkins
Databases: PostgreSQL, MongoDB, Redis, MySQL
Tools: Git, Jira, Confluence, VS Code

CERTIFICATIONS

AWS Certified Solutions Architect - Associate | Amazon Web Services | 2022
Certified Kubernetes Administrator (CKA) | CNCF | 2021
"""
        with open(resume_file, 'w') as f:
            f.write(sample_content)
        print("✅ Sample resume created")
    
    options = {
        'extractTechnologies': True,
        'enhanceWithAI': True,
        'performOCR': False
    }
    
    resume_id = upload_resume(resume_file, options)
    
    if not resume_id:
        return
    
    # Step 3: Get resume data
    resume_data = get_resume_data(resume_id)
    
    if not resume_data:
        return
    
    # Step 4: Get analytics
    analytics = get_analytics(resume_id)
    
    # Step 5: Match with job
    job_description = {
        "jobDescription": {
            "title": "Senior Software Engineer",
            "company": "Tech Corp",
            "location": "San Francisco, CA",
            "type": "full-time",
            "experience": {
                "minimum": 5,
                "preferred": 8,
                "level": "senior"
            },
            "description": "We are seeking a highly skilled Senior Software Engineer...",
            "requirements": {
                "required": [
                    "5+ years of software development experience",
                    "Strong proficiency in Python and JavaScript",
                    "Experience with cloud platforms (AWS preferred)",
                    "Understanding of microservices architecture"
                ],
                "preferred": [
                    "Experience with Docker and Kubernetes",
                    "Leadership experience",
                    "AWS certifications"
                ]
            },
            "skills": {
                "required": ["Python", "JavaScript", "AWS", "Microservices"],
                "preferred": ["Docker", "Kubernetes", "React", "PostgreSQL"]
            }
        },
        "options": {
            "includeExplanation": True,
            "detailedBreakdown": True,
            "suggestImprovements": True
        }
    }
    
    matching_result = match_with_job(resume_id, job_description)
    
    print("\n" + "=" * 60)
    print("✅ Example completed successfully!")
    print("=" * 60)
    print("\n💡 Next steps:")
    print("   1. Try uploading your own resume")
    print("   2. Explore the API documentation at http://localhost:8000/docs")
    print("   3. Test different job descriptions")
    print("   4. Check out market analytics at /analytics/market")


if __name__ == "__main__":
    main()