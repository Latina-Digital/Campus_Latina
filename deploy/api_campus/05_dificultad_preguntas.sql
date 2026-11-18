/* =====================================================================
   CAMPUS LATINA - dificultad de las preguntas de evaluación
   ---------------------------------------------------------------------
   Ejecutar UNA VEZ en SQL Server Management Studio sobre la base CAMPUS.
   Se puede volver a ejecutar sin problema: no repite cambios ni borra datos.

   1. Agrega la columna difficulty a dbo.CV_Preguntas:
        basica  - pregunta normal (así quedan todas las actuales)
        dificil - pregunta de situación o razonamiento
        calculo - operación matemática de aplicación (galones, arena, puntos...)
      Cada intento de evaluación incluye al menos 2 preguntas difíciles y
      1 de cálculo, si el banco las tiene. Se configura en
      Panel > Cursos > Preguntas, al crear o editar cada pregunta.

   2. Marca las preguntas difíciles y de cálculo que ya se cargaron en la
      API (solo si siguen como "basica", para no pisar cambios del Panel).

   La API no necesita cambios: dbo.spCampus_Datos acepta cualquier columna
   que exista en la tabla.
   ===================================================================== */

USE [CAMPUS];
GO

IF COL_LENGTH(N'dbo.CV_Preguntas', N'difficulty') IS NULL
    ALTER TABLE dbo.CV_Preguntas ADD difficulty NVARCHAR(10) NOT NULL
        CONSTRAINT DF_CV_Preguntas_difficulty DEFAULT N'basica';
GO

-- Difíciles: 2 por evaluación (5 en Elastomérico)
UPDATE dbo.CV_Preguntas SET difficulty = N'dificil'
WHERE difficulty = N'basica'
  AND id IN (55, 61,                     -- Cómo usar el Campus Latina
             75, 84,                     -- Satinado
             94, 105,                    -- Ultra Máximo Duralin
             139, 140, 141, 142, 143,    -- Ultra Máximo Elastomérico
             126, 128);                  -- Línea Induless
GO

-- Cálculo: al menos 1 por evaluación (3 en Elastomérico)
UPDATE dbo.CV_Preguntas SET difficulty = N'calculo'
WHERE difficulty = N'basica'
  AND id IN (147,                        -- Cómo usar el Campus Latina (puntos)
             148,                        -- Satinado (galones)
             149,                        -- Ultra Máximo Duralin (galones y agua)
             144, 145, 146,              -- Ultra Máximo Elastomérico (galones y arena)
             150);                       -- Línea Induless (kilos por caja)
GO

SELECT e.course_id, p.difficulty, COUNT(*) AS preguntas
FROM dbo.CV_Preguntas p JOIN dbo.CV_Evaluaciones e ON e.id = p.quiz_id
GROUP BY e.course_id, p.difficulty
ORDER BY e.course_id, p.difficulty;
GO
