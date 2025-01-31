document.addEventListener('DOMContentLoaded', async () => {
  // Récupération des données
  const response = await fetch('/api/dashboard-stats');
  const data = await response.json();

  // Mise à jour des KPI
  document.getElementById('projectsCount').textContent = data.projectsCount;
  document.getElementById('completedTasks').textContent = data.completedTasks;
  document.getElementById('overdueTasks').textContent = data.overdueTasks;
  document.getElementById('teamMembers').textContent = data.teamMembers;

  // Rendu des tâches
  const tasksContainer = document.getElementById('recentTasks');
  data.recentTasks.forEach(task => {
      tasksContainer.innerHTML += `
          <div class="list-group-item">
              <div class="d-flex justify-content-between">
                  <div>
                      <strong>${task.title}</strong>
                      <span class="badge bg-${getPriorityClass(task.priority)} ms-2">${task.priority}</span>
                  </div>
                  <small>${task.dueDate}</small>
              </div>
              <div class="text-muted">${task.project}</div>
          </div>
      `;
  });

  // Graphique
  new Chart(document.getElementById('progressChart'), {
      type: 'bar',
      data: {
          labels: data.projects.map(p => p.name),
          datasets: [{
              label: 'Progression (%)',
              data: data.projects.map(p => p.progress),
              backgroundColor: '#007bff'
          }]
      }
  });
});

function getPriorityClass(priority) {
  const classes = { 'Haute': 'danger', 'Moyenne': 'warning', 'Basse': 'success' };
  return classes[priority] || 'secondary';
}