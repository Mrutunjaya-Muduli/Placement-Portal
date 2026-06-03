from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import StudentProfile, JobPosting, Application, RecruiterProfile

class Command(BaseCommand):
    help = 'Seeds the database with realistic mock data for students, companies, and job postings.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Clearing existing non-admin data..."))
        
        # Clear existing data (but keep superusers)
        Application.objects.all().delete()
        JobPosting.objects.all().delete()
        StudentProfile.objects.all().delete()
        RecruiterProfile.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()

        self.stdout.write(self.style.SUCCESS("Database cleared! Seeding new mock data..."))

        # 1. Create Recruiter / Company accounts
        rec_stripe = User.objects.create_user(
            username='stripe', password='password123', email='recruiter@stripe.com', first_name='Stripe Recruiter'
        )
        RecruiterProfile.objects.create(user=rec_stripe, company_name='Stripe')

        rec_google = User.objects.create_user(
            username='google', password='password123', email='recruiter@google.com', first_name='Google Recruiter'
        )
        RecruiterProfile.objects.create(user=rec_google, company_name='Google')

        rec_tesla = User.objects.create_user(
            username='tesla', password='password123', email='recruiter@tesla.com', first_name='Tesla Recruiter'
        )
        RecruiterProfile.objects.create(user=rec_tesla, company_name='Tesla')

        rec_msft = User.objects.create_user(
            username='microsoft', password='password123', email='recruiter@microsoft.com', first_name='Microsoft Recruiter'
        )
        RecruiterProfile.objects.create(user=rec_msft, company_name='Microsoft')

        recruiter1_user = User.objects.create_user(
            username='recruiter', password='password123', email='recruiter@techcorp.com', first_name='TechCorp Recruiter'
        )
        RecruiterProfile.objects.create(user=recruiter1_user, company_name='TechCorp')
        
        self.stdout.write(self.style.SUCCESS("Created Recruiter Users: 'stripe', 'google', 'tesla', 'microsoft', 'recruiter' (Password: password123)"))

        # 2. Create Job Postings linked to recruiters
        job1 = JobPosting.objects.create(
            recruiter=rec_stripe,
            company_name='Stripe',
            job_role='Software Engineer - Core Infrastructure',
            package='18 LPA',
            eligibility='Minimum 8.0 CGPA, B.Tech CSE/IT',
            min_cgpa=8.00,
            eligible_branches='Computer Science, Information Technology, CSE, IT'
        )
        job2 = JobPosting.objects.create(
            recruiter=rec_google,
            company_name='Google',
            job_role='Associate Product Manager',
            package='24 LPA',
            eligibility='Minimum 8.5 CGPA, All branches eligible',
            min_cgpa=8.50,
            eligible_branches='All'
        )
        job3 = JobPosting.objects.create(
            recruiter=rec_tesla,
            company_name='Tesla',
            job_role='Embedded Systems Engineer',
            package='16 LPA',
            eligibility='Minimum 7.5 CGPA, ECE/EEE/CSE branches only',
            min_cgpa=7.50,
            eligible_branches='Electronics, Computer Science, ECE, CSE'
        )
        job4 = JobPosting.objects.create(
            recruiter=rec_msft,
            company_name='Microsoft',
            job_role='Support Engineer',
            package='12 LPA',
            eligibility='Minimum 7.0 CGPA, B.Tech/MCA',
            min_cgpa=7.00,
            eligible_branches='Computer Science, Information Technology, CSE, IT'
        )
        job5 = JobPosting.objects.create(
            recruiter=recruiter1_user,
            company_name='TechCorp',
            job_role='Cloud Solutions Architect',
            package='14 LPA',
            eligibility='Minimum 7.5 CGPA, B.Tech CSE/IT/ECE',
            min_cgpa=7.50,
            eligible_branches='Computer Science, Information Technology, Electronics, CSE, IT, ECE'
        )
        job6 = JobPosting.objects.create(
            recruiter=recruiter1_user,
            company_name='TechCorp',
            job_role='Data Science Intern',
            package='8 LPA',
            eligibility='Minimum 7.0 CGPA, All branches eligible',
            min_cgpa=7.00,
            eligible_branches='All'
        )
        self.stdout.write(self.style.SUCCESS(f"Created {JobPosting.objects.count()} Job Postings."))

        # 3. Create Students
        students_data = [
            {
                'username': 'alice',
                'password': 'password123',
                'name': 'Alice Smith',
                'email': 'alice@university.edu',
                'student_id': 'ST2026001',
                'branch': 'Computer Science & Engineering',
                'cgpa': 9.20,
                'skills': 'Python, Django, PostgreSQL, Docker, React'
            },
            {
                'username': 'bob',
                'password': 'password123',
                'name': 'Bob Johnson',
                'email': 'bob@university.edu',
                'student_id': 'ST2026002',
                'branch': 'Electronics & Communication',
                'cgpa': 7.80,
                'skills': 'C++, Embedded Systems, Arduino, HTML/CSS'
            },
            {
                'username': 'charlie',
                'password': 'password123',
                'name': 'Charlie Brown',
                'email': 'charlie@university.edu',
                'student_id': 'ST2026003',
                'branch': 'Information Technology',
                'cgpa': 8.10,
                'skills': 'JavaScript, Node.js, Express, MongoDB, Java'
            }
        ]

        students = []
        for s_info in students_data:
            user = User.objects.create_user(
                username=s_info['username'],
                password=s_info['password'],
                email=s_info['email'],
                first_name=s_info['name']
            )
            profile = StudentProfile.objects.create(
                user=user,
                student_id=s_info['student_id'],
                branch=s_info['branch'],
                cgpa=s_info['cgpa'],
                skills=s_info['skills']
            )
            students.append(profile)
            self.stdout.write(self.style.SUCCESS(f"Created Student User: '{s_info['username']}' (Password: password123)"))

        # 4. Create Applications
        # Alice (9.2 CGPA) applies for Stripe, Google, and TechCorp Architect
        Application.objects.create(student=students[0], job=job1, status='Shortlisted')
        Application.objects.create(student=students[0], job=job2, status='Applied')
        Application.objects.create(student=students[0], job=job5, status='Applied')

        # Bob (7.8 CGPA) applies for Tesla, Microsoft, and TechCorp Architect
        Application.objects.create(student=students[1], job=job3, status='Applied')
        Application.objects.create(student=students[1], job=job4, status='Selected')
        Application.objects.create(student=students[1], job=job5, status='Applied')

        # Charlie (8.1 CGPA) applies for Stripe, Microsoft, and TechCorp Intern
        Application.objects.create(student=students[2], job=job1, status='Rejected')
        Application.objects.create(student=students[2], job=job4, status='Applied')
        Application.objects.create(student=students[2], job=job6, status='Shortlisted')

        self.stdout.write(self.style.SUCCESS("Successfully seeded applications!"))
        self.stdout.write(self.style.SUCCESS("--- Database Seeding Completed ---"))
