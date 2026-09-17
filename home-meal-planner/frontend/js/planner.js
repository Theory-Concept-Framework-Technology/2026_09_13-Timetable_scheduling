(function () {
    "use strict";

    var API_BASE = "";
    var planData = null;
    var loading = false;

    var MEAL_TYPE_LABELS = {
        breakfast: "Breakfast",
        lunch: "Lunch",
        snack: "Snack",
        dinner: "Dinner"
    };

    var MEAL_ICONS = {
        breakfast: "🍳",
        lunch: "🍛",
        snack: "🥗",
        dinner: "🌙"
    };

    var KPI_ICONS = ["🔥", "💪", "🍞", "🥑"];

    function mealTypeBadge(mealType) {
        var label = MEAL_TYPE_LABELS[mealType] || mealType;
        var icon = MEAL_ICONS[mealType] || "🍽";
        return '<span class="meal-type-badge type-' + escapeHtml(mealType) + '">' +
            escapeHtml(icon + " " + label) + "</span>";
    }

    var LOCAL_ART = {
        breakfast: "assets/meals/breakfast.svg",
        lunch: "assets/meals/lunch.svg",
        snack: "assets/meals/snack.svg",
        dinner: "assets/meals/dinner.svg",
        default: "assets/meals/default.svg"
    };

    function mealArtClass(mealType) {
        if (mealType === "breakfast" || mealType === "lunch" || mealType === "snack" || mealType === "dinner") {
            return "meal-art-" + mealType;
        }
        return "meal-art-default";
    }

    function mealThumbHtml(image, mealType, name) {
        var alt = escapeHtml(name || "Meal");
        var artClass = mealArtClass(mealType);
        return '<div class="meal-thumb-wrap meal-art ' + artClass + '" role="img" aria-label="' + alt + '"></div>';
    }

    function gridThumbHtml(image, mealType) {
        return '<div class="grid-mini-art meal-art ' + mealArtClass(mealType) + '" aria-hidden="true"></div>';
    }

    function updateTodayPill() {
        var el = document.getElementById("today-pill");
        if (el && planData && planData.today) {
            el.textContent = "📆 " + planData.today + " · Tap any dish for the full recipe";
        }
    }

    function escapeHtml(text) {
        if (text === null || text === undefined) {
            return "";
        }
        var div = document.createElement("div");
        div.textContent = String(text);
        return div.innerHTML;
    }

    function readApiBase() {
        var meta = document.querySelector('meta[name="meal-api-base"]');
        if (meta && meta.getAttribute("content")) {
            return meta.getAttribute("content").replace(/\/$/, "");
        }
        var port = window.location.port;
        if (port === "8080" || port === "5500" || port === "3000" || port === "8002" || port === "8003") {
            return "http://127.0.0.1:8000";
        }
        if (port === "8000") {
            return "";
        }
        return "";
    }

    function apiUrl(path) {
        return API_BASE + path;
    }

    function showBanner(message, kind) {
        var el = document.getElementById("meals-api-banner");
        if (!el) {
            return;
        }
        el.hidden = false;
        el.className = "meals-banner meals-banner-" + (kind || "warn");
        el.textContent = message;
    }

    function hideBanner() {
        var el = document.getElementById("meals-api-banner");
        if (el) {
            el.hidden = true;
        }
    }

    function setDisclaimer(text) {
        var el = document.getElementById("meals-global-disclaimer");
        if (el && text) {
            el.textContent = text;
        }
    }

    function skeletonCards(count, targetId) {
        var root = document.getElementById(targetId);
        if (!root) {
            return;
        }
        root.innerHTML = new Array(count).join(
            '<div class="meal-card panel meals-skeleton"><span class="skeleton-line"></span></div>'
        );
    }

    function fetchJson(path, options) {
        return fetch(apiUrl(path), options || {}).then(function (response) {
            if (!response.ok) {
                var err = new Error("Request failed");
                err.status = response.status;
                throw err;
            }
            return response.json();
        });
    }

    function loadPlan() {
        if (loading) {
            return Promise.resolve(planData);
        }
        loading = true;
        if (!planData) {
            skeletonCards(4, "meals-today-grid");
        } else {
            var grid = document.getElementById("meals-today-grid");
            if (grid) {
                grid.classList.add("is-loading");
            }
        }
        return fetchJson("/api/meals/plans/current")
            .then(function (data) {
                planData = data;
                hideBanner();
                setDisclaimer(data.disclaimer || "");
                renderAll();
                loading = false;
                return data;
            })
            .catch(function (err) {
                loading = false;
                var msg = "Meal planner API is unavailable. Run the backend (run_api.bat) or start Docker Compose.";
                if (err.status === 429) {
                    msg = "Recipe service rate limit reached. Cached recipes may still be available shortly.";
                } else if (err.status === 401) {
                    msg = "Invalid API key configuration on the server.";
                }
                showBanner(msg, "error");
                renderOfflineEmpty();
                return null;
            });
    }

    function renderOfflineEmpty() {
        var grid = document.getElementById("meals-today-grid");
        if (grid) {
            grid.innerHTML = '<p class="muted">Connect the meal API to load today&apos;s meals.</p>';
        }
    }

    function formatMacros(slot) {
        return (
            Math.round(slot.calories || 0) + " kcal | Protein " +
            Math.round(slot.protein_g || 0) + "g | Carbs " +
            Math.round(slot.carbohydrates_g || 0) + "g | Fat " +
            Math.round(slot.fat_g || 0) + "g"
        );
    }

    function renderToday() {
        if (!planData || !planData.daily) {
            return;
        }
        var daily = planData.daily;
        var grid = document.getElementById("meals-today-grid");
        if (!grid) {
            return;
        }
        grid.innerHTML = (daily.meals || []).map(function (meal) {
            return (
                '<button type="button" class="meal-card meals-clickable" data-recipe-id="' +
                escapeHtml(meal.recipe_id) + '">' +
                mealThumbHtml(meal.image, meal.meal_type, meal.name) +
                '<div class="meal-card-body">' +
                mealTypeBadge(meal.meal_type) +
                '<span class="meal-card-time">⏰ ' + escapeHtml(meal.meal_time || "") + "</span>" +
                '<span class="meal-card-name">' + escapeHtml(meal.name) + "</span>" +
                '<span class="muted meal-card-macros">' + escapeHtml(Math.round(meal.calories) + " kcal · " +
                    Math.round(meal.protein_g || 0) + "g protein") + "</span>" +
                "</div></button>"
            );
        }).join("");

        bindMealClicks(grid);
        grid.classList.remove("is-loading");

        var kpis = document.getElementById("meals-today-nutrition");
        if (kpis) {
            kpis.innerHTML = [
                ["Calories", daily.total_calories + " kcal"],
                ["Protein", daily.total_protein_g + "g"],
                ["Carbs", daily.total_carbohydrates_g + "g"],
                ["Fat", daily.total_fat_g + "g"]
            ].map(function (pair, idx) {
                return '<div class="kpi-card"><span class="kpi-icon">' + (KPI_ICONS[idx] || "📊") +
                    '</span><span class="kpi-label">' + escapeHtml(pair[0]) +
                    '</span><strong class="kpi-value">' + escapeHtml(pair[1]) + "</strong></div>";
            }).join("");
        }

        var target = daily.calorie_target || 2000;
        var pct = Math.min(100, (daily.total_calories / target) * 100);
        var fill = document.getElementById("meals-calorie-bar-fill");
        var label = document.getElementById("meals-calorie-bar-label");
        if (fill) {
            fill.style.width = pct + "%";
        }
        if (label) {
            label.textContent = Math.round(daily.total_calories) + " / " + target + " kcal";
        }
    }

    function slotByDayAndType(plan, day, mealType) {
        var slots = (plan && plan.slots) || [];
        for (var i = 0; i < slots.length; i++) {
            if (slots[i].day === day && slots[i].meal_type === mealType) {
                return slots[i];
            }
        }
        return null;
    }

    function renderWeeklyGrid(containerId, compact) {
        if (!planData || !planData.plan) {
            return;
        }
        var root = document.getElementById(containerId);
        if (!root) {
            return;
        }
        var days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
        var types = ["breakfast", "lunch", "snack", "dinner"];
        var head = '<div class="meals-grid-row meals-grid-head"><span class="meals-grid-corner"></span>';
        days.forEach(function (d) {
            head += '<span class="meals-grid-day">' + escapeHtml(compact ? d.slice(0, 3).toUpperCase() : d) + "</span>";
        });
        head += "</div>";
        var body = types.map(function (type) {
            var row = '<div class="meals-grid-row row-' + type + '"><span class="meals-grid-meal-type">' +
                escapeHtml(MEAL_ICONS[type] + " " + MEAL_TYPE_LABELS[type]) + "</span>";
            days.forEach(function (day) {
                var slot = slotByDayAndType(planData.plan, day, type);
                if (!slot) {
                    row += '<span class="meals-grid-cell muted">—</span>';
                } else {
                    row += '<button type="button" class="meals-grid-cell meals-clickable" data-recipe-id="' +
                        escapeHtml(slot.recipe_id) + '">' +
                        '<span class="grid-cell-inner">' +
                        gridThumbHtml(slot.image, type) +
                        '<span class="meals-grid-meal-name">' + escapeHtml(slot.name) + "</span>" +
                        '<span class="meals-grid-kcal">' + escapeHtml(Math.round(slot.calories) + " kcal") + "</span>" +
                        "</span></button>";
                }
            });
            return row + "</div>";
        }).join("");
        root.innerHTML = head + body;
        bindMealClicks(root);
    }

    function renderMobileDays() {
        if (!planData || !planData.plan) {
            return;
        }
        var root = document.getElementById("meals-weekly-mobile");
        if (!root) {
            return;
        }
        var days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
        var types = ["breakfast", "lunch", "snack", "dinner"];
        root.innerHTML = days.map(function (day) {
            var blocks = types.map(function (type) {
                var slot = slotByDayAndType(planData.plan, day, type);
                if (!slot) {
                    return "";
                }
                return (
                    '<div class="meals-day-block">' +
                    "<h4>" + escapeHtml(MEAL_ICONS[type] + " " + (MEAL_TYPE_LABELS[type] || type)) + "</h4>" +
                    '<button type="button" class="meals-clickable meals-day-meal" data-recipe-id="' +
                    escapeHtml(slot.recipe_id) + '">' +
                    (slot.image && slot.image.indexOf("http") === 0
                        ? '<img src="' + escapeHtml(slot.image) + '" alt="">'
                        : '<div class="grid-mini-art meal-art ' + mealArtClass(type) + '"></div>') +
                    '<span><strong>' + escapeHtml(slot.name) + '</strong><br><span class="muted">' +
                    escapeHtml(Math.round(slot.calories) + " kcal") + "</span></span>" +
                    "</button></div>"
                );
            }).join("");
            return '<article class="panel meals-day-card"><h3>' + escapeHtml(day) + "</h3>" + blocks + "</article>";
        }).join("");
        bindMealClicks(root);
    }

    function renderWeekChart() {
        var root = document.getElementById("meals-weekly-chart");
        if (!root || !planData || !planData.weekly_nutrition) {
            return;
        }
        var days = planData.weekly_nutrition.days || [];
        var maxCal = 1;
        days.forEach(function (d) {
            if (d.total_calories > maxCal) {
                maxCal = d.total_calories;
            }
        });
        root.innerHTML = "<h4 class=\"subsection-title\">Daily calories (week)</h4>" +
            days.map(function (d) {
                var pct = Math.round((d.total_calories / maxCal) * 100);
                return (
                    '<div class="meals-week-chart-row">' +
                    '<span class="meals-week-chart-day">' + escapeHtml(d.day.slice(0, 3)) + "</span>" +
                    '<div class="meals-week-chart-bar"><div style="width:' + pct + '%"></div></div>' +
                    '<span class="meals-week-chart-val">' + escapeHtml(Math.round(d.total_calories) + "") + "</span>" +
                    "</div>"
                );
            }).join("");
    }

    function renderAll() {
        updateTodayPill();
        renderToday();
        renderWeeklyGrid("meals-weekly-preview", true);
        renderWeeklyGrid("meals-weekly-full", false);
        renderMobileDays();
        renderWeekChart();
    }

    function bindMealClicks(root) {
        if (!root) {
            return;
        }
        root.querySelectorAll(".meals-clickable[data-recipe-id]").forEach(function (btn) {
            btn.addEventListener("click", function () {
                openRecipe(btn.getAttribute("data-recipe-id"));
            });
        });
    }

    function openRecipe(recipeId) {
        if (!recipeId) {
            return;
        }
        var modal = document.getElementById("cell-modal");
        var content = document.getElementById("modal-content");
        if (!modal || !content) {
            return;
        }
        content.innerHTML = '<p class="muted">Loading recipe…</p>';
        modal.hidden = false;
        fetchJson("/api/meals/recipes/" + encodeURIComponent(recipeId))
            .then(function (recipe) {
                var n = recipe.nutrition || {};
                var ing = (recipe.ingredients || []).map(function (i) {
                    return "<li>" + escapeHtml(i.measure ? i.measure + " " : "") + escapeHtml(i.name) + "</li>";
                }).join("");
                var nutritionLine = Math.round(n.calories || 0) + " kcal | Protein " +
                    Math.round(n.protein_g || 0) + "g | Carbs " +
                    Math.round(n.carbohydrates_g || 0) + "g | Fat " +
                    Math.round(n.fat_g || 0) + "g";
                var sourceNote = n.source === "catalog"
                    ? "Catalog nutrition (approximate)."
                    : n.source === "api"
                        ? "API-provided nutrition (approximate)."
                        : "Estimated nutrition (approximate).";
                content.innerHTML =
                    (recipe.image ? '<img class="recipe-detail-img" src="' + escapeHtml(recipe.image) + '" alt="">' : "") +
                    "<h3 class=\"modal-subject\">" + escapeHtml(recipe.name) + "</h3>" +
                    "<p><strong>Serving size:</strong> " + escapeHtml(String(recipe.servings || 1)) + " serving(s)</p>" +
                    "<p><strong>Prep time:</strong> " + escapeHtml(recipe.preparation_time_min + " min") + "</p>" +
                    "<p><strong>Nutrition:</strong> " + escapeHtml(nutritionLine) + "</p>" +
                    "<p class=\"muted\">" + escapeHtml(sourceNote + " " + (n.disclaimer || "")) + "</p>" +
                    "<h4>Ingredients</h4><ul>" + ing + "</ul>" +
                    "<h4>Instructions</h4><p>" + escapeHtml(recipe.instructions || "No instructions available.") + "</p>";
            })
            .catch(function () {
                content.innerHTML = "<p>Could not load recipe details. The API may be unavailable.</p>";
            });
    }

    function runSearch() {
        var q = (document.getElementById("meals-search-input") || {}).value || "";
        var mealType = (document.getElementById("meals-filter-type") || {}).value || "";
        var cuisine = (document.getElementById("meals-filter-cuisine") || {}).value || "";
        var maxTime = (document.getElementById("meals-filter-time") || {}).value || "";
        var maxCal = (document.getElementById("meals-filter-max-cal") || {}).value || "";
        var highProtein = (document.getElementById("meals-filter-high-protein") || {}).checked;

        var params = new URLSearchParams();
        if (q) {
            params.set("q", q);
        }
        if (mealType) {
            params.set("meal_type", mealType);
        }
        if (cuisine) {
            params.set("cuisine", cuisine);
        }
        if (maxTime) {
            params.set("max_time", maxTime);
        }
        if (maxCal) {
            params.set("max_calories", maxCal);
        }
        if (highProtein) {
            params.set("high_protein", "true");
        }

        var resultsEl = document.getElementById("meals-search-results");
        var emptyEl = document.getElementById("meals-search-empty");
        if (resultsEl) {
            resultsEl.innerHTML = '<div class="meals-skeleton panel">Searching…</div>';
        }
        fetchJson("/api/meals/search?" + params.toString())
            .then(function (data) {
                if (emptyEl) {
                    emptyEl.hidden = (data.results || []).length > 0;
                }
                if (!resultsEl) {
                    return;
                }
                resultsEl.innerHTML = (data.results || []).map(function (r) {
                    var type = (r.meal_types && r.meal_types[0]) || "lunch";
                    return (
                        '<button type="button" class="meal-search-card meal-card meals-clickable" data-recipe-id="' +
                        escapeHtml(r.id) + '">' +
                        mealThumbHtml(r.image, type, r.name) +
                        '<div class="meal-card-body"><strong>' + escapeHtml(r.name) + "</strong>" +
                        '<span class="muted">' + escapeHtml(Math.round(r.calories) + " kcal · " +
                            Math.round(r.protein_g) + "g protein · " + r.preparation_time_min + " min") + "</span></div>" +
                        "</button>"
                    );
                }).join("");
                bindMealClicks(resultsEl);
            })
            .catch(function () {
                if (resultsEl) {
                    resultsEl.innerHTML = "<p class=\"muted\">Search failed. Check that the meal API is running.</p>";
                }
            });
    }

    function generatePlan() {
        var btn = document.getElementById("btn-generate-meal-plan");
        if (btn) {
            btn.disabled = true;
            btn.textContent = "Generating…";
        }
        fetchJson("/api/meals/plans/generate", { method: "POST" })
            .then(function (data) {
                planData = {
                    plan: data.plan,
                    daily: null,
                    weekly_nutrition: data.weekly_nutrition,
                    disclaimer: data.disclaimer
                };
                return fetchJson("/api/meals/plans/current");
            })
            .then(function (data) {
                planData = data;
                renderAll();
            })
            .catch(function () {
                showBanner("Could not generate a meal plan. Try again when the API is available.", "error");
            })
            .finally(function () {
                if (btn) {
                    btn.disabled = false;
                    btn.textContent = "✨ Shuffle fresh weekly menu";
                }
            });
    }

    function initMealsUi() {
        API_BASE = readApiBase();
        setDisclaimer(
            "Nutrition values are approximate estimates and may vary by serving size and ingredients."
        );
        var genBtn = document.getElementById("btn-generate-meal-plan");
        if (genBtn) {
            genBtn.addEventListener("click", generatePlan);
        }
        var searchBtn = document.getElementById("meals-search-btn");
        if (searchBtn) {
            searchBtn.addEventListener("click", runSearch);
        }
        var searchInput = document.getElementById("meals-search-input");
        if (searchInput) {
            searchInput.addEventListener("keydown", function (ev) {
                if (ev.key === "Enter") {
                    runSearch();
                }
            });
        }
        loadPlan();
    }

    function onSectionShown(section) {
        if (section === "meals-dashboard" || section === "meals-weekly") {
            if (!planData) {
                loadPlan();
            } else {
                renderAll();
            }
        }
    }

    window.HomeMealsPlanner = {
        init: initMealsUi,
        onSectionShown: onSectionShown,
        reload: loadPlan
    };

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initMealsUi);
    } else {
        initMealsUi();
    }
})();
