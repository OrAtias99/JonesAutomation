import { test, expect } from '@playwright/test';

test('request a call back flow', async ({ page }) => {
  // Test data: defined once, used for both filling and verifying
  const data = {
    name: 'John Smith',
    email: 'john.smith@example.com',
    phone: '0522316980',
    company: 'Test Company',
    website: 'https://example.com',
    employees: '51-500',
  };

  await page.goto('https://test.netlify.app/');

  // Fill in the form
  await page.getByRole('textbox', { name: 'Name *' }).fill(data.name);
  await page.getByRole('textbox', { name: 'Email *' }).fill(data.email);
  await page.getByRole('textbox', { name: 'Phone *' }).fill(data.phone);
  await page.getByRole('textbox', { name: 'Company' }).fill(data.company);
  await page.getByRole('textbox', { name: 'Website' }).fill(data.website);

  // Bonus: change Number of Employees from 1-10 to 51-500
  await page.getByLabel('Number of Employees').selectOption(data.employees);

  // Screenshot BEFORE clicking the button
  await page.screenshot({ path: 'before-submit.png', fullPage: true });

  await page.getByRole('button', { name: 'Request a call back' }).click();

  // Wait for the thank you page
  await page.waitForURL('**/thank-you.html*');
  await expect(
    page.getByRole('link', { name: 'Back to Home »' })
  ).toBeVisible();

  console.log('Reached the thank you page! URL: ' + page.url());

  // Verify that every field was sent correctly
  const params = new URL(page.url()).searchParams;
  expect(params.get('name')).toBe(data.name);
  expect(params.get('email')).toBe(data.email);
  expect(params.get('phone')).toBe(data.phone);
  expect(params.get('company')).toBe(data.company);
  expect(params.get('website')).toBe(data.website);
  expect(params.get('number_of_employees')).toBe(data.employees);

  console.log('All form fields were sent correctly.');
});