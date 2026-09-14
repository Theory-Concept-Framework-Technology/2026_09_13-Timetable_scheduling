(function () {
    "use strict";

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

    var data = loadDashboardData();

    var filters = {
        classGroup: "",
        section: "",
        teacher: "",
        room: "",
        day: ""
    };

    var tooltipEl = null;
    var modalEl = null;

    function teacherDisplay(row) {
        if (row.teacher_name) {
            return row.teacher_name;
        }
        if (data.teacherNames && row.teacher) {
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

    function subjectColor(courseName) {
        var key = String(courseName || "");
        return (data.colorMap && data.colorMap[key]) || "#e8eaf6";
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

    function cellInnerHtml(entries) {
        if (!entries.length) {
            return '<div class="school-cell-empty">—</div>';
        }
        var html = "";
        entries.forEach(function (row) {
            var bg = subjectColor(row.course_name);
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
                '<div class="school-cell-lesson" style="background:' + bg + '22;border-left:3px solid ' + bg + ';"' +
                ' data-lesson="' + payload + '">' +
                '<div class="school-subject">' + escapeHtml(String(row.course_name).toUpperCase()) + "</div>" +
                '<div class="school-teacher">' + escapeHtml(teacherDisplay(row)) + "</div>" +
                '<div class="school-room">Room ' + escapeHtml(row.room) + "</div>" +
                "</div>";
        });
        return html;
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

        var head = '<th class="col-time">Time</th>';
        days.forEach(function (day) {
            var short = dayShort[day] || day.substring(0, 3).toUpperCase();
            head += '<th class="col-day"><span class="day-full">' + escapeHtml(day) +
                '</span><span class="day-short">' + escapeHtml(short) + "</span></th>";
        });

        var body = "";
        timeRows.forEach(function (trow) {
            if (trow.type === "break") {
                body += "<tr class=\"row-break\"><td class=\"col-time\">" +
                    escapeHtml(trow.start + "–" + trow.end) + "</td>";
                days.forEach(function () {
                    body += '<td class="school-cell break-cell">' +
                        escapeHtml(trow.label) + "</td>";
                });
                body += "</tr>";
                return;
            }

            body += "<tr><td class=\"col-time time-slot\">" +
                escapeHtml(trow.label) + "</td>";

            days.forEach(function (day) {
                var entries = rows.filter(function (r) {
                    return r.day === day && Number(r.period) === Number(trow.period);
                });
                body += '<td class="school-cell">' + cellInnerHtml(entries) + "</td>";
            });
            body += "</tr>";
        });

        container.innerHTML =
            '<div class="school-table-scroll">' +
            '<table class="school-timetable' + (isMobileSingleDay ? " single-day" : "") + '">' +
            "<thead><tr>" + head + "</tr></thead><tbody>" + body + "</tbody></table></div>";

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

    function initNavigation() {
        document.querySelectorAll(".top-nav-link").forEach(function (btn) {
            btn.addEventListener("click", function () {
                var section = btn.getAttribute("data-section");
                document.querySelectorAll(".top-nav-link").forEach(function (b) {
                    b.classList.remove("active");
                });
                btn.classList.add("active");
                document.querySelectorAll(".page-section").forEach(function (sec) {
                    sec.classList.remove("active");
                });
                var target = document.getElementById("section-" + section);
                if (target) {
                    target.classList.add("active");
                }
                hideTooltip();
            });
        });
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

        fillSelect(
            "filter-class",
            "All Classes",
            data.classOptions || []
        );
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
    }

    function bindFilters() {
        function onFilterChange() {
            renderMainTimetable();
            renderTeacherPage();
            renderRoomPage();
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
        if (!data) {
            return;
        }
        initNavigation();
        initModal();
        initPrint();
        populateFilters();
        bindFilters();
        renderMainTimetable();
        renderTeacherPage();
        renderRoomPage();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
