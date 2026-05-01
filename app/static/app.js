const apiBase = "/tasks";
const taskForm = document.getElementById("taskForm");
const todoList = document.getElementById("todoList");
const inProgressList = document.getElementById("inProgressList");
const doneList = document.getElementById("doneList");
const toast = document.getElementById("toast");
const taskTemplate = document.getElementById("taskCardTemplate");

let draggedId = null;
let draggedStatus = null;

/**
 * Exibe uma mensagem temporária no topo da tela.
 */
function showToast(message) {
  toast.textContent = message;
  toast.classList.remove("hidden");
  window.clearTimeout(window.toastTimeout);
  window.toastTimeout = window.setTimeout(() => {
    toast.classList.add("hidden");
  }, 2200);
}

/**
 * Busca todas as tarefas do backend e renderiza na tela.
 */
async function fetchTasks() {
  const response = await fetch(apiBase);
  if (!response.ok) {
    showToast("Não foi possível carregar as tarefas.");
    return;
  }

  const result = await response.json();
  const tasks = Array.isArray(result) ? result : result.items || [];
  renderTasks(tasks);
}

/**
 * Formata uma data para o padrão local do navegador.
 */
function formatDate(dateString) {
  return new Date(dateString).toLocaleString([], {
    year: "numeric",
    month: "numeric",
    day: "numeric",
  });
}

/**
 * Converte uma data YYYY-MM-DD para data local, evitando deslocamento por fuso horário.
 */
function parseLocalDate(dateString) {
  const [year, month, day] = dateString.split("-").map(Number);
  return new Date(year, month - 1, day);
}

/**
 * Formata um prazo YYYY-MM-DD sem aplicar conversão UTC.
 */
function formatDueDate(dateString) {
  return parseLocalDate(dateString).toLocaleDateString([], {
    year: "numeric",
    month: "numeric",
    day: "numeric",
  });
}

function getTodayLocalDate() {
  const now = new Date();
  return new Date(now.getFullYear(), now.getMonth(), now.getDate());
}

function getDaysUntilDue(dueDateString) {
  const dueDate = parseLocalDate(dueDateString);
  const today = getTodayLocalDate();
  return Math.floor((dueDate.getTime() - today.getTime()) / 86400000);
}

/**
 * Retorna o tempo desde a criação da tarefa em horas e minutos.
 */
function formatDuration(dateString) {
  const created = new Date(dateString);
  const diffMs = Math.max(Date.now() - created.getTime(), 0);
  const hours = Math.floor(diffMs / 3600000);
  const minutes = Math.floor((diffMs % 3600000) / 60000);

  if (hours >= 1) {
    return `${hours}h ${minutes}m`;
  }
  return `${minutes}m`;
}

/**
 * Define a classe de cor do cartão de tarefa com base no prazo.
 */
function getDueDateClass(task) {
  if (!task.due_date || task.status === "done") {
    return "task-card--neutral";
  }

  const daysUntilDue = getDaysUntilDue(task.due_date);

  if (daysUntilDue <= 0) {
    return "task-card--red";
  }
  if (daysUntilDue === 1) {
    return "task-card--yellow";
  }
  return "task-card--green";
}

/**
 * Retorna o texto e a variante de estilo da urgência da tarefa.
 */
function getUrgencyText(task) {
  if (task.status === "done") {
    return { text: "Concluído", variant: "ok" };
  }
  if (!task.due_date) {
    return { text: "Sem prazo definido", variant: "ok" };
  }

  const daysUntilDue = getDaysUntilDue(task.due_date);

  if (daysUntilDue <= 0) {
    return { text: "Urgente", variant: "urgent" };
  }
  if (daysUntilDue === 1) {
    return { text: "Atenção", variant: "attention" };
  }
  return { text: "OK", variant: "ok" };
}

/**
 * Gera o texto que aparece no rodapé do cartão de tarefa.
 */
function getTaskMeta(task) {
  const createdAt = formatDate(task.created_at);
  const startText = `Iniciada em ${createdAt}`;
  const duration = formatDuration(task.created_at);

  if (task.due_date) {
    const dueDate = parseLocalDate(task.due_date);
    const dueText = `${dueDate.getDate()}/${dueDate.getMonth() + 1}`;
    if (task.status === "done") {
      return `${startText} • prazo ${dueText} • concluída`;
    }
    return `${startText} • prazo ${dueText} • ${task.status === "in_progress" ? `em andamento há ${duration}` : `planejada`}`;
  }

  if (task.status === "done") {
    return `${startText} • concluída`;
  }

  return startText;
}

/**
 * Texto do botão principal de ação no cartão, dependendo do status atual.
 */
function getToggleButtonText(status) {
  switch (status) {
    case "todo":
      return "Iniciar";
    case "in_progress":
      return "Concluir";
    case "done":
      return "Reabrir";
    default:
      return "Mover";
  }
}

/**
 * Calcula qual será o próximo status ao clicar no botão de ação.
 */
function getNextStatus(status) {
  switch (status) {
    case "todo":
      return "in_progress";
    case "in_progress":
      return "done";
    case "done":
      return "todo";
    default:
      return "todo";
  }
}

/**
 * Cria o elemento HTML do cartão de tarefa a partir do template.
 */
function createTaskCard(task) {
  const element = taskTemplate.content.firstElementChild.cloneNode(true);
  element.dataset.id = task.id;
  element.dataset.status = task.status;
  element.classList.add(getDueDateClass(task));

  element.querySelector(".task-title").textContent = task.title;
  element.querySelector(".task-desc").textContent = task.description || "Nenhuma descrição fornecida.";
  element.querySelector(".task-meta").textContent = getTaskMeta(task);
  element.querySelector(".task-due").textContent = task.due_date
    ? `Prazo: ${formatDueDate(task.due_date)}`
    : "Sem prazo definido.";

  const urgency = getUrgencyText(task);
  const urgencyElement = element.querySelector(".task-urgency");
  urgencyElement.textContent = urgency.text;
  urgencyElement.className = `task-urgency task-urgency--${urgency.variant}`;

  element.querySelector(".task-date").textContent = formatDate(task.created_at);
  const toggleButton = element.querySelector(".toggle-status");
  const deleteButton = element.querySelector(".delete-task");

  toggleButton.textContent = getToggleButtonText(task.status);
  toggleButton.addEventListener("click", () => toggleTaskStatus(task.id, getNextStatus(task.status)));
  deleteButton.addEventListener("click", () => deleteTask(task.id));

  element.addEventListener("dragstart", (event) => {
    draggedId = task.id;
    draggedStatus = task.status;
    event.dataTransfer.effectAllowed = "move";
    element.classList.add("dragging");
  });

  element.addEventListener("dragend", () => {
    element.classList.remove("dragging");
    draggedId = null;
    draggedStatus = null;
  });

  return element;
}

/**
 * Atualiza os indicadores do dashboard com as quantidades de tarefas em cada estado.
 */
function updateDashboard(tasks) {
  const onTrack = tasks.filter((task) => getUrgencyText(task).variant === "ok" && task.status !== "done").length;
  const attention = tasks.filter((task) => getUrgencyText(task).variant === "attention").length;
  const urgent = tasks.filter((task) => getUrgencyText(task).variant === "urgent").length;
  const completed = tasks.filter((task) => task.status === "done").length;

  document.getElementById("onTrackCount").textContent = onTrack;
  document.getElementById("attentionCount").textContent = attention;
  document.getElementById("urgentCount").textContent = urgent;
  document.getElementById("completedCount").textContent = completed;
}

/**
 * Atualiza a barra de progresso da meta de conclusão.
 */
function updateGoalProgress(tasks) {
  const completed = tasks.filter((task) => task.status === "done").length;
  const total = tasks.length;
  const percentage = total === 0 ? 0 : Math.round((completed / total) * 100);

  document.getElementById("goalProgressValue").textContent = `${percentage}%`;
  document.getElementById("goalProgressBar").style.width = `${percentage}%`;
  document.getElementById("goalProgressText").textContent =
    total === 0
      ? "Adicione tarefas para iniciar sua meta."
      : `${completed} de ${total} tarefas concluídas`;
}

/**
 * Atualiza os contadores de cada coluna do quadro.
 */
function updateColumnCounts(tasks) {
  document.getElementById("todoCount").textContent = tasks.filter((task) => task.status === "todo").length;
  document.getElementById("inProgressCount").textContent = tasks.filter((task) => task.status === "in_progress").length;
  document.getElementById("doneCount").textContent = tasks.filter((task) => task.status === "done").length;
}

/**
 * Renderiza todas as tarefas no quadro e atualiza os indicadores do dashboard.
 */
function renderTasks(tasks) {
  todoList.innerHTML = "";
  inProgressList.innerHTML = "";
  doneList.innerHTML = "";

  tasks.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

  tasks.forEach((task) => {
    const card = createTaskCard(task);
    if (task.status === "in_progress") {
      inProgressList.appendChild(card);
    } else if (task.status === "done") {
      doneList.appendChild(card);
    } else {
      todoList.appendChild(card);
    }
  });

  updateDashboard(tasks);
  updateGoalProgress(tasks);
  updateColumnCounts(tasks);
}

/**
 * Cria uma nova tarefa no backend.
 */
async function postTask(title, description, dueDate = null) {
  const response = await fetch(apiBase, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, description, due_date: dueDate }),
  });
  if (!response.ok) {
    const error = await response.json();
    const validationMessage = error.error?.details?.[0]?.msg;
    throw new Error(validationMessage || error.error?.message || "Não foi possível criar a tarefa.");
  }
  return response.json();
}

/**
 * Atualiza o status da tarefa escolhido pelo usuário.
 */
async function toggleTaskStatus(taskId, status) {
  const response = await fetch(`${apiBase}/${taskId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });
  if (!response.ok) {
    showToast("Não foi possível atualizar o status da tarefa.");
    return;
  }
  showToast("Tarefa movida com sucesso.");
  fetchTasks();
}

/**
 * Remove uma tarefa do backend.
 */
async function deleteTask(taskId) {
  const response = await fetch(`${apiBase}/${taskId}`, {
    method: "DELETE",
  });
  if (response.ok) {
    showToast("Tarefa removida.");
    fetchTasks();
  } else {
    showToast("Falha ao excluir a tarefa.");
  }
}

/**
 * Manipula o envio do formulário de criação de tarefa.
 */
async function handleFormSubmit(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const title = form.title.value.trim();
  const description = form.description.value.trim();
  const dueDate = form.due_date.value || null;

  if (!title) {
    showToast("O título da tarefa é obrigatório.");
    return;
  }

  try {
    await postTask(title, description, dueDate);
    form.reset();
    showToast("Tarefa criada com sucesso.");
    fetchTasks();
  } catch (error) {
    showToast(error.message);
  }
}

/**
 * Habilita o comportamento de arrastar e soltar dentro de uma coluna.
 */
function enableDrop(zone) {
  zone.addEventListener("dragover", (event) => {
    event.preventDefault();
    zone.classList.add("drag-over");
  });
  zone.addEventListener("dragleave", () => {
    zone.classList.remove("drag-over");
  });
  zone.addEventListener("drop", async (event) => {
    event.preventDefault();
    zone.classList.remove("drag-over");
    if (!draggedId) {
      return;
    }
    const status = zone.dataset.status;
    if (status && status !== draggedStatus) {
      await toggleTaskStatus(draggedId, status);
    }
  });
}

/**
 * Inicializa o comportamento da interface e carrega as tarefas.
 */
function init() {
  taskForm.addEventListener("submit", handleFormSubmit);
  enableDrop(todoList);
  enableDrop(inProgressList);
  enableDrop(doneList);
  fetchTasks();
}

init();
