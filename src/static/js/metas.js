(() => {
    const $ = id => document.getElementById(id);
    const money = new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 2 });
    const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    })[c]);
    let seleccion = null;
    let edicion = null;
    let referenciaMeta = crypto.randomUUID();
    let referenciaMovimiento = crypto.randomUUID();
    let revisionDetalle = 0;

    function aviso(texto, error = false) {
        const el = $('metaAviso');
        el.className = `alert alert-${error ? 'danger' : 'success'}`;
        el.textContent = texto;
        el.hidden = false;
    }

    function fecha(valor) {
        return valor ? valor.split('-').reverse().join('/') : 'Sin fecha objetivo';
    }

    function descripcion(meta) {
        return `Ahorrado: ${money.format(meta.ahorrado)} de ${money.format(meta.objetivo)} · Falta: ${money.format(meta.faltante)} · ${Number(meta.progreso)}% · ${fecha(meta.fecha_objetivo)}`;
    }

    async function cargarMetas() {
        try {
            const data = await api.request('GET', '/metas');
            $('listaMetas').innerHTML = data.metas.map(meta => `
                <div class="border rounded p-3 mb-2">
                    <div class="d-flex justify-content-between align-items-center gap-2">
                        <strong>${escape(meta.nombre)}</strong>
                        <button class="btn btn-sm btn-outline-primary" type="button" data-meta="${meta.id}">Ver detalle</button>
                    </div>
                    <div class="small mt-2">${escape(descripcion(meta))}</div>
                    <div class="progress mt-2" role="progressbar" aria-label="Progreso de ${escape(meta.nombre)}" aria-valuenow="${Math.min(100, Number(meta.progreso))}" aria-valuemin="0" aria-valuemax="100">
                        <div class="progress-bar" style="width:${Math.max(0, Math.min(100, Number(meta.progreso)))}%"></div>
                    </div>
                    ${Number(meta.ahorrado) >= Number(meta.objetivo) ? '<span class="badge bg-success mt-2">Objetivo alcanzado</span>' : ''}
                </div>`).join('') || '<p class="text-muted mb-0">Aún no tienes metas. Crea una para comenzar.</p>';
        } catch (error) {
            $('listaMetas').textContent = 'No fue posible cargar las metas.';
            aviso(error.message, true);
        }
    }

    async function cargarDetalle(id) {
        const revision = ++revisionDetalle;
        seleccion = null;
        $('detalleMeta').hidden = true;
        try {
            const data = await api.request('GET', `/metas/${id}`);
            if (revision !== revisionDetalle) return;
            seleccion = data.meta;
            $('tituloDetalleMeta').textContent = seleccion.nombre;
            $('resumenDetalleMeta').textContent = descripcion(seleccion);
            $('historialMeta').innerHTML = data.movimientos.map(m => `<tr>
                <td>${escape(m.fecha_creacion.replace('T', ' '))}</td>
                <td>${m.tipo === 'aporte' ? 'Aporte' : 'Retiro'}</td>
                <td>${escape(money.format(m.monto))}</td><td>${escape(m.nota || '—')}</td></tr>`).join('')
                || '<tr><td colspan="4" class="text-muted">Sin movimientos registrados.</td></tr>';
            $('detalleMeta').hidden = false;
        } catch (error) {
            if (revision !== revisionDetalle) return;
            seleccion = null;
            aviso(error.message, true);
        }
    }

    function cancelarEdicion() {
        edicion = null;
        $('formMeta').reset();
        $('tituloFormularioMeta').textContent = 'Nueva meta';
        $('cancelarEdicion').hidden = true;
    }

    $('listaMetas').addEventListener('click', event => {
        const boton = event.target.closest('[data-meta]');
        if (boton) cargarDetalle(Number(boton.dataset.meta));
    });
    $('cancelarEdicion').addEventListener('click', cancelarEdicion);
    $('editarMeta').addEventListener('click', () => {
        if (!seleccion) return;
        edicion = seleccion.id;
        $('nombreMeta').value = seleccion.nombre;
        $('objetivoMeta').value = seleccion.objetivo;
        $('fechaMeta').value = seleccion.fecha_objetivo || '';
        $('tituloFormularioMeta').textContent = 'Editar meta';
        $('cancelarEdicion').hidden = false;
        $('nombreMeta').focus();
    });
    $('formMeta').addEventListener('submit', async event => {
        event.preventDefault();
        const button = event.submitter || event.currentTarget.querySelector('button[type="submit"]');
        button.disabled = true;
        const idEditado = edicion;
        try {
            const data = { nombre: $('nombreMeta').value, objetivo: $('objetivoMeta').value, fecha_objetivo: $('fechaMeta').value || null };
            if (!idEditado) data.referencia = referenciaMeta;
            const result = await api.request(idEditado ? 'PUT' : 'POST', idEditado ? `/metas/${idEditado}` : '/metas', data);
            referenciaMeta = crypto.randomUUID();
            cancelarEdicion();
            aviso(result.message);
            await cargarMetas();
            await cargarDetalle(idEditado || result.id);
        } catch (error) {
            aviso(error.message, true);
        } finally {
            button.disabled = false;
        }
    });
    $('formMovimientoMeta').addEventListener('submit', async event => {
        event.preventDefault();
        if (!seleccion) return;
        const id = seleccion.id;
        const button = event.submitter || event.currentTarget.querySelector('button[type="submit"]');
        button.disabled = true;
        try {
            const result = await api.request('POST', `/metas/${id}/movimientos`, {
                tipo: $('tipoMovimientoMeta').value, monto: $('montoMovimientoMeta').value,
                nota: $('notaMovimientoMeta').value, referencia: referenciaMovimiento
            });
            referenciaMovimiento = crypto.randomUUID();
            $('formMovimientoMeta').reset();
            aviso(result.message);
            await cargarMetas();
            if (seleccion && seleccion.id === id) await cargarDetalle(id);
        } catch (error) {
            aviso(error.message, true);
        } finally {
            button.disabled = false;
        }
    });
    cargarMetas();
})();
