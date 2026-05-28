import io
import streamlit as st

def load_pdf(file):
    """
    Extract text from PDF file with multiple fallback methods
    """
    text = ""
    
    # Method 1: Try PyMuPDF (fitz) - fastest and most reliable
    try:
        import fitz
        pdf = fitz.open(stream=file.read(), filetype="pdf")
        for page_num in range(pdf.page_count):
            page = pdf.load_page(page_num)
            text += page.get_text()
        pdf.close()
        
        if text.strip():
            return text
            
    except ImportError:
        st.warning("PyMuPDF not available, trying PyPDF2...")
    except Exception as e:
        st.warning(f"PyMuPDF failed: {str(e)[:100]}...")
    
    # Method 2: Try PyPDF2
    try:
        from PyPDF2 import PdfReader
        file.seek(0)  # Reset file pointer
        pdf_reader = PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        if text.strip():
            return text
            
    except ImportError:
        st.warning("PyPDF2 not available, trying pdfplumber...")
    except Exception as e:
        st.warning(f"PyPDF2 failed: {str(e)[:100]}...")
    
    # Method 3: Try pdfplumber (if available)
    try:
        import pdfplumber
        file.seek(0)
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        
        if text.strip():
            return text
            
    except ImportError:
        pass
    except Exception as e:
        st.warning(f"pdfplumber failed: {str(e)[:100]}...")
    
    # If all methods fail
    if not text.strip():
        raise Exception(
            "Could not extract text from PDF. "
            "Please ensure the PDF contains selectable text (not scanned images). "
            "Try installing: pip install pymupdf PyPDF2 pdfplumber"
        )
    
    return text


def load_pdf_simple(file):
    """
    Simple PDF loader using only PyPDF2 (lightweight option)
    """
    try:
        from PyPDF2 import PdfReader
        text = ""
        pdf_reader = PdfReader(file)
        
        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        
        if not text.strip():
            raise Exception("No text could be extracted from the PDF")
        
        return text
        
    except ImportError:
        raise Exception(
            "PyPDF2 is not installed. Please run: pip install PyPDF2"
        )
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")