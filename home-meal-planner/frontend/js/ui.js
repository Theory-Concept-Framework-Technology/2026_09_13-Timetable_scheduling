(function () {
    "use strict";

    function navigateToSection(section) {
        document.querySelectorAll(".top-nav-link").forEach(function (btn) {
            btn.classList.toggle("active", btn.getAttribute("data-section") === section);
        });
        document.querySelectorAll(".page-section").forEach(function (sec) {
            sec.classList.remove("active");
        });
        var target = document.getElementById("section-" + section);
        if (target) {
            target.classList.add("active");
        }
        if (window.HomeMealsPlanner && window.HomeMealsPlanner.onSectionShown) {
            window.HomeMealsPlanner.onSectionShown(section);
        }
    }

    function closeModal() {
        var modal = document.getElementById("cell-modal");
        if (modal) {
            modal.hidden = true;
        }
    }

    function initNavigation() {
        document.querySelectorAll(".top-nav-link").forEach(function (btn) {
            btn.addEventListener("click", function () {
                navigateToSection(btn.getAttribute("data-section"));
            });
        });
        document.querySelectorAll("[data-goto-section]").forEach(function (btn) {
            btn.addEventListener("click", function () {
                navigateToSection(btn.getAttribute("data-goto-section"));
            });
        });
    }

    function initModal() {
        var closeBtn = document.getElementById("modal-close");
        var backdrop = document.getElementById("modal-backdrop");
        if (closeBtn) {
            closeBtn.addEventListener("click", closeModal);
        }
        if (backdrop) {
            backdrop.addEventListener("click", closeModal);
        }
    }

    function init() {
        initNavigation();
        initModal();
        navigateToSection("meals-dashboard");
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }

    window.MealPlannerUI = { navigateToSection: navigateToSection, closeModal: closeModal };
})();
