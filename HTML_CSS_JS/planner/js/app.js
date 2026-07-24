// ===== 1. 요소 선택 =====
const formEl = document.getElementById("goal-form");
const titleInput = document.getElementById("goal-title");
const categorySelect = document.getElementById("goal-category");
const dueInput = document.getElementById("goal-due");
const searchInput = document.getElementById("goal-search");

const listEl = document.getElementById("goal-list");
const emptyEl = document.getElementById("list-empty");
const tabsEl = document.getElementById("filter-tabs");
const sortEl = document.getElementById("sort-controls");

const progressFillEl = document.getElementById("progress-fill");
const progressTextEl = document.getElementById("progress-text");
const summaryEl = document.getElementById("category-summary");
const tipEl = document.getElementById("tip-text");

const themeToggleEl = document.getElementById("theme-toggle");

// ===== 2. 상태 =====
const STORAGE_KEY = "skala-planner-goals";
const THEME_KEY = "skala-planner-theme";

let goals = load();
let filter = "all"; // all | active | done
let sortMode = "default"; // default | due | latest
let justAddedId = null; // 방금 추가된 항목 id (등장 애니메이션용)

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

  if (!title || !due) {
    formEl.reportValidity();
    return;
  }

  const newGoal = {
    id: Date.now(),
    title: title,
    category: categorySelect.value,
    due: due,
    done: false,
  };

  goals.push(newGoal);
  justAddedId = newGoal.id;

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
    itemEl.classList.add("item-removing");
    itemEl.addEventListener("transitionend", function onEnd() {
      itemEl.removeEventListener("transitionend", onEnd);
      goals = goals.filter((g) => g.id !== id);
      save();
      render();
    });
    return;
  }
});

// ===== 5. 목표 제목 더블클릭 수정 =====
listEl.addEventListener("dblclick", function (e) {
  const textEl = e.target.closest(".item-text");
  if (!textEl) return;

  const itemEl = textEl.closest(".item");
  const id = Number(itemEl.dataset.id);
  const goal = goals.find((g) => g.id === id);
  if (!goal) return;

  const input = document.createElement("input");
  input.type = "text";
  input.className = "item-edit-input";
  input.value = goal.title;

  textEl.replaceWith(input);
  input.focus();
  input.select();

  let cancelled = false;

  function commit() {
    if (cancelled) return;
    const newTitle = input.value.trim();
    if (newTitle) {
      goal.title = newTitle;
      save();
    }
    render();
  }

  input.addEventListener("blur", commit);
  input.addEventListener("keydown", function (ev) {
    if (ev.key === "Enter") {
      input.blur();
    } else if (ev.key === "Escape") {
      cancelled = true;
      render();
    }
  });
});

// ===== 6. 탭 클릭 위임 (필터 전환) =====
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

// ===== 7. 정렬 버튼 =====
sortEl.addEventListener("click", function (e) {
  const btn = e.target.closest(".sort-btn");
  if (!btn) return;

  sortMode = btn.dataset.sort;

  sortEl
    .querySelectorAll(".sort-btn")
    .forEach((b) => b.classList.remove("is-active"));
  btn.classList.add("is-active");

  render();
});

function sortGoals(list) {
  const copy = [...list];

  if (sortMode === "due") {
    copy.sort((a, b) => {
      if (!a.due) return 1;
      if (!b.due) return -1;
      return a.due.localeCompare(b.due);
    });
  } else if (sortMode === "latest") {
    copy.sort((a, b) => b.id - a.id);
  }

  return copy;
}

// ===== 8. 검색 =====
searchInput.addEventListener("input", render);

// ===== 9. 필터 + 검색 =====
function visible(goal) {
  const keyword = searchInput.value.trim().toLowerCase();

  const matchesFilter =
    filter === "all" ||
    (filter === "active" && !goal.done) ||
    (filter === "done" && goal.done);

  const matchesKeyword = goal.title.toLowerCase().includes(keyword);

  return matchesFilter && matchesKeyword;
}

// ===== 10. 마감일 지남 여부 =====
function isOverdue(goal) {
  if (!goal.due || goal.done) return false;
  const today = new Date().toISOString().slice(0, 10);
  return goal.due < today;
}

// ===== 11. 렌더링 =====
function render() {
  const visibleGoals = sortGoals(goals.filter(visible));

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

    if (goal.id === justAddedId) {
      li.classList.add("item-new");
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          li.classList.remove("item-new");
        });
      });
      justAddedId = null;
    }
  });

  emptyEl.hidden = visibleGoals.length !== 0;

  updateProgress();
  updateSummary();
}

// ===== 12. 진행률 =====
function updateProgress() {
  const total = goals.length;
  const doneCount = goals.filter((g) => g.done).length;
  const percent = total === 0 ? 0 : Math.round((doneCount / total) * 100);

  progressFillEl.style.width = percent + "%";
  progressTextEl.textContent = `${doneCount} / ${total} 완료 (${percent}%)`;
}

// ===== 13. 분류별 요약 =====
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

// ===== 14. XSS 방지용 이스케이프 =====
function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// ===== 15. 다크 모드 =====
function loadTheme() {
  const saved = localStorage.getItem(THEME_KEY);
  if (saved === "dark") {
    document.body.classList.add("theme-dark");
    themeToggleEl.textContent = "라이트모드";
  }
}

themeToggleEl.addEventListener("click", function () {
  document.body.classList.toggle("theme-dark");
  const isDark = document.body.classList.contains("theme-dark");
  themeToggleEl.textContent = isDark ? "라이트모드" : "다크모드";
  localStorage.setItem(THEME_KEY, isDark ? "dark" : "light");
});

// ===== 16. 오늘 날짜 표시 =====
const todayEl = document.getElementById("today");
if (todayEl) {
  todayEl.textContent = new Date().toLocaleDateString("ko-KR", {
    year: "numeric",
    month: "long",
    day: "numeric",
    weekday: "long",
  });
}

// ===== 17. 초기 실행 =====
loadTheme();
render();
loadTip();

// ===== 18. 오늘의 팁 (fetch) =====
async function loadTip() {
  try {
    const response = await fetch("data/tips.json");

    if (!response.ok) {
      throw new Error("팁 데이터를 불러오지 못했습니다.");
    }

    const tips = await response.json();
    const random = tips[Math.floor(Math.random() * tips.length)];

    tipEl.textContent = `[${random.category}] ${random.tip}`;
  } catch (err) {
    tipEl.textContent =
      "오늘의 팁을 불러오지 못했어요. Live Server로 열었는지 확인해주세요.";
    console.error(err);
  }
}
