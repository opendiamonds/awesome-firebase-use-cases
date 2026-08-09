import { test, expect, Page } from '@playwright/test';

// Core UI regression — the flows that must never silently break. Deliberately
// LLM-free: none of these touch A1 architecture generation (that path calls
// OpenRouter, costs money, and is externally flaky). They exercise auth, RBAC
// visibility, and navigation against the ephemeral stack's seeded data.
//
// Seeded by schema_rbac.sql on the fresh test DB: one user, admin / admin123,
// role Platform_Admin. New registrations get role Developer.

const ADMIN = { username: 'admin', password: 'admin123' };

async function login(page: Page, username: string, password: string) {
  await page.goto('/');
  await page.getByPlaceholder('請輸入您的帳號').fill(username);
  await page.getByPlaceholder('請輸入密碼').fill(password);
  await page.getByRole('button', { name: '登入系統' }).click();
}

test.describe('身分驗證', () => {
  test('登入頁正常顯示', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByRole('heading', { name: 'Cloud-360' })).toBeVisible();
    await expect(page.getByRole('button', { name: '登入系統' })).toBeVisible();
  });

  test('錯誤密碼被拒並停留在登入頁', async ({ page }) => {
    await login(page, ADMIN.username, 'definitely-wrong-password');
    // Backend returns 401 "帳號或密碼錯誤"; the page shows it and does not navigate.
    await expect(page.getByText('帳號或密碼錯誤')).toBeVisible();
    await expect(page).not.toHaveURL(/\/workspace/);
  });

  test('管理員登入後進入工作區', async ({ page }) => {
    await login(page, ADMIN.username, ADMIN.password);
    await expect(page).toHaveURL(/\/workspace/);
    await expect(page.getByRole('button', { name: '架構', exact: true })).toBeVisible();
  });

  test('登出後返回登入頁', async ({ page }) => {
    await login(page, ADMIN.username, ADMIN.password);
    await expect(page).toHaveURL(/\/workspace/);
    await page.getByTitle('登出系統').click();
    await expect(page.getByRole('button', { name: '登入系統' })).toBeVisible();
  });
});

test.describe('角色權限存取控制 (RBAC)', () => {
  test('Platform_Admin 看得到系統管理區', async ({ page }) => {
    await login(page, ADMIN.username, ADMIN.password);
    await expect(page).toHaveURL(/\/workspace/);
    await expect(page.getByText('系統管理')).toBeVisible();
    await expect(page.getByRole('link', { name: '使用者角色' })).toBeVisible();
  });

  test('Developer 看不到系統管理區', async ({ page }) => {
    // Log in as pre-seeded Developer persona 'ian' to verify RBAC restrictions
    await login(page, 'ian', 'ian123');
    await expect(page).toHaveURL(/\/workspace/);
    // Developer has no J3 permission, so the admin section must be absent.
    await expect(page.getByText('系統管理')).toHaveCount(0);
  });
});
