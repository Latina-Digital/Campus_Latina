/* =====================================================================
   CAMPUS LATINA - actualización de octubre 2026
   ---------------------------------------------------------------------
   Ejecutar UNA VEZ en SQL Server Management Studio sobre la base CAMPUS,
   ANTES (o justo después) de publicar el código nuevo del campus.
   Se puede volver a ejecutar sin problema: no repite cambios ni borra datos.

   1. Agrega la columna coming_soon a dbo.CV_Cursos. Un curso marcado así se
      ve en el catálogo en gris con la etiqueta "Próximamente", pero nadie
      puede comenzarlo. Se cambia desde Panel > Cursos > "Marcar Próximamente"
      o "Habilitar curso".
   2. Deja los cursos como en la versión probada:
      - Elastomérico y Línea Induless (Silicón): publicados y "Próximamente".
   3. Evaluaciones: 10 minutos y 2 intentos (los nuevos cursos también usan
      2 intentos por defecto).

   La API no necesita cambios: dbo.spCampus_Datos acepta cualquier columna
   que exista en la tabla.
   ===================================================================== */

USE [CAMPUS];
GO

SET NOCOUNT ON;

-- 1. Columna "Próximamente"
IF COL_LENGTH(N'dbo.CV_Cursos', N'coming_soon') IS NULL
    ALTER TABLE dbo.CV_Cursos ADD coming_soon BIT NOT NULL CONSTRAINT DF_CV_Cursos_coming_soon DEFAULT 0;
GO

-- 2. Cursos próximamente (y publicados, para que se vean en el catálogo)
UPDATE dbo.CV_Cursos
SET coming_soon = 1, is_published = 1, updated_at = SYSUTCDATETIME()
WHERE slug IN (N'ultra-maximo-elastomerico-proteccion-contra-agua-y-fisuras',
               N'linea-induless-silicon-induzinc-y-clavos');

-- 3. Evaluaciones: 10 minutos y 2 intentos
UPDATE dbo.CV_Evaluaciones
SET time_limit_minutes = 10, max_attempts = 2
WHERE time_limit_minutes <> 10 OR max_attempts <> 2;

-- Valor por defecto de intentos para evaluaciones nuevas: 2
DECLARE @df sysname = (
    SELECT dc.name FROM sys.default_constraints dc
    JOIN sys.columns c ON c.object_id = dc.parent_object_id AND c.column_id = dc.parent_column_id
    WHERE dc.parent_object_id = OBJECT_ID(N'dbo.CV_Evaluaciones') AND c.name = N'max_attempts');
IF @df IS NOT NULL
    EXEC (N'ALTER TABLE dbo.CV_Evaluaciones DROP CONSTRAINT ' + QUOTENAME(@df));
ALTER TABLE dbo.CV_Evaluaciones ADD CONSTRAINT DF_CV_Evaluaciones_max_attempts DEFAULT 2 FOR max_attempts;
GO

-- Resultado
SELECT id, title, is_published, coming_soon FROM dbo.CV_Cursos ORDER BY id;
SELECT id, course_id, time_limit_minutes, max_attempts FROM dbo.CV_Evaluaciones ORDER BY id;
GO
