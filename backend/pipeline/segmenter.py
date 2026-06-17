import re
import nltk
from dataclasses import dataclass


@dataclass
class Segment:
    id: int
    label: str
    text: str
    char_start: int
    char_end: int
    token_count: int


HEADER_PATTERNS = [
    r'CLAUSE\s+\d+',
    r'SCHEDULE\s+[A-Z]',
    r'^\d+\.\s+[A-Z][A-Z]+',
    r'^[A-Z][A-Z\s]{4,}$',
]


def segment_by_headers(text: str) -> list[Segment]:
    lines = text.split('\n')
    header_indices = []

    for i, line in enumerate(lines):
        line = line.strip()
        for pattern in HEADER_PATTERNS:
            if re.search(pattern, line, re.MULTILINE):
                header_indices.append(i)
                break

    if len(header_indices) < 2:
        return []

    segments = []
    for idx, header_idx in enumerate(header_indices):
        start_line = header_idx
        end_line = header_indices[idx + 1] if idx + 1 < len(header_indices) else len(lines)

        section_lines = lines[start_line:end_line]
        section_text = '\n'.join(section_lines).strip()

        if not section_text:
            continue

        char_start = len('\n'.join(lines[:start_line]))
        char_end = char_start + len(section_text)

        segments.append(Segment(
            id=idx + 1,
            label=lines[header_idx].strip() or f'Section {idx + 1}',
            text=section_text,
            char_start=char_start,
            char_end=char_end,
            token_count=len(section_text.split()),
        ))

    return segments


def segment_by_sentences(text: str, max_tokens: int = 200) -> list[Segment]:
    try:
        sentences = nltk.sent_tokenize(text)
    except Exception:
        sentences = text.split('. ')

    segments = []
    current_sentences = []
    current_tokens = 0
    segment_id = 1
    char_pos = 0

    for sentence in sentences:
        token_count = len(sentence.split())

        if current_tokens + token_count > max_tokens and current_sentences:
            section_text = ' '.join(current_sentences).strip()
            segments.append(Segment(
                id=segment_id,
                label=f'Section {segment_id}',
                text=section_text,
                char_start=char_pos,
                char_end=char_pos + len(section_text),
                token_count=current_tokens,
            ))
            char_pos += len(section_text)
            segment_id += 1
            current_sentences = []
            current_tokens = 0

        current_sentences.append(sentence)
        current_tokens += token_count

    if current_sentences:
        section_text = ' '.join(current_sentences).strip()
        segments.append(Segment(
            id=segment_id,
            label=f'Section {segment_id}',
            text=section_text,
            char_start=char_pos,
            char_end=char_pos + len(section_text),
            token_count=current_tokens,
        ))

    return segments


def segment_semantic(text: str, max_tokens: int = 200) -> list[Segment]:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    
    try:
        sentences = nltk.sent_tokenize(text)
    except Exception:
        sentences = text.split('. ')

    if not sentences:
        return []

    vectorizer = TfidfVectorizer()
    try:
        tfidf_matrix = vectorizer.fit_transform(sentences)
        similarity_matrix = cosine_similarity(tfidf_matrix)
    except Exception:
        return segment_by_sentences(text, max_tokens)

    segments = []
    current_sentences = [sentences[0]]
    current_tokens = len(sentences[0].split())
    segment_id = 1
    char_pos = 0

    for i in range(1, len(sentences)):
        sentence = sentences[i]
        token_count = len(sentence.split())
        
        # Check similarity with previous sentence
        sim = similarity_matrix[i-1][i]
        
        # If similarity is low or chunk is getting too big, break chunk
        if (current_tokens + token_count > max_tokens) or (sim < 0.1 and current_tokens > 50):
            section_text = ' '.join(current_sentences).strip()
            segments.append(Segment(
                id=segment_id,
                label=f'Semantic Chunk {segment_id}',
                text=section_text,
                char_start=char_pos,
                char_end=char_pos + len(section_text),
                token_count=current_tokens,
            ))
            char_pos += len(section_text)
            segment_id += 1
            current_sentences = []
            current_tokens = 0

        current_sentences.append(sentence)
        current_tokens += token_count

    if current_sentences:
        section_text = ' '.join(current_sentences).strip()
        segments.append(Segment(
            id=segment_id,
            label=f'Semantic Chunk {segment_id}',
            text=section_text,
            char_start=char_pos,
            char_end=char_pos + len(section_text),
            token_count=current_tokens,
        ))

    return segments


def segment_contract(text: str) -> list[Segment]:
    from config import settings
    
    if settings.USE_SEMANTIC_CHUNKING:
        segments = segment_semantic(text, settings.MAX_SEGMENT_TOKENS)
    else:
        segments = segment_by_headers(text)
        if not segments:
            segments = segment_by_sentences(text, settings.MAX_SEGMENT_TOKENS)

    if not segments:
        raise ValueError('Contract could not be segmented')

    return segments


def segments_to_dict(segments: list[Segment]) -> list[dict]:
    return [
        {
            'id': s.id,
            'label': s.label,
            'text': s.text,
            'char_start': s.char_start,
            'char_end': s.char_end,
            'token_count': s.token_count,
        }
        for s in segments
    ]