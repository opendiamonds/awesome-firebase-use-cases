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

test.describe('Authentication', () => {
  test('login page renders', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByRole('heading', { name: 'Cloud-360' })).toBeVisible();
    await expect(page.getByRole('button', { name: '登入系統' })).toBeVisible();
  });

  test('rejects wrong credentials and stays on login', async ({ page }) => {
    await login(page, ADMIN.username, 'definitely-wrong-password');
    // Backend returns 401 "帳號或密碼錯誤"; the page shows it and does not navigate.
    await expect(page.getByText('帳號或密碼錯誤')).toBeVisible();
    await expect(page).not.toHaveURL(/\/workspace/);
  });

  test('admin logs in and reaches the workspace', async ({ page }) => {
    await login(page, ADMIN.username, ADMIN.password);
    await expect(page).toHaveURL(/\/workspace/);
    await expect(page.getByText('核心工作區')).toBeVisible();
  });

  test('logout returns to the login screen', async ({ page }) => {
    await login(page, ADMIN.username, ADMIN.password);
    await expect(page).toHaveURL(/\/workspace/);
    await page.getByTitle('登出系統').click();
    await expect(page.getByRole('button', { name: '登入系統' })).toBeVisible();
  });
});

test.describe('Role-based access control', () => {
  test('Platform_Admin sees the admin section', async ({ page }) => {
    await login(page, ADMIN.username, ADMIN.password);
    await expect(page).toHaveURL(/\/workspace/);
    await expect(page.getByText('系統管理')).toBeVisible();
    await expect(page.getByRole('link', { name: '使用者角色' })).toBeVisible();
  });

  test('a Developer does not see the admin section', async ({ page }) => {
    // Register a throwaway user; register assigns role Developer. Username must
    // be unique on this DB and match ^[a-z0-9_]{3,20}$ — derive it from the
    // worker + timestamp so parallel/retried runs never collide.
    const uniq = `dev_${process.env.PW_RUN_ID || 't'}${Date.now().toString().slice(-8)}`;
    await page.goto('/');
    await page.getByRole('button', { name: /立即註冊新帳號/ }).click();
    await page.getByPlaceholder('請輸入您的帳號').fill(uniq);
    await page.getByPlaceholder('請輸入密碼').fill('devpass123');
    await page.getByPlaceholder('請再次輸入密碼').fill('devpass123');
    await page.getByRole('button', { name: '立即註冊並登入' }).click();

    await expect(page).toHaveURL(/\/workspace/);
    // Developer has no J3 permission, so the admin section must be absent.
    await expect(page.getByText('系統管理')).toHaveCount(0);
  });
});
