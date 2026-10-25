(() => {
  const main = document.querySelector(".quiz-main");
  const bankNode = document.getElementById("question-bank");
  if (!main || !bankNode) return;

  const lang = main.dataset.lang;
  const t = JSON.parse(main.dataset.quizText);
  const bank = JSON.parse(bankNode.textContent);
  const size = 10;
  const storageKey = `dinoatlas-last-quiz-${lang}`;

  function shuffled(items) {
    const copy = [...items];
    for (let i = copy.length - 1; i > 0; i -= 1) {
      const j = Math.floor(Math.random() * (i + 1));
      [copy[i], copy[j]] = [copy[j], copy[i]];
    }
    return copy;
  }

  function getRound() {
    let previous = "";
    try { previous = localStorage.getItem(storageKey) || ""; } catch (_) { /* Storage may be disabled. */ }
    let round = shuffled(bank).slice(0, size);
    let signature = round.map((item) => item.id).sort().join("|");
    for (let attempt = 0; signature === previous && attempt < 20; attempt += 1) {
      round = shuffled(bank).slice(0, size);
      signature = round.map((item) => item.id).sort().join("|");
    }
    try { localStorage.setItem(storageKey, signature); } catch (_) { /* The quiz still works without storage. */ }
    return round;
  }

  const round = getRound();
  const panel = document.getElementById("question-panel");
  const resultPanel = document.getElementById("result-panel");
  const questionNumber = document.getElementById("question-number");
  const questionText = document.getElementById("question-text");
  const questionBadge = document.getElementById("question-badge");
  const optionsBox = document.getElementById("answer-options");
  const feedback = document.getElementById("feedback");
  const nextButton = document.getElementById("next-question");
  const progressBar = document.getElementById("progress-bar");
  let current = 0;
  let score = 0;

  function showQuestion() {
    const question = round[current];
    questionNumber.textContent = String(current + 1);
    progressBar.style.width = `${(current / size) * 100}%`;
    const kind = question.challenge ? t.challenge : t.regular;
    questionBadge.textContent = kind;
    document.getElementById("question-kind").textContent = kind;
    questionBadge.classList.toggle("is-challenge", question.challenge);
    questionText.textContent = question.prompt;
    optionsBox.replaceChildren();
    feedback.hidden = true;
    feedback.textContent = "";
    nextButton.disabled = true;
    nextButton.textContent = current === size - 1 ? t.finish : t.next;

    question.options.forEach((option, index) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "answer-option";
      button.innerHTML = `<span class="option-letter">${String.fromCharCode(65 + index)}</span>`;
      const label = document.createElement("span");
      label.textContent = option;
      button.append(label);
      button.addEventListener("click", () => chooseAnswer(button, option, question));
      optionsBox.append(button);
    });
  }

  function chooseAnswer(button, choice, question) {
    if (!nextButton.disabled) return;
    const isCorrect = choice === question.answer;
    if (isCorrect) score += 1;
    optionsBox.querySelectorAll("button").forEach((optionButton) => {
      optionButton.disabled = true;
      if (optionButton.lastElementChild.textContent === question.answer) optionButton.classList.add("is-correct");
    });
    if (!isCorrect) button.classList.add("is-wrong");
    feedback.hidden = false;
    const result = document.createElement("strong");
    result.textContent = isCorrect ? t.correct : `${t.incorrect} ${t.answer_was}${question.answer}`;
    const explanation = document.createElement("span");
    explanation.textContent = question.explanation;
    feedback.replaceChildren(result, explanation);
    nextButton.disabled = false;
  }

  function showResult() {
    panel.hidden = true;
    document.getElementById("quiz-progress-wrap").hidden = true;
    resultPanel.hidden = false;
    progressBar.style.width = "100%";
    document.getElementById("result-score").textContent = t.result.replace("{score}", score).replace("{total}", size);
    const percent = score / size;
    document.getElementById("result-message").textContent = percent === 1
      ? (lang === "no" ? "Fantastisk! Du kjenner fortidsdyrene svært godt." : "Fantastic! You know your prehistoric animals very well.")
      : percent >= 0.7
        ? (lang === "no" ? "Imponerende jobbet. Klar for en ny runde?" : "Great work. Ready for another round?")
        : (lang === "no" ? "Godt forsøkt — lær litt mer og prøv igjen!" : "Good effort — learn a little more and try again!");
  }

  nextButton.addEventListener("click", () => {
    if (nextButton.disabled) return;
    current += 1;
    if (current >= size) showResult();
    else showQuestion();
  });
  document.getElementById("restart-quiz").addEventListener("click", () => window.location.reload());
  showQuestion();
})();
