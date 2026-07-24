// ===== 1. 요소 선택 =====
const form = document.getElementById("goal-form");
const input = document.getElementById("goal-input");
const category = document.getElementById("goal-category");
const listEl = document.getElementById("goal-list");
const emptyEl = document.getElementById("list-empty");
const errorEl = document.getElementById("form-error");
const tabsEl = document.getElementById("filter-tabs");
const fillEl = document.getElementById("progress-fill");
const textEl = document.getElementById("progress-text");

document.getElementById("today").textContent = new Date().toLocaleDateString(
  "ko-KR",
  { dateStyle: "long" },
);

// ===== 2. 상태와 저장 =====
const STORAGE_KEY = "skala-planner"; // 플래너 데이터를 저장할 때 사용할 key 값 설정
let goals = load();
let filter = "all";

function load() {
  const saved = localStorage.getItem(STORAGE_KEY);
  return saved ? JSON.parse(saved) : [];
}

function save() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(goals));
}

// ===== 4. 목표 추가 =====
form.addEventListener("submit", (event) => {
  event.preventDefault();
  const title = input.value.trim();

  if (title === "") {
    errorEl.hidden = false;
    input.focus();
    return;
  }
  errorEl.hidden = true;

  goals.push({
    id: Date.now(),
    title: title,
    category: category.value,
    done: false,
  });

  input.value = "";
  save();
  render();
});

// ===== 5. 완료 토글 · 삭제 (이벤트 위임) =====
listEl.addEventListener("click", (event) => {
  const li = event.target.closest(".item");
  if (!li) return;

  const id = Number(li.dataset.id);

  if (event.target.matches(".item-check")) {
    const goal = goals.find((g) => g.id === id);
    goal.done = event.target.checked;
    save();
    render();
  }

  if (event.target.matches(".item-del")) {
    goals = goals.filter((g) => g.id !== id);
    save();
    render();
  }
});

// ===== 6. 필터 탭 =====
tabsEl.addEventListener("click", (event) => {
  const tab = event.target.closest(".tab");
  if (!tab) return;

  filter = tab.dataset.filter; // "all" | "active" | "done"
  document.querySelectorAll(".tab").forEach((t) => {
    t.classList.toggle("is-active", t === tab);
  });
  render();
});

function visible() {
  if (filter === "active") return goals.filter((g) => !g.done);
  if (filter === "done") return goals.filter((g) => g.done);
  return goals;
}

// ===== 7. 렌더링 =====
function render() {
  const items = visible();
  listEl.innerHTML = "";

  items.forEach((goal) => {
    const li = document.createElement("li");
    li.className = goal.done ? "item is-done" : "item";
    li.dataset.id = goal.id;
    li.innerHTML = `
      <input type="checkbox" class="item-check" ${goal.done ? "checked" : ""}>
      <span class="item-text">${escapeHtml(goal.title)}</span>
      <span class="badge">${goal.category}</span>
      <button type="button" class="item-del" aria-label="삭제">×</button>
    `;
    listEl.appendChild(li);
  });

  emptyEl.hidden = items.length > 0;
  updateProgress();
}

function updateProgress() {
  const total = goals.length;
  const done = goals.filter((g) => g.done).length;
  const percent = total === 0 ? 0 : Math.round((done / total) * 100);

  fillEl.style.width = percent + "%";
  textEl.textContent = `전체 ${total}개 중 ${done}개 완료 (${percent}%)`;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// ===== 초기 실행 =====
render();
