document.addEventListener("DOMContentLoaded", function () {
  const sameAsAboveCheckbox = document.getElementById("sameAsAbove");
  const differentAddressInputs = document.getElementById("differentAddressInputs");

  differentAddressInputs.classList.remove("hidden");

  sameAsAboveCheckbox.addEventListener("change", function () {
    if (sameAsAboveCheckbox.checked) {
      differentAddressInputs.classList.add("hidden");
    } else {
      differentAddressInputs.classList.remove("hidden");
    }
  });

  const steps = Array.from(document.querySelectorAll(".step"));
  const nextButtons = document.querySelectorAll(".next");
  const prevButtons = document.querySelectorAll(".prev");
  const form = document.getElementById("multiStepForm");
  const progressBar = document.getElementById("progressBar");
  let currentStep = 0;

  nextButtons.forEach((button) => {
    button.addEventListener("click", () => {
      if (currentStep < steps.length - 1) {
        steps[currentStep].classList.remove("active");
        steps[currentStep + 1].classList.add("active");
        currentStep++;
        updateProgressBar();
      }
    });
  });

  prevButtons.forEach((button) => {
    button.addEventListener("click", () => {
      if (currentStep > 0) {
        steps[currentStep].classList.remove("active");
        steps[currentStep - 1].classList.add("active");
        currentStep--;
        updateProgressBar();
      }
    });
  });

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    alert("Successfully submitted.");
  });

  document.getElementById("addRow").addEventListener("click", () => {
    const newRow = document.createElement("tr");
    const srNumber = document.createElement("td");
    srNumber.textContent = document.getElementById("tableBody").rows.length + 1;
    newRow.appendChild(srNumber);
    for (let i = 0; i < 6; i++) {
        const newCell = document.createElement("td");
        const input = document.createElement("input");
        if (i === 3 || i === 4) {
            input.type = "number";
        } else {
            input.type = "text";
        }
        input.classList.add("form-control");
        newCell.appendChild(input);
        newRow.appendChild(newCell);
    }
    const actionsCell = document.createElement("td");
    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.classList.add("btn", "btn-danger", "btn-sm", "deleteRow");
    deleteButton.textContent = "Delete";
    actionsCell.appendChild(deleteButton);
    newRow.appendChild(actionsCell);
    document.getElementById("tableBody").appendChild(newRow);
    addDeleteEvent();
  });

  function addDeleteEvent() {
    document.querySelectorAll(".deleteRow").forEach((button) => {
      button.addEventListener("click", () => {
        button.closest("tr").remove();
      });
    });
  }

  addDeleteEvent();

  function updateProgressBar() {
    const progress = (currentStep / (steps.length - 1)) * 100;
    progressBar.style.width = progress + "%";
  }
});

document.addEventListener("DOMContentLoaded", function () {
  const footer = document.querySelector(".footer");

  function checkScroll() {
    const scrollPosition = window.scrollY + window.innerHeight;
    const bodyHeight = document.body.scrollHeight;

    if (scrollPosition >= bodyHeight) {
      footer.classList.add("show");
    } else {
      footer.classList.remove("show");
    }
  }

  window.addEventListener("scroll", checkScroll);
  window.addEventListener("resize", checkScroll);
});