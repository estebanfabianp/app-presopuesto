-- =================================================================
-- CREACIÓN DE TABLAS DE DOCUMENTACIÓN DEL SISTEMA
-- Proyecto: app-presupuesto
-- Descripción: Tablas para gestión de documentación técnica y arquitectura
-- Propósito: Mantener documentación del sistema en base de datos
-- Versión: 1.0 - Tablas de documentación
-- =================================================================

-- =================================================================
-- TABLA DE DOCUMENTACIÓN TÉCNICA
-- Para mantener documentación técnica en la BD
-- =================================================================

CREATE TABLE IF NOT EXISTS `documentacion_sistema` (
  `id_doc` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID único de documentación',
  `tipo` enum('TABLA','VISTA','PROCEDIMIENTO','FUNCION','TRIGGER','EVENTO') NOT NULL COMMENT 'Tipo de objeto documentado',
  `nombre_objeto` varchar(100) NOT NULL COMMENT 'Nombre del objeto de BD',
  `descripcion_corta` varchar(255) NOT NULL COMMENT 'Descripción breve del propósito',
  `descripcion_larga` text DEFAULT NULL COMMENT 'Documentación detallada',
  `casos_uso` text DEFAULT NULL COMMENT 'Casos de uso principales',
  `ejemplos` text DEFAULT NULL COMMENT 'Ejemplos de consultas o uso',
  `consideraciones` text DEFAULT NULL COMMENT 'Consideraciones especiales',
  `fecha_creacion` datetime NOT NULL DEFAULT current_timestamp() COMMENT 'Fecha de documentación',
  `fecha_actualizacion` datetime DEFAULT NULL ON UPDATE current_timestamp() COMMENT 'Última actualización',
  `version` varchar(20) DEFAULT '1.0' COMMENT 'Versión de la documentación',
  PRIMARY KEY (`id_doc`),
  UNIQUE KEY `uk_doc_objeto` (`tipo`, `nombre_objeto`),
  KEY `idx_doc_tipo` (`tipo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Documentación técnica del sistema de base de datos';

-- =================================================================
-- TABLA DE ARQUITECTURA DEL SISTEMA
-- =================================================================

CREATE TABLE IF NOT EXISTS `arquitectura_sistema` (
  `id_componente` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID único del componente',
  `nombre_componente` varchar(100) NOT NULL COMMENT 'Nombre del componente de arquitectura',
  `tipo_componente` enum('CAPA','MODULO','SERVICIO','INTEGRACION','HERRAMIENTA') NOT NULL COMMENT 'Tipo de componente',
  `descripcion` text NOT NULL COMMENT 'Descripción detallada del componente',
  `dependencias` json COMMENT 'Dependencias con otros componentes',
  `tecnologias` json COMMENT 'Tecnologías utilizadas',
  `responsabilidades` text COMMENT 'Responsabilidades específicas',
  `patrones_aplicados` json COMMENT 'Patrones de diseño aplicados',
  `metricas_rendimiento` json COMMENT 'Métricas de rendimiento esperadas',
  `contacto_responsable` varchar(100) COMMENT 'Responsable del componente',
  `fecha_creacion` datetime NOT NULL DEFAULT current_timestamp(),
  `version` varchar(20) DEFAULT '1.0' COMMENT 'Versión del componente',
  PRIMARY KEY (`id_componente`),
  UNIQUE KEY `uk_componente` (`nombre_componente`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Documentación de arquitectura del sistema';

-- Script completado exitosamente
SELECT 'TABLAS DE DOCUMENTACIÓN CREADAS EXITOSAMENTE' AS resultado;