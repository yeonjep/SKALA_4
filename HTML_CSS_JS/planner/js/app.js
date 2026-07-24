// ===== 1. 요소 선택 =====
const formEl = document.getElementById("goal-form");
const titleInput = document.getElementById("goal-title");
const categorySelect = document.getElementById("goal-category");
const dueInput = document.getElementById("goal-due");
const searchInput = document.getElementById("goal-search");

const listEl = document.getElementById("goal-list");
const emptyEl = document.getElementById("list-empty");
const tabsEl = document.getElementById("filter-tabs");

const progressFillEl = document.getElementById("progress-fill");
const progressTextEl = document.getElementById("progress-text");
const summaryEl = document.getElementById("category-summary");

// ===== 2. 상태 =====
const STORAGE_KEY = "skala-planner-goals";
let goals = load();
let filter = "all"; // all | active | done

function load() {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return [];
  try {
    return JSON.parse(raw);
  } catch (e) {
    return [];
  }
}

function save() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(goals));
}

// ===== 3. 목표 추가 (폼 제출) =====
formEl.addEventListener("submit", function (e) {
  e.preventDefault();

  const title = titleInput.value.trim();
  const due = dueInput.value;

  // 제목 또는 마감일이 비어 있으면 추가하지 않음
  if (!title || !due) {
    formEl.reportValidity();
    return;
  }

  goals.push({
    id: Date.now(),
    title: title,
    category: categorySelect.value,
    due: due,
    done: false,
  });

  save();
  render();

  titleInput.value = "";
  dueInput.value = "";
  titleInput.focus();
});

// ===== 4. 목록 클릭 위임 (완료 토글 / 삭제) =====
listEl.addEventListener("click", function (e) {
  const itemEl = e.target.closest(".item");
  if (!itemEl) return;

  const id = Number(itemEl.dataset.id);

  if (e.target.classList.contains("item-check")) {
    const goal = goals.find((g) => g.id === id);
    if (goal) goal.done = !goal.done;
    save();
    render();
    return;
  }

  if (e.target.classList.contains("item-del")) {
    goals = goals.filter((g) => g.id !== id);
    save();
    render();
    return;
  }
});

// ===== 5. 탭 클릭 위임 (필터 전환) =====
tabsEl.addEventListener("click", function (e) {
  const btn = e.target.closest(".tab");
  if (!btn) return;

  filter = btn.dataset.filter;

  tabsEl
    .querySelectorAll(".tab")
    .forEach((t) => t.classList.remove("is-active"));
  btn.classList.add("is-active");

  render();
});

// ===== 6. 검색 (F6) =====
searchInput.addEventListener("input", render);

// ===== 7. 필터 + 검색 =====
function visible(goal) {
  const keyword = searchInput.value.trim().toLowerCase();

  const matchesFilter =
    filter === "all" ||
    (filter === "active" && !goal.done) ||
    (filter === "done" && goal.done);

  const matchesKeyword = goal.title.toLowerCase().includes(keyword);

  return matchesFilter && matchesKeyword;
}

// ===== 8. 마감일 지남 여부 (F5) =====
function isOverdue(goal) {
  if (!goal.due || goal.done) return false;
  const today = new Date().toISOString().slice(0, 10);
  return goal.due < today;
}

// ===== 9. 렌더링 =====
function render() {
  const visibleGoals = goals.filter(visible);

  listEl.innerHTML = "";

  visibleGoals.forEach((goal) => {
    const li = document.createElement("li");
    li.className =
      "item" +
      (goal.done ? " is-done" : "") +
      (isOverdue(goal) ? " is-overdue" : "");
    li.dataset.id = goal.id;

    li.innerHTML = `
      <input type="checkbox" class="item-check" ${goal.done ? "checked" : ""}>
      <span class="item-text">${escapeHtml(goal.title)}</span>
      ${goal.due ? `<span class="item-due">${goal.due}</span>` : ""}
      <span class="item-badge">${escapeHtml(goal.category)}</span>
      <button type="button" class="item-del" aria-label="삭제">&times;</button>
    `;

    listEl.appendChild(li);
  });

  emptyEl.hidden = visibleGoals.length !== 0;

  updateProgress();
  updateSummary();
}

// ===== 10. 진행률 (F3) =====
function updateProgress() {
  const total = goals.length;
  const doneCount = goals.filter((g) => g.done).length;
  const percent = total === 0 ? 0 : Math.round((doneCount / total) * 100);

  progressFillEl.style.width = percent + "%";
  progressTextEl.textContent = `${doneCount} / ${total} 완료`;
}

// ===== 11. 분류별 요약 (F7) =====
function updateSummary() {
  const remaining = goals.filter((g) => !g.done);

  const counts = remaining.reduce((acc, g) => {
    acc[g.category] = (acc[g.category] || 0) + 1;
    return acc;
  }, {});

  const parts = Object.keys(counts).map((cat) => `${cat} ${counts[cat]}개`);

  summaryEl.textContent = parts.length
    ? `남은 목표 — ${parts.join(" · ")}`
    : "남은 목표가 없습니다.";
}

// ===== 12. XSS 방지용 이스케이프 =====
function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// ===== 13. 오늘 날짜 표시 =====
const todayEl = document.getElementById("today");
if (todayEl) {
  todayEl.textContent = new Date().toLocaleDateString("ko-KR", {
    year: "numeric",
    month: "long",
    day: "numeric",
    weekday: "long",
  });
}

// ===== 14. 초기 렌더 =====
render();
