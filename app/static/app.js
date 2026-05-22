const groupsGrid = document.querySelector("#groupsGrid");
const teamCount = document.querySelector("#teamCount");
const drawButton = document.querySelector("#drawButton");
const simulateButton = document.querySelector("#simulateButton");
const bracketBoard = document.querySelector("#bracketBoard");
const championBadge = document.querySelector("#championBadge");
const alertBox = document.querySelector("#alertBox");
const tournamentDetails = document.querySelector("#tournamentDetails");
const bestPlayerName = document.querySelector("#bestPlayerName");
const bestPlayerMeta = document.querySelector("#bestPlayerMeta");
const topScorersList = document.querySelector("#topScorersList");
const topAssistersList = document.querySelector("#topAssistersList");
const groupResultsPanel = document.querySelector("#groupResultsPanel");
const groupResultsGrid = document.querySelector("#groupResultsGrid");
const penaltiesList = document.querySelector("#penaltiesList");
const executiveDashboard = document.querySelector("#executiveDashboard");
const dashboardChampion = document.querySelector("#dashboardChampion");
const dashboardGoldenBoot = document.querySelector("#dashboardGoldenBoot");
const dashboardGoldenBootMeta = document.querySelector("#dashboardGoldenBootMeta");
const dashboardGoalsAverage = document.querySelector("#dashboardGoalsAverage");
const dashboardGoalsMeta = document.querySelector("#dashboardGoalsMeta");

function showAlert(message, type = "danger") {
  alertBox.className = `alert alert-${type}`;
  alertBox.textContent = message;
}

function clearAlert() {
  alertBox.className = "alert d-none";
  alertBox.textContent = "";
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Error HTTP ${response.status}`);
  }
  return response.json();
}

function groupTeams(teams) {
  return teams.reduce((accumulator, team) => {
    accumulator[team.group] = accumulator[team.group] || [];
    accumulator[team.group].push(team);
    return accumulator;
  }, {});
}

function renderGroups(teams) {
  const grouped = groupTeams(teams);
  const groups = "ABCDEFGH".split("");
  teamCount.textContent = `${teams.length} equipos`;
  groupsGrid.innerHTML = groups.map((group) => {
    const items = grouped[group] || [];
    return `
      <article class="group-card">
        <header>
          <h3>Grupo ${group}</h3>
          <span>${items.length}/4</span>
        </header>
        <ol>
          ${items.map((team) => `
            <li>
              <span>${team.name}</span>
              <span class="confederation-pill">${team.confederation}</span>
            </li>
          `).join("")}
        </ol>
      </article>
    `;
  }).join("");
}

function resetBracket() {
  championBadge.textContent = "Esperando simulacion";
  bracketBoard.className = "bracket-board empty-state";
  bracketBoard.innerHTML = "<p>Ejecuta la simulacion para ver octavos, cuartos, semifinal y final.</p>";
  groupResultsPanel.classList.add("d-none");
  executiveDashboard.classList.add("d-none");
  tournamentDetails.classList.add("d-none");
}

function renderBracket(result) {
  championBadge.textContent = "Simulacion completa";
  bracketBoard.className = "bracket-board";
  bracketBoard.innerHTML = `
    <div class="bracket-columns">
      ${result.bracket.map((round) => `
        <section class="round-column">
          <h3>${round.name}</h3>
          ${round.matches.map(renderMatch).join("")}
        </section>
      `).join("")}
    </div>
  `;
}

function renderMatch(match) {
  const homeWinner = match.winner === match.home_team;
  const awayWinner = match.winner === match.away_team;
  return `
    <article class="match-card">
      <div class="team-row ${homeWinner ? "winner" : ""}">
        <span>${match.home_team}</span>
        <span class="score">${match.home_goals}</span>
      </div>
      <div class="team-row ${awayWinner ? "winner" : ""}">
        <span>${match.away_team}</span>
        <span class="score">${match.away_goals}</span>
      </div>
      ${match.decided_by ? `<div class="decided-by">Definido por ${match.decided_by}</div>` : ""}
    </article>
  `;
}

function renderTournamentDetails(result) {
  tournamentDetails.classList.remove("d-none");
  bestPlayerName.textContent = result.best_player.player;
  bestPlayerMeta.textContent = `${result.best_player.team} | ${result.best_player.goals} goles | ${result.best_player.assists} asistencias | ${result.best_player.score} pts`;
  topScorersList.innerHTML = renderRanking(result.top_scorers, "goals", "goles");
  topAssistersList.innerHTML = renderRanking(result.top_assisters, "assists", "asist.");
  penaltiesList.innerHTML = renderPenalties(result.penalties);
}

function renderGroupResults(result) {
  groupResultsPanel.classList.remove("d-none");
  groupResultsGrid.innerHTML = result.groups.map(renderGroupResult).join("");
}

function renderExecutiveDashboard(metrics) {
  executiveDashboard.classList.remove("d-none");
  dashboardChampion.textContent = metrics.champion;
  dashboardGoldenBoot.textContent = metrics.golden_boot.player;
  dashboardGoldenBootMeta.textContent = `${metrics.golden_boot.team} | ${metrics.golden_boot.goals} goles`;
  dashboardGoalsAverage.textContent = metrics.goals_per_match_average.toFixed(2);
  dashboardGoalsMeta.textContent = `${metrics.total_goals} goles en ${metrics.total_matches} partidos`;
}

function renderRanking(players, statKey, label) {
  return players.map((player, index) => `
    <div class="ranking-row">
      <span class="ranking-position">${index + 1}</span>
      <span class="ranking-name">
        <strong>${player.player}</strong>
        <span>${player.team} | ${player.goals} G | ${player.assists} A</span>
        <span>Grupos: ${player.group_goals} G / ${player.group_assists} A | Eliminacion: ${player.knockout_goals} G / ${player.knockout_assists} A</span>
      </span>
      <span class="ranking-value">${player[statKey]} ${label}</span>
    </div>
  `).join("");
}

function renderPenalties(penalties) {
  if (!penalties.length) {
    return "<p class=\"muted-copy mb-0\">No hubo partidos definidos por penales en esta simulacion.</p>";
  }
  return penalties.map((penalty) => `
    <div class="penalty-row">
      <span class="penalty-round">${penalty.round}</span>
      <strong>${penalty.winner}</strong>
      <span>elimino a ${penalty.loser} (${penalty.home_team} ${penalty.home_goals} - ${penalty.away_goals} ${penalty.away_team})</span>
    </div>
  `).join("");
}

function renderGroupResult(group) {
  return `
    <section class="group-result-card">
      <h4>Grupo ${group.group}</h4>
      ${group.matches.map(renderGroupMatch).join("")}
      <table class="standing-table">
        <thead>
          <tr>
            <th>Equipo</th>
            <th>Pts</th>
            <th>GF</th>
            <th>GC</th>
            <th>DG</th>
          </tr>
        </thead>
        <tbody>
          ${group.standings.map((row) => `
            <tr>
              <td>${row.team}</td>
              <td>${row.points}</td>
              <td>${row.goals_for}</td>
              <td>${row.goals_against}</td>
              <td>${row.goal_difference}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    </section>
  `;
}

function renderGroupMatch(match) {
  const goals = match.goals.length
    ? `<div class="goal-list">${match.goals.map((goal) => `${goal.minute}' ${goal.scorer}${goal.assistant ? ` (${goal.assistant})` : ""}`).join(" · ")}</div>`
    : "";
  return `
    <div class="result-line">
      <span>${match.home_team}</span>
      <strong class="result-score">${match.home_goals} - ${match.away_goals}</strong>
      <span>${match.away_team}</span>
    </div>
    ${goals}
  `;
}

async function loadTeams() {
  const teams = await requestJson("/teams");
  renderGroups(teams);
}

async function simulateWorldCup() {
  clearAlert();
  simulateButton.disabled = true;
  drawButton.disabled = true;
  simulateButton.textContent = "Simulando...";
  try {
    const result = await requestJson("/simulator/run", { method: "POST" });
    const metrics = await requestJson("/metrics/dashboard");
    const teams = await requestJson("/teams");
    renderGroups(teams);
    renderGroupResults(result);
    renderBracket(result);
    renderExecutiveDashboard(metrics);
    renderTournamentDetails(result);
    showAlert(`La simulacion finalizo. Campeon: ${result.champion}.`, "success");
  } catch (error) {
    showAlert(error.message);
  } finally {
    simulateButton.disabled = false;
    drawButton.disabled = false;
    simulateButton.textContent = "Simular Mundial";
  }
}

async function drawGroups() {
  clearAlert();
  drawButton.disabled = true;
  simulateButton.disabled = true;
  drawButton.textContent = "Sorteando...";
  try {
    const teams = await requestJson("/simulator/draw", { method: "POST" });
    renderGroups(teams);
    resetBracket();
    showAlert("Sorteo realizado: cada grupo respeta confederaciones sin repetir.", "success");
  } catch (error) {
    showAlert(error.message);
  } finally {
    drawButton.disabled = false;
    simulateButton.disabled = false;
    drawButton.textContent = "Sortear Grupos";
  }
}

drawButton.addEventListener("click", drawGroups);
simulateButton.addEventListener("click", simulateWorldCup);

loadTeams().catch((error) => showAlert(error.message));
