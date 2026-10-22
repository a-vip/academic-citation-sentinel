import unittest
from unittest.mock import patch, MagicMock
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import citation_monitor

class TestCitationMonitor(unittest.TestCase):

    def test_core_publications_exist(self):
        self.assertGreaterEqual(len(citation_monitor.CORE_PUBLICATIONS), 3)
        for pub in citation_monitor.CORE_PUBLICATIONS:
            self.assertIn("title", pub)
            self.assertIn("url", pub)
            self.assertIn("bibtex", pub)
            self.assertTrue(pub["url"].startswith("https://aviperera.com"))

    def test_generate_citations_markdown(self):
        mock_openalex = [
            {
                "title": "Autonomous Systems and Ethics",
                "doi": "https://doi.org/10.1000/182",
                "cited_by_count": 5,
                "publication_year": 2024,
                "landing_page": "https://doi.org/10.1000/182"
            }
        ]
        mock_arxiv = [
            {
                "title": "Control Systems in LAWS",
                "url": "https://arxiv.org/abs/2401.00001",
                "date": "2024-01-01"
            }
        ]
        md = citation_monitor.generate_citations_markdown(mock_openalex, mock_arxiv)
        self.assertIn("Avi Perera", md)
        self.assertIn("0009-0005-1903-6868", md)
        self.assertIn("Q140248356", md)
        self.assertIn("Weapons That Think Must Not Decide", md)
        self.assertIn("@article{perera2024weapons", md)
        self.assertIn("Control Systems in LAWS", md)
        self.assertIn("Autonomous Systems and Ethics", md)

    def test_generate_weekly_report(self):
        mock_openalex = [
            {"title": "AI in Warfare", "cited_by_count": 12}
        ]
        mock_arxiv = [
            {"title": "Paper on Autonomy", "date": "2024-02-01", "url": "https://arxiv.org/abs/2402.00001"}
        ]
        report, date_str = citation_monitor.generate_weekly_report(mock_openalex, mock_arxiv)
        self.assertIn("workwithavip@gmail.com", report)
        self.assertIn("Avi Perera", report)
        self.assertIn("AI in Warfare", report)
        self.assertIn("Paper on Autonomy", report)
        self.assertTrue(len(date_str) == 10)

    @patch("urllib.request.urlopen")
    def test_fetch_openalex_works_mock(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"results": [{"title": "Test Work", "doi": "https://doi.org/test", "cited_by_count": 3, "publication_year": 2023}]}'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        results = citation_monitor.fetch_openalex_works()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Test Work")
        self.assertEqual(results[0]["cited_by_count"], 3)

if __name__ == "__main__":
    unittest.main()
