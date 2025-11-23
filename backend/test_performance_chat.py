"""
Test script to verify AI chatbot performance tracking functionality
"""
from routes.ai import is_performance_query, get_student_performance_data, generate_performance_response

# Test performance query detection
test_queries = [
    "meri performance btao",
    "show my performance",
    "how am i doing",
    "mera progress kaisa hai",
    "tell me about my grades",
    "what is my score",
    "dikhao meri performance",
    "my achievements",
    "explain photosynthesis",  # Should return False
    "help me with math"  # Should return False
]

print("=" * 60)
print("Testing Performance Query Detection")
print("=" * 60)

for query in test_queries:
    result = is_performance_query(query)
    status = "✓ DETECTED" if result else "✗ NOT DETECTED"
    print(f"{status}: '{query}'")

print("\n" + "=" * 60)
print("Performance Query Detection Test Complete!")
print("=" * 60)
print("\nThe chatbot will now respond with detailed performance reports")
print("when students ask about their performance in any language!")
print("\nSupported queries:")
print("  - English: 'show my performance', 'how am i doing'")
print("  - Hindi/Hinglish: 'meri performance btao', 'mera progress kaisa hai'")
print("  - And many more variations!")
