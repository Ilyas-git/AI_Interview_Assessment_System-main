"""
NLP Analysis Service for Interview Assessment
Provides scoring for clarity, relevance, confidence, and overall performance
"""
import re
from collections import Counter


# Filler words that indicate lack of confidence
FILLER_WORDS = [
    "uh", "um", "ah", "eh", "umm", "uuh", "umh", "hmm", "like", 
    "you know", "basically", "actually", "literally", "right", 
    "i mean", "sort of", "kind of", "well"
]

# Technical terms that indicate domain knowledge
TECHNICAL_TERMS = [
    "tensorflow", "keras", "pytorch", "cnn", "rnn", "lstm", "transformer",
    "conv2d", "maxpooling", "mobilenet", "efficientnet", "vgg16", "vgg19",
    "resnet", "bert", "gpt", "attention", "embedding", "dropout", "batch",
    "epoch", "learning rate", "optimizer", "adam", "sgd", "loss function",
    "accuracy", "precision", "recall", "f1", "auc", "roc", "confusion matrix",
    "overfitting", "underfitting", "regularization", "cross validation",
    "train", "validation", "test", "dataset", "preprocessing", "augmentation",
    "smote", "normalization", "standardization", "feature", "model", "layer",
    "neuron", "activation", "relu", "sigmoid", "softmax", "gradient",
    "backpropagation", "forward pass", "inference", "deployment", "api",
    "machine learning", "deep learning", "neural network", "classification",
    "regression", "clustering", "nlp", "computer vision", "object detection"
]


def count_filler_words(text: str) -> dict:
    """Count occurrences of filler words in text"""
    text_lower = text.lower()
    filler_counts = {}
    total_fillers = 0
    
    for filler in FILLER_WORDS:
        # Use word boundary matching
        pattern = r'\b' + re.escape(filler) + r'\b'
        count = len(re.findall(pattern, text_lower))
        if count > 0:
            filler_counts[filler] = count
            total_fillers += count
    
    return {
        "counts": filler_counts,
        "total": total_fillers
    }


def count_technical_terms(text: str) -> dict:
    """Count occurrences of technical terms in text"""
    text_lower = text.lower()
    term_counts = {}
    total_terms = 0
    
    for term in TECHNICAL_TERMS:
        pattern = r'\b' + re.escape(term) + r'\b'
        count = len(re.findall(pattern, text_lower))
        if count > 0:
            term_counts[term] = count
            total_terms += count
    
    return {
        "counts": term_counts,
        "total": total_terms,
        "unique": len(term_counts)
    }


def calculate_clarity_score(text: str) -> dict:
    """
    Calculate clarity score based on:
    - Sentence structure (avg words per sentence)
    - Word variety (unique words ratio)
    - No excessive repetition
    """
    words = text.lower().split()
    word_count = len(words)
    
    if word_count == 0:
        return {"score": 0, "feedback": "No text provided"}
    
    # Count sentences
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    sentence_count = max(len(sentences), 1)
    
    # Average words per sentence (ideal: 15-25)
    avg_words_per_sentence = word_count / sentence_count
    
    # Word variety (unique/total ratio)
    unique_words = len(set(words))
    variety_ratio = unique_words / word_count
    
    # Calculate score components
    # Sentence length score (penalize too short or too long)
    if 10 <= avg_words_per_sentence <= 30:
        sentence_score = 100
    elif avg_words_per_sentence < 10:
        sentence_score = max(50, avg_words_per_sentence * 10)
    else:
        sentence_score = max(50, 100 - (avg_words_per_sentence - 30) * 2)
    
    # Variety score
    variety_score = min(100, variety_ratio * 200)
    
    # Word count bonus (more content = better, up to a point)
    if word_count >= 50:
        length_score = 100
    else:
        length_score = (word_count / 50) * 100
    
    # Combined score
    clarity_score = (sentence_score * 0.3 + variety_score * 0.4 + length_score * 0.3)
    clarity_score = min(100, max(0, clarity_score))
    
    # Generate feedback
    feedback = []
    if word_count < 30:
        feedback.append("Try to provide more detailed responses")
    if variety_ratio < 0.4:
        feedback.append("Consider using more varied vocabulary")
    if avg_words_per_sentence > 40:
        feedback.append("Consider breaking long sentences into shorter ones")
    
    return {
        "score": round(clarity_score, 1),
        "word_count": word_count,
        "sentence_count": sentence_count,
        "avg_words_per_sentence": round(avg_words_per_sentence, 1),
        "vocabulary_variety": round(variety_ratio * 100, 1),
        "feedback": feedback if feedback else ["Good clarity in your response"]
    }


def calculate_confidence_score(text: str) -> dict:
    """
    Calculate confidence score based on:
    - Filler word frequency (fewer = more confident)
    - Assertive language usage
    """
    words = text.lower().split()
    word_count = len(words)
    
    if word_count == 0:
        return {"score": 0, "feedback": "No text provided"}
    
    # Count fillers
    filler_info = count_filler_words(text)
    filler_ratio = filler_info["total"] / word_count
    
    # Score calculation (fewer fillers = higher score)
    # 0% fillers = 100, 10%+ fillers = 0
    confidence_score = max(0, 100 - (filler_ratio * 1000))
    
    # Check for hedging phrases
    hedging_phrases = ["i think", "maybe", "probably", "i guess", "not sure", "might be"]
    hedging_count = sum(1 for phrase in hedging_phrases if phrase in text.lower())
    confidence_score -= hedging_count * 5
    
    confidence_score = min(100, max(0, confidence_score))
    
    # Generate feedback
    feedback = []
    if filler_info["total"] > 3:
        top_fillers = sorted(filler_info["counts"].items(), key=lambda x: x[1], reverse=True)[:3]
        feedback.append(f"Reduce filler words like: {', '.join([f[0] for f in top_fillers])}")
    if hedging_count > 2:
        feedback.append("Try to be more assertive in your statements")
    
    return {
        "score": round(confidence_score, 1),
        "filler_words": filler_info,
        "feedback": feedback if feedback else ["You speak with good confidence"]
    }


def calculate_relevance_score(text: str, question: str = None) -> dict:
    """
    Calculate relevance score based on:
    - Technical term usage
    - Topic coverage
    """
    words = text.lower().split()
    word_count = len(words)
    
    if word_count == 0:
        return {"score": 0, "feedback": "No text provided"}
    
    # Count technical terms
    tech_info = count_technical_terms(text)
    
    # Score based on technical term density and variety
    # Bonus for unique technical terms used
    term_density = tech_info["total"] / word_count
    unique_bonus = min(30, tech_info["unique"] * 3)
    
    # Base score from density (higher density = more technical)
    base_score = min(70, term_density * 500)
    
    relevance_score = base_score + unique_bonus
    relevance_score = min(100, max(0, relevance_score))
    
    # Generate feedback
    feedback = []
    if tech_info["unique"] < 3:
        feedback.append("Try to incorporate more technical concepts in your answer")
    if word_count < 50:
        feedback.append("Provide more detailed explanation of technical concepts")
    
    return {
        "score": round(relevance_score, 1),
        "technical_terms": tech_info,
        "feedback": feedback if feedback else ["Good use of technical terminology"]
    }


def analyze_interview_response(text: str, question: str = None) -> dict:
    """
    Full NLP analysis of interview response
    Returns comprehensive scoring and feedback
    """
    # Calculate individual scores
    clarity = calculate_clarity_score(text)
    confidence = calculate_confidence_score(text)
    relevance = calculate_relevance_score(text, question)
    
    # Calculate overall score (weighted average)
    overall_score = (
        clarity["score"] * 0.3 +
        confidence["score"] * 0.3 +
        relevance["score"] * 0.4
    )
    
    # Generate overall feedback
    overall_feedback = []
    if overall_score >= 80:
        overall_feedback.append("Excellent response! Well-structured and confident.")
    elif overall_score >= 60:
        overall_feedback.append("Good response with room for improvement.")
    elif overall_score >= 40:
        overall_feedback.append("Satisfactory response. Consider the feedback below.")
    else:
        overall_feedback.append("Needs improvement. Focus on the areas highlighted.")
    
    # Combine all feedback
    all_feedback = {
        "clarity": clarity["feedback"],
        "confidence": confidence["feedback"],
        "relevance": relevance["feedback"],
        "overall": overall_feedback
    }
    
    return {
        "scores": {
            "clarity": clarity["score"],
            "confidence": confidence["score"],
            "relevance": relevance["score"],
            "overall": round(overall_score, 1)
        },
        "details": {
            "clarity": clarity,
            "confidence": confidence,
            "relevance": relevance
        },
        "feedback": all_feedback
    }
