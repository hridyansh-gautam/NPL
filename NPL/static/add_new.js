document.addEventListener("DOMContentLoaded", function() {
    const prevBtns = document.querySelectorAll(".btn-prev");
    const nextBtns = document.querySelectorAll(".btn-next");
    const progress = document.getElementById("progress");
    const formSteps = document.querySelectorAll(".form-step");
    const progressSteps = document.querySelectorAll(".progress-step");
  
    let formStepsNum = 0;
  
    nextBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        formStepsNum++;
        updateFormSteps(formStepsNum);
        updateProgressbar(formStepsNum);
      });
    });
  
    prevBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        formStepsNum--;
        updateFormSteps(formStepsNum);
        updateProgressbar(formStepsNum);
      });
    });
  
    progressSteps.forEach((progressStep, idx) => {
      progressStep.addEventListener("click", () => {
        formStepsNum = idx;
        updateFormSteps(formStepsNum);
        updateProgressbar(formStepsNum);
      });
    });
  
    function updateFormSteps(formStepsNum) {
      formSteps.forEach((formStep, idx) => {
        if (idx === formStepsNum) {
          formStep.classList.add("form-step-active");
        } else {
          formStep.classList.remove("form-step-active");
        }
      });
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