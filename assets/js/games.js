(function () {
  "use strict";

  var isZh = (document.documentElement.lang || "").toLowerCase().startsWith("zh");

  var T = {
    reaction: {
      start: isZh ? "开始" : "Start",
      wait: isZh ? "等待…" : "Wait…",
      go: isZh ? "点击！" : "Click!",
      tooSoon: isZh ? "太早了！再试一次" : "Too soon! Try again",
      result: isZh ? "反应时间：" : "Reaction: ",
      ms: isZh ? " 毫秒" : " ms",
      retry: isZh ? "再来一次" : "Try again",
    },
    memory: {
      win: isZh ? "全部配对成功！" : "All pairs matched!",
      moves: isZh ? "步数：" : "Moves: ",
      retry: isZh ? "重新开始" : "Restart",
    },
    guess: {
      placeholder: isZh ? "输入数字" : "Enter number",
      go: isZh ? "猜" : "Guess",
      higher: isZh ? "再大一点" : "Go higher",
      lower: isZh ? "再小一点" : "Go lower",
      win: isZh ? "猜对了！用了 " : "Correct in ",
      attempts: isZh ? " 次" : " tries",
      invalid: isZh ? "请输入 1–100 的整数" : "Enter an integer from 1 to 100",
      retry: isZh ? "新一局" : "New game",
    },
    clicks: {
      start: isZh ? "开始 10 秒" : "Start 10s",
      tap: isZh ? "点！" : "Tap!",
      result: isZh ? "共点击 " : "Clicks: ",
      times: isZh ? " 次" : "",
      retry: isZh ? "再来" : "Again",
    },
  };

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text != null) node.textContent = text;
    return node;
  }

  function initReaction(panel) {
    var t = T.reaction;
    var status = el("p", "game-status", "");
    var score = el("p", "game-score", "");
    var btn = el("button", "game-btn", t.start);
    btn.type = "button";
    var timer = null;
    var startAt = 0;

    function reset() {
      clearTimeout(timer);
      timer = null;
      btn.disabled = false;
      btn.className = "game-btn";
      btn.textContent = t.start;
      status.textContent = "";
      score.textContent = "";
    }

    btn.addEventListener("click", function () {
      if (btn.textContent === t.retry) {
        reset();
        return;
      }
      if (btn.textContent === t.go) {
        var ms = Date.now() - startAt;
        btn.className = "game-btn";
        btn.textContent = t.retry;
        status.textContent = "";
        score.textContent = t.result + ms + t.ms;
        return;
      }
      btn.disabled = true;
      btn.className = "game-btn is-waiting";
      btn.textContent = t.wait;
      status.textContent = "";
      score.textContent = "";
      var delay = 1000 + Math.random() * 3000;
      timer = setTimeout(function () {
        startAt = Date.now();
        btn.disabled = false;
        btn.className = "game-btn is-ready";
        btn.textContent = t.go;
      }, delay);
    });

    btn.addEventListener("mousedown", function (e) {
      if (btn.className.indexOf("is-waiting") !== -1 && btn.textContent === t.wait) {
        e.preventDefault();
        clearTimeout(timer);
        timer = null;
        btn.disabled = false;
        btn.className = "game-btn";
        btn.textContent = t.start;
        status.textContent = t.tooSoon;
      }
    });

    panel.appendChild(btn);
    panel.appendChild(status);
    panel.appendChild(score);
  }

  function initMemory(panel) {
    var t = T.memory;
    var icons = ["🍎", "🍊", "🎵", "📷"];
    var pairs = icons.concat(icons);
    var flipped = [];
    var matched = 0;
    var moves = 0;
    var lock = false;
    var status = el("p", "game-status", "");
    var score = el("p", "game-score", "");
    var board = el("div", "memory-board");
    var retry = el("button", "game-btn", t.retry);
    retry.type = "button";
    retry.hidden = true;

    function shuffle(arr) {
      var a = arr.slice();
      for (var i = a.length - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1));
        var tmp = a[i];
        a[i] = a[j];
        a[j] = tmp;
      }
      return a;
    }

    function build() {
      board.innerHTML = "";
      flipped = [];
      matched = 0;
      moves = 0;
      lock = false;
      status.textContent = "";
      score.textContent = "";
      retry.hidden = true;
      shuffle(pairs).forEach(function (icon) {
        var card = el("button", "memory-card", "?");
        card.type = "button";
        card.dataset.icon = icon;
        card.addEventListener("click", function () {
          if (lock || card.disabled || card.classList.contains("is-flipped")) return;
          card.classList.add("is-flipped");
          card.textContent = icon;
          flipped.push(card);
          if (flipped.length === 2) {
            moves++;
            score.textContent = t.moves + moves;
            lock = true;
            var a = flipped[0];
            var b = flipped[1];
            if (a.dataset.icon === b.dataset.icon) {
              a.classList.add("is-matched");
              b.classList.add("is-matched");
              a.disabled = true;
              b.disabled = true;
              matched += 2;
              flipped = [];
              lock = false;
              if (matched === pairs.length) {
                status.textContent = t.win;
                retry.hidden = false;
              }
            } else {
              setTimeout(function () {
                a.classList.remove("is-flipped");
                b.classList.remove("is-flipped");
                a.textContent = "?";
                b.textContent = "?";
                flipped = [];
                lock = false;
              }, 600);
            }
          }
        });
        board.appendChild(card);
      });
    }

    retry.addEventListener("click", build);
    panel.appendChild(board);
    panel.appendChild(status);
    panel.appendChild(score);
    panel.appendChild(retry);
    build();
  }

  function initGuess(panel) {
    var t = T.guess;
    var target = Math.floor(Math.random() * 100) + 1;
    var attempts = 0;
    var status = el("p", "game-status", "");
    var score = el("p", "game-score", "");
    var row = el("div", "guess-row");
    var input = el("input");
    input.type = "number";
    input.min = "1";
    input.max = "100";
    input.placeholder = t.placeholder;
    var btn = el("button", "game-btn", t.go);
    btn.type = "button";
    var retry = el("button", "game-btn", t.retry);
    retry.type = "button";
    retry.hidden = true;

    function reset() {
      target = Math.floor(Math.random() * 100) + 1;
      attempts = 0;
      input.value = "";
      input.disabled = false;
      btn.hidden = false;
      retry.hidden = true;
      status.textContent = "";
      score.textContent = "";
    }

    function guess() {
      var n = parseInt(input.value, 10);
      if (isNaN(n) || n < 1 || n > 100) {
        status.textContent = t.invalid;
        return;
      }
      attempts++;
      if (n === target) {
        status.textContent = t.win + attempts + t.attempts;
        input.disabled = true;
        btn.hidden = true;
        retry.hidden = false;
      } else if (n < target) {
        status.textContent = t.higher;
      } else {
        status.textContent = t.lower;
      }
      score.textContent = (isZh ? "已猜 " : "Attempts: ") + attempts;
    }

    btn.addEventListener("click", guess);
    input.addEventListener("keydown", function (e) {
      if (e.key === "Enter") guess();
    });
    retry.addEventListener("click", reset);

    row.appendChild(input);
    row.appendChild(btn);
    panel.appendChild(row);
    panel.appendChild(status);
    panel.appendChild(score);
    panel.appendChild(retry);
  }

  function initClicks(panel) {
    var t = T.clicks;
    var count = 0;
    var running = false;
    var timer = null;
    var status = el("p", "game-status", "");
    var score = el("p", "game-score", "");
    var startBtn = el("button", "game-btn", t.start);
    startBtn.type = "button";
    var target = el("button", "clicks-target", "0");
    target.type = "button";
    target.disabled = true;

    function reset() {
      clearTimeout(timer);
      running = false;
      count = 0;
      target.textContent = "0";
      target.disabled = true;
      startBtn.hidden = false;
      startBtn.textContent = t.start;
      status.textContent = "";
      score.textContent = "";
    }

    startBtn.addEventListener("click", function () {
      if (startBtn.textContent === t.retry) {
        reset();
        return;
      }
      count = 0;
      running = true;
      target.textContent = "0";
      target.disabled = false;
      startBtn.hidden = true;
      status.textContent = isZh ? "剩余 10 秒" : "10 seconds left";
      var end = Date.now() + 10000;
      function tick() {
        var left = Math.max(0, end - Date.now());
        status.textContent = (isZh ? "剩余 " : "") + (left / 1000).toFixed(1) + (isZh ? " 秒" : "s left");
        if (left > 0) {
          timer = setTimeout(tick, 100);
        } else {
          running = false;
          target.disabled = true;
          startBtn.hidden = false;
          startBtn.textContent = t.retry;
          status.textContent = "";
          score.textContent = t.result + count + t.times;
        }
      }
      tick();
    });

    target.addEventListener("click", function () {
      if (!running) return;
      count++;
      target.textContent = String(count);
    });

    panel.appendChild(startBtn);
    panel.appendChild(target);
    panel.appendChild(status);
    panel.appendChild(score);
  }

  var games = {
    reaction: initReaction,
    memory: initMemory,
    guess: initGuess,
    clicks: initClicks,
  };

  document.querySelectorAll("[data-game]").forEach(function (panel) {
    var id = panel.getAttribute("data-game");
    if (games[id]) games[id](panel);
  });
})();
