// =========================
// CARTE DU BENIN
// =========================

document.addEventListener("DOMContentLoaded", function () {

    const map = L.map("benin-map").setView([9.6, 2.4], 7);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap"
    }).addTo(map);

});