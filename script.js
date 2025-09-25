document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("taskForm");
  const columns = {
    today: document.querySelector("#today ul"),
    upcoming: document.querySelector("#upcoming ul"),
    completed: document.querySelector("#completed ul"),
  };

  function loadTasks() {
    fetch("/api/tasks")
      .then(res => res.json())
      .then(data => {
        console.log("Fetched tasks:", data); // Debug log
        ["today", "upcoming", "completed"].forEach(section => {
          columns[section].innerHTML = "";
          data[section].forEach(task => {
            const li = document.createElement("li");
            li.innerHTML = `
              <strong>${task.title}</strong><br>
              ${task.description || ""}<br>
              ${task.due_date} ${task.due_time}<br>
              ${section !== "completed" ? `<button onclick="completeTask(${task.id})">Complete</button>` : ""}
              <button onclick="deleteTask(${task.id})">Delete</button>
            `;
            columns[section].appendChild(li);
          });
        });
      });
  }

  form.addEventListener("submit", e => {
    e.preventDefault();
    const formData = new FormData(form);
    fetch("/add", {
      method: "POST",
      body: formData
    }).then(() => {
      form.reset();
      loadTasks();
    });
  });

  window.completeTask = function(id) {
    fetch(`/complete/${id}`).then(loadTasks);
  };

  window.deleteTask = function(id) {
    fetch(`/delete/${id}`).then(loadTasks);
  };

  loadTasks();
});
