
let _arbol = [];
let _flat = [];
let _idEliminar = null;
let _modoBusqueda = false;
let _soloActivas = false;
let _filtroTipo = 'all';

/* ── Utilidades ───────────────────────────────────────────── */
function mostrarAlerta(msg, tipo = 'danger', c = 'alertaGlobal') {
    const el = document.getElementById(c);
    el.className = `alert alert-${tipo}`;
    el.innerHTML = `<i class="fas fa-${tipo === 'success' ? 'check-circle' : 'exclamation-circle'}"></i> ${msg}`;
    el.style.display = 'block';
    if (tipo === 'success') setTimeout(() => { el.style.display = 'none'; }, 4000);
}
function ocultarAlerta(c = 'alertaGlobal') { document.getElementById(c).style.display = 'none'; }
function escHtml(s) {
    return String(s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function encontrar(id, lista) {
    for (const n of lista) {
        if (n.id === id) return n;
        const h = encontrar(id, n.subcategorias || []);
        if (h) return h;
    }
    return null;
}

/* ── Carga ────────────────────────────────────────────────── */
async function cargarCategorias(q = '') {
    document.getElementById('loadingCategorias').style.display = 'block';
    document.getElementById('tablaCategorias').style.display = 'none';
    document.getElementById('emptyCategorias').style.display = 'none';
    ocultarAlerta();
    _modoBusqueda = !!q;

    try {
        let url = q ? `/categorias?q=${encodeURIComponent(q)}` : '/categorias';
        if (_soloActivas) url += (url.includes('?') ? '&' : '?') + 'solo_activas=true';
        const data = await api.request('GET', url);
        _flat = data.categorias || [];
        _arbol = data.arbol || [];
        renderTabla();
    } catch (err) {
        mostrarAlerta(err.message || 'Error al cargar categorías');
        document.getElementById('loadingCategorias').style.display = 'none';
    }
}

/* ── Render ───────────────────────────────────────────────── */
function badgeEstado(estado) {
    return `<span class="badge ${estado ? 'bg-success' : 'bg-secondary'}">${estado ? 'Activa' : 'Inactiva'}</span>`;
}
function badgeUso(uso) {
    return `<span class="badge bg-light text-dark border uso-badge">${uso}</span>`;
}
function iconoCategoria(c) {
    return `<span class="cat-dot" style="background:${escHtml(c.color)};"></span><i class="fas ${escHtml(c.icono)}" style="color:${escHtml(c.color)};"></i>`;
}
function etiquetaJerarquia(c) {
    if (c.parent_id) {
        return '<span class="cat-pill cat-pill-secondary">Subcategoría</span>';
    }
    return '<span class="cat-pill cat-pill-primary">Categoría principal</span>';
}
function textoResumen(c) {
    if (c.parent_id) {
        return c.nombre_padre ? `Subcategoría de ${escHtml(c.nombre_padre)}` : 'Subcategoría';
    }
    const hijos = Number(c.hijos || 0);
    return hijos > 0 ? `${hijos} subcategoría${hijos !== 1 ? 's' : ''}` : 'Sin subcategorías';
}
function textoRuta(c) {
    if (c.ruta) {
        return `Ruta: ${escHtml(c.ruta)}`;
    }
    return c.parent_id ? 'Jerarquía: subcategoría' : 'Jerarquía: categoría principal';
}

function actualizarResumen() {
    const total = _flat.length;
    const principales = _flat.filter(c => !c.parent_id).length;
    const subcategorias = _flat.filter(c => c.parent_id).length;
    const activas = _flat.filter(c => c.estado).length;
    document.getElementById('statTotalCategorias').textContent = total;
    document.getElementById('statPrincipales').textContent = principales;
    document.getElementById('statSubcategorias').textContent = subcategorias;
    document.getElementById('statActivas').textContent = activas;
}

function renderFlatList(items, titulo) {
    const footer = document.getElementById('footerTotal');
    const body = document.getElementById('tbodyCategorias');
    body.innerHTML = items.map(c => `
        <tr class="${c.estado ? '' : 'cat-inactiva'}">
            <td>
                <div class="cat-row-title">
                    <span class="mt-1">${iconoCategoria(c)}</span>
                    <div class="cat-row-text">
                        <div class="fw-semibold">${escHtml(c.nombre)}</div>
                        <div class="small text-muted">${escHtml(textoResumen(c))}</div>
                        <div class="small text-muted mt-1">${escHtml(textoRuta(c))}</div>
                    </div>
                </div>
            </td>
            <td>${etiquetaJerarquia(c)}</td>
            <td class="text-center">${badgeUso(c.uso)}</td>
            <td class="text-center">${badgeEstado(c.estado)}</td>
            <td class="text-center">${botonesAcciones(c)}</td>
        </tr>`).join('');

    document.getElementById('tablaCategorias').style.display = 'table';
    footer.style.display = 'block';
    footer.textContent = titulo;
}

function renderTabla() {
    document.getElementById('loadingCategorias').style.display = 'none';
    const footer = document.getElementById('footerTotal');
    actualizarResumen();

    if (_modoBusqueda) {
        const items = _flat.filter(c => _filtroTipo === 'all'
            || (_filtroTipo === 'principales' && !c.parent_id)
            || (_filtroTipo === 'subcategorias' && c.parent_id)
            || (_filtroTipo === 'inactivas' && !c.estado));

        if (items.length === 0) {
            document.getElementById('emptyCategorias').style.display = 'block';
            footer.style.display = 'none';
            return;
        }
        document.getElementById('tablaCategorias').style.display = 'table';
        footer.style.display = 'block';
        footer.textContent = `${items.length} resultado${items.length !== 1 ? 's' : ''}`;
        renderFlatList(items, `${items.length} resultado${items.length !== 1 ? 's' : ''}`);
        return;
    }

    if (_arbol.length === 0) {
        document.getElementById('emptyCategorias').style.display = 'block';
        footer.style.display = 'none';
        return;
    }

    document.getElementById('tablaCategorias').style.display = 'table';
    const totalPadres = _arbol.length;
    const totalHijos = _flat.filter(c => c.parent_id).length;
    const totalUso = _flat.reduce((s, c) => s + c.uso, 0);
    footer.style.display = 'block';
    footer.textContent = `${totalPadres} categoría${totalPadres !== 1 ? 's' : ''} raíz · ${totalHijos} subcategoría${totalHijos !== 1 ? 's' : ''} · ${totalUso} uso${totalUso !== 1 ? 's' : ''} registrado${totalUso !== 1 ? 's' : ''}`;

    if (_filtroTipo === 'subcategorias') {
        const items = _flat.filter(c => c.parent_id && (!_soloActivas || c.estado));
        renderFlatList(items, `${items.length} subcategoría${items.length !== 1 ? 's' : ''}`);
        return;
    }

    if (_filtroTipo === 'inactivas') {
        const items = _flat.filter(c => !c.estado);
        renderFlatList(items, `${items.length} inactiva${items.length !== 1 ? 's' : ''}`);
        return;
    }

    let html = '';
    const arbolFiltrado = _arbol
        .map(padre => ({
            ...padre,
            subcategorias: (padre.subcategorias || []).filter(hijo => _filtroTipo !== 'principales' || true)
        }))
        .filter(padre => _filtroTipo !== 'principales' || !padre.parent_id);

    arbolFiltrado.forEach(padre => {
        const tieneHijos = padre.subcategorias && padre.subcategorias.length > 0;
        const toggleId = `toggle-${padre.id}`;
        const subId = `sub-${padre.id}`;

        html += `
        <tr class="cat-row-padre ${padre.estado ? '' : 'cat-inactiva'}">
            <td>
                <div class="cat-row-title">
                    ${tieneHijos
                        ? `<span class="cat-toggle me-1 mt-1" id="${toggleId}" onclick="toggleSubcats(${padre.id})" title="Expandir/Colapsar">
                               <i class="fas fa-chevron-down text-muted small"></i>
                           </span>`
                        : `<span class="me-1 mt-1" style="display:inline-block;width:18px;"></span>`}
                    <span class="me-2 mt-1">${iconoCategoria(padre)}</span>
                    <div class="cat-row-text">
                        <div class="fw-semibold">${escHtml(padre.nombre)}</div>
                        <div class="small text-muted">${tieneHijos ? `${padre.subcategorias.length} subcategoría${padre.subcategorias.length !== 1 ? 's' : ''} vinculadas` : 'Sin subcategorías'}</div>
                        <div class="small text-muted mt-1">${escHtml(textoRuta(padre))}</div>
                    </div>
                </div>
            </td>
            <td>${etiquetaJerarquia(padre)}</td>
            <td class="text-center">${badgeUso(padre.uso)}</td>
            <td class="text-center">${badgeEstado(padre.estado)}</td>
            <td class="text-center">
                <button class="btn btn-sm btn-outline-success me-1"
                        onclick="abrirModalNueva(${padre.id})"
                        data-bs-toggle="modal" data-bs-target="#modalCategoria"
                        title="Agregar subcategoría">
                    <i class="fas fa-plus"></i>
                </button>
                ${botonesAcciones(padre)}
            </td>
        </tr>`;

        if (tieneHijos) {
            html += `<tr id="${subId}">
                <td colspan="5" class="p-0 border-0">
                    <table class="table mb-0">`;
            padre.subcategorias.forEach(hijo => {
                html += `
                    <tr class="cat-row-hijo ${hijo.estado ? '' : 'cat-inactiva'}">
                        <td>
                            <div class="cat-row-title">
                                <span class="text-muted mt-1"><i class="fas fa-level-up-alt fa-rotate-90"></i></span>
                                <span class="mt-1">${iconoCategoria(hijo)}</span>
                                <div class="cat-row-text">
                                    <div class="fw-semibold">${escHtml(hijo.nombre)}</div>
                                    <div class="small text-muted">${escHtml(textoResumen(hijo))}</div>
                                    <div class="small text-muted mt-1">${escHtml(textoRuta(hijo))}</div>
                                </div>
                            </div>
                        </td>
                        <td style="width:110px;">${etiquetaJerarquia(hijo)}</td>
                        <td class="text-center" style="width:80px;">${badgeUso(hijo.uso)}</td>
                        <td class="text-center" style="width:90px;">${badgeEstado(hijo.estado)}</td>
                        <td class="text-center" style="width:190px;">${botonesAcciones(hijo)}</td>
                    </tr>`;
            });
            html += `</table></td></tr>`;
        }
    });

    document.getElementById('tbodyCategorias').innerHTML = html;
}

function botonesAcciones(c) {
    return `
        <button class="btn btn-sm btn-outline-primary me-1" onclick="abrirModalEditar(${c.id})"
                data-bs-toggle="modal" data-bs-target="#modalCategoria" title="Editar">
            <i class="fas fa-edit"></i>
        </button>
        <button class="btn btn-sm ${c.estado ? 'btn-outline-warning' : 'btn-outline-success'} me-1"
                onclick="toggleEstado(${c.id})"
                title="${c.estado ? 'Inactivar' : 'Activar'}">
            <i class="fas fa-${c.estado ? 'toggle-on' : 'toggle-off'}"></i>
        </button>
        <button class="btn btn-sm btn-outline-danger"
                onclick="confirmarEliminar(${c.id}, '${escHtml(c.nombre)}')" title="Eliminar">
            <i class="fas fa-trash"></i>
        </button>`;
}

function toggleSubcats(padreId) {
    const toggle = document.getElementById(`toggle-${padreId}`);
    const sub = document.getElementById(`sub-${padreId}`);
    if (!sub) return;
    const oculto = sub.style.display === 'none';
    sub.style.display = oculto ? '' : 'none';
    toggle.classList.toggle('collapsed', !oculto);
}

/* ── Modales ──────────────────────────────────────────────── */
function _actualizarPreview() {
    const icono = document.getElementById('catIcono').value.trim() || 'fa-tag';
    const color = document.getElementById('catColorHex').value.trim() || '#6c757d';
    const nombre = document.getElementById('catNombre').value.trim() || 'Vista previa';
    document.getElementById('previewDot').style.background = color;
    document.getElementById('previewIcon').className = `fas ${icono}`;
    document.getElementById('previewIcon').style.color = color;
    document.getElementById('iconPreview').innerHTML = `<i class="fas ${icono}"></i>`;
    document.getElementById('previewNombre').textContent = nombre;
}

function abrirModalNueva(parentId) {
    document.getElementById('modalCategoriaTitle').textContent =
        parentId ? 'Nueva subcategoría' : 'Nueva categoría';
    document.getElementById('formCategoria').reset();
    document.getElementById('catId').value = '';
    document.getElementById('catParentId').value = parentId || '';
    document.getElementById('catIcono').value = 'fa-tag';
    document.getElementById('catColor').value = '#6c757d';
    document.getElementById('catColorHex').value = '#6c757d';

    // Modo "nueva subcategoría": mostrar info del padre, ocultar selector
    const wrapperPadre = document.getElementById('wrapperPadre');
    const wrapperSelector = document.getElementById('wrapperSelectorPadre');
    if (parentId) {
        const padre = encontrar(parentId, _arbol);
        document.getElementById('labelPadre').textContent = padre ? padre.nombre : `#${parentId}`;
        wrapperPadre.style.display = 'block';
        wrapperSelector.style.display = 'none';
    } else {
        wrapperPadre.style.display = 'none';
        wrapperSelector.style.display = 'none';
    }
    _actualizarPreview();
    ocultarAlerta('alertaModal');
}

function abrirModalEditar(id) {
    const c = _flat.find(x => x.id === id);
    if (!c) return;
    document.getElementById('modalCategoriaTitle').textContent =
        c.parent_id ? 'Editar subcategoría' : 'Editar categoría';
    document.getElementById('catId').value = c.id;
    document.getElementById('catParentId').value = c.parent_id || '';
    document.getElementById('catNombre').value = c.nombre;
    document.getElementById('catIcono').value = c.icono || 'fa-tag';
    document.getElementById('catColor').value = c.color || '#6c757d';
    document.getElementById('catColorHex').value = c.color || '#6c757d';

    // En edición siempre mostrar el selector de padre (para poder reasignarlo)
    document.getElementById('wrapperPadre').style.display = 'none';
    const wrapperSelector = document.getElementById('wrapperSelectorPadre');
    // Poblar el select con las categorías raíz (excluyendo la propia si es padre)
    const select = document.getElementById('catParentSelect');
    select.innerHTML = '<option value="">— Sin padre (categoría raíz) —</option>';
    _flat.filter(x => !x.parent_id && x.id !== id).forEach(p => {
        const opt = document.createElement('option');
        opt.value = p.id;
        opt.textContent = p.nombre;
        if (p.id === c.parent_id) opt.selected = true;
        select.appendChild(opt);
    });
    wrapperSelector.style.display = 'block';

    _actualizarPreview();
    ocultarAlerta('alertaModal');
}

async function toggleEstado(id) {
    try {
        const res = await api.request('PATCH', `/categorias/${id}/estado`);
        mostrarAlerta(
            res.estado ? 'Categoría activada.' : 'Categoría inactivada.',
            res.estado ? 'success' : 'warning'
        );
        await cargarCategorias(document.getElementById('inputBusqueda').value.trim());
    } catch (err) {
        mostrarAlerta(err.message || 'Error al cambiar estado.');
    }
}

function confirmarEliminar(id, nombre) {
    _idEliminar = id;
    document.getElementById('nombreEliminar').textContent = nombre;
    new bootstrap.Modal(document.getElementById('modalEliminar')).show();
}

/* ── Guardar ──────────────────────────────────────────────── */
document.getElementById('formCategoria').addEventListener('submit', async (e) => {
    e.preventDefault();
    ocultarAlerta('alertaModal');
    const id = document.getElementById('catId').value;

    // parent_id: si hay selector visible usarlo, si no usar el hidden
    const selectorVisible = document.getElementById('wrapperSelectorPadre').style.display !== 'none';
    let parentId;
    if (selectorVisible) {
        const v = document.getElementById('catParentSelect').value;
        parentId = v ? parseInt(v) : null;
    } else {
        const v = document.getElementById('catParentId').value;
        parentId = v ? parseInt(v) : null;
    }

    const nombre = document.getElementById('catNombre').value.trim();
    const icono = document.getElementById('catIcono').value.trim() || 'fa-tag';
    const color = document.getElementById('catColorHex').value.trim() || '#6c757d';

    if (!nombre) { mostrarAlerta('El nombre es obligatorio.', 'danger', 'alertaModal'); return; }

    const payload = { nombre, parent_id: parentId, icono, color };
    const btn = document.getElementById('btnGuardarCategoria');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

    try {
        if (id) {
            await api.request('PUT', `/categorias/${id}`, payload);
        } else {
            await api.request('POST', '/categorias', payload);
        }
        bootstrap.Modal.getInstance(document.getElementById('modalCategoria')).hide();
        mostrarAlerta(id ? 'Categoría actualizada.' : 'Categoría creada.', 'success');
        await cargarCategorias(document.getElementById('inputBusqueda').value.trim());
    } catch (err) {
        mostrarAlerta(err.message || 'Error al guardar.', 'danger', 'alertaModal');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-save"></i> Guardar';
    }
});

/* ── Eliminar ─────────────────────────────────────────────── */
document.getElementById('btnConfirmarEliminar').addEventListener('click', async () => {
    if (!_idEliminar) return;
    try {
        await api.request('DELETE', `/categorias/${_idEliminar}`);
        bootstrap.Modal.getInstance(document.getElementById('modalEliminar')).hide();
        mostrarAlerta('Categoría eliminada.', 'success');
        await cargarCategorias(document.getElementById('inputBusqueda').value.trim());
    } catch (err) {
        bootstrap.Modal.getInstance(document.getElementById('modalEliminar')).hide();
        mostrarAlerta(err.message || 'Error al eliminar.');
    } finally { _idEliminar = null; }
});

/* ── Controles ───────────────────────────────────────────── */
let _debounce;
document.getElementById('inputBusqueda').addEventListener('input', (e) => {
    clearTimeout(_debounce);
    _debounce = setTimeout(() => cargarCategorias(e.target.value.trim()), 350);
});
document.getElementById('btnLimpiarBusqueda').addEventListener('click', () => {
    document.getElementById('inputBusqueda').value = '';
    cargarCategorias();
});
document.getElementById('toggleSoloActivas').addEventListener('change', (e) => {
    _soloActivas = e.target.checked;
    cargarCategorias(document.getElementById('inputBusqueda').value.trim());
});

document.querySelectorAll('.filtro-cat').forEach(btn => {
    btn.addEventListener('click', () => {
        _filtroTipo = btn.dataset.filter || 'all';
        document.querySelectorAll('.filtro-cat').forEach(b => {
            b.classList.toggle('active', b === btn);
            b.classList.toggle('btn-primary', b === btn);
            b.classList.toggle('btn-outline-primary', b !== btn);
        });
        renderTabla();
    });
});

// Sincronizar color picker ↔ hex input
document.getElementById('catColor').addEventListener('input', (e) => {
    document.getElementById('catColorHex').value = e.target.value;
    _actualizarPreview();
});
document.getElementById('catColorHex').addEventListener('input', (e) => {
    const v = e.target.value;
    if (/^#[0-9a-fA-F]{6}$/.test(v)) document.getElementById('catColor').value = v;
    _actualizarPreview();
});
document.getElementById('catIcono').addEventListener('input', _actualizarPreview);
document.getElementById('catNombre').addEventListener('input', _actualizarPreview);

document.addEventListener('DOMContentLoaded', () => cargarCategorias());
