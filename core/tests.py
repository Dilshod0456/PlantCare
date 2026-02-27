"""
Tests for core application functionality
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class HealthCheckTestCase(TestCase):
    """Tests for health check endpoint"""
    
    def setUp(self):
        self.client = Client()
    
    def test_health_check_endpoint(self):
        """Test health check returns valid response"""
        response = self.client.get(reverse('health_check'))
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('status', data)
        self.assertIn('components', data)
        self.assertIn('database', data['components'])
        self.assertIn('ml_model', data['components'])
    
    def test_version_info_endpoint(self):
        """Test version info returns valid data"""
        response = self.client.get(reverse('version_info'))
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('app_name', data)
        self.assertIn('app_version', data)
        self.assertEqual(data['app_name'], 'PlantCare')


class HomePageTestCase(TestCase):
    """Tests for home page"""
    
    def setUp(self):
        self.client = Client()
    
    def test_home_page_loads(self):
        """Test home page loads successfully"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PlantCare')

