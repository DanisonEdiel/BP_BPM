document.getElementById("reembolsoForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const form = e.target;
  const mensajeDiv = document.getElementById("mensaje");
  mensajeDiv.innerText = ""; // Limpiar mensaje anterior

  const archivo = form.archivo.files[0];

  // Recolectar y sanitizar campos
  const campos = {
    nombre: form.nombre.value.trim(),
    cedula: form.cedula.value.trim(),
    departamento: form.departamento.value.trim(),
    correo: form.correo.value.trim(),
    telefono: form.telefono.value.trim(),
    fechaGasto: form.fechaGasto.value,
    tipoGasto: form.tipoGasto.value,
    numeroFactura: form.numeroFactura.value.trim(),
    monto: parseFloat(form.monto.value),
    medioPago: form.medioPago.value,
    descripcion: form.descripcion.value.trim()
  };

  // Validaciones básicas
  const camposIncompletos = Object.values(campos).some(
    val => val === "" || val === null || val === undefined
  );

  if (camposIncompletos || isNaN(campos.monto) || campos.monto <= 0 || !archivo) {
    mensajeDiv.innerText = "⚠️ Por favor completa todos los campos y adjunta un archivo válido.";
    return;
  }

  try {
    // ✅ Crear FormData para solicitud tipo multipart/form-data
    const formData = new FormData();
    formData.append("archivo", archivo);
    formData.append("solicitud", JSON.stringify(campos));  // Enviar como string plano, no blob

    // Enviar solicitud al backend
    const response = await fetch("http://localhost:8000/reembolso", {
      method: "POST",
      body: formData
    });

    if (response.ok) {
      mensajeDiv.innerText = "✅ Solicitud enviada correctamente.";
      form.reset();
    } else {
      try {
        const error = await response.json();
        if (Array.isArray(error.detail)) {
          const errores = error.detail
            .map(e => `• ${e.msg} (${e.loc.join(" > ")})`)
            .join("\n");
          mensajeDiv.innerText = "❌ Errores del formulario:\n" + errores;
        } else {
          mensajeDiv.innerText = "❌ Error: " + (error.detail || "Desconocido");
        }
      } catch (errParseo) {
        const textoPlano = await response.text();
        mensajeDiv.innerText = "❌ Error inesperado:\n" + textoPlano;
      }
    }
  } catch (error) {
    console.error("❌ Error de red:", error);
    mensajeDiv.innerText = "❌ No se pudo conectar al servidor.";
  }
});
