/**
 * Organizador de Custos - Frontend Application
 * Handles all DOM interactions, API calls, and Chart.js rendering.
 * Includes income (receitas) management and balance calculation.
 */

// ── State ──
let currentMonth = new Date().getMonth() + 1;
let currentYear = new Date().getFullYear();
let categorias = [];
let gastosChart = null;
let editingId = null;
let editingReceitaId = null;
let editingInvestId = null;

// ── Month Names ──
const MESES = [
    '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
];

// ── Helpers ──
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
}

function formatDate(dateStr) {
    const [y, m, d] = dateStr.split('-');
    return `${d}/${m}/${y}`;
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    setTimeout(() => { toast.className = 'toast'; }, 3000);
}

const TOKEN_KEY = 'org_custos_token';
const USERNAME_KEY = 'org_custos_username';

function getToken() { return localStorage.getItem(TOKEN_KEY); }

async function api(url, options = {}) {
    try {
        const headers = { 'Content-Type': 'application/json' };
        const token = getToken();
        if (token) { headers['Authorization'] = `Bearer ${token}`; }

        const resp = await fetch(url, {
            ...options,
            headers: { ...headers, ...(options.headers || {}) }
        });

        const data = await resp.json();
        if (!resp.ok) {
            if (resp.status === 401 && !url.includes('/api/login') && !url.includes('/api/register')) {
                logout(); // invalid token
            }
            throw new Error(data.erro || 'Erro desconhecido');
        }
        return data;
    } catch (err) {
        showToast(err.message, 'error');
        throw err;
    }
}

// ── Month Navigation ──
function updateMonthLabel() {
    document.getElementById('current-month-label').textContent =
        `${MESES[currentMonth]} ${currentYear}`;
}


function updateFormDates() {
    const m = String(currentMonth).padStart(2, '0');
    const today = new Date();
    let day;
    if (currentMonth === today.getMonth() + 1 && currentYear === today.getFullYear()) {
        day = String(today.getDate()).padStart(2, '0');
    } else {
        day = '01';
    }
    const dateVal = `${currentYear}-${m}-${day}`;
    document.getElementById('data').value = dateVal;
    document.getElementById('receita-data').value = dateVal;
    document.getElementById('invest-data').value = dateVal;
}

document.getElementById('btn-prev-month').addEventListener('click', () => {
    currentMonth--;
    if (currentMonth < 1) { currentMonth = 12; currentYear--; }
    updateMonthLabel();
    updateFormDates();
    loadData();
});

document.getElementById('btn-next-month').addEventListener('click', () => {
    currentMonth++;
    if (currentMonth > 12) { currentMonth = 1; currentYear++; }
    updateMonthLabel();
    updateFormDates();
    loadData();
});

// ── Load All Data ──
async function loadData() {
    await Promise.all([
        loadCategorias(),
        loadGastos(),
        loadReceitas(),
        loadInvestimentos(),
        loadResumo()
    ]);
}

// ═══════════════════════════════════════════
// CATEGORIAS
// ═══════════════════════════════════════════

async function loadCategorias() {
    categorias = await api('/api/categorias');
    renderCategoriaSelect();
    renderCategoriaList();
}

function renderCategoriaSelect() {
    const select = document.getElementById('categoria');
    select.innerHTML = '<option value="">Selecione...</option>';
    categorias.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c.id;
        opt.textContent = c.nome;
        select.appendChild(opt);
    });
}

function renderCategoriaList() {
    const ul = document.getElementById('lista-categorias');
    ul.innerHTML = '';
    categorias.forEach(c => {
        const li = document.createElement('li');
        li.innerHTML = `
            <div class="cat-info">
                <span class="cat-dot" style="background:${c.cor}"></span>
                <span class="cat-name">${c.nome}</span>
            </div>
            <button onclick="deleteCategoria(${c.id})" title="Remover">
                <i class="fas fa-trash-alt"></i>
            </button>
        `;
        ul.appendChild(li);
    });
}

document.getElementById('btn-add-cat').addEventListener('click', async () => {
    const nome = document.getElementById('nova-categoria').value.trim();
    const cor = document.getElementById('cor-categoria').value;
    if (!nome) { showToast('Nome da categoria é obrigatório', 'error'); return; }
    await api('/api/categorias', {
        method: 'POST',
        body: JSON.stringify({ nome, cor })
    });
    document.getElementById('nova-categoria').value = '';
    showToast('Categoria criada!');
    await loadCategorias();
});

async function deleteCategoria(id) {
    if (!confirm('Remover esta categoria?')) return;
    await api(`/api/categorias/${id}`, { method: 'DELETE' });
    showToast('Categoria removida');
    await loadCategorias();
}

// ═══════════════════════════════════════════
// GASTOS
// ═══════════════════════════════════════════

async function loadGastos() {
    const mes = String(currentMonth).padStart(2, '0');
    const gastos = await api(`/api/gastos?mes=${mes}&ano=${currentYear}`);
    renderGastosTable(gastos);
}

function renderGastosTable(gastos) {
    const tbody = document.getElementById('tbody-gastos');
    const emptyMsg = document.getElementById('table-empty');

    if (gastos.length === 0) {
        tbody.innerHTML = '';
        emptyMsg.style.display = 'block';
        return;
    }

    emptyMsg.style.display = 'none';
    tbody.innerHTML = gastos.map(g => `
        <tr>
            <td>${formatDate(g.data)}</td>
            <td><strong>${g.descricao}</strong></td>
            <td>
                <span class="cat-badge">
                    <span class="cat-dot" style="background:${g.categoria_cor || '#94a3b8'}"></span>
                    ${g.categoria_nome || 'Sem categoria'}
                </span>
            </td>
            <td class="valor-col">${formatCurrency(g.valor)}</td>
            <td class="anotacao-col" title="${(g.anotacao || '').replace(/"/g, '&quot;')}">${g.anotacao || '—'}</td>
            <td>
                <div class="actions-col">
                    <button class="btn btn-sm btn-secondary" onclick="editGasto(${g.id})" title="Editar">
                        <i class="fas fa-pen"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteGasto(${g.id})" title="Excluir">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

// Form: Create / Edit Gasto
document.getElementById('form-gasto').addEventListener('submit', async (e) => {
    e.preventDefault();

    const dados = {
        descricao: document.getElementById('descricao').value.trim(),
        valor: parseFloat(document.getElementById('valor').value),
        categoria_id: document.getElementById('categoria').value || null,
        data: document.getElementById('data').value,
        anotacao: document.getElementById('anotacao').value.trim()
    };

    if (editingId) {
        await api(`/api/gastos/${editingId}`, {
            method: 'PUT',
            body: JSON.stringify(dados)
        });
        showToast('Gasto atualizado!');
        cancelEdit();
    } else {
        await api('/api/gastos', {
            method: 'POST',
            body: JSON.stringify(dados)
        });
        showToast('Gasto adicionado!');
    }

    document.getElementById('form-gasto').reset();
    document.getElementById('data').value = new Date().toISOString().split('T')[0];
    await Promise.all([loadGastos(), loadResumo()]);
});

async function editGasto(id) {
    const mes = String(currentMonth).padStart(2, '0');
    const gastos = await api(`/api/gastos?mes=${mes}&ano=${currentYear}`);
    const g = gastos.find(x => x.id === id);
    if (!g) return;

    editingId = id;
    document.getElementById('gasto-id').value = id;
    document.getElementById('descricao').value = g.descricao;
    document.getElementById('valor').value = g.valor;
    document.getElementById('categoria').value = g.categoria_id || '';
    document.getElementById('data').value = g.data;
    document.getElementById('anotacao').value = g.anotacao || '';

    document.getElementById('form-title').textContent = 'Editar Gasto';
    document.getElementById('btn-cancelar').style.display = 'inline-flex';
    document.getElementById('btn-salvar').innerHTML = '<i class="fas fa-check"></i> Atualizar';

    document.getElementById('form-gasto').scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function cancelEdit() {
    editingId = null;
    document.getElementById('gasto-id').value = '';
    document.getElementById('form-gasto').reset();
    document.getElementById('data').value = new Date().toISOString().split('T')[0];
    document.getElementById('form-title').textContent = 'Novo Gasto';
    document.getElementById('btn-cancelar').style.display = 'none';
    document.getElementById('btn-salvar').innerHTML = '<i class="fas fa-save"></i> Salvar';
}

document.getElementById('btn-cancelar').addEventListener('click', cancelEdit);

async function deleteGasto(id) {
    if (!confirm('Tem certeza que deseja excluir este gasto?')) return;
    await api(`/api/gastos/${id}`, { method: 'DELETE' });
    showToast('Gasto removido');
    await Promise.all([loadGastos(), loadResumo()]);
}

// ═══════════════════════════════════════════
// RECEITAS (Income)
// ═══════════════════════════════════════════

async function loadReceitas() {
    const mes = String(currentMonth).padStart(2, '0');
    const receitas = await api(`/api/receitas?mes=${mes}&ano=${currentYear}`);
    renderReceitasTable(receitas);
}

function renderReceitasTable(receitas) {
    const tbody = document.getElementById('tbody-receitas');
    const emptyMsg = document.getElementById('receitas-empty');

    if (receitas.length === 0) {
        tbody.innerHTML = '';
        emptyMsg.style.display = 'block';
        return;
    }

    emptyMsg.style.display = 'none';
    tbody.innerHTML = receitas.map(r => `
        <tr>
            <td>${formatDate(r.data)}</td>
            <td><strong>${r.descricao}</strong></td>
            <td class="valor-col receita-valor">${formatCurrency(r.valor)}</td>
            <td class="anotacao-col" title="${(r.anotacao || '').replace(/"/g, '&quot;')}">${r.anotacao || '—'}</td>
            <td>
                <div class="actions-col">
                    <button class="btn btn-sm btn-secondary" onclick="editReceita(${r.id})" title="Editar">
                        <i class="fas fa-pen"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteReceita(${r.id})" title="Excluir">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

// Form: Create / Edit Receita
document.getElementById('form-receita').addEventListener('submit', async (e) => {
    e.preventDefault();

    const dados = {
        descricao: document.getElementById('receita-descricao').value.trim(),
        valor: parseFloat(document.getElementById('receita-valor').value),
        data: document.getElementById('receita-data').value,
        anotacao: document.getElementById('receita-anotacao').value.trim()
    };

    if (editingReceitaId) {
        await api(`/api/receitas/${editingReceitaId}`, {
            method: 'PUT',
            body: JSON.stringify(dados)
        });
        showToast('Receita atualizada!');
        cancelEditReceita();
    } else {
        await api('/api/receitas', {
            method: 'POST',
            body: JSON.stringify(dados)
        });
        showToast('Receita adicionada!');
    }

    document.getElementById('form-receita').reset();
    document.getElementById('receita-data').value = new Date().toISOString().split('T')[0];
    await Promise.all([loadReceitas(), loadResumo()]);
});

async function editReceita(id) {
    const mes = String(currentMonth).padStart(2, '0');
    const receitas = await api(`/api/receitas?mes=${mes}&ano=${currentYear}`);
    const r = receitas.find(x => x.id === id);
    if (!r) return;

    editingReceitaId = id;
    document.getElementById('receita-id').value = id;
    document.getElementById('receita-descricao').value = r.descricao;
    document.getElementById('receita-valor').value = r.valor;
    document.getElementById('receita-data').value = r.data;
    document.getElementById('receita-anotacao').value = r.anotacao || '';

    document.getElementById('form-receita-title').textContent = 'Editar Receita';
    document.getElementById('btn-cancelar-receita').style.display = 'inline-flex';
    document.getElementById('btn-salvar-receita').innerHTML = '<i class="fas fa-check"></i> Atualizar';

    document.getElementById('form-receita').scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function cancelEditReceita() {
    editingReceitaId = null;
    document.getElementById('receita-id').value = '';
    document.getElementById('form-receita').reset();
    document.getElementById('receita-data').value = new Date().toISOString().split('T')[0];
    document.getElementById('form-receita-title').textContent = 'Nova Receita';
    document.getElementById('btn-cancelar-receita').style.display = 'none';
    document.getElementById('btn-salvar-receita').innerHTML = '<i class="fas fa-save"></i> Salvar Receita';
}

document.getElementById('btn-cancelar-receita').addEventListener('click', cancelEditReceita);

async function deleteReceita(id) {
    if (!confirm('Tem certeza que deseja excluir esta receita?')) return;
    await api(`/api/receitas/${id}`, { method: 'DELETE' });
    showToast('Receita removida');
    await Promise.all([loadReceitas(), loadResumo()]);
}

// ═══════════════════════════════════════════
// RESUMO MENSAL + CHART
// ═══════════════════════════════════════════

async function loadResumo() {
    const mes = String(currentMonth).padStart(2, '0');
    const resumo = await api(`/api/resumo?mes=${mes}&ano=${currentYear}`);

    // Dashboard values
    document.getElementById('total-receitas').textContent = formatCurrency(resumo.total_receitas);
    document.getElementById('total-mes').textContent = formatCurrency(resumo.total_gastos);
    document.getElementById('total-invest').textContent = formatCurrency(resumo.total_investimentos);
    document.getElementById('qtd-gastos').textContent = resumo.quantidade;

    // Saldo with color
    const saldoEl = document.getElementById('saldo-mes');
    saldoEl.textContent = formatCurrency(resumo.saldo);
    if (resumo.saldo >= 0) {
        saldoEl.style.color = '#34d399'; // green
    } else {
        saldoEl.style.color = '#f87171'; // red
    }

    // Caixa: total disponível do mês anterior
    const caixaEl = document.getElementById('caixa-valor');
    caixaEl.textContent = formatCurrency(resumo.caixa);

    const media = resumo.quantidade > 0 ? resumo.total_gastos / resumo.quantidade : 0;
    document.getElementById('media-gasto').textContent = formatCurrency(media);

    // Total Disponível with color
    const dispEl = document.getElementById('total-disponivel');
    dispEl.textContent = formatCurrency(resumo.total_disponivel);
    if (resumo.total_disponivel >= 0) {
        dispEl.style.color = '#34d399';
    } else {
        dispEl.style.color = '#f87171';
    }

    renderChart(resumo.por_categoria);
}

function renderChart(data) {
    const canvas = document.getElementById('grafico-categorias');
    const emptyMsg = document.getElementById('chart-empty');

    if (data.length === 0) {
        canvas.style.display = 'none';
        emptyMsg.style.display = 'block';
        if (gastosChart) { gastosChart.destroy(); gastosChart = null; }
        return;
    }

    canvas.style.display = 'block';
    emptyMsg.style.display = 'none';

    const labels = data.map(d => d.nome);
    const values = data.map(d => d.total);
    const colors = data.map(d => d.cor);

    if (gastosChart) gastosChart.destroy();

    gastosChart = new Chart(canvas, {
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
                            return ` ${formatCurrency(ctx.parsed)} (${pct}%)`;
                        }
                    }
                }
            },
            animation: {
                animateRotate: true,
                animateScale: true,
                duration: 800,
                easing: 'easeOutCubic'
            }
        }
    });
}

// ═══════════════════════════════════════════
// CURRENCY CONVERTER
// ═══════════════════════════════════════════

document.getElementById('btn-converter').addEventListener('click', async () => {
    const valor = parseFloat(document.getElementById('conv-valor').value);
    const de = document.getElementById('conv-de').value;
    const para = document.getElementById('conv-para').value;

    if (isNaN(valor) || valor <= 0) {
        showToast('Insira um valor válido para converter', 'error');
        return;
    }

    const btn = document.getElementById('btn-converter');
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Convertendo...';
    btn.disabled = true;

    try {
        const result = await api(`/api/conversao?valor=${valor}&de=${de}&para=${para}`);
        const div = document.getElementById('resultado-conversao');
        div.style.display = 'block';
        div.innerHTML = `
            <div>${valor.toFixed(2)} ${de} = <strong>${result.valor_convertido.toFixed(2)} ${para}</strong></div>
            <div class="rate">Taxa: 1 ${de} = ${result.taxa.toFixed(4)} ${para}</div>
        `;
    } catch (err) {
        // Error already shown by api()
    } finally {
        btn.innerHTML = '<i class="fas fa-sync-alt"></i> Converter';
        btn.disabled = false;
    }
});

// ═══════════════════════════════════════════
// AUTHENTICATION
// ═══════════════════════════════════════════

function checkAuth() {
    if (getToken()) {
        document.getElementById('auth-section').style.display = 'none';
        document.getElementById('app-content').style.display = 'block';
        document.getElementById('user-greeting').textContent = `Olá, ${localStorage.getItem(USERNAME_KEY) || 'Usuário'}!`;
        return true;
    } else {
        document.getElementById('auth-section').style.display = 'flex';
        document.getElementById('app-content').style.display = 'none';
        return false;
    }
}

function logout() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USERNAME_KEY);
    window.location.reload();
}

document.getElementById('btn-logout').addEventListener('click', logout);

document.getElementById('go-to-register').addEventListener('click', (e) => {
    e.preventDefault();
    document.getElementById('login-container').style.display = 'none';
    document.getElementById('register-container').style.display = 'block';
});
document.getElementById('go-to-login').addEventListener('click', (e) => {
    e.preventDefault();
    document.getElementById('register-container').style.display = 'none';
    document.getElementById('login-container').style.display = 'block';
});

document.getElementById('form-login').addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = {
        username: document.getElementById('login-user').value.trim(),
        password: document.getElementById('login-pass').value.trim()
    };
    try {
        const res = await api('/api/login', { method: 'POST', body: JSON.stringify(data) });
        localStorage.setItem(TOKEN_KEY, res.token);
        localStorage.setItem(USERNAME_KEY, res.username);
        showToast('Login realizado!');
        setTimeout(() => window.location.reload(), 500);
    } catch (err) { }
});

document.getElementById('form-register').addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = {
        username: document.getElementById('reg-user').value.trim(),
        password: document.getElementById('reg-pass').value.trim()
    };
    try {
        await api('/api/register', { method: 'POST', body: JSON.stringify(data) });
        showToast('Conta criada! Faça login.');
        alert('Conta cadastrada com sucesso! Clique em OK para fazer login.');
        document.getElementById('form-register').reset();
        document.getElementById('go-to-login').click();

        // Auto-fill login and focus password
        document.getElementById('login-user').value = data.username;
        setTimeout(() => document.getElementById('login-pass').focus(), 100);
    } catch (err) {
        // api() already shows error toast, but we can alert it just to be safe if they didn't notice
        alert(err.message || 'Erro ao criar conta');
    }
});

// ═══════════════════════════════════════════
// INIT
// ═══════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    if (!checkAuth()) return;

    // Set default dates to today
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('data').value = today;
    document.getElementById('receita-data').value = today;
    document.getElementById('invest-data').value = today;
    updateMonthLabel();
    loadData();
});

// ═══════════════════════════════════════════
// CAIXA (Cash Box) CONFIG
// ═══════════════════════════════════════════

document.getElementById('card-caixa').addEventListener('click', async () => {
    const configEl = document.getElementById('caixa-config');
    if (configEl.style.display === 'none') {
        try {
            const data = await api('/api/caixa');
            document.getElementById('caixa-saldo-inicial').value = data.saldo_inicial || '';
        } catch (e) { /* ignore */ }
        configEl.style.display = 'block';
        document.getElementById('caixa-saldo-inicial').focus();
    } else {
        configEl.style.display = 'none';
    }
});

document.getElementById('btn-salvar-caixa').addEventListener('click', async () => {
    const valor = parseFloat(document.getElementById('caixa-saldo-inicial').value) || 0;
    await api('/api/caixa', {
        method: 'PUT',
        body: JSON.stringify({ saldo_inicial: valor })
    });
    showToast('Saldo inicial atualizado!');
    document.getElementById('caixa-config').style.display = 'none';
    await loadResumo();
});

document.getElementById('btn-cancelar-caixa').addEventListener('click', () => {
    document.getElementById('caixa-config').style.display = 'none';
});

// ═══════════════════════════════════════════
// INVESTIMENTOS
// ═══════════════════════════════════════════

async function loadInvestimentos() {
    const mes = String(currentMonth).padStart(2, '0');
    const investimentos = await api(`/api/investimentos?mes=${mes}&ano=${currentYear}`);
    renderInvestimentosTable(investimentos);
}

function renderInvestimentosTable(investimentos) {
    const tbody = document.getElementById('tbody-investimentos');
    const emptyMsg = document.getElementById('investimentos-empty');

    if (investimentos.length === 0) {
        tbody.innerHTML = '';
        emptyMsg.style.display = 'block';
        return;
    }

    emptyMsg.style.display = 'none';
    tbody.innerHTML = investimentos.map(i => `
        <tr>
            <td>${formatDate(i.data)}</td>
            <td><strong>${i.descricao}</strong></td>
            <td><span class="cat-badge invest-badge">${i.tipo}</span></td>
            <td class="valor-col invest-valor">${formatCurrency(i.valor)}</td>
            <td class="anotacao-col" title="${(i.anotacao || '').replace(/"/g, '&quot;')}">${i.anotacao || '\u2014'}</td>
            <td>
                <div class="actions-col">
                    <button class="btn btn-sm btn-secondary" onclick="editInvestimento(${i.id})" title="Editar">
                        <i class="fas fa-pen"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteInvestimento(${i.id})" title="Excluir">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

// Form: Create / Edit Investimento
document.getElementById('form-investimento').addEventListener('submit', async (e) => {
    e.preventDefault();

    const dados = {
        descricao: document.getElementById('invest-descricao').value.trim(),
        valor: parseFloat(document.getElementById('invest-valor').value),
        tipo: document.getElementById('invest-tipo').value,
        data: document.getElementById('invest-data').value,
        anotacao: document.getElementById('invest-anotacao').value.trim()
    };

    if (editingInvestId) {
        await api(`/api/investimentos/${editingInvestId}`, {
            method: 'PUT',
            body: JSON.stringify(dados)
        });
        showToast('Investimento atualizado!');
        cancelEditInvest();
    } else {
        await api('/api/investimentos', {
            method: 'POST',
            body: JSON.stringify(dados)
        });
        showToast('Investimento adicionado!');
    }

    document.getElementById('form-investimento').reset();
    document.getElementById('invest-data').value = new Date().toISOString().split('T')[0];
    await Promise.all([loadInvestimentos(), loadResumo()]);
});

async function editInvestimento(id) {
    const mes = String(currentMonth).padStart(2, '0');
    const investimentos = await api(`/api/investimentos?mes=${mes}&ano=${currentYear}`);
    const i = investimentos.find(x => x.id === id);
    if (!i) return;

    editingInvestId = id;
    document.getElementById('invest-id').value = id;
    document.getElementById('invest-descricao').value = i.descricao;
    document.getElementById('invest-valor').value = i.valor;
    document.getElementById('invest-tipo').value = i.tipo;
    document.getElementById('invest-data').value = i.data;
    document.getElementById('invest-anotacao').value = i.anotacao || '';

    document.getElementById('form-invest-title').textContent = 'Editar Investimento';
    document.getElementById('btn-cancelar-invest').style.display = 'inline-flex';
    document.getElementById('btn-salvar-invest').innerHTML = '<i class="fas fa-check"></i> Atualizar';

    document.getElementById('form-investimento').scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function cancelEditInvest() {
    editingInvestId = null;
    document.getElementById('invest-id').value = '';
    document.getElementById('form-investimento').reset();
    document.getElementById('invest-data').value = new Date().toISOString().split('T')[0];
    document.getElementById('form-invest-title').textContent = 'Novo Investimento';
    document.getElementById('btn-cancelar-invest').style.display = 'none';
    document.getElementById('btn-salvar-invest').innerHTML = '<i class="fas fa-save"></i> Salvar';
}

document.getElementById('btn-cancelar-invest').addEventListener('click', cancelEditInvest);

async function deleteInvestimento(id) {
    if (!confirm('Tem certeza que deseja excluir este investimento?')) return;
    await api(`/api/investimentos/${id}`, { method: 'DELETE' });
    showToast('Investimento removido');
    await Promise.all([loadInvestimentos(), loadResumo()]);
}
