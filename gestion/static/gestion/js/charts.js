function readJsonScript(id) {
    const node = document.getElementById(id);
    if (!node) return [];
    try {
        return JSON.parse(node.textContent);
    } catch (_error) {
        return [];
    }
}

function drawBars(canvas, labels, values, color) {
    const ctx = canvas.getContext("2d");
    const width = canvas.clientWidth;
    const height = Number(canvas.getAttribute("height")) || 260;
    canvas.width = width * window.devicePixelRatio;
    canvas.height = height * window.devicePixelRatio;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    ctx.clearRect(0, 0, width, height);

    const max = Math.max(...values, 1);
    const left = 120;
    const rowHeight = Math.max(34, (height - 30) / Math.max(labels.length, 1));
    ctx.font = "13px system-ui";
    labels.forEach((label, index) => {
        const y = 20 + index * rowHeight;
        const barWidth = ((width - left - 38) * values[index]) / max;
        ctx.fillStyle = "#68746e";
        ctx.fillText(String(label).slice(0, 20), 0, y + 14);
        ctx.fillStyle = color;
        ctx.fillRect(left, y, barWidth, 18);
        ctx.fillStyle = "#18211d";
        ctx.fillText(values[index], left + barWidth + 8, y + 14);
    });
}

function drawLine(canvas, labels, values) {
    const ctx = canvas.getContext("2d");
    const width = canvas.clientWidth;
    const height = Number(canvas.getAttribute("height")) || 240;
    canvas.width = width * window.devicePixelRatio;
    canvas.height = height * window.devicePixelRatio;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    ctx.clearRect(0, 0, width, height);

    const padding = 36;
    const max = Math.max(...values, 1);
    ctx.strokeStyle = "#dbe4de";
    ctx.beginPath();
    ctx.moveTo(padding, 16);
    ctx.lineTo(padding, height - padding);
    ctx.lineTo(width - 12, height - padding);
    ctx.stroke();

    if (!values.length) return;
    ctx.strokeStyle = "#116a57";
    ctx.lineWidth = 3;
    ctx.beginPath();
    values.forEach((value, index) => {
        const x = padding + ((width - padding - 24) * index) / Math.max(values.length - 1, 1);
        const y = height - padding - ((height - padding - 30) * value) / max;
        if (index === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    });
    ctx.stroke();
    ctx.fillStyle = "#18211d";
    ctx.font = "12px system-ui";
    labels.forEach((label, index) => {
        const x = padding + ((width - padding - 24) * index) / Math.max(labels.length - 1, 1);
        ctx.fillText(label, x - 16, height - 10);
    });
}

function renderCharts() {
    const estado = readJsonScript("estado-data");
    const tipo = readJsonScript("tipo-data");
    const mes = readJsonScript("mes-data");

    document.querySelectorAll("canvas[data-chart]").forEach((canvas) => {
        const chart = canvas.dataset.chart;
        if (chart === "estado") {
            drawBars(canvas, estado.map((item) => item.estado), estado.map((item) => item.total), "#2563a6");
        }
        if (chart === "tipo") {
            drawBars(canvas, tipo.map((item) => item.tipo__nombre), tipo.map((item) => item.total), "#c7782d");
        }
        if (chart === "mes") {
            drawLine(canvas, mes.map((item) => item.mes), mes.map((item) => item.total));
        }
    });
}

window.addEventListener("load", renderCharts);
window.addEventListener("resize", renderCharts);
