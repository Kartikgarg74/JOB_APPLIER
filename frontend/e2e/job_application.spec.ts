import { test, expect } from '@playwright/test';

test.describe('Job Application E2E Flow', () => {
  test('user can login, upload resume, search jobs, and apply', async ({ page }) => {
    // Go to login page
    await page.goto('/login');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/');

    // Upload resume
    await page.goto('/resume-editor');
    const fileChooserPromise = page.waitForEvent('filechooser');
    await page.click('input[type="file"]');
    const fileChooser = await fileChooserPromise;
    await fileChooser.setFiles('fixtures/test_resume.pdf');
    await expect(page.locator('text=Resume uploaded')).toBeVisible();

    // Search jobs
    await page.goto('/jobs');
    await page.fill('input[placeholder="Search jobs"]', 'Software Engineer');
    await page.click('button[type="submit"]');
    await expect(page.locator('text=Software Engineer')).toBeVisible();

    // Apply to a job
    await page.click('text=Apply');
    await expect(page.locator('text=Application submitted')).toBeVisible();
  });
});
