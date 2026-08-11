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

// 使用者管理頁的回歸 —— 本專案**第一批**進入該頁的 e2e case（team-practices
// 測試底線 C）。這條路徑上原本沒有任何自動化斷言：`tsc -b` 對後端回應形狀無感、
// 既有六個 case 無一導覽至此，所以「後端漏欄位 → 前端渲染成空白」不會被發現。
//
// seed 只有 admin 一個帳號，湊不出第二頁；需要多頁的 case 以公開註冊端點自行
// 建立帳號（既有的「Developer 看不到系統管理區」已示範同一手法）。
test.describe('使用者管理頁 — 最後活動時間與分頁', () => {
  async function gotoAdmin(page: Page) {
    await login(page, ADMIN.username, ADMIN.password);
    await expect(page).toHaveURL(/\/workspace/);
    await page.getByRole('link', { name: '使用者角色' }).click();
    await expect(page.getByRole('heading', { name: '使用者角色指派' })).toBeVisible();
  }

  /** 以公開註冊端點建立一個帳號（不經 UI，比逐次填表快得多）。 */
  async function registerUser(page: Page, username: string) {
    const res = await page.request.post('/api/auth/register', {
      data: { username, password: 'pagepass123', requested_role: 'Developer' },
    });
    if (!res.ok()) throw new Error(`註冊 ${username} 失敗：${res.status()} ${await res.text()}`);
  }

  test('表格出現最後活動時間欄，且該欄有值或無紀錄破折號', async ({ page }) => {
    await gotoAdmin(page);
    await expect(
      page.getByRole('columnheader', { name: '最後活動時間' })
    ).toBeVisible();

    // admin 剛登入過，其最後活動時間必定已被記錄 —— 斷言的是**具體的時間值**，
    // 不是「有值或破折號都算過」（後者對任何實作都恆真）。
    const adminRow = page.getByRole('row').filter({ hasText: ADMIN.username }).first();
    await expect(adminRow.getByText(/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/)).toBeVisible();
  });

  test('分頁控制可見且顯示總筆數與目前頁次', async ({ page }) => {
    await gotoAdmin(page);
    const pager = page.getByRole('navigation', { name: '使用者清單分頁' });
    await expect(pager).toBeVisible();
    await expect(pager.getByText(/\d+ 筆/)).toBeVisible();
    // 目前頁次以 aria-current 標示，且**不只靠顏色** —— 方括號是非色彩線索。
    await expect(pager.locator('[aria-current="page"]')).toHaveText('[1]');
  });

  test('切換到第 2 頁取得不重複的帳號，且處置後仍停在第 2 頁', async ({ page }) => {
    // 每頁 20 筆，故需要 21 個以上的帳號才會有第 2 頁（seed 已有 admin）。
    const rid = (process.env.PW_RUN_ID || '0').replace(/\D/g, '').slice(-3);
    const stamp = Date.now().toString(36);
    await page.goto('/');
    for (let i = 0; i < 21; i += 1) {
      await registerUser(page, `pg${rid}${stamp}${i.toString(36)}`.slice(0, 20));
    }

    await gotoAdmin(page);
    const pager = page.getByRole('navigation', { name: '使用者清單分頁' });

    const firstPageNames = await page.getByRole('row').allInnerTexts();
    await pager.getByRole('button', { name: '2', exact: true }).click();
    await expect(pager.locator('[aria-current="page"]')).toHaveText('[2]');

    const secondPageNames = await page.getByRole('row').allInnerTexts();
    expect(secondPageNames).not.toEqual(firstPageNames);

    // AC-5.6：在第 2 頁停用一個帳號後，畫面**仍在第 2 頁**。現行實作若沿用整份
    // 重抓（`fetchUsers()`），這條會紅 —— 那正是本斷言存在的理由。
    const firstToggle = page.getByRole('button', { name: '停用' }).first();
    await firstToggle.click();
    // 只斷言 toast（「✔ 已停用 <帳號>」），不要用會同時命中表格內狀態文字的
    // 寬鬆比對 —— 後者在 strict mode 下會撞到三個元素。
    await expect(page.getByText(/^✔ 已停用 /)).toBeVisible();
    await expect(pager.locator('[aria-current="page"]')).toHaveText('[2]');
  });

  test('角色調整仍可用且不影響最後活動時間欄（NFR-7 回歸）', async ({ page }) => {
    // reviewer Iteration 2 的新發現 N4：文件宣稱桌面 e2e 已涵蓋 NFR-7 的三項既有
    // 操作，實際只有「啟停用」。這裡補上「角色調整」——它是本 intent 動到的三個
    // 回應構造點之一，且既有的 requested_role 漏傳正是發生在這條路徑上。
    await gotoAdmin(page);
    const row = page.getByRole('row').filter({ hasText: ADMIN.username }).first();
    // 只能在**保有 J3a:edit 的角色之間**切換：後端拒絕把最後一位可編輯使用者
    // 角色的管理員降權（`user_router.py` 的 admin_edit_count 檢查），而 seed 的
    // 測試環境只有 admin 一個已核准帳號。Project_Admin 與 Platform_Admin 是預設
    // 矩陣中僅有的兩個 J3a:edit 角色，故在這兩者之間來回。
    await row.getByRole('combobox').selectOption('Project_Admin');
    await expect(page.getByText(/^✔ 已更新 /)).toBeVisible();
    // 關鍵斷言：角色調整後該列的最後活動時間**不得變成空白**。既有的
    // requested_role 就是在這個端點漏傳的，新欄位比照現行寫法會複製同一缺陷。
    await expect(row.getByText(/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/)).toBeVisible();
    await row.getByRole('combobox').selectOption('Platform_Admin');
    await expect(page.getByText(/^✔ 已更新 /)).toBeVisible();
  });

  test('切頁期間分頁控制不消失，且鍵盤可達可觸發（AC-5.9／AC-5.10）', async ({ page }) => {
    const rid = (process.env.PW_RUN_ID || '0').replace(/\D/g, '').slice(-3);
    const stamp = Date.now().toString(36);
    await page.goto('/');
    for (let i = 0; i < 21; i += 1) {
      await registerUser(page, `kb${rid}${stamp}${i.toString(36)}`.slice(0, 20));
    }
    await gotoAdmin(page);
    const pager = page.getByRole('navigation', { name: '使用者清單分頁' });

    // AC-5.9：頁碼按鈕可用鍵盤到達並**觸發**（不只是可聚焦）。
    const pageTwo = pager.getByRole('button', { name: '2', exact: true });
    await pageTwo.focus();
    await expect(pageTwo).toBeFocused();

    // AC-5.10：切頁期間控制項**仍在畫面上**。刻意延遲清單回應，在回應抵達前
    // 斷言 nav 仍然存在 —— 若控制項被放在會被整塊替換的容器內，這裡會失敗。
    await page.route('**/api/auth/list**', async (route) => {
      await new Promise((r) => setTimeout(r, 1200));
      await route.continue();
    });
    await pageTwo.press('Enter');
    await expect(pager).toBeVisible();
    await expect(pager).toHaveAttribute('aria-busy', 'true');
    await page.unroute('**/api/auth/list**');
    await expect(pager.locator('[aria-current="page"]')).toHaveText('[2]');
  });

  test('刪除後仍停在原頁次，且清單重新同步（AC-5.6 的刪除子句）', async ({ page }) => {
    const rid = (process.env.PW_RUN_ID || '0').replace(/\D/g, '').slice(-3);
    const stamp = Date.now().toString(36);
    await page.goto('/');
    for (let i = 0; i < 21; i += 1) {
      await registerUser(page, `dl${rid}${stamp}${i.toString(36)}`.slice(0, 20));
    }
    await gotoAdmin(page);
    const pager = page.getByRole('navigation', { name: '使用者清單分頁' });
    await pager.getByRole('button', { name: '2', exact: true }).click();
    await expect(pager.locator('[aria-current="page"]')).toHaveText('[2]');

    const totalBefore = Number(
      ((await pager.getByText(/\d+ 筆/).innerText()).match(/(\d+)/) || ['0'])[0]
    );

    // 刪除鈕只在帳號已停用後出現，故先停用再刪除。停用沒有確認對話框，只有
    // 刪除有 —— 為停用也掛一個 once handler 會讓它殘留到刪除時重複處理。
    await page.getByRole('button', { name: '停用' }).first().click();
    await expect(page.getByText(/^✔ 已停用 /)).toBeVisible();
    page.once('dialog', (d) => d.accept());
    await page.getByRole('button', { name: '刪除' }).first().click();
    await expect(page.getByText(/^✔ 已刪除 /)).toBeVisible();

    // AC-5.6：頁次不變（現行的整份重抓會把使用者拉回第 1 頁 —— 這條就是要抓它）。
    await expect(pager.locator('[aria-current="page"]')).toHaveText('[2]');
    // 總筆數本地遞減，且背景重抓完成後仍然一致。
    await expect(pager.getByText(new RegExp(`${totalBefore - 1} 筆`))).toBeVisible();
  });

  test('超出範圍的頁次顯示空態並可回到第 1 頁（AC-5.4 的 UI 子句）', async ({ page }) => {
    await gotoAdmin(page);
    // 直接讓清單端點回一個超出範圍的頁 —— seed 只有 admin，第 5 頁必為空。
    await page.route('**/api/auth/list**', async (route) => {
      const url = new URL(route.request().url());
      url.searchParams.set('page', '5');
      await route.continue({ url: url.toString() });
    });
    await page.reload();
    await expect(page.getByText('這一頁沒有資料。')).toBeVisible();
    const pager = page.getByRole('navigation', { name: '使用者清單分頁' });
    // 空態下**分頁控制仍在畫面上**（因為它在容器之外），且提供回到第 1 頁。
    await expect(pager).toBeVisible();
    await page.unroute('**/api/auth/list**');
    await page.getByRole('button', { name: '回到第 1 頁' }).click();
    await expect(page.getByText('這一頁沒有資料。')).toHaveCount(0);
  });

  test('小螢幕改為卡片佈局，分頁控制仍可用', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await gotoAdmin(page);
    // 斷點以下：表格隱藏、卡片出現。
    await expect(page.getByRole('table')).toBeHidden();
    await expect(page.getByText('最後活動', { exact: true }).first()).toBeVisible();
    const pager = page.getByRole('navigation', { name: '使用者清單分頁' });
    await expect(pager).toBeVisible();
    // AC-5.7：小螢幕也必須能**跳至特定頁次**（不只逐頁前後移動），且呈現總筆數。
    // 目前頁碼帶方括號（非色彩線索）；單頁時它是唯一的頁碼按鈕，且**呈現但停用**。
    const currentPage = pager.locator('[aria-current="page"]');
    await expect(currentPage).toBeVisible();
    await expect(currentPage).toHaveText('[1]');
    await expect(pager.getByText(/\d+ 筆/)).toBeVisible();
  });
});
