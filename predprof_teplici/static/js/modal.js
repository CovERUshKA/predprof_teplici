
const modals = document.querySelectorAll(".modal");

const overlay = document.querySelector(".overlay");

const openModalBtns = document.querySelectorAll(".btn-open");

const closeModals = [];

for (let modal of modals){
    closeModals.push(function () {
        modal.classList.add("hidden");
        overlay.classList.add("hidden");
    }
    )
}
// close modal function
// close the modal when the close button and overlay is clicked
for (let i = 0; i < modals.length; i++){
    overlay.addEventListener("click", closeModals[i]);
}

// close modal when the Esc key is pressed
for (let i = 0; i < modals.length; i++){
    document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !modals[i].classList.contains("hidden")) {
        closeModals[i]();
    }
    });
}

// open modal function
for (let i = 0; i < modals.length; i++){
    const openModal = function () {
        modals[i].classList.remove("hidden");
        overlay.classList.remove("hidden");
    };
    // open modal event
    openModalBtns[i].addEventListener("click", openModal);

}