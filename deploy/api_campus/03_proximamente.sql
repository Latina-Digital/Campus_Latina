/* =====================================================================
   CAMPUS LATINA - cursos "Próximamente"
   ---------------------------------------------------------------------
   Ejecutar UNA VEZ en SQL Server Management Studio sobre la base CAMPUS,
   ANTES de actualizar el código del campus en el servidor.

   1. Agrega la columna coming_soon a dbo.CV_Cursos. Un curso marcado así
      se ve en el catálogo con la etiqueta "Próximamente", pero nadie
      puede comenzarlo. Se habilita desde Panel > Cursos > Editar,
      desmarcando "Próximamente".
   2. Marca como "Próximamente" los cursos de Elastomérico y Silicón (Induless).

   Se puede volver a ejecutar sin problema: no repite cambios.
   ===================================================================== */

USE [CAMPUS];
GO

IF COL_LENGTH(N'dbo.CV_Cursos', N'coming_soon') IS NULL
    ALTER TABLE dbo.CV_Cursos ADD coming_soon BIT NOT NULL CONSTRAINT DF_CV_Cursos_coming_soon DEFAULT 0;
GO

UPDATE dbo.CV_Cursos
SET coming_soon = 1
WHERE slug IN (N'ultra-maximo-elastomerico-proteccion-contra-agua-y-fisuras',
               N'linea-induless-silicon-induzinc-y-clavos');

SELECT id, title, coming_soon FROM dbo.CV_Cursos ORDER BY id;
GO
