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
    // 1. 註冊新帳號 dev_xxx
    const rid = (process.env.PW_RUN_ID || '0').replace(/\D/g, '').slice(-4);
    const uniq = `dev_${rid}${Date.now().toString(36)}`.slice(0, 20);
    await page.goto('/');
    await page.getByRole('button', { name: /立即註冊新帳號/ }).click();
    await page.getByPlaceholder('請輸入您的帳號').fill(uniq);
    await page.getByPlaceholder('請輸入密碼').fill('devpass123');
    await page.getByPlaceholder('請再次輸入密碼').fill('devpass123');
    await page.getByRole('button', { name: '送出註冊申請' }).click();

    // 2. 註冊後會跳至 /waiting-approval 等待審核頁
    await expect(page).toHaveURL(/\/waiting-approval/);

    // 3. 登出並以系統管理員身分登入以審核該申請
    await page.getByRole('button', { name: '登出' }).click();
    await login(page, ADMIN.username, ADMIN.password);
    await expect(page).toHaveURL(/\/workspace/);

    // 4. 前往審核頁面進行核准
    await page.goto('/admin/authorization-requests');
    // 監聽並自動接受 confirm 彈窗
    page.once('dialog', dialog => dialog.accept());
    // 定位含有該使用者帳號的表格列，點擊其核准按鈕
    const row = page.locator('tr').filter({ hasText: uniq });
    await row.getByRole('button', { name: '核准' }).click();
    // 等待 Toast 成功訊息出現
    await expect(page.getByText(/已核准/)).toBeVisible();

    // 5. 登出管理員，改用已核准的 Developer 登入
    await page.getByTitle('登出系統').click();
    await login(page, uniq, 'devpass123');
    await expect(page).toHaveURL(/\/workspace/);

    // 6. 驗證 Developer 權限：看不到系統管理區
    await expect(page.getByText('系統管理')).toHaveCount(0);
  });
});
