const express = require("express");
const cors = require("cors");
const multer = require("multer");
const path = require("path");
const fs = require("fs");
const sqlite3 = require("sqlite3").verbose();

const app = express();
const PORT = 3000;

// Permitir peticiones cross-origin
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

// Configuración de SQLite
const DB_PATH = path.join(__dirname, "reembolsos.db");
const db = new sqlite3.Database(DB_PATH, (err) => {
  if (err) {
    console.error("Error al conectar a la base de datos SQLite:", err.message);
  } else {
    console.log("Conectado a la base de datos SQLite");
  }
});

// Crear tabla si no existe (solo al iniciar)
db.run(`
  CREATE TABLE IF NOT EXISTS reembolsos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    cedula TEXT NOT NULL,
    departamento TEXT NOT NULL,
    correo TEXT NOT NULL,
    telefono TEXT,
    fecha_gasto TEXT NOT NULL,
    tipo_gasto TEXT NOT NULL,
    numero_factura TEXT NOT NULL,
    monto REAL NOT NULL,
    medio_pago TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    archivo TEXT NOT NULL,
    aprobado INTEGER DEFAULT 1,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  )
`, (err) => {
  if (err) {
    console.error("Error al crear tabla:", err.message);
  } else {
    console.log("Tabla de reembolsos creada o ya existente");
  }
});

// Endpoint que recibe formulario
app.post("/api/reembolsos-aprobados", upload.single("archivo"), (req, res) => {
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
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `;

    const values = [
      nombre, cedula, departamento, correo, telefono || null,
      fechaGasto, tipoGasto, numeroFactura, parseFloat(monto),
      medioPago, descripcion, archivo, 1
    ];

    db.run(insertQuery, values, function(err) {
      if (err) {
        console.error("Error al insertar reembolso:", err.message);
        return res.status(500).json({ mensaje: "Error al registrar el reembolso." });
      }
      
      res.status(200).json({
        mensaje: "Reembolso aprobado registrado correctamente",
        id: this.lastID
      });
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ mensaje: "Error al registrar el reembolso." });
  }
});

// Endpoint para obtener todos los reembolsos
app.get("/api/reembolsos", (req, res) => {
  db.all("SELECT * FROM reembolsos ORDER BY fecha_registro DESC", [], (err, rows) => {
    if (err) {
      console.error(err);
      return res.status(500).json({ mensaje: "Error al obtener reembolsos" });
    }
    res.json(rows);
  });
});

// Servir archivos estáticos para acceder a facturas subidas
app.use("/uploads", express.static(UPLOADS_DIR));

// Iniciar servidor
app.listen(PORT, () => {
  console.log(`API SQLite corriendo en http://localhost:${PORT}`);
});
