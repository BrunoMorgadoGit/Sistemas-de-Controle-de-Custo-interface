// ── Toast ────────────────────────────────────────────────────
function showToast(msg, type) {
    const t = document.getElementById('toast');
    if (!t) return;
    t.textContent = msg;
    t.className = `toast ${type || 'success'} show`;
    setTimeout(() => { t.className = 'toast'; }, 3000);
}

function setupGlobalToast() {
    const toastEl = document.getElementById('server-toast');
    const serverToast = toastEl ? JSON.parse(toastEl.textContent) : null;
    if (serverToast) showToast(serverToast);
}

// ── Cat-dot colors (global) ─────────────────────────────────
function applyCatDotColors() {
    document.querySelectorAll('.cat-dot[data-cor]').forEach(el => {
        el.style.background = el.dataset.cor;
    });
}

// ── Chart (dashboard only) ──────────────────────────────────
function initChart() {
    const chartDataEl = document.getElementById('chart-data');
    if (!chartDataEl) return;

    const chartData = JSON.parse(chartDataEl.textContent);
    if (!Array.isArray(chartData) || chartData.length === 0) return;

    const canvas = document.getElementById('grafico-categorias');
    const emptyMsg = document.getElementById('chart-empty');
    if (!canvas) return;

    canvas.style.display = 'block';
    if (emptyMsg) emptyMsg.style.display = 'none';

    const labels = chartData.map(d => d.nome);
    const values = chartData.map(d => d.total);
    const colors = chartData.map(d => d.cor);

    new Chart(canvas, {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{
                data: values,
                backgroundColor: colors,
                borderColor: 'rgba(10, 14, 26, 0.8)',
                borderWidth: 3,
                hoverOffset: 8,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#8899b8',
                        font: { family: 'Inter', size: 12, weight: '500' },
                        padding: 16,
                        usePointStyle: true,
                        pointStyleWidth: 10
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(16, 24, 48, 0.95)',
                    titleColor: '#e8edf5',
                    bodyColor: '#8899b8',
                    borderColor: 'rgba(56, 189, 248, 0.2)',
                    borderWidth: 1,
                    cornerRadius: 8,
                    padding: 12,
                    titleFont: { family: 'Inter', weight: '600' },
                    bodyFont: { family: 'Inter' },
                    callbacks: {
                        label: function (ctx) {
                            const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                            const pct = ((ctx.parsed / total) * 100).toFixed(1);
                            const fmt = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });
                            return ` ${fmt.format(ctx.parsed)} (${pct}%)`;
                        }
                    }
                }
            },
            animation: { animateRotate: true, animateScale: true, duration: 800, easing: 'easeOutCubic' }
        }
    });
}

// ── Caixa config toggle (dashboard only) ────────────────────
function initCaixaToggle() {
    const card = document.getElementById('card-caixa');
    const cfg = document.getElementById('caixa-config');
    const cancelBtn = document.getElementById('btn-cancelar-caixa');

    if (!card || !cfg) return;

    card.addEventListener('click', () => {
        cfg.classList.toggle('hidden');
        if (!cfg.classList.contains('hidden')) {
            const input = document.getElementById('caixa-saldo-inicial');
            if (input) input.focus();
        }
    });

    if (cancelBtn) {
        cancelBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            cfg.classList.add('hidden');
        });
    }
}

// ── Conversor de Moedas (ferramentas only) ───────────────────
function initConversor() {
    const btn = document.getElementById('btn-converter');
    if (!btn) return;

    btn.addEventListener('click', async () => {
        const valor = parseFloat(document.getElementById('conv-valor').value);
        const de = document.getElementById('conv-de').value;
        const para = document.getElementById('conv-para').value;

        if (isNaN(valor) || valor <= 0) {
            showToast('Insira um valor válido para converter', 'error');
            return;
        }

        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Convertendo...';
        btn.disabled = true;

        try {
            const resp = await fetch(`/api/conversao?valor=${encodeURIComponent(valor)}&de=${encodeURIComponent(de)}&para=${encodeURIComponent(para)}`);
            const data = await resp.json();
            if (!resp.ok) throw new Error(data.erro || 'Erro desconhecido');

            const div = document.getElementById('resultado-conversao');
            div.style.display = 'block';
            div.innerHTML = `
                <div>${valor.toFixed(2)} ${de} = <strong>${data.valor_convertido.toFixed(2)} ${para}</strong></div>
                <div class="rate">Taxa: 1 ${de} = ${data.taxa.toFixed(4)} ${para}</div>
            `;
        } catch (err) {
            showToast(err.message, 'error');
        } finally {
            btn.innerHTML = '<i class="fas fa-sync-alt"></i> Converter';
            btn.disabled = false;
        }
    });
}

// ── Sidebar toggle ──────────────────────────────────────────
function initSidebar() {
    const toggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');

    if (!toggle || !sidebar) return;

    toggle.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
    });
}

// ── Init ─────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    setupGlobalToast();
    applyCatDotColors();
    initSidebar();
    initChart();
    initCaixaToggle();
    initConversor();
});
