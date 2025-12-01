"""
Shared BDD step definitions used across multiple feature files.

Includes error message handling and other common verification steps.
"""

from behave import then


@then("error message contains \"{expected_text}\"")
def step_error_message_contains(context, expected_text):
    """Verify error message contains expected text (single or alternative separated by 'or')"""
    # Check stderr first, then stdout (some errors go to stdout)
    error_output = getattr(context, 'stderr', '') or getattr(context, 'stdout', '') or getattr(context, 'error_message', '')

    # Handle "text1" or "text2" pattern
    texts = [t.strip() for t in expected_text.split(' or ')]
    found = any(text.lower() in error_output.lower() for text in texts)

    assert found, \
        f"Expected error to contain any of {texts}. Got: {error_output}"
