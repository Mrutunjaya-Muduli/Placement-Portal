from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from core.models import StudentProfile, RecruiterProfile, Notification, JobPosting, Application

class EditProfileTests(TestCase):
    def setUp(self):
        # Create student 1
        self.student_user1 = User.objects.create_user(
            username='alice', password='password123', email='alice@university.edu', first_name='Alice Smith'
        )
        self.profile1 = StudentProfile.objects.create(
            user=self.student_user1, student_id='ST2026001', branch='Computer Science & Engineering', cgpa=9.20, skills='Python'
        )

        # Create student 2
        self.student_user2 = User.objects.create_user(
            username='bob', password='password123', email='bob@university.edu', first_name='Bob Johnson'
        )
        self.profile2 = StudentProfile.objects.create(
            user=self.student_user2, student_id='ST2026002', branch='Electronics & Communication', cgpa=7.80, skills='C++'
        )

        # Create recruiter
        self.recruiter_user = User.objects.create_user(
            username='stripe', password='password123', email='stripe@stripe.com', first_name='Stripe Recruiter'
        )
        self.recruiter_profile = RecruiterProfile.objects.create(
            user=self.recruiter_user, company_name='Stripe'
        )

    def test_edit_profile_unauthenticated(self):
        url = reverse('edit_profile')
        response = self.client.get(url)
        # Should redirect to login since login_required is active
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_edit_profile_recruiter_denied(self):
        self.client.login(username='stripe', password='password123')
        url = reverse('edit_profile')
        response = self.client.get(url)
        # Should redirect to home with error message
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))

    def test_edit_profile_get_prefilled(self):
        self.client.login(username='alice', password='password123')
        url = reverse('edit_profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Alice Smith')
        self.assertContains(response, 'alice@university.edu')
        self.assertContains(response, 'ST2026001')
        self.assertContains(response, 'Computer Science & Engineering')

    def test_edit_profile_post_success(self):
        self.client.login(username='alice', password='password123')
        url = reverse('edit_profile')
        post_data = {
            'name': 'Alice Smithson',
            'email': 'alice.smithson@university.edu',
            'student_id': 'ST2026001-NEW',
            'branch': 'Information Technology',
            'cgpa': '9.50',
            'skills': 'Python, Django, React'
        }
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('student_dashboard'))
        
        # Verify database was updated
        self.student_user1.refresh_from_db()
        self.profile1.refresh_from_db()
        self.assertEqual(self.student_user1.first_name, 'Alice Smithson')
        self.assertEqual(self.student_user1.email, 'alice.smithson@university.edu')
        self.assertEqual(self.profile1.student_id, 'ST2026001-NEW')
        self.assertEqual(self.profile1.branch, 'Information Technology')
        self.assertEqual(float(self.profile1.cgpa), 9.50)
        self.assertEqual(self.profile1.skills, 'Python, Django, React')

    def test_edit_profile_post_duplicate_id(self):
        self.client.login(username='alice', password='password123')
        url = reverse('edit_profile')
        post_data = {
            'name': 'Alice Smith',
            'email': 'alice@university.edu',
            'student_id': 'ST2026002', # Claimed by Bob
            'branch': 'Computer Science & Engineering',
            'cgpa': '9.20',
            'skills': 'Python'
        }
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 200)
        # Should stay on page and show error
        self.assertContains(response, 'Student ID &quot;ST2026002&quot; already exists.')
        
        # Verify database was NOT updated
        self.profile1.refresh_from_db()
        self.assertEqual(self.profile1.student_id, 'ST2026001')

class NotificationTests(TestCase):
    def setUp(self):
        # Create student user
        self.student_user = User.objects.create_user(
            username='alice', password='password123', email='alice@university.edu', first_name='Alice Smith'
        )
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user, student_id='ST2026001', branch='Computer Science & Engineering', cgpa=9.20, skills='Python'
        )

        # Create recruiter user
        self.recruiter_user = User.objects.create_user(
            username='stripe', password='password123', email='stripe@stripe.com', first_name='Stripe Recruiter'
        )
        self.recruiter_profile = RecruiterProfile.objects.create(
            user=self.recruiter_user, company_name='Stripe'
        )

        # Create Job
        self.job = JobPosting.objects.create(
            recruiter=self.recruiter_user,
            company_name='Stripe',
            job_role='Software Engineer',
            package='15 LPA',
            eligibility='Min 8.0 CGPA',
            min_cgpa=8.00,
            eligible_branches='All'
        )

        # Create Application
        self.app = Application.objects.create(student=self.student_profile, job=self.job, status='Applied')

    def test_notification_created_on_status_change(self):
        self.client.login(username='stripe', password='password123')
        url = reverse('update_status', args=[self.app.id])
        
        # Verify no notifications currently
        self.assertEqual(Notification.objects.filter(student=self.student_profile).count(), 0)
        
        # Post to update status
        response = self.client.post(url, {'status': 'Shortlisted'})
        self.assertEqual(response.status_code, 302)
        
        # Verify notification was created
        self.assertEqual(Notification.objects.filter(student=self.student_profile).count(), 1)
        notif = Notification.objects.filter(student=self.student_profile).first()
        self.assertIn("Shortlisted", notif.message)
        self.assertFalse(notif.is_read)

    def test_mark_notifications_read(self):
        # Create a mock notification
        notif = Notification.objects.create(
            student=self.student_profile,
            message="Your status was updated",
            is_read=False
        )
        self.assertEqual(Notification.objects.filter(student=self.student_profile, is_read=False).count(), 1)

        # Log in as student
        self.client.login(username='alice', password='password123')
        url = reverse('mark_notifications_read')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('student_dashboard'))
        
        # Verify notification is marked as read
        self.assertEqual(Notification.objects.filter(student=self.student_profile, is_read=False).count(), 0)
        notif.refresh_from_db()
        self.assertTrue(notif.is_read)

class AdminDashboardTests(TestCase):
    def setUp(self):
        # Create staff user
        self.staff_user = User.objects.create_user(
            username='admin', password='password123', email='admin@portal.com', is_staff=True
        )
        # Create a recruiter
        self.recruiter_user = User.objects.create_user(
            username='rec_techcorp', password='password123', email='rec@techcorp.com', first_name='TechCorp Recruiter'
        )
        self.recruiter_profile = RecruiterProfile.objects.create(
            user=self.recruiter_user, company_name='TechCorp'
        )

    def test_admin_dashboard_recruiter_directory(self):
        self.client.login(username='admin', password='password123')
        url = reverse('admin_dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TechCorp Recruiter')
        self.assertContains(response, 'TechCorp')
        self.assertContains(response, 'rec@techcorp.com')

class StudentDashboardTimelineTests(TestCase):
    def setUp(self):
        # Create student user
        self.student_user = User.objects.create_user(
            username='alice', password='password123', email='alice@university.edu', first_name='Alice Smith'
        )
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user, student_id='ST2026001', branch='Computer Science & Engineering', cgpa=9.20, skills='Python'
        )

        # Create recruiter user
        self.recruiter_user = User.objects.create_user(
            username='stripe', password='password123', email='stripe@stripe.com', first_name='Stripe Recruiter'
        )
        self.recruiter_profile = RecruiterProfile.objects.create(
            user=self.recruiter_user, company_name='Stripe'
        )

        # Create Job
        self.job = JobPosting.objects.create(
            recruiter=self.recruiter_user,
            company_name='Stripe',
            job_role='Software Engineer',
            package='15 LPA',
            eligibility='Min 8.0 CGPA',
            min_cgpa=8.00,
            eligible_branches='All'
        )

        # Create Applications with different status for testing
        self.app_applied = Application.objects.create(student=self.student_profile, job=self.job, status='Applied')

    def test_student_dashboard_timeline_applied(self):
        self.client.login(username='alice', password='password123')
        url = reverse('student_dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Verify container elements exist
        self.assertContains(response, 'timeline-container')
        self.assertContains(response, 'timeline-line')
        self.assertContains(response, 'timeline-fill-line')
        
        # Under Applied, Step 1 (Applied) is active
        self.assertContains(response, 'timeline-step active')
        self.assertContains(response, '📩')
        
    def test_student_dashboard_timeline_shortlisted(self):
        self.app_applied.status = 'Shortlisted'
        self.app_applied.save()
        
        self.client.login(username='alice', password='password123')
        url = reverse('student_dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Verify shortlisted specific content
        self.assertContains(response, 'Cleared Round')

    def test_student_dashboard_timeline_selected(self):
        self.app_applied.status = 'Selected'
        self.app_applied.save()
        
        self.client.login(username='alice', password='password123')
        url = reverse('student_dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(response, 'Offer Made!')
        self.assertContains(response, '🎉')

    def test_student_dashboard_timeline_rejected(self):
        self.app_applied.status = 'Rejected'
        self.app_applied.save()
        
        self.client.login(username='alice', password='password123')
        url = reverse('student_dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(response, 'Closed')
        self.assertContains(response, '✗')

class HomepageTests(TestCase):
    def setUp(self):
        # Create student user
        self.student_user = User.objects.create_user(
            username='alice', password='password123', email='alice@university.edu', first_name='Alice Smith'
        )
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user, student_id='ST2026001', branch='Computer Science & Engineering', cgpa=9.20, skills='Python'
        )

        # Create recruiter user
        self.recruiter_user = User.objects.create_user(
            username='stripe', password='password123', email='stripe@stripe.com', first_name='Stripe Recruiter'
        )
        self.recruiter_profile = RecruiterProfile.objects.create(
            user=self.recruiter_user, company_name='Stripe'
        )

        # Create Job
        self.job = JobPosting.objects.create(
            recruiter=self.recruiter_user,
            company_name='Stripe',
            job_role='Software Engineer',
            package='15 LPA',
            eligibility='Min 8.0 CGPA',
            min_cgpa=8.00,
            eligible_branches='All'
        )
        
        # Create application (Selected)
        self.app = Application.objects.create(
            student=self.student_profile,
            job=self.job,
            status='Selected'
        )

    def test_homepage_loads_with_statistics(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check context stats are correct
        self.assertEqual(response.context['total_students'], 1)
        self.assertEqual(response.context['total_recruiters'], 1)
        self.assertEqual(response.context['active_drives'], 1)
        self.assertEqual(response.context['placed_students'], 1)
        
        # Verify rendered elements on homepage
        self.assertContains(response, 'Registered Students')
        self.assertContains(response, 'Partner Employers')
        self.assertContains(response, 'Active Job Drives')
        self.assertContains(response, 'Successful Offers')
        
        # Verify marquee list includes Google, Stripe, Microsoft
        self.assertContains(response, 'Stripe')
        self.assertContains(response, 'Google')
        self.assertContains(response, 'Microsoft')

class JobListAccessTests(TestCase):
    def setUp(self):
        # Create student user
        self.student_user = User.objects.create_user(
            username='alice', password='password123', email='alice@university.edu', first_name='Alice Smith'
        )
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user, student_id='ST2026001', branch='Computer Science & Engineering', cgpa=9.20, skills='Python'
        )

        # Create recruiter user
        self.recruiter_user = User.objects.create_user(
            username='stripe', password='password123', email='stripe@stripe.com', first_name='Stripe Recruiter'
        )
        self.recruiter_profile = RecruiterProfile.objects.create(
            user=self.recruiter_user, company_name='Stripe'
        )

        # Create Job
        self.job = JobPosting.objects.create(
            recruiter=self.recruiter_user,
            company_name='Stripe',
            job_role='Software Engineer',
            package='15 LPA',
            eligibility='Min 8.0 CGPA',
            min_cgpa=8.00,
            eligible_branches='All'
        )

    def test_anonymous_user_can_access_job_list(self):
        url = reverse('job_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Stripe')
        self.assertContains(response, 'Software Engineer')
        self.assertContains(response, 'Login to Apply')

    def test_student_user_can_access_job_list(self):
        self.client.login(username='alice', password='password123')
        url = reverse('job_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Stripe')
        self.assertContains(response, 'Software Engineer')
        self.assertContains(response, 'Apply Now')

    def test_recruiter_user_can_access_job_list(self):
        self.client.login(username='stripe', password='password123')
        url = reverse('job_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Stripe')
        self.assertContains(response, 'Software Engineer')

class FooterShortcutAndRedirectionTests(TestCase):
    def setUp(self):
        # Create student user
        self.student_user = User.objects.create_user(
            username='student_user', password='password123', email='student@univ.edu', first_name='Student User'
        )
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user, student_id='ST9999', branch='Computer Science', cgpa=9.00
        )

        # Create recruiter user
        self.recruiter_user = User.objects.create_user(
            username='recruiter_user', password='password123', email='recruiter@company.com', first_name='Recruiter User'
        )
        self.recruiter_profile = RecruiterProfile.objects.create(
            user=self.recruiter_user, company_name='Company Inc.'
        )

    def test_unauthenticated_dashboard_redirects_to_login_with_next(self):
        url = reverse('student_dashboard')
        response = self.client.get(url)
        # Should redirect to our login page at /login/ instead of /accounts/login/
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
        self.assertTrue('next=/dashboard/' in response.url or 'next=%2Fdashboard%2F' in response.url)

    def test_login_redirects_to_next_url(self):
        # Submit login form as student and ensure we go to next URL
        login_url = reverse('login') + '?next=' + reverse('edit_profile')
        response = self.client.post(login_url, {
            'username': 'student_user',
            'password': 'password123',
            'role': 'student'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('edit_profile'))

    def test_recruiter_access_student_dashboard_redirects_to_home_with_error(self):
        self.client.login(username='recruiter_user', password='password123')
        url = reverse('student_dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))
        
        # Follow the redirect and verify message
        response = self.client.get(response.url)
        self.assertContains(response, 'Access denied. Student profile required.')

    def test_student_access_recruiter_dashboard_redirects_to_home_with_error(self):
        self.client.login(username='student_user', password='password123')
        url = reverse('company_dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))

        # Follow the redirect and verify message
        response = self.client.get(response.url)
        self.assertContains(response, 'Access denied. Recruiter account required.')

class PlacementCalendarTests(TestCase):
    def setUp(self):
        # Create recruiter
        self.recruiter_user = User.objects.create_user(
            username='stripe', password='password123', email='stripe@stripe.com', first_name='Stripe Recruiter'
        )
        self.recruiter_profile = RecruiterProfile.objects.create(
            user=self.recruiter_user, company_name='Stripe'
        )
        
        # Create student
        self.student_user = User.objects.create_user(
            username='alice', password='password123', email='alice@univ.edu', first_name='Alice Smith'
        )
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user, student_id='ST1000', branch='Computer Science', cgpa=9.00
        )

    def test_post_job_saves_calendar_dates(self):
        self.client.login(username='stripe', password='password123')
        url = reverse('post_job')
        
        post_data = {
            'job_role': 'Frontend Developer',
            'package': '12 LPA',
            'eligibility': 'Min 8.0 CGPA',
            'min_cgpa': '8.00',
            'eligible_branches': 'All',
            'application_deadline': '2026-07-01',
            'drive_date': '2026-07-15'
        }
        
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('company_dashboard'))
        
        # Verify db was populated with dates
        job = JobPosting.objects.get(job_role='Frontend Developer')
        self.assertEqual(str(job.application_deadline), '2026-07-01')
        self.assertEqual(str(job.drive_date), '2026-07-15')

    def test_export_ics_returns_valid_file(self):
        self.client.login(username='alice', password='password123')
        job = JobPosting.objects.create(
            recruiter=self.recruiter_user,
            company_name='Stripe',
            job_role='Backend Engineer',
            package='18 LPA',
            eligibility='Min 8.5 CGPA',
            min_cgpa=8.50,
            eligible_branches='All',
            application_deadline='2026-08-01',
            drive_date='2026-08-10'
        )
        
        url = reverse('export_job_ics', args=[job.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/calendar')
        self.assertIn('attachment; filename="Stripe_drive.ics"', response['Content-Disposition'])
        
        content = response.content.decode('utf-8')
        self.assertIn('BEGIN:VCALENDAR', content)
        self.assertIn('SUMMARY:Apply By: Stripe - Backend Engineer', content)
        self.assertIn('SUMMARY:Placement Drive: Stripe - Backend Engineer', content)
        self.assertIn('END:VCALENDAR', content)

    def test_calendar_page_loads_and_contains_events(self):
        job = JobPosting.objects.create(
            recruiter=self.recruiter_user,
            company_name='Stripe',
            job_role='Backend Engineer',
            package='18 LPA',
            eligibility='Min 8.5 CGPA',
            min_cgpa=8.50,
            eligible_branches='All',
            application_deadline='2026-08-01',
            drive_date='2026-08-10'
        )
        
        url = reverse('placement_calendar')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Stripe - Apply Deadline')
        self.assertContains(response, 'Stripe - Drive Date')


