import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/auth-context';
import { apiUrl } from '../config/api';
import { SuggestionRichText } from '../components/SuggestionRichText';
import { LensCriteriaEditor } from '../components/LensCriteriaEditor';
import { downloadReviewPdf } from '../utils/exportReviewPdf';

type DiagramItem = {
  id: number;
  title: string;
  updated_at?: string;
  is_owner?: boolean;
};

type Finding = {
  code: string;
  pillar: string;
  severity: string;
  title: string;
  message: string;
  recommendation_hint?: string;
  node_ids?: string[];
  source?: string;
  lens_risk?: string;
};

type RiskCounts = {
  HIGH_RISK?: number;
  MEDIUM_RISK?: number;
  NO_RISK?: number;
};

type Review = {
  id: number;
  diagram_id: number;
  status: string;
  overall_score: number | null;
  scores?: {
    source_of_truth?: string;
    pillar_scores?: Record<string, number>;
    weights?: Record<string, number>;
    overall_score?: number;
    risk_counts?: RiskCounts;
    heuristic?: {
      pillar_scores?: Record<string, number>;
      overall_score?: number;
    };
    lens?: {
      risk_counts?: RiskCounts;
      overall_score?: number;
      pillar_scores?: Record<string, number>;
      lens_name?: string;
    };
    lens_error?: string;
    findings_source?: string;
  } | null;
  findings?: Finding[];
  suggestions_text?: string | null;
  error_message?: string | null;
  created_at?: string | null;
  provider?: string;
};

const PILLAR_LABELS: Record<string, string> = {
  operational_excellence: 'Operational Excellence',
  security: 'Security',
  reliability: 'Reliability',
  performance_efficiency: 'Performance Efficiency',
  cost_optimization: 'Cost Optimization',
};

async function readSse(
  response: Response,
  onEvent: (data: Record<string, unknown>) => void
) {
  if (!response.body) throw new Error('無串流回應');
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split('\n\n');
    buffer = parts.pop() || '';
    for (const part of parts) {
      const line = part
        .split('\n')
        .find((l) => l.startsWith('data: '));
      if (!line) continue;
      try {
        onEvent(JSON.parse(line.slice(6)));
      } catch {
        /* ignore malformed chunk */
      }
    }
  }
}

export const AssessmentPage = () => {
  const { token, can } = useAuth();
  const canEdit = can('A3', 'edit');
  const canEditLens = can('A3', 'review');
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [mainTab, setMainTab] = useState<'reviews' | 'lens'>('reviews');

  const [diagrams, setDiagrams] = useState<DiagramItem[]>([]);
  // URL 的 ?diagramId= 只作為初始值；使用者從下拉改選後以其選擇為準（derive，
  // 不用 effect 從 searchParams 同步 state）。
  const [diagramOverride, setDiagramOverride] = useState<number | null>(null);
  const [provider, setProvider] = useState('aws');
  const [replaceLatest, setReplaceLatest] = useState(false);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [active, setActive] = useState<Review | null>(null);
  const [suggestionsLive, setSuggestionsLive] = useState('');
  const [phase, setPhase] = useState<string>('idle');
  const [error, setError] = useState<string | null>(null);
  // 記錄「歷史評核已載入哪張圖」，loadingList 由此推導；如此 effect body 內不需
  // 同步 setState（react-hooks/set-state-in-effect）。事件處理可直接設回 null 以
  // 重新顯示載入中。
  const [loadedFor, setLoadedFor] = useState<number | null>(null);
  const [openingId, setOpeningId] = useState<number | null>(null);
  const [exportingPdf, setExportingPdf] = useState(false);
  const resultRef = useRef<HTMLDivElement | null>(null);

  const authHeaders = useMemo(
    () => ({
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    }),
    [token]
  );

  // 純抓取，完全不碰 state。react-hooks/set-state-in-effect 會做過程間分析：
  // 只要 effect 同步呼叫的函式內部有 setState 就會被擋，因此 state 更新一律留在
  // 呼叫端的 callback 內（規則允許的形式）。
  const fetchDiagrams = useCallback(async () => {
    const res = await fetch(apiUrl('/api/collab/diagrams'), {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) return null;
    return res.json();
  }, [token]);

  const fetchReviews = useCallback(
    async (diagramId: number) => {
      const res = await fetch(
        apiUrl(`/api/architecture/reviews?diagram_id=${diagramId}`),
        { headers: { Authorization: `Bearer ${token}` } }
      );
      return res.ok ? res.json() : null;
    },
    [token]
  );

  // 事件處理呼叫用：先切到 loading 再抓。
  const loadReviews = useCallback(
    (diagramId: number) => {
      setLoadedFor(null);
      return fetchReviews(diagramId)
        .then((data) => { if (data) setReviews(data); })
        .finally(() => setLoadedFor(diagramId));
    },
    [fetchReviews]
  );

  const urlDiagramId = useMemo(() => {
    const q = searchParams.get('diagramId');
    if (!q) return null;
    const id = Number(q);
    return Number.isNaN(id) ? null : id;
  }, [searchParams]);
  const selectedDiagramId = diagramOverride ?? urlDiagramId;
  const loadingList = selectedDiagramId !== null && loadedFor !== selectedDiagramId;

  useEffect(() => {
    let cancelled = false;
    fetchDiagrams().then((data) => { if (!cancelled && data) setDiagrams(data); });
    return () => { cancelled = true; };
  }, [fetchDiagrams]);

  useEffect(() => {
    if (!selectedDiagramId) return;
    let cancelled = false;
    fetchReviews(selectedDiagramId)
      .then((data) => { if (!cancelled && data) setReviews(data); })
      .finally(() => { if (!cancelled) setLoadedFor(selectedDiagramId); });
    return () => { cancelled = true; };
  }, [selectedDiagramId, fetchReviews]);

  const applySseEvent = (data: Record<string, unknown>) => {
    const type = String(data.type || '');
    if (type === 'rules_done') {
      setPhase('rules');
      setActive((prev) => ({
        ...(prev || { id: Number(data.review_id), diagram_id: selectedDiagramId || 0, status: 'rules_complete' }),
        id: Number(data.review_id),
        status: 'rules_complete',
        overall_score: (data.overall_score as number) ?? null,
        scores: data.scores as Review['scores'],
        findings: data.findings as Finding[],
      }));
    } else if (type === 'lens_done') {
      setPhase('lens');
      setActive((prev) => ({
        ...(prev || { id: Number(data.review_id), diagram_id: selectedDiagramId || 0, status: 'rules_complete' }),
        id: Number(data.review_id),
        status: 'rules_complete',
        overall_score: (data.overall_score as number) ?? null,
        scores: data.scores as Review['scores'],
        findings: (data.findings as Finding[]) || prev?.findings || [],
      }));
      requestAnimationFrame(() => {
        resultRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    } else if (type === 'suggestion_delta') {
      setPhase('suggestions');
      setSuggestionsLive((s) => s + String(data.content || ''));
      // Keep result panel in view while streaming
      requestAnimationFrame(() => {
        resultRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      });
    } else if (type === 'complete') {
      setPhase('done');
      const text = String(data.suggestions_text || '');
      if (text) setSuggestionsLive(text);
      setActive((prev) =>
        prev
          ? {
              ...prev,
              status: 'complete',
              suggestions_text: text || prev.suggestions_text,
              overall_score:
                data.overall_score != null
                  ? (data.overall_score as number)
                  : prev.overall_score,
              scores: (data.scores as Review['scores']) || prev.scores,
              error_message: null,
            }
          : prev
      );
      if (selectedDiagramId) loadReviews(selectedDiagramId);
      requestAnimationFrame(() => {
        resultRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    } else if (type === 'unsupported') {
      setPhase('unsupported');
      setError(String(data.message || '未支援的雲端提供者'));
      if (selectedDiagramId) loadReviews(selectedDiagramId);
    } else if (type === 'error') {
      if (data.code === 'lens_error') {
        // Q6=A / Q5=B: heuristics continue; soft warning; may include heuristic findings
        setError(`Lens 失敗，已保留啟發式分數／發現：${String(data.message || '')}`);
        setActive((prev) =>
          prev
            ? {
                ...prev,
                scores: (data.scores as Review['scores']) || prev.scores,
                findings:
                  (data.findings as Finding[]) || prev.findings || [],
              }
            : prev
        );
        return;
      }
      setPhase('error');
      setError(String(data.message || '評核失敗'));
      const fallbackText = String(data.suggestions_text || '');
      if (fallbackText) setSuggestionsLive(fallbackText);
      setActive((prev) =>
        prev
          ? {
              ...prev,
              status: String(data.status || prev.status),
              error_message: String(data.message || ''),
              scores: (data.scores as Review['scores']) || prev.scores,
              overall_score:
                data.overall_score != null
                  ? (data.overall_score as number)
                  : prev.overall_score,
              suggestions_text: fallbackText || prev.suggestions_text,
            }
          : prev
      );
      if (selectedDiagramId) loadReviews(selectedDiagramId);
    }
  };

  const runReview = async () => {
    if (!selectedDiagramId || !canEdit) return;
    setError(null);
    setSuggestionsLive('');
    setActive(null);
    setPhase('running');
    try {
      const res = await fetch(apiUrl('/api/architecture/reviews'), {
        method: 'POST',
        headers: authHeaders,
        body: JSON.stringify({
          diagram_id: selectedDiagramId,
          provider,
          replace_latest: replaceLatest,
        }),
      });
      if (!res.ok) {
        const detail = await res.text();
        throw new Error(detail || `HTTP ${res.status}`);
      }
      await readSse(res, applySseEvent);
    } catch (e) {
      setPhase('error');
      setError(e instanceof Error ? e.message : '發起評核失敗');
    }
  };

  const retrySuggestions = async () => {
    if (!active?.id || !canEdit) return;
    setError(null);
    setSuggestionsLive('');
    setPhase('suggestions');
    try {
      const res = await fetch(
        apiUrl(`/api/architecture/reviews/${active.id}/retry-suggestions`),
        { method: 'POST', headers: authHeaders }
      );
      if (!res.ok) throw new Error(await res.text());
      await readSse(res, applySseEvent);
    } catch (e) {
      setPhase('error');
      setError(e instanceof Error ? e.message : '重試建議失敗');
    }
  };

  const openReview = async (preview: Review) => {
    setError(null);
    setOpeningId(preview.id);
    // 先用列表資料立刻顯示，避免「沒反應」
    setActive(preview);
    setSuggestionsLive(preview.suggestions_text || '');
    setPhase(preview.status);
    requestAnimationFrame(() => {
      resultRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
    try {
      const res = await fetch(apiUrl(`/api/architecture/reviews/${preview.id}`), {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) {
        const detail = await res.text();
        setError(detail || `無法開啟評核 #${preview.id}（HTTP ${res.status}）`);
        return;
      }
      const data = (await res.json()) as Review;
      setActive(data);
      setSuggestionsLive(data.suggestions_text || '');
      setPhase(data.status);
      setError(data.error_message || null);
      requestAnimationFrame(() => {
        resultRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : '開啟評核失敗');
    } finally {
      setOpeningId(null);
    }
  };

  const canDownloadPdf =
    Boolean(active) &&
    (active?.status === 'complete' || active?.status === 'rules_only') &&
    can('A3', 'view');

  const exportPdf = async () => {
    if (!active || !canDownloadPdf) return;
    setExportingPdf(true);
    setError(null);
    try {
      const diagramTitle =
        diagrams.find((d) => d.id === active.diagram_id)?.title ||
        diagrams.find((d) => d.id === selectedDiagramId)?.title;
      await downloadReviewPdf({
        id: active.id,
        diagramTitle,
        status: active.status,
        overall_score: active.overall_score,
        created_at: active.created_at,
        provider: active.provider,
        lensName: active.scores?.lens?.lens_name,
        findings_source: active.scores?.findings_source,
        pillar_scores: active.scores?.pillar_scores,
        risk_counts: active.scores?.risk_counts || active.scores?.lens?.risk_counts,
        findings: active.findings,
        suggestions_text: suggestionsLive || active.suggestions_text,
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : 'PDF 匯出失敗');
    } finally {
      setExportingPdf(false);
    }
  };

  // Prefer Lens scores; also accept lens payload without source_of_truth (compat)
  const lensReady =
    active?.scores?.source_of_truth === 'offline_lens' ||
    Boolean(active?.scores?.lens) ||
    Boolean(active?.scores?.risk_counts);
  const pillarScores = lensReady
    ? active?.scores?.pillar_scores || active?.scores?.lens?.pillar_scores || {}
    : {};
  const riskCounts = lensReady
    ? active?.scores?.risk_counts || active?.scores?.lens?.risk_counts || null
    : null;
  const displayOverall = lensReady
    ? active?.overall_score ?? active?.scores?.overall_score ?? null
    : null;
  const lensPending =
    active != null &&
    !lensReady &&
    (phase === 'running' ||
      phase === 'rules' ||
      active.scores?.source_of_truth === 'pending_lens');
  const lensFailed =
    !lensReady &&
    (active?.scores?.source_of_truth === 'heuristic' ||
      Boolean(active?.scores?.lens_error));
  const suggestionsText = (suggestionsLive || active?.suggestions_text || '').trim();
  const isStreamingSuggestions =
    phase === 'suggestions' || phase === 'lens' || phase === 'running';
  const suggestionsPlaceholder = (() => {
    if (phase === 'running' || phase === 'rules' || phase === 'lens') {
      return '（評核進行中，稍後串流建議…）';
    }
    if (phase === 'suggestions') {
      return '（Agent 正在串流產生建議…）';
    }
    if (active?.status === 'rules_only') {
      return '（Agent 建議失敗，可點「重試建議」；若已有備援文字會顯示於上方）';
    }
    if (active?.status === 'complete' || active?.status === 'unsupported') {
      return '（本次評核無 Agent 建議文字）';
    }
    return '（尚無建議）';
  })();

  return (
    <div className="h-full overflow-y-auto bg-gray-50 p-6">
      <div className="max-w-5xl mx-auto space-y-6">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 tracking-tight">評估儀表板</h1>
            <p className="text-sm text-gray-500 mt-1">
              Well-Architected 評核：離線 Lens 分數與風險計數＋AI 改善建議（本期 AWS／無 AWS API）
            </p>
          </div>
          <button
            type="button"
            onClick={() => navigate('/workspace')}
            className="text-sm font-semibold text-brand-700 hover:underline"
          >
            返回工作區
          </button>
        </div>

        {canEditLens && (
          <div className="flex gap-1 border-b border-gray-200">
            <button
              type="button"
              onClick={() => setMainTab('reviews')}
              className={`px-4 py-2 text-sm font-semibold border-b-2 -mb-px ${
                mainTab === 'reviews'
                  ? 'border-brand-600 text-brand-700'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              評核
            </button>
            <button
              type="button"
              onClick={() => setMainTab('lens')}
              className={`px-4 py-2 text-sm font-semibold border-b-2 -mb-px ${
                mainTab === 'lens'
                  ? 'border-brand-600 text-brand-700'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Lens 標準
            </button>
          </div>
        )}

        {canEditLens && mainTab === 'lens' && token ? (
          <LensCriteriaEditor token={token} />
        ) : (
          <>
        <div className="bg-white border border-gray-100 rounded-2xl p-4 shadow-sm space-y-3">
          <div className="flex flex-wrap gap-3 items-end">
            <label className="flex flex-col gap-1 text-xs font-semibold text-gray-500">
              架構圖
              <select
                className="border border-gray-200 rounded-xl px-3 py-2 text-sm font-semibold text-gray-800 min-w-[12rem]"
                value={selectedDiagramId ?? ''}
                onChange={(e) =>
                  setDiagramOverride(e.target.value ? Number(e.target.value) : null)
                }
              >
                <option value="">— 選擇 —</option>
                {diagrams.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.title}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex flex-col gap-1 text-xs font-semibold text-gray-500">
              Provider
              <select
                className="border border-gray-200 rounded-xl px-3 py-2 text-sm font-semibold text-gray-800"
                value={provider}
                onChange={(e) => setProvider(e.target.value)}
              >
                <option value="aws">AWS</option>
                <option value="gcp" disabled>
                  GCP（未實作）
                </option>
                <option value="azure" disabled>
                  Azure（未實作）
                </option>
              </select>
            </label>
            <label className="flex items-center gap-2 text-sm text-gray-700 pb-2">
              <input
                type="checkbox"
                checked={replaceLatest}
                onChange={(e) => setReplaceLatest(e.target.checked)}
              />
              隱藏先前完整評核（replace_latest）
            </label>
            <button
              type="button"
              disabled={!selectedDiagramId || !canEdit || phase === 'running'}
              onClick={runReview}
              className="ml-auto px-4 py-2 rounded-xl bg-brand-600 text-white text-sm font-bold disabled:opacity-40"
            >
              {phase === 'running' ? '評核中…' : '執行評核'}
            </button>
          </div>
          {!canEdit && (
            <p className="text-xs text-amber-700 bg-amber-50 border border-amber-100 rounded-lg px-3 py-2">
              您僅有檢視權限，可開啟歷史報告，無法發起新評核。
            </p>
          )}
          {error && (
            <p className="text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2">
              {error}
            </p>
          )}
        </div>

        <div className="bg-white border border-gray-100 rounded-2xl p-5 shadow-sm">
          <h2 className="text-sm font-bold text-gray-800 mb-3">
            歷史評核 {loadingList ? '（載入中）' : ''}
          </h2>
          {!selectedDiagramId && (
            <p className="text-sm text-gray-400">請先選擇架構圖</p>
          )}
          {selectedDiagramId && reviews.length === 0 && !loadingList && (
            <p className="text-sm text-gray-400">尚無評核紀錄</p>
          )}
          <ul className="divide-y divide-gray-100">
            {reviews.map((r) => {
              const selected = active?.id === r.id;
              return (
                <li
                  key={r.id}
                  className={`py-3 flex items-center gap-3 ${
                    selected ? 'bg-brand-50/60 -mx-2 px-2 rounded-xl' : ''
                  }`}
                >
                  <button
                    type="button"
                    className="flex-1 min-w-0 text-left"
                    onClick={() => openReview(r)}
                    disabled={openingId === r.id}
                  >
                    <div className="text-sm font-semibold text-gray-900">
                      #{r.id} · {r.status} · 分數 {r.overall_score ?? '—'}
                      {r.suggestions_text ? ' · 有建議' : ''}
                    </div>
                    <div className="text-xs text-gray-400">
                      {r.created_at ? new Date(r.created_at).toLocaleString() : ''}
                    </div>
                  </button>
                  <button
                    type="button"
                    onClick={() => openReview(r)}
                    disabled={openingId === r.id}
                    className="text-xs font-bold text-brand-700 px-3 py-1.5 rounded-lg bg-brand-50 disabled:opacity-50"
                  >
                    {openingId === r.id ? '開啟中…' : selected ? '檢視中' : '開啟'}
                  </button>
                </li>
              );
            })}
          </ul>
        </div>

        {active && (
          <div
            ref={resultRef}
            className="bg-white border border-brand-100 rounded-2xl p-5 shadow-sm space-y-4 scroll-mt-4"
          >
            <div className="flex flex-wrap items-baseline gap-3">
              <div className="text-3xl font-bold text-gray-900">
                {displayOverall ?? '—'}
              </div>
              <div className="text-sm text-gray-500">
                評核 #{active.id} · Lens 總分 · 狀態{' '}
                <span className="font-semibold text-gray-800">{active.status}</span>
                {lensReady && (
                  <span className="ml-2 text-xs font-semibold text-brand-700">
                    離線 Lens
                  </span>
                )}
                {lensPending && (
                  <span className="ml-2 text-xs font-semibold text-amber-700">
                    Lens 評分中…
                  </span>
                )}
                {lensFailed && (
                  <span className="ml-2 text-xs font-semibold text-red-700">
                    Lens 失敗（無分數可顯示）
                  </span>
                )}
                {!lensReady && !lensPending && !lensFailed && (
                  <span className="ml-2 text-xs font-semibold text-gray-500">
                    無 Lens 分數（舊版或未完成）
                  </span>
                )}
              </div>
              <div className="ml-auto flex flex-wrap gap-2">
                {canDownloadPdf && (
                  <button
                    type="button"
                    onClick={exportPdf}
                    disabled={exportingPdf}
                    className="text-sm font-bold text-brand-700 bg-brand-50 px-3 py-1.5 rounded-lg disabled:opacity-50"
                  >
                    {exportingPdf ? '產生 PDF…' : '下載 PDF'}
                  </button>
                )}
                {active.status === 'rules_only' && canEdit && (
                  <button
                    type="button"
                    onClick={retrySuggestions}
                    className="text-sm font-bold text-indigo-700 bg-indigo-50 px-3 py-1.5 rounded-lg"
                  >
                    重試建議
                  </button>
                )}
              </div>            </div>

            {riskCounts && (
              <div className="flex flex-wrap gap-2">
                {(
                  [
                    ['HIGH_RISK', '高風險', 'bg-red-100 text-red-800'],
                    ['MEDIUM_RISK', '中風險', 'bg-amber-100 text-amber-900'],
                    ['NO_RISK', '無風險', 'bg-emerald-100 text-emerald-800'],
                  ] as const
                ).map(([key, label, cls]) => (
                  <div
                    key={key}
                    className={`rounded-xl px-3 py-2 text-sm font-bold ${cls}`}
                  >
                    {label}{' '}
                    <span className="tabular-nums">
                      {riskCounts[key] ?? 0}
                    </span>
                  </div>
                ))}
                {active.scores?.lens?.lens_name && (
                  <div className="text-xs text-gray-500 self-center">
                    Lens：{active.scores.lens.lens_name}
                  </div>
                )}
              </div>
            )}

            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-2">
              {Object.keys(PILLAR_LABELS).map((key) => (
                <div
                  key={key}
                  className="border border-gray-100 rounded-xl px-3 py-2 bg-gray-50"
                >
                  <div className="text-[11px] font-semibold text-gray-500">
                    {PILLAR_LABELS[key]}
                  </div>
                  <div className="text-lg font-bold text-gray-900">
                    {pillarScores[key] != null ? Math.round(pillarScores[key]) : '—'}
                  </div>
                </div>
              ))}
            </div>

            <div>
              <h2 className="text-sm font-bold text-gray-800 mb-2">
                發現
                {active.scores?.findings_source === 'offline_lens' && (
                  <span className="ml-2 text-[11px] font-semibold text-brand-700">
                    Custom Lens
                  </span>
                )}
                {active.scores?.findings_source === 'heuristic' && (
                  <span className="ml-2 text-[11px] font-semibold text-amber-700">
                    啟發式備援
                  </span>
                )}
              </h2>
              <ul className="space-y-2 max-h-64 overflow-y-auto">
                {(active.findings || []).map((f) => (
                  <li
                    key={`${f.code}-${f.title}`}
                    className="border border-gray-100 rounded-xl px-3 py-2 text-sm"
                  >
                    <div className="flex gap-2 items-center flex-wrap">
                      <span className="text-[10px] font-bold uppercase tracking-wide text-white bg-gray-700 px-1.5 py-0.5 rounded">
                        {f.pillar}
                      </span>
                      <span
                        className={`text-[10px] font-bold uppercase tracking-wide px-1.5 py-0.5 rounded ${
                          f.severity === 'high' || f.severity === 'critical'
                            ? 'bg-red-100 text-red-800'
                            : f.severity === 'warn'
                              ? 'bg-amber-100 text-amber-900'
                              : 'bg-gray-100 text-gray-600'
                        }`}
                      >
                        {f.lens_risk || f.severity}
                      </span>
                      <span className="font-semibold text-gray-900">{f.title}</span>
                      <span className="text-xs text-gray-400 ml-auto">{f.code}</span>
                    </div>
                    <p className="text-gray-600 mt-1">{f.message}</p>
                    {f.recommendation_hint && (
                      <p className="text-xs text-brand-700 mt-1">提示：{f.recommendation_hint}</p>
                    )}
                  </li>
                ))}
                {(active.findings || []).length === 0 && (
                  <li className="text-sm text-gray-400">
                    {phase === 'running' || phase === 'rules' || phase === 'lens'
                      ? '（等待 Lens 評核結果…）'
                      : '尚無中／高風險發現'}
                  </li>
                )}
              </ul>
            </div>

            <div>
              <h2 className="text-sm font-bold text-gray-800 mb-2 flex items-center gap-2">
                改善建議
                {isStreamingSuggestions && (
                  <span className="text-[11px] font-semibold text-brand-600 animate-pulse">
                    串流中…
                  </span>
                )}
              </h2>
              <div className="bg-white border border-gray-100 rounded-xl p-4 min-h-[6rem] shadow-sm">
                <SuggestionRichText
                  text={suggestionsText}
                  streaming={Boolean(isStreamingSuggestions && suggestionsText)}
                  empty={suggestionsPlaceholder}
                />
              </div>
              {active.error_message && active.status === 'rules_only' && (
                <p className="text-xs text-red-600 mt-2">
                  Agent 錯誤：{active.error_message}
                  {canEdit ? ' — 可點「重試建議」再試。' : ''}
                </p>
              )}
            </div>
          </div>
        )}
          </>
        )}
      </div>
    </div>
  );
};
