import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def split_sentences(text: str) -> list:
    """Split text into sentences using regex."""
    if not text:
        return []
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]

def generate_summary(text: str, length: str = "medium") -> str:
    """
    Generate AI-powered summary using BART model.
    Falls back to simple extraction if model fails.
    """
    if not text or not text.strip():
        return "No text content found to summarize."

    # Clean up text
    cleaned_text = re.sub(r'\s+', ' ', text.strip())

    try:
        from transformers import pipeline
        
        # Configure summary length
        max_length = {"short": 60, "medium": 120, "long": 200}[length]
        min_length = max_length // 3

        # Truncate text if too long for BART
        if len(cleaned_text) > 1000:
            cleaned_text = cleaned_text[:1000]

        # Load BART model (cached on first run)
        summarizer = pipeline(
            "summarization",
            model="facebook/bart-large-cnn",
            tokenizer="facebook/bart-large-cnn",
            device=-1  # CPU
        )

        # Generate summary
        result = summarizer(
            cleaned_text,
            max_length=max_length,
            min_length=min_length,
            do_sample=False,
            truncation=True
        )
        
        summary_text = result[0]['summary_text'].strip()
        
        # Format output
        return f"**AI Summary:** {summary_text}"
        
    except Exception as e:
        logger.warning(f"BART model failed, falling back to sentence extraction: {e}")
        # Fallback: extract first few sentences
        sentences = split_sentences(cleaned_text)
        n_map = {"short": 1, "medium": 3, "long": 6}
        n = n_map.get(length, 3)
        fallback = " ".join(sentences[:max(1, min(n, len(sentences)))]).strip()
        return f"**Fallback Summary:** {fallback[:500]}..." if fallback else "Could not generate summary."

def generate_improvements(text: str) -> str:
    """Generate improvement suggestions for the document."""
    if not text:
        return "No text to analyze."
    
    suggestions = []
    sentences = split_sentences(text)
    word_count = len(text.split())
    
    # Check for long sentences
    long_sentences = [s for s in sentences if len(s.split()) > 40]
    if long_sentences:
        suggestions.append(f"📝 {len(long_sentences)} long sentence(s) detected; consider breaking them up for better readability.")
    
    # Check for passive voice
    passive_indicators = [" was ", " were ", " been ", " being "]
    passive_count = sum(1 for s in sentences if any(indicator in s.lower() for indicator in passive_indicators))
    if passive_count > 0:
        suggestions.append(f"🔄 {passive_count} sentence(s) may contain passive voice; consider active voice for clarity.")
    
    # Check document length
    if word_count < 100:
        suggestions.append("📏 Document is quite short; consider adding more detailed content.")
    elif word_count > 1000:
        suggestions.append("📊 Document is comprehensive; consider adding headings or bullet points for structure.")
    
    # Check for key sections
    text_lower = text.lower()
    has_intro = any(word in text_lower for word in ['introduction', 'overview', 'summary', 'abstract'])
    has_conclusion = any(word in text_lower for word in ['conclusion', 'summary', 'finally'])
    
    if not has_intro:
        suggestions.append("📋 Consider adding an introduction to provide context.")
    if not has_conclusion:
        suggestions.append("🔚 Consider adding a conclusion to summarize key points.")
    
    if not suggestions:
        suggestions.append("✅ Document appears well-structured and professional.")
    
    return "\n".join(f"• {suggestion}" for suggestion in suggestions)

# Test the functions
if __name__ == "__main__":
    # Example usage
    test_text = "Infosys Navigate your next COURSE COMPLETION CERTIFICATE FARHEENSAYED M NALBAND"
    print("AI Summary:", generate_summary(test_text, "medium"))
    print("Improvements:", generate_improvements(test_text))