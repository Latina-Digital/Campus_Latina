/* =====================================================================
   CAMPUS LATINA - fecha límite de los cursos ("Plazo cerrado")
   ---------------------------------------------------------------------
   Ejecutar UNA VEZ en SQL Server Management Studio sobre la base CAMPUS.
   Se puede volver a ejecutar sin problema: no repite cambios ni borra datos.

   Agrega la columna available_until ("Disponible hasta") a dbo.CV_Cursos.
   Es el último día en que se puede tomar el curso; desde el día siguiente
   el curso se ve con la etiqueta "Plazo cerrado" y nadie puede tomarlo.
   Vacío = sin límite (así quedan todos los cursos actuales).
   Se configura en Panel > Cursos > Datos del curso.

   La API no necesita cambios: dbo.spCampus_Datos acepta cualquier columna
   que exista en la tabla.
   ===================================================================== */

USE [CAMPUS];
GO

IF COL_LENGTH(N'dbo.CV_Cursos', N'available_until') IS NULL
    ALTER TABLE dbo.CV_Cursos ADD available_until DATE NULL;
GO

SELECT id, title, is_published, coming_soon, available_until FROM dbo.CV_Cursos ORDER BY id;
GO
