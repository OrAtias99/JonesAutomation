# Jones Automation Exercise

## Part A - Playwright automation (JavaScript)

Automation for the "Request a call back" form at https://test.netlify.app/

### What the test does
1. Fills in Name, Email, Phone, Company and Website
2. Changes Number of Employees from 1-10 to 51-500
3. Takes a screenshot (before-submit.png) before submitting
4. Clicks "Request a call back"
5. Waits for the thank-you page and logs to the console
6. Verifies that every field value was sent correctly in the URL

### How to run
    npm install
    npx playwright install chromium
    npx playwright test --headed

The test file is in tests/callback.spec.js.

## Part B - QA analysis

- Jones_Automation_Exercise_Part_B.pdf: bug analysis of the billing UI mock-up, sample test cases and a product solution.
- test_payment_form.py: the sample test cases in Python (pytest + Playwright).
  Only a mock-up image was provided, so the tests target a placeholder URL and
  assumed selectors. They are expected to fail until pointed at a real environment.

### How to run (Python)
    pip install pytest pytest-playwright
    playwright install chromium
    pytest test_payment_form.py --headed
