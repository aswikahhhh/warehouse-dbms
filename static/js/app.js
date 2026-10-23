document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-toggle-form]").forEach(button => {
    button.addEventListener("click", () => {
      const panel = document.getElementById("add-panel");
      if (!panel) return;
      panel.hidden = !panel.hidden;
      if (!panel.hidden) panel.querySelector("input, select")?.focus();
    });
  });
  const search = document.querySelector("[data-table-search]");
  const table = document.querySelector("[data-search-table]");
  if (search && table) search.addEventListener("input", () => {
    const q = search.value.toLowerCase().trim();
    table.querySelectorAll("tbody tr").forEach(row => {
      row.hidden = !row.innerText.toLowerCase().includes(q);
    });
  });
});
