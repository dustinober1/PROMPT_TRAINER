import { expect, test, type Page, type Route } from '@playwright/test';

type ScoringType = 'yes_no' | 'meets' | 'numerical';

interface Criterion {
  id: number;
  rubric_id: number;
  name: string;
  description?: string;
  order: number;
}

interface Rubric {
  id: number;
  name: string;
  scoring_type: ScoringType;
  created_at: string;
  criteria: Criterion[];
}

interface Paper {
  id: number;
  title: string;
  content: string;
  rubric_id: number | null;
  rubric_name: string | null;
  submission_date: string;
  created_at: string;
}

interface Evaluation {
  id: number;
  paper_id: number;
  paper_title: string;
  rubric_id: number;
  rubric_name: string;
  rubric_scoring_type: ScoringType;
  prompt_id: number;
  model_response: {
    evaluations: Array<{
      criterion_id: number;
      criterion_name: string;
      score: string;
      reasoning: string;
    }>;
  };
  is_correct: boolean | null;
  created_at: string;
  feedback: Array<{
    id: number;
    evaluation_id: number;
    rubric_id: number;
    criterion_id: number;
    model_score: string;
    user_corrected_score: string;
    user_explanation?: string;
    created_at: string;
  }>;
  rubric_criteria: Criterion[];
}

interface Prompt {
  id: number;
  version: number;
  template_text: string;
  parent_version_id: number | null;
  created_at: string;
  is_active: boolean;
}

async function fulfillJson(route: Route, data: unknown, status = 200) {
  await route.fulfill({
    status,
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(data),
  });
}

async function setupSyntheticBackend(page: Page) {
  const now = new Date().toISOString();

  const state: {
    rubrics: Rubric[];
    papers: Paper[];
    evaluations: Evaluation[];
    prompts: Prompt[];
  } = {
    rubrics: [
      {
        id: 1,
        name: 'Default Essay Rubric',
        scoring_type: 'yes_no',
        created_at: now,
        criteria: [
          { id: 101, rubric_id: 1, name: 'Thesis clarity', description: 'States a clear thesis', order: 0 },
          { id: 102, rubric_id: 1, name: 'Evidence', description: 'Supports arguments with evidence', order: 1 },
        ],
      },
    ],
    papers: [],
    evaluations: [],
    prompts: [
      {
        id: 1,
        version: 1,
        template_text: 'Evaluate {{paper_content}} using rubric {{rubric}} and respond with scores.',
        parent_version_id: null,
        created_at: now,
        is_active: true,
      },
    ],
  };

  let rubricIdCounter = state.rubrics.length + 1;
  let criterionIdCounter = 200;
  let paperIdCounter = 1;
  let evaluationIdCounter = 1;
  let feedbackIdCounter = 1;
  let promptIdCounter = 2;

  await page.route('**/health', async (route) => {
    await fulfillJson(route, { status: 'ok', adapter: 'stub' });
  });

  await page.route('**/api/metrics/accuracy', async (route) => {
    const total = state.evaluations.length;
    const correct = state.evaluations.filter((ev) => ev.is_correct === true).length;
    const accuracy_percent = total === 0 ? null : (correct / total) * 100;
    await fulfillJson(route, { total, correct, accuracy_percent, timestamp: now, adapter: 'stub' });
  });

  await page.route('**/api/rubrics/**', async (route) => {
    const url = new URL(route.request().url());
    const path = url.pathname;
    const method = route.request().method();

    if (method === 'GET' && path === '/api/rubrics/') {
      await fulfillJson(route, state.rubrics);
      return;
    }

    if (method === 'GET' && /^\/api\/rubrics\/\d+/.test(path)) {
      const id = Number(path.split('/')[3]);
      const found = state.rubrics.find((r) => r.id === id);
      if (found) {
        await fulfillJson(route, found);
      } else {
        await fulfillJson(route, { detail: 'Not found' }, 404);
      }
      return;
    }

    if (method === 'POST' && path === '/api/rubrics/') {
      const payload = JSON.parse(route.request().postData() || '{}');
      const rubricId = rubricIdCounter++;
      const criteria: Criterion[] = (payload.criteria || []).map((c: Criterion, index: number) => ({
        id: criterionIdCounter++,
        rubric_id: rubricId,
        name: c.name,
        description: c.description,
        order: index,
      }));
      const newRubric: Rubric = {
        id: rubricId,
        name: payload.name,
        scoring_type: payload.scoring_type as ScoringType,
        created_at: new Date().toISOString(),
        criteria,
      };
      state.rubrics.push(newRubric);
      await fulfillJson(route, newRubric, 201);
      return;
    }

    if (method === 'DELETE' && /^\/api\/rubrics\/\d+/.test(path)) {
      const id = Number(path.split('/')[3]);
      state.rubrics = state.rubrics.filter((r) => r.id !== id);
      state.papers = state.papers.map((p) =>
        p.rubric_id === id ? { ...p, rubric_id: null, rubric_name: null } : p
      );
      await fulfillJson(route, { ok: true });
      return;
    }

    await route.continue();
  });

  await page.route('**/api/papers/**', async (route) => {
    const url = new URL(route.request().url());
    const path = url.pathname;
    const method = route.request().method();

    if (method === 'GET' && path === '/api/papers/') {
      await fulfillJson(route, state.papers);
      return;
    }

    if (method === 'POST' && path === '/api/papers/') {
      const payload = JSON.parse(route.request().postData() || '{}');
      const rubric = state.rubrics.find((r) => r.id === payload.rubric_id) || null;
      const paper: Paper = {
        id: paperIdCounter++,
        title: payload.title,
        content: payload.content,
        rubric_id: rubric ? rubric.id : null,
        rubric_name: rubric ? rubric.name : null,
        submission_date: new Date().toISOString(),
        created_at: new Date().toISOString(),
      };
      state.papers.unshift(paper);
      await fulfillJson(route, paper, 201);
      return;
    }

    if (method === 'DELETE' && /^\/api\/papers\/\d+/.test(path)) {
      const id = Number(path.split('/')[3]);
      state.papers = state.papers.filter((p) => p.id !== id);
      await fulfillJson(route, { ok: true });
      return;
    }

    await route.continue();
  });

  await page.route('**/api/evaluations/**', async (route) => {
    const url = new URL(route.request().url());
    const path = url.pathname;
    const method = route.request().method();

    if (method === 'GET' && path === '/api/evaluations/') {
      await fulfillJson(route, state.evaluations);
      return;
    }

    if (method === 'POST' && path === '/api/evaluations/') {
      const payload = JSON.parse(route.request().postData() || '{}');
      const rubric = state.rubrics.find((r) => r.id === payload.rubric_id);
      const paper = state.papers.find((p) => p.id === payload.paper_id);
      if (!rubric || !paper) {
        await fulfillJson(route, { detail: 'Not found' }, 404);
        return;
      }
      const evaluation: Evaluation = {
        id: evaluationIdCounter++,
        paper_id: paper.id,
        paper_title: paper.title,
        rubric_id: rubric.id,
        rubric_name: rubric.name,
        rubric_scoring_type: rubric.scoring_type,
        prompt_id: 1,
        model_response: {
          evaluations: rubric.criteria.map((criterion) => ({
            criterion_id: criterion.id,
            criterion_name: criterion.name,
            score: 'yes',
            reasoning: `Synthetic reasoning for ${criterion.name}`,
          })),
        },
        is_correct: null,
        created_at: new Date().toISOString(),
        feedback: [],
        rubric_criteria: rubric.criteria,
      };
      state.evaluations.unshift(evaluation);
      await fulfillJson(route, evaluation, 201);
      return;
    }

    if (method === 'PATCH' && /^\/api\/evaluations\/\d+\/feedback/.test(path)) {
      const id = Number(path.split('/')[3]);
      const evaluation = state.evaluations.find((ev) => ev.id === id);
      const isCorrect = url.searchParams.get('is_correct') === 'true';
      if (evaluation) {
        evaluation.is_correct = isCorrect;
        await fulfillJson(route, evaluation);
      } else {
        await fulfillJson(route, { detail: 'Not found' }, 404);
      }
      return;
    }

    if (method === 'POST' && /^\/api\/evaluations\/\d+\/feedback/.test(path)) {
      const id = Number(path.split('/')[3]);
      const evaluation = state.evaluations.find((ev) => ev.id === id);
      if (!evaluation) {
        await fulfillJson(route, { detail: 'Not found' }, 404);
        return;
      }
      const payload = JSON.parse(route.request().postData() || '{}');
      const entry = {
        id: feedbackIdCounter++,
        evaluation_id: evaluation.id,
        rubric_id: evaluation.rubric_id,
        criterion_id: payload.criterion_id,
        model_score: payload.model_score || 'yes',
        user_corrected_score: payload.user_corrected_score,
        user_explanation: payload.user_explanation,
        created_at: new Date().toISOString(),
      };
      evaluation.feedback.push(entry);
      await fulfillJson(route, entry, 201);
      return;
    }

    await route.continue();
  });

  await page.route('**/api/prompts/**', async (route) => {
    const url = new URL(route.request().url());
    const path = url.pathname;
    const method = route.request().method();

    if (method === 'GET' && path === '/api/prompts/') {
      await fulfillJson(route, state.prompts);
      return;
    }

    if (method === 'PUT' && /^\/api\/prompts\/\d+/.test(path)) {
      const id = Number(path.split('/')[3]);
      const prompt = state.prompts.find((p) => p.id === id);
      const payload = JSON.parse(route.request().postData() || '{}');
      if (prompt) {
        prompt.template_text = payload.template_text ?? prompt.template_text;
        await fulfillJson(route, prompt);
      } else {
        await fulfillJson(route, { detail: 'Not found' }, 404);
      }
      return;
    }

    if (method === 'POST' && path === '/api/prompts/') {
      const payload = JSON.parse(route.request().postData() || '{}');
      const prompt: Prompt = {
        id: promptIdCounter++,
        version: state.prompts.length + 1,
        template_text: payload.template_text,
        parent_version_id: payload.parent_version_id ?? null,
        created_at: new Date().toISOString(),
        is_active: !!payload.is_active,
      };
      state.prompts = state.prompts.map((p) => ({ ...p, is_active: false }));
      state.prompts.push(prompt);
      await fulfillJson(route, prompt, 201);
      return;
    }

    if (method === 'POST' && /^\/api\/prompts\/\d+\/activate/.test(path)) {
      const id = Number(path.split('/')[3]);
      state.prompts = state.prompts.map((p) => ({ ...p, is_active: p.id === id }));
      const prompt = state.prompts.find((p) => p.id === id);
      await fulfillJson(route, prompt || { detail: 'Not found' });
      return;
    }

    await route.continue();
  });
}

test.beforeEach(async ({ page }) => {
  await setupSyntheticBackend(page);
});

test('users can navigate and exercise forms with synthetic data', async ({ page }) => {
  await page.goto('/');

  await expect(page.getByText('Backend Status:')).toBeVisible();
  await expect(page.getByText('Connected')).toBeVisible();

  const paperTitle = 'Synthetic Paper A';
  const paperContent = 'This is synthetic paper content used for UI testing.';

  await page.getByLabel('Paper Title').fill(paperTitle);
  await page.getByLabel('Rubric (optional)').selectOption('1');
  await page.getByLabel('Paper Content').fill(paperContent);
  await page.getByRole('button', { name: 'Submit Paper' }).click();

  await expect(page.getByText('Paper submitted successfully!')).toBeVisible();
  await expect(page.getByText(paperTitle)).toBeVisible();

  await page.getByRole('button', { name: 'Evaluate' }).first().click();
  await expect(page.getByText('Evaluation created.')).toBeVisible();

  await page.getByRole('button', { name: 'Rubrics' }).first().click();

  const rubricName = 'Synthetic Rubric 2';
  await page.getByLabel('Rubric Name').fill(rubricName);
  await page.getByRole('radio', { name: 'Numerical Score' }).check();
  await page.getByRole('button', { name: '+ Add Criterion' }).click();
  await page.getByPlaceholder('Criterion name (required)').nth(0).fill('Clarity');
  await page.getByPlaceholder('Description (optional)').nth(0).fill('Measures clarity of writing');
  await page.getByPlaceholder('Criterion name (required)').nth(1).fill('Structure');
  await page.getByPlaceholder('Description (optional)').nth(1).fill('Checks organization and flow');
  await page.getByRole('button', { name: 'Remove' }).first().click();
  await page.getByRole('button', { name: '+ Add Criterion' }).click();
  await page.getByPlaceholder('Criterion name (required)').nth(1).fill('Depth');
  await page.getByPlaceholder('Description (optional)').nth(1).fill('Evaluates argument depth');

  await page.getByRole('button', { name: 'Create Rubric' }).click();
  await expect(page.getByText('Rubric created successfully!')).toBeVisible();
  await expect(page.getByText(rubricName)).toBeVisible();

  await page.getByRole('button', { name: 'Evaluations' }).first().click();
  await expect(page.getByRole('heading', { name: /Evaluations/ })).toBeVisible();

  await page.getByRole('button', { name: /Eval #/ }).first().click();
  await page.getByRole('button', { name: 'Mark Incorrect' }).click();
  await expect(page.getByText('Marked incorrect')).toBeVisible();

  await page.locator('select').first().selectOption('no');
  await page.locator('textarea').first().fill('Human reviewer disagrees with the model.');
  await page.getByRole('button', { name: /Save Feedback/ }).first().click();
  await expect(page.getByText('Feedback saved')).toBeVisible();

  await page.getByRole('button', { name: 'Prompts' }).first().click();
  await expect(page.getByText('Edit Prompt')).toBeVisible();

  const updatedTemplate =
    'Evaluate {{paper_content}} using rubric {{rubric}} with extra guidance for tone.';
  await page.locator('textarea').first().fill(updatedTemplate);
  await page.getByRole('button', { name: 'Save Changes' }).click();
  await expect(page.getByText('Prompt updated')).toBeVisible();

  await page.getByRole('button', { name: 'Create New Version' }).click();
  await expect(page.getByText('New prompt version created and activated')).toBeVisible();
});
