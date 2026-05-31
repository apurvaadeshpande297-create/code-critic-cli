import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add project root to sys.path so we can import modules correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai_reviewer.cli import main
from ai_reviewer.file_handler import read_source_file, FileHandlerError
from ai_reviewer.config import Config, ConfigError

class TestAICli(unittest.TestCase):

    def setUp(self):
        # Paths to our test sample files
        self.cpp_file = "test_samples/sample_leak.cpp"
        self.py_file = "test_samples/sample_slow.py"
        self.nonexistent_file = "test_samples/does_not_exist.py"
        
    @patch('ai_reviewer.renderer.Renderer.print_score_panel')
    @patch('ai_reviewer.ai_client.AIClient.generate_feedback')
    @patch('ai_reviewer.ai_client.AIClient.get_info_string')
    def test_review_cpp(self, mock_info, mock_feedback, mock_print_score):
        """Test the review command on C++ files."""
        mock_info.return_value = "MOCK_GEMINI (Model: gemini-2.5-flash)"
        mock_feedback.return_value = (
            "## Bug Risks\n"
            "- [Critical] Memory leak at `new int[size]` (line 5)\n"
            "## Style Improvements\n"
            "- [Warning] Use PascalCase for functions\n"
            "## Optimization Suggestions\n"
            "- [Suggestion] Use `std::vector` instead of raw array\n"
            "## Complexity Analysis\n"
            "- Time Complexity: O(N)\n"
        )
        
        # We patch os.environ to fake having keys
        with patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key_here"}):
            exit_code = main(["review", self.cpp_file])
            self.assertEqual(exit_code, 0)
            mock_feedback.assert_called_once()
            
            # Verify that the score panel was printed with the expected statistics
            mock_print_score.assert_called_once()
            score_info = mock_print_score.call_args[0][0]
            # Deductions: Critical (-3), Warning (-1), Suggestion (-0.25) -> Total = -4.25
            # Score: 10 - 4.25 = 5.75
            self.assertEqual(score_info["score"], 5.75)
            self.assertEqual(score_info["score_str"], "5.75/10")
            self.assertEqual(score_info["critical"], 1)
            self.assertEqual(score_info["warning"], 1)
            self.assertEqual(score_info["suggestion"], 1)
            self.assertEqual(score_info["status"], "Needs Improvement")

    @patch('ai_reviewer.ai_client.AIClient.generate_feedback')
    def test_explain_python(self, mock_feedback):
        """Test the explain command on Python files."""
        mock_feedback.return_value = (
            "1. **High-Level Summary**: This is a sample script with slow functions.\n"
            "2. **Key Components**: contains `find_common_elements`.\n"
        )
        
        with patch.dict(os.environ, {"OPENAI_API_KEY": "fake_key_here", "AI_PROVIDER": "openai"}):
            exit_code = main(["explain", self.py_file])
            self.assertEqual(exit_code, 0)
            mock_feedback.assert_called_once()

    @patch('ai_reviewer.ai_client.AIClient.generate_feedback')
    def test_complexity_python_with_output(self, mock_feedback):
        """Test complexity analysis and export to markdown."""
        mock_feedback.return_value = (
            "1. **Time Complexity**: O(N*M)\n"
            "2. **Space Complexity**: O(1) aux\n"
        )
        
        output_report = "test_samples/test_report.md"
        if os.path.exists(output_report):
            os.remove(output_report)
            
        with patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key_here"}):
            exit_code = main(["complexity", self.py_file, "-o", output_report])
            self.assertEqual(exit_code, 0)
            self.assertTrue(os.path.exists(output_report))
            
            # Clean up output
            os.remove(output_report)

    @patch('ai_reviewer.ai_client.AIClient.generate_feedback')
    def test_testgen_python(self, mock_feedback):
        """Test the testgen command on Python files."""
        mock_feedback.return_value = (
            "## Basic Test Cases\n"
            "### Standard List\n"
            "- **Input:** list1=[1,2], list2=[2,3]\n"
            "- **Expected Behavior:** [2]\n"
            "- **Reason:** Typical inputs to check logic\n"
        )
        
        with patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key_here"}):
            exit_code = main(["testgen", self.py_file])
            self.assertEqual(exit_code, 0)
            mock_feedback.assert_called_once()

    def test_invalid_file(self):
        """Verify the tool exits cleanly when file is missing."""
        exit_code = main(["review", self.nonexistent_file])
        self.assertEqual(exit_code, 1)

    def test_missing_api_keys(self):
        """Verify tool displays error and exits when no API keys are configured."""
        # Clear environment variables for keys
        with patch.dict(os.environ, {}, clear=True):
            # We must also clear external env variables like GEMINI_API_KEY if they exist in shell
            # patch.dict with clear=True handles this, but let's be sure
            exit_code = main(["review", self.py_file])
            self.assertEqual(exit_code, 1)

if __name__ == '__main__':
    unittest.main()
