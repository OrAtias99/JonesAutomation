"""
Part B - Sample test cases for the "Account Information" payment form.

=============================================================================
IMPORTANT NOTES (READ BEFORE RUNNING)
=============================================================================

1. NO LIVE PAGE WAS PROVIDED
   The exercise included only a UI mock-up image, not a live page.
   BASE_URL and every selector in SEL are ASSUMPTIONS based on the labels
   visible in the mock-up. These tests are expected to FAIL until they are
   pointed at a real environment. They are submitted as ready-to-run code,
   not as passing tests.

2. EXPECTED RESULTS
   Expected results follow standard payment-form behavior, since no
   requirements document was provided.

3. LANGUAGES
   Part A of the exercise (Playwright automation) is written in JavaScript.
   Part B (these sample test cases) is written in Python (pytest + Playwright).

=============================================================================
HOW TO RUN WITH REAL DETAILS
=============================================================================

Setup (once):
    pip install pytest pytest-playwright
    playwright install chromium

Run (headed, so the browser is visible):
    pytest test_payment_form.py --headed

Run a single test:
    pytest test_payment_form.py -k tc02 --headed

Before running against a real environment, update these in ONE place:
    a. BASE_URL  - replace the placeholder with the real payment page URL.
    b. SEL       - the values are label texts used with get_by_label().
                   If the real labels differ (e.g. "Card number" vs
                   "Card Number (No dashes or spaces)"), change them here.
                   If a field has no <label>, switch field() to another
                   locator (get_by_placeholder, get_by_role, or a
                   data-testid / id selector).
    c. Dropdown option values - select_option() may need the option's
       "value" or its visible "label". Check the real HTML:
           * Month: "01" vs "1" vs "January"
           * Year:  "2027" vs "27"
           * State: select by label="New York" or by value="NY"
    d. Error marking - the tests assume an invalid field gets
       aria-invalid="true" and that an error text containing "expired"
       is shown. If the real site marks errors differently (CSS class,
       different wording), change those assertions only.
    e. Success criteria in TC-01 - the test assumes the URL changes after
       a successful submit. If the real flow shows a confirmation message
       on the same URL, assert on that message instead.

Test data:
    VALID_CARD (4111111111111111) is a standard Visa TEST number that passes
    Luhn validation. Never use real card numbers in automated tests.
    If the environment is connected to a real payment processor, use that
    processor's official sandbox test cards instead.

=============================================================================
DESIGN NOTES
=============================================================================

- fill_valid_form() is a helper so the same lines are not repeated in
  every test.
- TC-02 uses datetime.date.today() so the "expired month" is calculated
  dynamically and the test never goes stale.
- In January there is no earlier month in the current year, so TC-02 is
  explicitly skipped instead of failing for the wrong reason.
  (An alternative is to use last year with any month.)
- Each test checks one thing, so when a test fails it is clear what broke.
- In TC-03 the expect() calls carry a message, so a failure shows exactly
  which field was not flagged.
- Only fields marked with * in the mock-up are checked as required,
  to avoid inventing requirements.
"""
import datetime

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://example.com/payment"  # TODO: replace with the real URL

# All selectors in one place (assumed, based on the mock-up labels)
SEL = {
    "card_type": "Card Type",
    "card_number": "Card Number",
    "exp_month": "Month",
    "exp_year": "Year",
    "first_name": "First Name",
    "last_name": "Last Name",
    "street": "Credit Card Billing Street Address",
    "city": "City",
    "state": "State or Province",
    "postal": "Postal Code",
    "payment_amount": "Payment Amount",
}

# Standard Visa TEST number (passes Luhn). Never use real cards in tests.
VALID_CARD = "4111111111111111"

REQUIRED_FIELDS = [
    "card_type", "card_number", "exp_month", "exp_year",
    "first_name", "last_name", "street", "city", "state", "postal",
]


@pytest.fixture
def form(page: Page) -> Page:
    """Open the payment screen before each test."""
    page.goto(BASE_URL)
    return page


def field(page: Page, key: str):
    """Locate a form field by its label (see SEL)."""
    return page.get_by_label(SEL[key])


def fill_valid_form(page: Page, month: int, year: int) -> None:
    """Fill every required field with valid data."""
    field(page, "card_type").select_option(label="VISA")
    field(page, "card_number").fill(VALID_CARD)
    field(page, "exp_month").select_option(f"{month:02d}")
    field(page, "exp_year").select_option(str(year))
    field(page, "first_name").fill("John")
    field(page, "last_name").fill("Smith")
    field(page, "street").fill("1 Main St")
    field(page, "city").fill("New York")
    field(page, "state").select_option(label="New York")
    field(page, "postal").fill("10001")


def test_tc01_successful_payment_with_valid_details(form: Page):
    """TC-01 (High): Happy path - valid details move the user forward."""
    today = datetime.date.today()
    fill_valid_form(form, month=today.month, year=today.year + 1)

    form.get_by_role("button", name="Continue").click()

    # No validation errors, and the user left the form screen
    expect(form.locator("[aria-invalid='true']")).to_have_count(0)
    expect(form).not_to_have_url(BASE_URL)


def test_tc02_expired_card_is_rejected(form: Page):
    """TC-02 (High): Negative - expiration month already passed this year."""
    today = datetime.date.today()
    if today.month == 1:
        pytest.skip("No earlier month exists in January of the current year")

    expired_month = today.month - 1
    fill_valid_form(form, month=expired_month, year=today.year)

    form.get_by_role("button", name="Continue").click()

    # Payment is blocked: still on the form, expiration flagged
    expect(form).to_have_url(BASE_URL)
    expect(field(form, "exp_month")).to_have_attribute("aria-invalid", "true")
    expect(form.get_by_text("expired", exact=False)).to_be_visible()
    # Data in other fields is preserved
    expect(field(form, "first_name")).to_have_value("John")
    expect(field(form, "city")).to_have_value("New York")


def test_tc03_required_fields_left_empty(form: Page):
    """TC-03 (Medium): Negative - submit with all required fields empty."""
    form.get_by_role("button", name="Continue").click()

    # Form is not submitted
    expect(form).to_have_url(BASE_URL)
    # Every required field is flagged as invalid
    for key in REQUIRED_FIELDS:
        expect(field(form, key), f"{key} should be flagged").to_have_attribute(
            "aria-invalid", "true"
        )