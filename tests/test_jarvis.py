""
Tests for the Jarvis personal assistant.
"""
import unittest
from unittest.mock import patch, MagicMock

from jarvis import Jarvis, __version__

class TestJarvis(unittest.TestCase):
    """Test cases for the Jarvis class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.jarvis = Jarvis()
    
    def test_greeting(self):
        """Test the greeting message."""
        greeting = self.jarvis.greet()
        self.assertIn("Jarvis", greeting)
        self.assertIn("assistant", greeting.lower())
    
    def test_listening_state(self):
        """Test listening state management."""
        self.assertFalse(self.jarvis.is_listening)
        self.jarvis.start_listening()
        self.assertTrue(self.jarvis.is_listening)
        self.jarvis.stop_listening()
        self.assertFalse(self.jarvis.is_listening)
    
    def test_status(self):
        """Test status information."""
        status = self.jarvis.get_status()
        self.assertEqual(status['name'], 'Jarvis')
        self.assertEqual(status['version'], __version__)
        self.assertIn('config', status)

if __name__ == '__main__':
    unittest.main()
