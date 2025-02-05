window.onload = function() {
    // بارگذاری داده‌ها از localStorage به جدول برنامه
    var times = ["8_10", "10_12", "14_16"];
    var days = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday"];

    // بارگذاری دروس از localStorage و نمایش در جدول
    for (var i = 0; i < days.length; i++) {
        for (var j = 0; j < times.length; j++) {
            var cellId = days[i] + "_" + times[j];
            var subject = localStorage.getItem(cellId);  // دریافت درس از localStorage
            if (subject) {
                document.getElementById(cellId).innerText = subject;  // نمایش درس در سلول مناسب
            }
        }
    }
}
