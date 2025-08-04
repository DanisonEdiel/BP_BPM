const express = require("express");
const cors = require("cors");
const multer = require("multer");
const path = require("path");
const fs = require("fs");
const { Pool } = require("pg");

const app = express();
const PORT = 3000;

// Permitir peticiones cross-origin (si hace falta)
app.use(cors());

// Crear carpeta para uploads si no existe
const UPLOADS_DIR = path.join(__dirname, "uploads");
if (!fs.existsSync(UPLOADS_DIR)) fs.mkdirSync(UPLOADS_DIR);

// Config multer para recibir archivo (pdf, jpg, png)
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, UPLOADS_DIR),
  filename: (req, file, cb) => {
    // timestamp + nombre original para evitar colisiones
    cb(null, Date.now() + "_" + file.originalname);
  }
});
const upload = multer({ storage });

// Configuración conexión a PostgreSQL
const pool = new Pool({
  user: "postgres",
  host: "localhost",
  database: "reembolsos",
  password: "example",
  port: 5435,
});

// Crear tabla si no existe (solo al iniciar)
const createTable = async () => {
  const query = `
  CREATE TABLE IF NOT EXISTS reembolsos (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    cedula TEXT NOT NULL,
    departamento TEXT NOT NULL,
    correo TEXT NOT NULL,
    telefono TEXT,
    fecha_gasto DATE NOT NULL,
    tipo_gasto TEXT NOT NULL,
    numero_factura TEXT NOT NULL,
    monto NUMERIC(10,2) NOT NULL,
    medio_pago TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    archivo TEXT NOT NULL,
    aprobado BOOLEAN DEFAULT true,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );
  `;
  await pool.query(query);
};
createTable().catch(console.error);

// Endpoint que recibe formulario (UiPath lo enviará aquí)
app.post("/api/reembolsos-aprobados", upload.single("archivo"), async (req, res) => {
  try {
    const {
      nombre,
      cedula,
      departamento,
      correo,
      telefono,
      fechaGasto,
      tipoGasto,
      numeroFactura,
      monto,
      medioPago,
      descripcion
    } = req.body;

    if (!req.file) {
      return res.status(400).json({ mensaje: "El archivo es obligatorio." });
    }

    const archivo = req.file.filename;

    const insertQuery = `
      INSERT INTO reembolsos (
        nombre, cedula, departamento, correo, telefono,
        fecha_gasto, tipo_gasto, numero_factura, monto,
        medio_pago, descripcion, archivo, aprobado
      ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13)
      RETURNING id
    `;

    const values = [
      nombre, cedula, departamento, correo, telefono || null,
      fechaGasto, tipoGasto, numeroFactura, parseFloat(monto),
      medioPago, descripcion, archivo, true
    ];

    const result = await pool.query(insertQuery, values);

    res.status(200).json({
      mensaje: "Reembolso aprobado registrado correctamente",
      id: result.rows[0].id
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ mensaje: "Error al registrar el reembolso." });
  }
});

// Servir archivos estáticos para acceder a facturas subidas (opcional)
app.use("/uploads", express.static(UPLOADS_DIR));

// Iniciar servidor
app.listen(PORT, () => {
  console.log(`API corriendo en http://localhost:${PORT}`);
});
