(() => {
    const $ = id => document.getElementById(id);
    let detalle = null;
    let pagoActivo = null;
    let ajusteActivo = null;
    let referenciaPago = null;

    function aviso(message, tipo = 'danger') {
        const el = $('prestamoAviso');
        el.className = `alert alert-${tipo}`;
        el.textContent = message;
        el.hidden = false;
        el.scrollIntoView({ block: 'nearest' });
    }

    function fechaHoy() {
        const fecha = new Date();
        return `${fecha.getFullYear()}-${String(fecha.getMonth() + 1).padStart(2, '0')}-${String(fecha.getDate()).padStart(2, '0')}`;
    }

    function agregarCargo(container, nombre = '', monto = '') {
        const row = document.createElement('div');
        row.className = 'row g-2 mb-2';
        const nameCol = document.createElement('div');
        nameCol.className = 'col-6';
        const name = document.createElement('input');
        name.className = 'form-control cargo-nombre';
        name.placeholder = 'Nombre del cargo';
        name.setAttribute('aria-label', 'Nombre del cargo');
        name.maxLength = 100;
        name.required = true;
        name.value = nombre;
        nameCol.appendChild(name);
        const amountCol = document.createElement('div');
        amountCol.className = 'col-4';
        const amount = document.createElement('input');
        amount.className = 'form-control cargo-monto';
        amount.type = 'number';
        amount.min = '0';
        amount.step = '0.01';
        amount.required = true;
        amount.value = monto;
        amount.setAttribute('aria-label', 'Importe del cargo');
        amountCol.appendChild(amount);
        const buttonCol = document.createElement('div');
        buttonCol.className = 'col-2';
        const remove = document.createElement('button');
        remove.type = 'button';
        remove.className = 'btn btn-outline-danger';
        remove.textContent = '×';
        remove.setAttribute('aria-label', 'Quitar cargo');
        remove.addEventListener('click', () => row.remove());
        buttonCol.appendChild(remove);
        row.append(nameCol, amountCol, buttonCol);
        container.appendChild(row);
    }

    function leerCargos(container) {
        return Array.from(container.children, row => ({
            nombre: row.querySelector('.cargo-nombre').value,
            monto: row.querySelector('.cargo-monto').value,
        }));
    }

    function celda(row, text) {
        const cell = document.createElement('td');
        cell.textContent = text;
        row.appendChild(cell);
    }

    function boton(texto, onClick) {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'btn btn-outline-primary btn-sm me-1 mb-1';
        button.textContent = texto;
        button.addEventListener('click', onClick);
        return button;
    }

    async function cargarLista() {
        const data = await api.request('GET', '/prestamos');
        const container = $('listaPrestamos');
        container.replaceChildren();
        if (!data.prestamos.length) {
            container.textContent = 'Aún no tienes préstamos registrados.';
            return;
        }
        for (const prestamo of data.prestamos) {
            const row = document.createElement('div');
            row.className = 'd-flex flex-wrap justify-content-between align-items-center border-bottom py-2 gap-2';
            const info = document.createElement('span');
            info.textContent = `${prestamo.nombre} · ${prestamo.acreedor} · Capital pendiente: ${formatCurrency(Number(prestamo.saldo))}`;
            row.append(info, boton('Ver cuotas', () => cargarDetalle(prestamo.id)));
            container.appendChild(row);
        }
    }

    async function cargarCuentas() {
        const data = await api.request('GET', '/prestamos/cuentas');
        const select = $('cuentaPago');
        select.length = 1;
        for (const cuenta of data.cuentas) {
            const option = document.createElement('option');
            option.value = cuenta.id_cuenta;
            option.textContent = `${cuenta.nombre} (${cuenta.moneda})`;
            select.appendChild(option);
        }
    }

    async function cargarDetalle(id) {
        try {
            detalle = await api.request('GET', `/prestamos/${id}`);
            $('detallePrestamo').hidden = false;
            $('panelPago').hidden = true;
            $('panelAjuste').hidden = true;
            $('detalleTitulo').textContent = `${detalle.prestamo.nombre} · ${detalle.prestamo.acreedor}`;
            $('detalleResumen').textContent = `Capital pendiente: ${formatCurrency(Number(detalle.prestamo.saldo))} · Tasa EA: ${detalle.prestamo.tasa_ea}%`;
            const body = $('cuotasPrestamo');
            body.replaceChildren();
            const primera = detalle.cuotas.find(c => !c.cancelada && Number(c.pendiente) > 0);
            $('abrirAbono').hidden = !primera;
            for (const cuota of detalle.cuotas) {
                const row = document.createElement('tr');
                const cargos = cuota.cargos.map(c => `${c.nombre}: ${formatCurrency(Number(c.monto))}`).join(', ') || '—';
                const parcial = Number(cuota.capital_pagado) > 0 || Number(cuota.interes_pagado) > 0 || cuota.cargos.some(c => Number(c.pagado) > 0);
                celda(row, String(cuota.numero));
                celda(row, cuota.fecha);
                celda(row, formatCurrency(Number(cuota.capital)));
                celda(row, formatCurrency(Number(cuota.interes)));
                celda(row, cargos);
                celda(row, formatCurrency(cuota.cancelada ? 0 : Number(cuota.pendiente)));
                celda(row, cuota.cancelada ? 'Cancelada por abono' : Number(cuota.pendiente) === 0 ? 'Pagada' : parcial ? 'Pago parcial' : 'Pendiente');
                const action = document.createElement('td');
                if (primera && cuota.id === primera.id) action.appendChild(boton('Pagar', () => abrirPago('cuota', cuota)));
                if (!cuota.cancelada && Number(cuota.pendiente) > 0 && !parcial) {
                    action.appendChild(boton('Ajustar', () => abrirAjuste(cuota, primera && cuota.id === primera.id)));
                }
                row.appendChild(action);
                body.appendChild(row);
            }
            const pagos = $('pagosPrestamo');
            pagos.replaceChildren();
            if (!detalle.pagos.length) {
                const row = document.createElement('tr');
                celda(row, 'Sin pagos registrados.');
                pagos.appendChild(row);
            }
            for (const pago of detalle.pagos) {
                const row = document.createElement('tr');
                const cuota = detalle.cuotas.find(c => c.id === pago.id_cuota);
                celda(row, pago.fecha);
                celda(row, cuota ? `Cuota ${cuota.numero}` : 'Abono extraordinario');
                celda(row, formatCurrency(Number(pago.total)));
                celda(row, formatCurrency(Number(pago.capital)));
                celda(row, formatCurrency(Number(pago.interes)));
                celda(row, pago.cargos.map(c => `${c.nombre}: ${formatCurrency(Number(c.monto))}`).join(', ') || '—');
                pagos.appendChild(row);
            }
        } catch (error) {
            aviso(error.message);
        }
    }

    function abrirPago(tipo, cuota) {
        pagoActivo = { tipo, numero_cuota: cuota ? cuota.numero : null };
        referenciaPago = crypto.randomUUID();
        $('tituloPago').textContent = cuota ? `Pagar cuota ${cuota.numero}` : 'Abono extraordinario a capital';
        $('montoPago').value = cuota ? cuota.pendiente : '';
        $('montoPago').max = cuota ? cuota.pendiente : detalle.prestamo.saldo;
        $('fechaPago').value = fechaHoy();
        $('cuentaPago').value = '';
        $('panelAjuste').hidden = true;
        $('panelPago').hidden = false;
        $('panelPago').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function abrirAjuste(cuota, primera) {
        ajusteActivo = cuota.numero;
        $('tituloAjuste').textContent = `Ajustar cuota ${cuota.numero}`;
        $('capitalAjuste').value = cuota.capital;
        $('interesAjuste').value = cuota.interes;
        $('capitalAjuste').readOnly = !primera;
        $('interesAjuste').readOnly = !primera;
        $('cargosAjuste').replaceChildren();
        for (const cargo of cuota.cargos) agregarCargo($('cargosAjuste'), cargo.nombre, cargo.monto);
        $('panelPago').hidden = true;
        $('panelAjuste').hidden = false;
        $('panelAjuste').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    async function procesar(form, action) {
        const submit = form.querySelector('[type=submit]');
        submit.disabled = true;
        $('prestamoAviso').hidden = true;
        try {
            await action();
        } catch (error) {
            aviso(error.message);
        } finally {
            submit.disabled = false;
        }
    }

    document.addEventListener('DOMContentLoaded', async () => {
        $('primeraFecha').value = fechaHoy();
        $('agregarCargoInicial').addEventListener('click', () => agregarCargo($('cargosIniciales')));
        $('agregarCargoAjuste').addEventListener('click', () => agregarCargo($('cargosAjuste')));
        $('abrirAbono').addEventListener('click', () => abrirPago('abono', null));
        $('cancelarPago').addEventListener('click', () => { $('panelPago').hidden = true; });
        $('cancelarAjuste').addEventListener('click', () => { $('panelAjuste').hidden = true; });
        $('formPrestamo').addEventListener('submit', event => {
            event.preventDefault();
            procesar(event.target, async () => {
                const result = await api.request('POST', '/prestamos', {
                    nombre: $('nombrePrestamo').value, acreedor: $('acreedorPrestamo').value,
                    capital: $('capitalPrestamo').value, tasa_ea: $('tasaPrestamo').value,
                    numero_cuotas: Number($('numeroCuotas').value), frecuencia: $('frecuenciaPrestamo').value,
                    metodo: $('metodoPrestamo').value, primera_fecha: $('primeraFecha').value,
                    cargos: leerCargos($('cargosIniciales')),
                });
                event.target.reset();
                $('cargosIniciales').replaceChildren();
                $('primeraFecha').value = fechaHoy();
                await cargarLista();
                await cargarDetalle(result.id);
                aviso('Préstamo creado correctamente.', 'success');
            });
        });
        $('formPago').addEventListener('submit', event => {
            event.preventDefault();
            procesar(event.target, async () => {
                await api.request('POST', `/prestamos/${detalle.prestamo.id}/pagos`, {
                    ...pagoActivo, monto: $('montoPago').value, fecha: $('fechaPago').value,
                    id_cuenta: $('cuentaPago').value ? Number($('cuentaPago').value) : null,
                    referencia: referenciaPago,
                });
                await cargarLista();
                await cargarDetalle(detalle.prestamo.id);
                aviso('Pago registrado correctamente.', 'success');
            });
        });
        $('formAjuste').addEventListener('submit', event => {
            event.preventDefault();
            procesar(event.target, async () => {
                await api.request('PUT', `/prestamos/${detalle.prestamo.id}/cuotas/${ajusteActivo}`, {
                    capital: $('capitalAjuste').value, interes: $('interesAjuste').value,
                    cargos: leerCargos($('cargosAjuste')),
                });
                await cargarDetalle(detalle.prestamo.id);
                aviso('Cuota ajustada correctamente.', 'success');
            });
        });
        try {
            await Promise.all([cargarLista(), cargarCuentas()]);
        } catch (error) {
            aviso(error.message);
        }
    });
})();
