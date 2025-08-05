document.getElementById("reembolsoForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const form = e.target;
  const mensajeDiv = document.getElementById("mensaje");
  mensajeDiv.innerText = ""; // Limpiar mensaje anterior

  const archivo = form.archivo.files[0];

  // Recolectar campos
  const campos = {
    nombre: form.nombre.value.trim(),
    cedula: form.cedula.value.trim(),
    departamento: form.departamento.value.trim(),
    correo: form.correo.value.trim(),
    telefono: form.telefono.value.trim(),
    fechaGasto: form.fechaGasto.value,
    tipoGasto: form.tipoGasto.value,
    numeroFactura: form.numeroFactura.value.trim(),
    monto: form.monto.value,
    medioPago: form.medioPago.value,
    descripcion: form.descripcion.value.trim()
  };

  // Validaciones básicas
  const camposIncompletos = Object.values(campos).some(
    val => val === "" || val === null || val === undefined
  );

  if (camposIncompletos || isNaN(parseFloat(campos.monto)) || parseFloat(campos.monto) <= 0 || !archivo) {
    mensajeDiv.innerText = "⚠️ Por favor completa todos los campos y adjunta un archivo válido.";
    return;
  }

  try {
    // Crear FormData y agregar campos individualmente
    const formData = new FormData();
    formData.append("archivo", archivo);

    // Añadir cada campo al FormData con la clave que espera backend
    formData.append("nombre", campos.nombre);
    formData.append("cedula", campos.cedula);
    formData.append("departamento", campos.departamento);
    formData.append("correo", campos.correo);
    formData.append("telefono", campos.telefono);
    formData.append("fechaGasto", campos.fechaGasto);
    formData.append("tipoGasto", campos.tipoGasto);
    formData.append("numeroFactura", campos.numeroFactura);
    formData.append("monto", campos.monto);
    formData.append("medioPago", campos.medioPago);
    formData.append("descripcion", campos.descripcion);

    // Crear objeto JSON para enviar al backend de procesos BPM
    const jsonData = JSON.stringify({
      nombre: campos.nombre,
      cedula: campos.cedula,
      departamento: campos.departamento,
      correo: campos.correo,
      telefono: campos.telefono,
      fechaGasto: campos.fechaGasto,
      tipoGasto: campos.tipoGasto,
      numeroFactura: campos.numeroFactura,
      monto: campos.monto,
      medioPago: campos.medioPago,
      descripcion: campos.descripcion
    });

    // Crear FormData para enviar al backend BPM (FastAPI)
    const bpmFormData = new FormData();
    bpmFormData.append("solicitud", jsonData);
    bpmFormData.append("archivo", archivo);

    // Enviar al backend de procesos BPM (FastAPI)
    const response = await fetch("http://localhost:8000/reembolso", {
      method: "POST",
      body: bpmFormData
    });

    if (response.ok) {
      mensajeDiv.innerText = "✅ Solicitud enviada correctamente.";
      form.reset();
    } else {
      let errorMsg = "❌ Error desconocido.";
      try {
        const errorJson = await response.json();
        errorMsg = errorJson.mensaje || JSON.stringify(errorJson);
      } catch {
        const text = await response.text();
        errorMsg = text || errorMsg;
      }
      mensajeDiv.innerText = errorMsg;
    }
  } catch (error) {
    console.error("❌ Error de red:", error);
    mensajeDiv.innerText = "❌ No se pudo conectar al servidor.";
  }
});
