const prevBtns = document.querySelectorAll(".btn-prev");
const nextBtns = document.querySelectorAll(".btn-next");
const progress = document.getElementById("progress");
const formSteps = document.querySelectorAll(".form-step");
const progressSteps = document.querySelectorAll(".progress-step");

let formStepsNum = 0;

nextBtns.forEach((btn) => {
  btn.addEventListener("click", () => {
    formStepsNum++;
    updateFormSteps();
    updateProgressbar();
  });
});

prevBtns.forEach((btn) => {
  btn.addEventListener("click", () => {
    formStepsNum--;
    updateFormSteps();
    updateProgressbar();
  });
});

function updateFormSteps() {
  formSteps.forEach((formStep) => {
    formStep.classList.contains("form-step-active") &&
      formStep.classList.remove("form-step-active");
  });

  formSteps[formStepsNum].classList.add("form-step-active");
}

function updateProgressbar() {
  progressSteps.forEach((progressStep, idx) => {
    if (idx < formStepsNum + 1) {
      progressStep.classList.add("progress-step-active");
    } else {
      progressStep.classList.remove("progress-step-active");
    }
  });

  const progressActive = document.querySelectorAll(".progress-step-active");

  progress.style.width =
    ((progressActive.length - 1) / (progressSteps.length - 1)) * 100 + "%";
}

document.addEventListener("DOMContentLoaded", function() {
  const progressSteps = document.querySelectorAll(".progress-step");
  const formSteps = document.querySelectorAll(".form-step");
  const progress = document.getElementById("progress");

  progressSteps.forEach((progressStep, idx) => {
      progressStep.addEventListener("click", () => {
          updateFormSteps(idx);
          updateProgressbar(idx);
      });
  });

  const addRowButtons = document.querySelectorAll(".addRow");
  addRowButtons.forEach((button) => {
      button.addEventListener("click", (event) => {
          const sheetIndex = event.target.dataset.sheet;
          $.ajax({
              url: '/add_row',
              type: 'POST',
              data: { sheet_index: sheetIndex },
              success: function(response) {
                  if (response.status === 'success') {
                      formSteps[sheetIndex].querySelector('.table-responsive').innerHTML = response.html;
                  } else {
                      console.error(response.message);
                  }
              },
              error: function(xhr, status, error) {
                  console.error(error);
              }
          });
      });
  });

  const deleteRowButtons = document.querySelectorAll(".deleteRow");
  deleteRowButtons.forEach((button) => {
      button.addEventListener("click", (event) => {
          const sheetIndex = event.target.dataset.sheet;
          const rowIndex = event.target.dataset.row;
          $.ajax({
              url: '/delete_row',
              type: 'POST',
              data: {
                  sheet_index: sheetIndex,
                  row_index: rowIndex
              },
              success: function(response) {
                  if (response.status === 'success') {
                      formSteps[sheetIndex].querySelector('.table-responsive').innerHTML = response.html;
                  } else {
                      console.error(response.message);
                  }
              },
              error: function(xhr, status, error) {
                  console.error(error);
              }
          });
      });
  });

  function updateFormSteps(formStepsNum) {
      formSteps.forEach((formStep) => {
          formStep.classList.contains("form-step-active") &&
              formStep.classList.remove("form-step-active");
      });
      formSteps[formStepsNum].classList.add("form-step-active");
  }

  function updateProgressbar(formStepsNum) {
      progressSteps.forEach((progressStep, idx) => {
          if (idx <= formStepsNum) {
              progressStep.classList.add("progress-step-active");
          } else {
              progressStep.classList.remove("progress-step-active");
          }
      });

      const progressActive = document.querySelectorAll(".progress-step-active");
      progress.style.width = ((progressActive.length - 1) / (progressSteps.length - 1)) * 100 + "%";
  }
});