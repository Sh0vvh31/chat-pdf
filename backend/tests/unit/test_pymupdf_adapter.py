import pytest
from unittest.mock import patch, MagicMock
from src.infrastructure.extraction.pymupdf_adapter import PyMuPDFExtractor

def test_pymupdf_extract_success():
    extractor = PyMuPDFExtractor()
    
    # Mock fitz.open and the document it returns
    with patch("src.infrastructure.extraction.pymupdf_adapter.fitz.open") as mock_open:
        mock_doc = MagicMock()
        mock_open.return_value = mock_doc
        
        # Simulate a document with 2 pages
        mock_doc.__len__.return_value = 2
        
        # Mock page 1
        mock_page_1 = MagicMock()
        mock_page_1.get_text.return_value = "Page 1 Content\n"
        
        # Mock page 2
        mock_page_2 = MagicMock()
        mock_page_2.get_text.return_value = "  Page 2 Content  "
        
        # Configure load_page to return different pages
        mock_doc.load_page.side_effect = [mock_page_1, mock_page_2]
        
        # Run extraction
        chunks = extractor.extract("dummy.pdf")
        
        assert len(chunks) == 2
        
        assert chunks[0].page_number == 1
        assert chunks[0].content == "Page 1 Content"  # stripped
        assert chunks[0].chunk_type == "text"
        
        assert chunks[1].page_number == 2
        assert chunks[1].content == "Page 2 Content"
        
        mock_open.assert_called_once_with("dummy.pdf")
        mock_doc.close.assert_called_once()

def test_pymupdf_extract_empty_page():
    extractor = PyMuPDFExtractor()
    with patch("src.infrastructure.extraction.pymupdf_adapter.fitz.open") as mock_open:
        mock_doc = MagicMock()
        mock_open.return_value = mock_doc
        mock_doc.__len__.return_value = 1
        
        mock_page = MagicMock()
        mock_page.get_text.return_value = "   \n " # Empty after strip
        mock_doc.load_page.return_value = mock_page
        
        chunks = extractor.extract("empty.pdf")
        
        assert len(chunks) == 0 # Empty pages should be skipped
