(function () {
    "use strict";

    var STORAGE = {
        theme: "sts-theme",
        font: "sts-font",
        borderMode: "sts-border-mode",
        fillColors: "sts-colors-fill",
        borderColors: "sts-colors-border"
    };

    function loadDashboardData() {
        var el = document.getElementById("dashboard-data");
        if (!el || !el.textContent) {
            return null;
        }
        try {
            return JSON.parse(el.textContent);
        } catch (e) {
            console.error("Failed to parse dashboard data", e);
            return null;
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

    function readJsonStorage(key, fallback) {
        try {
            var raw = localStorage.getItem(key);
            if (!raw) {
                return fallback;
            }
            return JSON.parse(raw);
        } catch (e) {
            return fallback;
        }
    }

    function writeJsonStorage(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            /* ignore */
        }
    }

    var data = loadDashboardData();

    var filters = {
        classGroup: "",
        section: "",
        teacher: "",
        room: "",
        day: ""
    };

    var prefs = {
        theme: "light",
        font: "modern",
        borderMode: "teacher",
        fillMap: {},
        borderMap: {}
    };

    var tooltipEl = null;
    var modalEl = null;

    function initPrefsFromStorage() {
        try {
            prefs.theme = localStorage.getItem(STORAGE.theme) || "light";
            prefs.font = localStorage.getItem(STORAGE.font) || "modern";
            prefs.borderMode = localStorage.getItem(STORAGE.borderMode) || "teacher";
        } catch (e) {
            /* ignore */
        }
        if (data) {
            prefs.fillMap = readJsonStorage(STORAGE.fillColors, data.colorMap || {});
            prefs.borderMap = readJsonStorage(
                STORAGE.borderColors,
                Object.assign(
                    {},
                    data.defaultBorderMapTeacher || {},
                    data.defaultBorderMapDay || {}
                )
            );
        }
    }

    function applyThemeFont() {
        document.documentElement.setAttribute("data-theme", prefs.theme);
        document.documentElement.setAttribute("data-font", prefs.font);
        var themeSel = document.getElementById("theme-select");
        var fontSel = document.getElementById("font-pair");
        var borderSel = document.getElementById("border-mode");
        if (themeSel) {
            themeSel.value = prefs.theme;
        }
        if (fontSel) {
            fontSel.value = prefs.font;
        }
        if (borderSel) {
            borderSel.value = prefs.borderMode;
        }
        updateBorderLegend();
    }

    function teacherDisplay(row) {
        if (row.teacher_name) {
            return row.teacher_name;
        }
        if (data && data.teacherNames && row.teacher) {
            return data.teacherNames[row.teacher] || row.teacher;
        }
        return row.teacher || "";
    }

    function uniqueSorted(arr) {
        var set = {};
        arr.forEach(function (v) {
            if (v !== null && v !== undefined && v !== "") {
                set[String(v)] = true;
            }
        });
        return Object.keys(set).sort();
    }

    function fillSelect(id, allLabel, values, allValue) {
        var sel = document.getElementById(id);
        if (!sel) {
            return;
        }
        var emptyVal = allValue !== undefined ? allValue : "";
        sel.innerHTML = "";
        var optAll = document.createElement("option");
        optAll.value = emptyVal;
        optAll.textContent = allLabel;
        sel.appendChild(optAll);
        values.forEach(function (v) {
            var opt = document.createElement("option");
            opt.value = v;
            opt.textContent = v;
            sel.appendChild(opt);
        });
    }

    function filteredRows(extra) {
        if (!data || !data.timetable) {
            return [];
        }
        var extraTeacher = extra && extra.teacher ? extra.teacher : "";
        var extraRoom = extra && extra.room ? extra.room : "";

        return data.timetable.filter(function (row) {
            if (filters.section && String(row.section) !== filters.section) {
                return false;
            }
            if (filters.teacher && String(row.teacher) !== filters.teacher) {
                return false;
            }
            if (extraTeacher && String(row.teacher) !== extraTeacher) {
                return false;
            }
            if (filters.room && String(row.room) !== filters.room) {
                return false;
            }
            if (extraRoom && String(row.room) !== extraRoom) {
                return false;
            }
            if (filters.day && String(row.day) !== filters.day) {
                return false;
            }
            return true;
        });
    }

    function defaultFillColor(courseName) {
        var key = String(courseName || "");
        if (prefs.fillMap[key]) {
            return prefs.fillMap[key];
        }
        if (data && data.colorMap && data.colorMap[key]) {
            return data.colorMap[key];
        }
        return "#E8EAF6";
    }

    function borderColorForLesson(row) {
        if (prefs.borderMode === "none") {
            return "transparent";
        }
        if (prefs.borderMode === "course") {
            return defaultFillColor(row.course_name);
        }
        var key;
        if (prefs.borderMode === "day") {
            key = String(row.day);
            if (prefs.borderMap[key]) {
                return prefs.borderMap[key];
            }
            if (data && data.defaultBorderMapDay && data.defaultBorderMapDay[key]) {
                return data.defaultBorderMapDay[key];
            }
        } else {
            key = String(row.teacher);
            if (prefs.borderMap[key]) {
                return prefs.borderMap[key];
            }
            if (data && data.defaultBorderMapTeacher && data.defaultBorderMapTeacher[key]) {
                return data.defaultBorderMapTeacher[key];
            }
        }
        return "#64748B";
    }

    function buildTimeRows() {
        var rows = [];
        var periods = data.periods || [];
        var periodTimes = data.periodTimes || {};
        var breaks = data.breakRows || [];

        periods.forEach(function (p) {
            var times = periodTimes[String(p)] || ["", ""];
            rows.push({
                type: "period",
                period: p,
                start: times[0],
                end: times[1],
                label: times[0] + "–" + times[1]
            });
            breaks.forEach(function (br) {
                if (Number(br.after_period) === Number(p)) {
                    rows.push({
                        type: "break",
                        start: br.start,
                        end: br.end,
                        label: br.label || "Break"
                    });
                }
            });
        });
        return rows;
    }

    function lessonBlockHtml(row) {
        var fill = defaultFillColor(row.course_name);
        var border = borderColorForLesson(row);
        var payload = encodeURIComponent(JSON.stringify({
            course_name: row.course_name,
            teacher: teacherDisplay(row),
            teacher_id: row.teacher,
            room: row.room,
            day: row.day,
            period: row.period,
            section: row.section
        }));
        return (
            '<div class="school-cell-lesson" style="background:' + fill + ";border-color:" + border + ';"' +
            ' data-lesson="' + payload + '">' +
            '<div class="school-subject">' + escapeHtml(String(row.course_name).toUpperCase()) + "</div>" +
            '<div class="school-teacher">' + escapeHtml(teacherDisplay(row)) + "</div>" +
            '<div class="school-room">' + escapeHtml(row.day) + " · " + escapeHtml(timeRangeForPeriod(row.period)) + "</div>" +
            "</div>"
        );
    }

    function cellInnerHtml(entries, useDayInFooter) {
        if (!entries.length) {
            return '<div class="grid-slot-inner grid-slot-empty">—</div>';
        }
        var html = '<div class="grid-slot-inner grid-slot-stack">';
        entries.forEach(function (row) {
            if (useDayInFooter) {
                html += lessonBlockHtml(row);
            } else {
                var fill = defaultFillColor(row.course_name);
                var border = borderColorForLesson(row);
                var payload = encodeURIComponent(JSON.stringify({
                    course_name: row.course_name,
                    teacher: teacherDisplay(row),
                    teacher_id: row.teacher,
                    room: row.room,
                    day: row.day,
                    period: row.period,
                    section: row.section
                }));
                html +=
                    '<div class="school-cell-lesson" style="background:' + fill + ";border-color:" + border + ';"' +
                    ' data-lesson="' + payload + '">' +
                    '<div class="school-subject">' + escapeHtml(String(row.course_name).toUpperCase()) + "</div>" +
                    '<div class="school-teacher">' + escapeHtml(teacherDisplay(row)) + "</div>" +
                    '<div class="school-room">Room ' + escapeHtml(row.room) + "</div>" +
                    "</div>";
            }
        });
        html += "</div>";
        return html;
    }

    function buildSlotColumns() {
        var days = data.days || [];
        var periods = data.periods || [];
        var periodTimes = data.periodTimes || {};
        var dayShort = data.dayShort || {};
        var slots = [];
        days.forEach(function (day) {
            periods.forEach(function (p) {
                var times = periodTimes[String(p)] || ["", ""];
                var short = dayShort[day] || day.substring(0, 3);
                slots.push({
                    day: day,
                    period: p,
                    label: short + " " + times[0]
                });
            });
        });
        return slots;
    }

    function renderRoomGanttGrid() {
        var container = document.getElementById("room-gantt-grid-container");
        if (!container || !data || !data.timetable) {
            return;
        }

        var slots = buildSlotColumns();
        var slotCount = slots.length;
        var allRooms = uniqueSorted(
            (data.timetable || []).map(function (r) { return r.room; })
        );
        var filterSel = document.getElementById("gantt-room-select");
        var roomFilter = filterSel && filterSel.value ? filterSel.value : "";
        var rooms = roomFilter
            ? allRooms.filter(function (r) { return String(r) === String(roomFilter); })
            : allRooms;

        var colCount = slotCount + 1;
        var gridStyle =
            "grid-template-columns: var(--room-col-width) repeat(" +
            slotCount + ", minmax(72px, 1fr));";

        var html = '<div class="school-table-scroll"><div class="timetable-grid timetable-grid--room-gantt" style="' +
            gridStyle + '">';

        html += '<div class="grid-head grid-room-head">Room</div>';
        slots.forEach(function (slot) {
            html += '<div class="grid-head grid-slot-head" title="' +
                escapeHtml(slot.day + " " + timeRangeForPeriod(slot.period)) + '">' +
                escapeHtml(slot.label) + "</div>";
        });

        rooms.forEach(function (roomId) {
            html += '<div class="grid-room-label">' + escapeHtml(roomId) + "</div>";
            slots.forEach(function (slot) {
                var entries = data.timetable.filter(function (r) {
                    return String(r.room) === String(roomId) &&
                        r.day === slot.day &&
                        Number(r.period) === Number(slot.period);
                });
                html += '<div class="grid-slot">' + cellInnerHtml(entries, true) + "</div>";
            });
        });

        html += "</div></div>";
        container.innerHTML = html;
        bindLessonInteractions(container);
    }

    function refreshAllGrids() {
        renderMainTimetable();
        renderTeacherPage();
        renderRoomPage();
        renderRoomGanttGrid();
    }

    function renderSchoolTimetable(containerId, rows, dayList) {
        var container = document.getElementById(containerId);
        if (!container || !data) {
            return;
        }

        var days = dayList || data.days || [];
        var dayShort = data.dayShort || {};
        var timeRows = buildTimeRows();
        var mobileDay = document.getElementById("filter-mobile-day");
        var isMobileSingleDay = false;
        if (mobileDay && window.matchMedia("(max-width: 768px)").matches) {
            if (mobileDay.value) {
                days = [mobileDay.value];
                isMobileSingleDay = true;
            }
        }

        var colCount = days.length + 1;
        var gridStyle = "grid-template-columns: var(--time-col-width) repeat(" + days.length + ", 1fr);";

        var html = '<div class="school-table-scroll"><div class="timetable-grid' +
            (isMobileSingleDay ? " single-day" : "") + '" style="' + gridStyle + '">';

        html += '<div class="grid-head grid-time-head">Time</div>';
        days.forEach(function (day) {
            var short = dayShort[day] || day.substring(0, 3).toUpperCase();
            html += '<div class="grid-head grid-day-head"><span class="day-full">' + escapeHtml(day) +
                '</span><span class="day-short">' + escapeHtml(short) + "</span></div>";
        });

        timeRows.forEach(function (trow) {
            if (trow.type === "break") {
                html += '<div class="grid-time grid-break-label">' +
                    escapeHtml(trow.start + "–" + trow.end) + "</div>";
                html += '<div class="grid-break-row" style="grid-column: 2 / ' + (colCount + 1) + ';">' +
                    escapeHtml(trow.label) + "</div>";
                return;
            }

            html += '<div class="grid-time time-slot">' + escapeHtml(trow.label) + "</div>";
            days.forEach(function (day) {
                var entries = rows.filter(function (r) {
                    return r.day === day && Number(r.period) === Number(trow.period);
                });
                html += '<div class="grid-slot">' + cellInnerHtml(entries) + "</div>";
            });
        });

        html += "</div></div>";
        container.innerHTML = html;
        bindLessonInteractions(container);
    }

    function bindLessonInteractions(root) {
        var lessons = root.querySelectorAll(".school-cell-lesson");
        lessons.forEach(function (el) {
            el.addEventListener("mouseenter", function (ev) {
                showTooltip(el, ev);
            });
            el.addEventListener("mousemove", function (ev) {
                moveTooltip(ev);
            });
            el.addEventListener("mouseleave", hideTooltip);
            el.addEventListener("click", function () {
                openModal(el);
            });
        });
    }

    function lessonFromEl(el) {
        try {
            return JSON.parse(decodeURIComponent(el.getAttribute("data-lesson")));
        } catch (e) {
            return null;
        }
    }

    function timeRangeForPeriod(period) {
        var times = (data.periodTimes && data.periodTimes[String(period)]) || ["", ""];
        return times[0] + "–" + times[1];
    }

    function showTooltip(el, ev) {
        var lesson = lessonFromEl(el);
        if (!lesson || !tooltipEl) {
            return;
        }
        tooltipEl.innerHTML =
            "<div><strong>Subject</strong><br>" + escapeHtml(lesson.course_name) + "</div>" +
            "<div><strong>Teacher</strong><br>" + escapeHtml(lesson.teacher) + "</div>" +
            "<div><strong>Room</strong><br>" + escapeHtml(lesson.room) + "</div>" +
            "<div><strong>Time</strong><br>" + escapeHtml(timeRangeForPeriod(lesson.period)) + "</div>";
        tooltipEl.hidden = false;
        moveTooltip(ev);
    }

    function moveTooltip(ev) {
        if (!tooltipEl || tooltipEl.hidden) {
            return;
        }
        tooltipEl.style.left = (ev.clientX + 14) + "px";
        tooltipEl.style.top = (ev.clientY + 14) + "px";
    }

    function hideTooltip() {
        if (tooltipEl) {
            tooltipEl.hidden = true;
        }
    }

    function openModal(el) {
        var lesson = lessonFromEl(el);
        if (!lesson || !modalEl) {
            return;
        }
        var content = document.getElementById("modal-content");
        if (!content) {
            return;
        }
        content.innerHTML =
            '<h3 class="modal-subject">' + escapeHtml(lesson.course_name) + "</h3>" +
            "<p><strong>Teacher:</strong> " + escapeHtml(lesson.teacher) + "</p>" +
            "<p><strong>Room:</strong> " + escapeHtml(lesson.room) + "</p>" +
            "<p><strong>Day:</strong> " + escapeHtml(lesson.day) + "</p>" +
            "<p><strong>Time:</strong> " + escapeHtml(timeRangeForPeriod(lesson.period)) + "</p>" +
            (lesson.section ? "<p><strong>Section:</strong> " + escapeHtml(lesson.section) + "</p>" : "");
        modalEl.hidden = false;
    }

    function closeModal() {
        if (modalEl) {
            modalEl.hidden = true;
        }
    }

    function navigateToSection(section) {
        document.querySelectorAll(".top-nav-link").forEach(function (b) {
            b.classList.toggle("active", b.getAttribute("data-section") === section);
        });
        document.querySelectorAll(".page-section").forEach(function (sec) {
            sec.classList.remove("active");
        });
        var target = document.getElementById("section-" + section);
        if (target) {
            target.classList.add("active");
        }
        hideTooltip();
        closeAppearancePanel();
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

    function renderHomeKpis() {
        var row = document.getElementById("home-kpi-row");
        if (!row || !data || !data.kpis) {
            return;
        }
        var k = data.kpis;
        var status = k.optimization_status || "N/A";
        var cards = [
            ["Courses", k.total_courses],
            ["Teachers", k.total_teachers],
            ["Rooms", k.total_rooms],
            ["Scheduled", k.scheduled_classes],
            ["Status", status]
        ];
        row.innerHTML = cards.map(function (pair) {
            return '<div class="kpi-card"><span class="kpi-label">' + escapeHtml(pair[0]) +
                '</span><strong class="kpi-value">' + escapeHtml(pair[1]) + "</strong></div>";
        }).join("");
    }

    function populateFilters() {
        if (!data) {
            return;
        }
        var sections = data.sections || uniqueSorted(
            (data.timetable || []).map(function (r) { return r.section; })
        );
        var teachers = uniqueSorted((data.timetable || []).map(function (r) { return r.teacher; }));
        var rooms = uniqueSorted((data.timetable || []).map(function (r) { return r.room; }));
        var days = data.days || [];

        fillSelect("filter-class", "All Classes", data.classOptions || []);
        fillSelect("filter-section", "All Sections", sections);
        fillSelect("filter-teacher", "All Teachers", teachers);
        fillSelect("filter-room", "All Rooms", rooms);
        fillSelect("filter-day", "All Days", days);

        var weekSel = document.getElementById("filter-week");
        if (weekSel && data.weekOptions) {
            weekSel.innerHTML = "";
            data.weekOptions.forEach(function (w) {
                var opt = document.createElement("option");
                opt.value = w;
                opt.textContent = w;
                weekSel.appendChild(opt);
            });
        }

        var mobileDay = document.getElementById("filter-mobile-day");
        if (mobileDay) {
            mobileDay.innerHTML = "";
            days.forEach(function (d) {
                var opt = document.createElement("option");
                opt.value = d;
                opt.textContent = d;
                mobileDay.appendChild(opt);
            });
        }

        var teacherPage = document.getElementById("teacher-page-select");
        if (teacherPage) {
            teacherPage.innerHTML = "";
            teachers.forEach(function (t) {
                var opt = document.createElement("option");
                opt.value = t;
                var name = (data.teacherNames && data.teacherNames[t]) || t;
                opt.textContent = name + " (" + t + ")";
                teacherPage.appendChild(opt);
            });
        }

        var roomPage = document.getElementById("room-page-select");
        if (roomPage) {
            roomPage.innerHTML = "";
            rooms.forEach(function (r) {
                var opt = document.createElement("option");
                opt.value = r;
                opt.textContent = r;
                roomPage.appendChild(opt);
            });
        }

        var ganttRoom = document.getElementById("gantt-room-select");
        if (ganttRoom) {
            ganttRoom.innerHTML = "";
            var optAll = document.createElement("option");
            optAll.value = "";
            optAll.textContent = "All rooms";
            ganttRoom.appendChild(optAll);
            rooms.forEach(function (r) {
                var opt = document.createElement("option");
                opt.value = r;
                opt.textContent = r;
                ganttRoom.appendChild(opt);
            });
        }
    }

    function bindFilters() {
        function onFilterChange() {
            refreshAllGrids();
        }

        var map = {
            "filter-section": "section",
            "filter-teacher": "teacher",
            "filter-room": "room",
            "filter-day": "day",
            "filter-class": "classGroup"
        };

        Object.keys(map).forEach(function (id) {
            var el = document.getElementById(id);
            if (!el) {
                return;
            }
            el.addEventListener("change", function () {
                filters[map[id]] = el.value;
                onFilterChange();
            });
        });

        var mobileDay = document.getElementById("filter-mobile-day");
        if (mobileDay) {
            mobileDay.addEventListener("change", renderMainTimetable);
        }

        var teacherPage = document.getElementById("teacher-page-select");
        if (teacherPage) {
            teacherPage.addEventListener("change", renderTeacherPage);
        }

        var roomPage = document.getElementById("room-page-select");
        if (roomPage) {
            roomPage.addEventListener("change", renderRoomPage);
        }

        var ganttRoom = document.getElementById("gantt-room-select");
        if (ganttRoom) {
            ganttRoom.addEventListener("change", renderRoomGanttGrid);
        }
    }

    function renderMainTimetable() {
        renderSchoolTimetable("school-timetable-container", filteredRows());
    }

    function renderTeacherPage() {
        var sel = document.getElementById("teacher-page-select");
        if (!sel || !sel.value) {
            return;
        }
        renderSchoolTimetable(
            "teacher-timetable-container",
            filteredRows({ teacher: sel.value }),
            data.days
        );
    }

    function renderRoomPage() {
        var sel = document.getElementById("room-page-select");
        if (!sel || !sel.value) {
            return;
        }
        var roomId = sel.value;
        var stats = document.getElementById("room-stats-panel");
        if (stats && data.roomUtilization) {
            var info = null;
            data.roomUtilization.forEach(function (r) {
                if (String(r.room_id) === String(roomId)) {
                    info = r;
                }
            });
            if (info) {
                stats.innerHTML =
                    "<p><strong>Room:</strong> " + escapeHtml(roomId) + "</p>" +
                    "<p><strong>Capacity:</strong> " + escapeHtml(info.capacity) + "</p>" +
                    "<p><strong>Classes scheduled:</strong> " + escapeHtml(info.classes_scheduled) + "</p>" +
                    "<p><strong>Utilization:</strong> " + escapeHtml(info.utilization_pct) + "%</p>";
            }
        }
        renderSchoolTimetable(
            "room-timetable-container",
            filteredRows({ room: roomId }),
            data.days
        );
    }

    function updateBorderLegend() {
        var el = document.getElementById("border-legend");
        var title = document.getElementById("border-color-title");
        var section = document.getElementById("border-color-section");
        if (!el) {
            return;
        }
        var mode = prefs.borderMode;
        if (mode === "none" || mode === "course") {
            if (section) {
                section.hidden = true;
            }
            el.textContent = mode === "none"
                ? "Lesson blocks have no accent border."
                : "Border matches the course fill color.";
            return;
        }
        if (section) {
            section.hidden = false;
        }
        if (mode === "day") {
            el.textContent = "Colored border describes the day of the week for each lesson block.";
            if (title) {
                title.textContent = "Border colors (days)";
            }
        } else {
            el.textContent = "Colored border describes the assigned teacher for each lesson block.";
            if (title) {
                title.textContent = "Border colors (teachers)";
            }
        }
    }

    function courseKeysForFill() {
        if (!data || !data.colorMap) {
            return [];
        }
        return Object.keys(data.colorMap).sort();
    }

    function borderKeysForMode() {
        if (!data) {
            return [];
        }
        if (prefs.borderMode === "day") {
            return (data.days || []).slice();
        }
        return (data.teacherIds || uniqueSorted(
            (data.timetable || []).map(function (r) { return r.teacher; })
        ));
    }

    function defaultBorderForKey(key) {
        if (prefs.borderMode === "day" && data.defaultBorderMapDay) {
            return data.defaultBorderMapDay[key] || "#64748B";
        }
        if (data.defaultBorderMapTeacher) {
            return data.defaultBorderMapTeacher[key] || "#64748B";
        }
        return "#64748B";
    }

    function renderColorPickers() {
        var fillList = document.getElementById("fill-color-list");
        var borderList = document.getElementById("border-color-list");
        if (!fillList || !data) {
            return;
        }

        fillList.innerHTML = courseKeysForFill().map(function (key) {
            var val = prefs.fillMap[key] || data.colorMap[key] || "#E8EAF6";
            return '<label class="color-picker-row"><span>' + escapeHtml(key) +
                '</span><input type="color" data-fill-key="' + escapeHtml(key) + '" value="' +
                escapeHtml(val) + '"></label>';
        }).join("");

        fillList.querySelectorAll("input[type=color]").forEach(function (input) {
            input.addEventListener("input", function () {
                prefs.fillMap[input.getAttribute("data-fill-key")] = input.value;
                writeJsonStorage(STORAGE.fillColors, prefs.fillMap);
                refreshAllGrids();
            });
        });

        if (!borderList) {
            return;
        }
        if (prefs.borderMode === "none" || prefs.borderMode === "course") {
            borderList.innerHTML = "";
            return;
        }

        borderList.innerHTML = borderKeysForMode().map(function (key) {
            var label = key;
            if (prefs.borderMode === "teacher" && data.teacherNames && data.teacherNames[key]) {
                label = data.teacherNames[key] + " (" + key + ")";
            }
            var val = prefs.borderMap[key] || defaultBorderForKey(key);
            return '<label class="color-picker-row"><span>' + escapeHtml(label) +
                '</span><input type="color" data-border-key="' + escapeHtml(key) + '" value="' +
                escapeHtml(val) + '"></label>';
        }).join("");

        borderList.querySelectorAll("input[type=color]").forEach(function (input) {
            input.addEventListener("input", function () {
                prefs.borderMap[input.getAttribute("data-border-key")] = input.value;
                writeJsonStorage(STORAGE.borderColors, prefs.borderMap);
                refreshAllGrids();
            });
        });
    }

    function openAppearancePanel() {
        var panel = document.getElementById("appearance-panel");
        var btn = document.getElementById("btn-appearance");
        if (panel) {
            panel.hidden = false;
        }
        if (btn) {
            btn.setAttribute("aria-expanded", "true");
        }
        renderColorPickers();
    }

    function closeAppearancePanel() {
        var panel = document.getElementById("appearance-panel");
        var btn = document.getElementById("btn-appearance");
        if (panel) {
            panel.hidden = true;
        }
        if (btn) {
            btn.setAttribute("aria-expanded", "false");
        }
    }

    function initAppearance() {
        applyThemeFont();
        renderColorPickers();

        var themeSel = document.getElementById("theme-select");
        if (themeSel) {
            themeSel.addEventListener("change", function () {
                prefs.theme = themeSel.value;
                localStorage.setItem(STORAGE.theme, prefs.theme);
                applyThemeFont();
            });
        }

        var fontSel = document.getElementById("font-pair");
        if (fontSel) {
            fontSel.addEventListener("change", function () {
                prefs.font = fontSel.value;
                localStorage.setItem(STORAGE.font, prefs.font);
                applyThemeFont();
            });
        }

        var borderSel = document.getElementById("border-mode");
        if (borderSel) {
            borderSel.addEventListener("change", function () {
                prefs.borderMode = borderSel.value;
                localStorage.setItem(STORAGE.borderMode, prefs.borderMode);
                updateBorderLegend();
                renderColorPickers();
                refreshAllGrids();
            });
        }

        var resetFill = document.getElementById("reset-fill-colors");
        if (resetFill) {
            resetFill.addEventListener("click", function () {
                prefs.fillMap = Object.assign({}, data.colorMap || {});
                writeJsonStorage(STORAGE.fillColors, prefs.fillMap);
                renderColorPickers();
                refreshAllGrids();
            });
        }

        var resetBorder = document.getElementById("reset-border-colors");
        if (resetBorder) {
            resetBorder.addEventListener("click", function () {
                prefs.borderMap = Object.assign(
                    {},
                    data.defaultBorderMapTeacher || {},
                    data.defaultBorderMapDay || {}
                );
                writeJsonStorage(STORAGE.borderColors, prefs.borderMap);
                renderColorPickers();
                refreshAllGrids();
            });
        }

        var openBtn = document.getElementById("btn-appearance");
        if (openBtn) {
            openBtn.addEventListener("click", function () {
                var panel = document.getElementById("appearance-panel");
                if (panel && panel.hidden) {
                    openAppearancePanel();
                } else {
                    closeAppearancePanel();
                }
            });
        }

        var homeOpen = document.getElementById("home-open-appearance");
        if (homeOpen) {
            homeOpen.addEventListener("click", openAppearancePanel);
        }

        var closeBtn = document.getElementById("appearance-close");
        if (closeBtn) {
            closeBtn.addEventListener("click", closeAppearancePanel);
        }
    }

    function initSplash() {
        var splash = document.getElementById("splash-overlay");
        if (!splash) {
            return;
        }
        var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        if (reduceMotion) {
            splash.classList.add("splash-hidden");
            return;
        }
        splash.classList.remove("splash-hidden");
        window.setTimeout(function () {
            splash.classList.add("splash-fade-out");
            window.setTimeout(function () {
                splash.classList.add("splash-hidden");
            }, 500);
        }, 1500);
    }

    function initPrint() {
        var btn = document.getElementById("btn-print");
        if (btn) {
            btn.addEventListener("click", function () {
                document.body.classList.add("print-timetable");
                window.print();
                window.addEventListener("afterprint", function () {
                    document.body.classList.remove("print-timetable");
                }, { once: true });
            });
        }
    }

    function initModal() {
        modalEl = document.getElementById("cell-modal");
        tooltipEl = document.getElementById("cell-tooltip");
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
        initPrefsFromStorage();
        initSplash();
        if (!data) {
            return;
        }
        initAppearance();
        initNavigation();
        initModal();
        initPrint();
        populateFilters();
        bindFilters();
        renderHomeKpis();
        refreshAllGrids();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
