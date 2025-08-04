# Usar una imagen base de Node.js oficial
FROM node:20-alpine

# Crear y establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos de dependencias
COPY package*.json ./

# Instalar dependencias
RUN npm install

# Copiar el resto de los archivos de la aplicación
COPY . .

# Exponer el puerto por defecto (puedes cambiarlo si tu app usa otro)
EXPOSE 3000

# Comando para iniciar la aplicación
CMD ["npm", "start"]