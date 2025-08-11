-- SQL para PostgreSQL: crear BD, tabla e insertar datos
-- Ejecuta este script con psql, por ejemplo:
--   psql -U <usuario> -h <host> -f setup/tabla_programas.sql

-- Crear BD "tech-flow" si no existe (requiere psql; usa \gexec)
SELECT 'CREATE DATABASE "tech-flow"'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'tech-flow')\gexec

-- Conectarse a la BD "tech-flow" (psql)
\connect "tech-flow"

-- Crear tabla si no existe
CREATE TABLE IF NOT EXISTS programas (
  id SERIAL PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  precio FLOAT
);

-- Insertar registros
INSERT INTO programas (nombre, precio) VALUES
  ('Data Engineer', 2100),
  ('Data Architect', 2400),
  ('Data Visualization', 2000),
  ('Marketing Analytics', 2300);


