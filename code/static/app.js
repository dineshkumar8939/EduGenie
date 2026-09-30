const task = document.getElementById("task");
const input = document.getElementById("input");
const level = document.getElementById("level");
const levelWrap = document.getElementById("level-wrap");
const submitBtn = document.getElementById("submit-btn");
const clearBtn = document.getElementById("clear-btn");
const result = document.getElementById("result");
const resultTitle = document.getElementById("result-title");
const errorBox = document.getElementById("error");
const loader = document.getElementById("loader");

const taskNames = {
  qa: "Question & Answer",
  explain: "Concept Explanation",
  quiz: "Generated Quiz",
  summarize: "Summary",
  learn: "Learning Path"
};

task.addEventListener("change", () => {
  const isLearn = task.value === "learn";
  levelWrap.classList.toggle("hidden", !isLearn);

  const placeholders = {
    qa: "Example: What is the difference between TCP and UDP?",
    explain: "Example: Explain the Pythagoras theorem in simple terms.",
    quiz: "Example: JavaScript arrays and array methods",
    summarize: "Paste the educational passage you want to summarize...",
    learn: "Example: AWS Cloud Computing"
  };

  input.placeholder = placeholders[task.value];
  submitBtn.textContent = task.value === "quiz"
    ? "Generate Quiz"
    : "Generate Answer";
});

clearBtn.addEventListener("click", () => {
  input.value = "";
  errorBox.classList.add("hidden");
  result.className = "result empty";
  result.innerHTML = `
    <div class="empty-icon">✦</div>
    <p>Choose a task and send your request.</p>
  `;
  resultTitle.textContent = "Your answer will appear here";
});

function setLoading(isLoading) {
  submitBtn.disabled = isLoading;
  loader.classList.toggle("hidden", !isLoading);
}

function showError(message) {
  errorBox.textContent = message;
  errorBox.classList.remove("hidden");
}

function clearError() {
  errorBox.textContent = "";
  errorBox.classList.add("hidden");
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderAnswer(text) {
  result.className = "result";
  result.innerHTML = `<div class="answer">${escapeHtml(text)}</div>`;
}

function renderQuiz(quiz) {
  result.className = "result";
  result.innerHTML = "";

  quiz.forEach((item, index) => {
    const wrapper = document.createElement("div");
    wrapper.className = "quiz-question";

    wrapper.innerHTML = `
      <h4>${index + 1}. ${escapeHtml(item.question)}</h4>
      ${item.options.map((option, optionIndex) => `
        <label class="option">
          <input
            type="radio"
            name="question-${index}"
            value="${escapeHtml(option)}"
          />
          ${escapeHtml(option)}
        </label>
      `).join("")}
    `;

    result.appendChild(wrapper);
  });

  const actions = document.createElement("div");
  actions.className = "quiz-actions";
  actions.innerHTML = `
    <button class="primary" id="check-quiz">Check Answers</button>
    <span id="score" class="score"></span>
  `;
  result.appendChild(actions);

  document.getElementById("check-quiz").addEventListener("click", () => {
    let score = 0;

    quiz.forEach((item, index) => {
      const selected = document.querySelector(
        `input[name="question-${index}"]:checked`
      );
      if (selected && selected.value === item.answer) {
        score++;
      }
    });

    document.getElementById("score").textContent =
      `Score: ${score}/${quiz.length}`;
  });
}

async function submitRequest() {
  clearError();

  const value = input.value.trim();
  if (!value) {
    showError("Please enter some text first.");
    return;
  }

  setLoading(true);
  result.className = "result empty";
  result.innerHTML = "<p>EduGenie is thinking...</p>";
  resultTitle.textContent = taskNames[task.value];

  try {
    let endpoint;
    let payload;

    if (task.value === "qa") {
      endpoint = "/qa";
      payload = { text: value };
    } else if (task.value === "explain") {
      endpoint = "/explain";
      payload = { text: value };
    } else if (task.value === "summarize") {
      endpoint = "/summarize";
      payload = { text: value };
    } else if (task.value === "quiz") {
      endpoint = "/quiz";
      payload = { topic: value, count: 3 };
    } else {
      endpoint = "/learn/recommendations";
      payload = { topic: value, level: level.value };
    }

    const response = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Request failed.");
    }

    if (task.value === "quiz") {
      if (!Array.isArray(data.quiz)) {
        throw new Error("The server returned an invalid quiz.");
      }
      renderQuiz(data.quiz);
    } else {
      renderAnswer(data.result);
    }
  } catch (error) {
    result.className = "result empty";
    result.innerHTML = "<p>Something went wrong.</p>";
    showError(error.message);
  } finally {
    setLoading(false);
  }
}

submitBtn.addEventListener("click", submitRequest);

input.addEventListener("keydown", (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
    submitRequest();
  }
});
