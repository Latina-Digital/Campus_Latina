/* =====================================================================
   CAMPUS LATINA (versión nueva) - tablas y procedimiento de datos
   ---------------------------------------------------------------------
   Ejecutar en SQL Server Management Studio sobre la base CAMPUS.
   Se puede ejecutar varias veces: no borra datos.

   - Las tablas nuevas llevan el prefijo CV_ (dbo.CV_Cursos, dbo.CV_Modulos, ...)
     para no chocar con las del campus anterior (dbo.Categorias, dbo.Modulos, ...),
     que no se tocan.
   - No hay tabla de usuarios: los usuarios vienen de api/syspro/users.
     Cada registro guarda el usuario de Syspro en la columna "username"
     (igual que UsuarioLogin en dbo.HistorialIntentos), y donde hace falta mostrarlo
     también el nombre y el supervisor.
   - dbo.spCampus_Datos: un solo procedimiento para consultar, crear, modificar
     y eliminar filas de cualquier tabla CV_. No acepta otras tablas.
   - Los nombres de columna son los mismos que usa el campus, así la API
     los devuelve tal cual. Las fechas se guardan en hora UTC.
   ===================================================================== */

USE [CAMPUS];
GO

-- =============================================
-- 1. CATÁLOGO DE PRODUCTOS
-- =============================================
IF OBJECT_ID(N'dbo.CV_LineasProducto', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.CV_LineasProducto (
        id      INT IDENTITY(1,1) PRIMARY KEY,
        name    NVARCHAR(80) NOT NULL CONSTRAINT UQ_CV_LineasProducto_name UNIQUE,
        slug    NVARCHAR(90) NOT NULL CONSTRAINT UQ_CV_LineasProducto_slug UNIQUE,
        icon    NVARCHAR(40) NOT NULL DEFAULT N'package',
        [order] INT NOT NULL DEFAULT 0
    );
END
GO

IF OBJECT_ID(N'dbo.CV_Productos', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.CV_Productos (
        id            INT IDENTITY(1,1) PRIMARY KEY,
        brand         NVARCHAR(20)  NOT NULL DEFAULT N'latina',    -- latina o induless
        line_id       INT NULL REFERENCES dbo.CV_LineasProducto(id) ON DELETE SET NULL,
        name          NVARCHAR(120) NOT NULL,
        slug          NVARCHAR(140) NOT NULL CONSTRAINT UQ_CV_Productos_slug UNIQUE,
        summary       NVARCHAR(220) NOT NULL DEFAULT N'',
        description   NVARCHAR(MAX) NOT NULL DEFAULT N'',
        features      NVARCHAR(MAX) NOT NULL DEFAULT N'',
        uses          NVARCHAR(MAX) NOT NULL DEFAULT N'',
        presentations NVARCHAR(200) NOT NULL DEFAULT N'',
        image         NVARCHAR(255) NOT NULL DEFAULT N'',          -- ruta del archivo en el servidor (media)
        datasheet     NVARCHAR(255) NOT NULL DEFAULT N'',
        is_active     BIT NOT NULL DEFAULT 1,
        [order]       INT NOT NULL DEFAULT 0,
        created_at    DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
    );
END
GO

-- =============================================
-- 2. CURSOS
-- =============================================
IF OBJECT_ID(N'dbo.CV_Categorias', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.CV_Categorias (
        id          INT IDENTITY(1,1) PRIMARY KEY,
        name        NVARCHAR(80)  NOT NULL CONSTRAINT UQ_CV_Categorias_name UNIQUE,
        slug        NVARCHAR(90)  NOT NULL CONSTRAINT UQ_CV_Categorias_slug UNIQUE,
        description NVARCHAR(200) NOT NULL DEFAULT N'',
        icon        NVARCHAR(40)  NOT NULL DEFAULT N'book-open',
        [order]     INT NOT NULL DEFAULT 0
    );
END
GO

IF OBJECT_ID(N'dbo.CV_Cursos', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.CV_Cursos (
        id               INT IDENTITY(1,1) PRIMARY KEY,
        title            NVARCHAR(140) NOT NULL,
        slug             NVARCHAR(160) NOT NULL CONSTRAINT UQ_CV_Cursos_slug UNIQUE,
        brand            NVARCHAR(20)  NOT NULL DEFAULT N'latina',  -- latina, induless, corporativo
        category_id      INT NULL REFERENCES dbo.CV_Categorias(id) ON DELETE SET NULL,
        level            NVARCHAR(20)  NOT NULL DEFAULT N'basico',  -- basico, intermedio, avanzado
        summary          NVARCHAR(240) NOT NULL DEFAULT N'',
        description      NVARCHAR(MAX) NOT NULL DEFAULT N'',
        outcomes         NVARCHAR(MAX) NOT NULL DEFAULT N'',
        cover            NVARCHAR(255) NOT NULL DEFAULT N'',
        instructor_name  NVARCHAR(120) NOT NULL DEFAULT N'Equipo de Capacitación Latina',
        instructor_title NVARCHAR(120) NOT NULL DEFAULT N'Industrial Latina S.A.',
        is_published     BIT NOT NULL DEFAULT 0,
        is_featured      BIT NOT NULL DEFAULT 0,
        is_mandatory     BIT NOT NULL DEFAULT 0,
        coming_soon      BIT NOT NULL DEFAULT 0,  -- "Próximamente": visible pero no se puede tomar
        [order]          INT NOT NULL DEFAULT 0,
        created_at       DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
        updated_at       DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
    );
END
GO

-- Productos relacionados con cada curso
IF OBJECT_ID(N'dbo.CV_CursoProductos', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.CV_CursoProductos (
        id         INT IDENTITY(1,1) PRIMARY KEY,
        course_id  INT NOT NULL REFERENCES dbo.CV_Cursos(id) ON DELETE CASCADE,
        product_id INT NOT NULL REFERENCES dbo.CV_Productos(id) ON DELETE CASCADE,
        CONSTRAINT UQ_CV_CursoProductos UNIQUE (course_id, product_id)
    );
END
GO

-- Cursos guardados por cada usuario
IF OBJECT_ID(N'dbo.CV_CursosGuardados', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.CV_CursosGuardados (
        id        INT IDENTITY(1,1) PRIMARY KEY,
        course_id INT NOT NULL REFERENCES dbo.CV_Cursos(id) ON DELETE CASCADE,
        username  NVARCHAR(150) NOT NULL,
        CONSTRAINT UQ_CV_CursosGuardados UNIQUE (course_id, username)
    );
    CREATE INDEX IX_CV_CursosGuardados_user ON dbo.CV_CursosGuardados(username);
END
GO

IF OBJECT_ID(N'dbo.CV_Modulos', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.CV_Modulos (
        id          INT IDENTITY(1,1) PRIMARY KEY,
        course_id   INT NOT NULL REFERENCES dbo.CV_Cursos(id) ON DELETE CASCADE,
        title       NVARCHAR(140) NOT NULL,
        description NVARCHAR(240) NOT NULL DEFAULT N'',
        [order]     INT NOT NULL DEFAULT 0
    );
    CREATE INDEX IX_CV_Modulos_course ON dbo.CV_Modulos(course_id);
END
GO

IF OBJECT_ID(N'dbo.CV_Lecciones', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.CV_Lecciones (
        id                 INT IDENTITY(1,1) PRIMARY KEY,
        module_id          INT NOT NULL REFERENCES dbo.CV_Modulos(id) ON DELETE CASCADE,
        title              NVARCHAR(160) NOT NULL,
        kind               NVARCHAR(12)  NOT NULL DEFAULT N'lectura',  -- video, youtube, lectura, documento
        [order]            INT NOT NULL DEFAULT 0,
        duration_minutes   INT NOT NULL DEFAULT 5,
        video              NVARCHAR(255) NOT NULL DEFAULT N'',
        youtube_url        NVARCHAR(200) NOT NULL DEFAULT N'',
        document           NVARCHAR(255) NOT NULL DEFAULT N'',
        content            NVARCHAR(MAX) NOT NULL DEFAULT N'',
        require_full_watch BIT NOT NULL DEFAULT 1
    );
    CREATE INDEX IX_CV_Lecciones_module ON dbo.CV_Lecciones(module_id);
END
GO

-- Materiales descargables de cada curso
IF OBJECT_ID(N'dbo.CV_Materiales', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.CV_Materiales (
        id        INT IDENTITY(1,1) PRIMARY KEY,
        course_id INT NOT NULL REFERENCES dbo.CV_Cursos(id) ON DELETE CASCADE,
        title     NVARCHAR(140) NOT NULL,
        [file]    NVARCHAR(255) NOT NULL DEFAULT N'',
        url       NVARCHAR(200) NOT NULL DEFAULT N''
    );
END
GO

-- Una fila por usuario y curso. Guarda también nombre, supervisor y rol del usuario
-- (copiados de Syspro al entrar) para el ranking, "Mi equipo" y los reportes.
-- last_lesson_id no tiene llave foránea: SQL Server no permite dos caminos de
-- borrado en cascada desde CV_Cursos. El campus lo trata como vacío si la
-- lección ya no existe.
IF OBJECT_ID(N'dbo.CV_Inscripciones', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.CV_Inscripciones (
        id             INT IDENTITY(1,1) PRIMARY KEY,
        username       NVARCHAR(150) NOT NULL,
        full_name      NVARCHAR(150) NOT NULL DEFAULT N'',
        supervisor     NVARCHAR(150) NOT NULL DEFAULT N'',
        role           NVARCHAR(20)  NOT NULL DEFAULT N'ejecutivo',
        course_id      INT NOT NULL REFERENCES dbo.CV_Cursos(id) ON DELETE CASCADE,
        created_at     DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
        last_accessed  DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
        last_lesson_id INT NULL,
        completed_at   DATETIME2 NULL,
        CONSTRAINT UQ_CV_Inscripciones UNIQUE (username, course_id)
    );
    CREATE INDEX IX_CV_Inscripciones_course ON dbo.CV_Inscripciones(course_id);
    CREATE INDEX IX_CV_Inscripciones_supervisor ON dbo.CV_Inscripciones(supervisor);
END
GO

IF OBJECT_ID(N'dbo.CV_ProgresoLecciones', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.CV_ProgresoLecciones (
        id                   INT IDENTITY(1,1) PRIMARY KEY,
        username             NVARCHAR(150) NOT NULL,
        lesson_id            INT NOT NULL REFERENCES dbo.CV_Lecciones(id) ON DELETE CASCADE,
        position_seconds     FLOAT NOT NULL DEFAULT 0,
        max_position_seconds FLOAT NOT NULL DEFAULT 0,
        completed_at         DATETIME2 NULL,
        updated_at           DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
        CONSTRAINT UQ_CV_ProgresoLecciones UNIQUE (username, lesson_id)
    );
    CREATE INDEX IX_CV_ProgresoLecciones_lesson ON dbo.CV_ProgresoLecciones(lesson_id);
END
GO

IF OBJECT_ID(N'dbo.CV_Resenas', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.CV_Resenas (
        id         INT IDENTITY(1,1) PRIMARY KEY,
        username   NVARCHAR(150) NOT NULL,
        full_name  NVARCHAR(150) NOT NULL DEFAULT N'',
        course_id  INT NOT NULL REFERENCES dbo.CV_Cursos(id) ON DELETE CASCADE,
        rating     SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
        comment    NVARCHAR(800) NOT NULL DEFAULT N'',
        created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
        CONSTRAINT UQ_CV_Resenas UNIQUE (username, course_id)
    );
END
GO

-- Rutas de aprendizaje
IF OBJECT_ID(N'dbo.CV_Rutas', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.CV_Rutas (
        id           INT IDENTITY(1,1) PRIMARY KEY,
        title        NVARCHAR(140) NOT NULL,
        slug         NVARCHAR(160) NOT NULL CONSTRAINT UQ_CV_Rutas_slug UNIQUE,
        summary      NVARCHAR(240) NOT NULL DEFAULT N'',
        description  NVARCHAR(MAX) NOT NULL DEFAULT N'',
        brand        NVARCHAR(20)  NOT NULL DEFAULT N'latina',
        cover        NVARCHAR(255) NOT NULL DEFAULT N'',
        is_published BIT NOT NULL DEFAULT 1,
        [order]      INT NOT NULL DEFAULT 0,
        created_at   DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
    );
END
GO

IF OBJECT_ID(N'dbo.CV_RutaCursos', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.CV_RutaCursos (
        id        INT IDENTITY(1,1) PRIMARY KEY,
        path_id   INT NOT NULL REFERENCES dbo.CV_Rutas(id) ON DELETE CASCADE,
        course_id INT NOT NULL REFERENCES dbo.CV_Cursos(id) ON DELETE CASCADE,
        [order]   INT NOT NULL DEFAULT 0,
        CONSTRAINT UQ_CV_RutaCursos UNIQUE (path_id, course_id)
    );
END
GO

-- =============================================
-- 3. EVALUACIONES
-- =============================================
IF OBJECT_ID(N'dbo.CV_Evaluaciones', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.CV_Evaluaciones (
        id                    INT IDENTITY(1,1) PRIMARY KEY,
        course_id             INT NOT NULL CONSTRAINT UQ_CV_Evaluaciones_course UNIQUE
                              REFERENCES dbo.CV_Cursos(id) ON DELETE CASCADE,
        title                 NVARCHAR(140) NOT NULL DEFAULT N'Evaluación final',
        instructions          NVARCHAR(MAX) NOT NULL DEFAULT N'',
        time_limit_minutes    INT NOT NULL DEFAULT 10,
        questions_per_attempt INT NOT NULL DEFAULT 10,
        passing_score         INT NOT NULL DEFAULT 70,
        max_attempts          INT NOT NULL DEFAULT 2,          -- 0 = ilimitados
        show_review           BIT NOT NULL DEFAULT 1
    );
END
GO

IF OBJECT_ID(N'dbo.CV_Preguntas', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.CV_Preguntas (
        id          INT IDENTITY(1,1) PRIMARY KEY,
        quiz_id     INT NOT NULL REFERENCES dbo.CV_Evaluaciones(id) ON DELETE CASCADE,
        [text]      NVARCHAR(MAX) NOT NULL,
        explanation NVARCHAR(MAX) NOT NULL DEFAULT N'',
        [order]     INT NOT NULL DEFAULT 0
    );
    CREATE INDEX IX_CV_Preguntas_quiz ON dbo.CV_Preguntas(quiz_id);
END
GO

IF OBJECT_ID(N'dbo.CV_Opciones', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.CV_Opciones (
        id          INT IDENTITY(1,1) PRIMARY KEY,
        question_id INT NOT NULL REFERENCES dbo.CV_Preguntas(id) ON DELETE CASCADE,
        [text]      NVARCHAR(400) NOT NULL,
        is_correct  BIT NOT NULL DEFAULT 0,
        [order]     INT NOT NULL DEFAULT 0
    );
    CREATE INDEX IX_CV_Opciones_question ON dbo.CV_Opciones(question_id);
END
GO

-- question_ids, choice_order y answers guardan texto JSON.
IF OBJECT_ID(N'dbo.CV_Intentos', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.CV_Intentos (
        id                 INT IDENTITY(1,1) PRIMARY KEY,
        username           NVARCHAR(150) NOT NULL,
        quiz_id            INT NOT NULL REFERENCES dbo.CV_Evaluaciones(id) ON DELETE CASCADE,
        started_at         DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
        finished_at        DATETIME2 NULL,
        time_limit_minutes INT NOT NULL DEFAULT 10,
        passing_score      INT NOT NULL DEFAULT 70,
        question_ids       NVARCHAR(MAX) NOT NULL DEFAULT N'[]',
        choice_order       NVARCHAR(MAX) NOT NULL DEFAULT N'{}',
        answers            NVARCHAR(MAX) NOT NULL DEFAULT N'{}',
        score              INT NULL,
        correct_count      INT NOT NULL DEFAULT 0,
        total              INT NOT NULL DEFAULT 0,
        passed             BIT NOT NULL DEFAULT 0,
        timed_out          BIT NOT NULL DEFAULT 0
    );
    CREATE INDEX IX_CV_Intentos_user ON dbo.CV_Intentos(username);
    CREATE INDEX IX_CV_Intentos_quiz ON dbo.CV_Intentos(quiz_id);
END
GO

-- =============================================
-- 4. CERTIFICADOS Y ANUNCIOS
-- =============================================
-- attempt_id no tiene llave foránea por la misma razón que last_lesson_id.
IF OBJECT_ID(N'dbo.CV_Certificados', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.CV_Certificados (
        id           INT IDENTITY(1,1) PRIMARY KEY,
        username     NVARCHAR(150) NOT NULL,
        course_id    INT NOT NULL REFERENCES dbo.CV_Cursos(id) ON DELETE CASCADE,
        code         NVARCHAR(24)  NOT NULL CONSTRAINT UQ_CV_Certificados_code UNIQUE,
        issued_at    DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
        score        INT NULL,
        hours        DECIMAL(5,1) NOT NULL DEFAULT 1,
        attempt_id   INT NULL,
        holder_name  NVARCHAR(160) NOT NULL,
        course_title NVARCHAR(160) NOT NULL,
        is_revoked   BIT NOT NULL DEFAULT 0,
        CONSTRAINT UQ_CV_Certificados UNIQUE (username, course_id)
    );
END
GO

IF OBJECT_ID(N'dbo.CV_Anuncios', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.CV_Anuncios (
        id         INT IDENTITY(1,1) PRIMARY KEY,
        title      NVARCHAR(140) NOT NULL,
        body       NVARCHAR(600) NOT NULL,
        tone       NVARCHAR(10)  NOT NULL DEFAULT N'info',     -- info, nuevo, urgente
        link_url   NVARCHAR(300) NOT NULL DEFAULT N'',
        link_label NVARCHAR(40)  NOT NULL DEFAULT N'Ver más',
        is_active  BIT NOT NULL DEFAULT 1,
        created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
    );
END
GO

-- =============================================
-- 5. PROCEDIMIENTO DE DATOS
-- =============================================
/*
   @Accion  CONSULTAR | CREAR | MODIFICAR | ELIMINAR
   @Tabla   nombre de la tabla SIN el prefijo CV_ (ej: 'Cursos' -> dbo.CV_Cursos)
   @Id      id de la fila (MODIFICAR lo exige; CONSULTAR y ELIMINAR lo aceptan)
   @Filtro  JSON con condiciones "columna = valor", unidas con AND:
              {"username": "XBRIONES"}   columna = valor
              {"id": [1, 2, 3]}          columna IN (1, 2, 3)
              {"completed_at": null}     columna IS NULL
   @Datos   JSON con los valores a guardar: {"title": "Duralin", "is_published": true}

   Devuelve siempre filas:
     CONSULTAR  las filas encontradas (ordenadas por id)
     CREAR      la fila creada, con su id
     MODIFICAR  la fila modificada
     ELIMINAR   los id eliminados

   Seguridad: solo trabaja con tablas dbo.CV_*. Los nombres de tabla y columna
   se validan contra el catálogo de SQL Server y los valores viajan como
   parámetros, nunca se pegan dentro del SQL.
*/
CREATE OR ALTER PROCEDURE dbo.spCampus_Datos
    @Accion VARCHAR(20)   = 'CONSULTAR',
    @Tabla  NVARCHAR(120) = N'',
    @Id     INT           = 0,
    @Filtro NVARCHAR(MAX) = NULL,
    @Datos  NVARCHAR(MAX) = NULL
WITH EXECUTE AS OWNER
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @t     NVARCHAR(300) = N'dbo.' + QUOTENAME(N'CV_' + @Tabla);
    DECLARE @obj   INT = OBJECT_ID(@t, N'U');
    DECLARE @where NVARCHAR(MAX) = N'';
    DECLARE @cols  NVARCHAR(MAX) = N'';
    DECLARE @vals  NVARCHAR(MAX) = N'';
    DECLARE @set   NVARCHAR(MAX) = N'';
    DECLARE @sql   NVARCHAR(MAX);
    DECLARE @malo  NVARCHAR(4000);
    DECLARE @msg   NVARCHAR(4000);

    IF @obj IS NULL
        THROW 50001, N'Tabla no permitida.', 1;

    IF @Filtro = N'' SET @Filtro = NULL;
    IF @Datos  = N'' SET @Datos  = NULL;
    IF @Filtro IS NOT NULL AND ISJSON(@Filtro) = 0
        THROW 50002, N'Filtro no es un JSON válido.', 1;
    IF @Datos IS NOT NULL AND ISJSON(@Datos) = 0
        THROW 50003, N'Datos no es un JSON válido.', 1;

    -- Toda clave del filtro debe ser una columna real (si no, un error de escritura
    -- haría que la condición se ignore y se afecten más filas de las esperadas).
    SELECT TOP (1) @malo = f.[key]
    FROM OPENJSON(@Filtro) f
    WHERE NOT EXISTS (SELECT 1 FROM sys.columns c
                      WHERE c.object_id = @obj AND c.name COLLATE Latin1_General_BIN2 = f.[key]);
    IF @malo IS NOT NULL
    BEGIN
        SET @msg = N'Columna desconocida en Filtro: ' + @malo;
        THROW 50004, @msg, 1;
    END

    -- En Datos tampoco se aceptan el id ni columnas inexistentes.
    SELECT TOP (1) @malo = f.[key]
    FROM OPENJSON(@Datos) f
    WHERE NOT EXISTS (SELECT 1 FROM sys.columns c
                      WHERE c.object_id = @obj AND c.name COLLATE Latin1_General_BIN2 = f.[key]
                        AND c.is_identity = 0 AND c.is_computed = 0);
    IF @malo IS NOT NULL
    BEGIN
        SET @msg = N'Columna no válida en Datos: ' + @malo;
        THROW 50005, @msg, 1;
    END

    -- Condiciones: los valores se leen de @Filtro dentro del SQL dinámico.
    IF @Id <> 0
        SET @where = N' AND [id] = @Id';

    SELECT @where = @where + N' AND ' + QUOTENAME(c.name) +
        CASE f.[type]
            WHEN 0 THEN N' IS NULL'
            WHEN 4 THEN N' IN (SELECT [value] COLLATE DATABASE_DEFAULT FROM OPENJSON(@Filtro, N''$."'
                        + REPLACE(c.name, N'''', N'''''') + N'"''))'
            ELSE N' = (SELECT [value] COLLATE DATABASE_DEFAULT FROM OPENJSON(@Filtro) WHERE [key] = N'''
                        + REPLACE(c.name, N'''', N'''''') + N''')'
        END
    FROM OPENJSON(@Filtro) f
    JOIN sys.columns c ON c.object_id = @obj AND c.name COLLATE Latin1_General_BIN2 = f.[key];

    IF @Accion = 'CONSULTAR'
    BEGIN
        SET @sql = N'SELECT * FROM ' + @t + N' WHERE 1 = 1' + @where + N' ORDER BY [id];';
    END
    ELSE IF @Accion = 'CREAR'
    BEGIN
        SELECT @cols = @cols + N', ' + QUOTENAME(c.name),
               @vals = @vals + N', ' +
                   CASE WHEN f.[type] = 0 THEN N'NULL'
                        ELSE N'(SELECT [value] FROM OPENJSON(@Datos) WHERE [key] = N'''
                             + REPLACE(c.name, N'''', N'''''') + N''')'
                   END
        FROM OPENJSON(@Datos) f
        JOIN sys.columns c ON c.object_id = @obj AND c.name COLLATE Latin1_General_BIN2 = f.[key];

        IF @cols = N''
            SET @sql = N'INSERT INTO ' + @t + N' OUTPUT INSERTED.* DEFAULT VALUES;';
        ELSE
            SET @sql = N'INSERT INTO ' + @t + N' (' + STUFF(@cols, 1, 2, N'') + N') OUTPUT INSERTED.* SELECT '
                     + STUFF(@vals, 1, 2, N'') + N';';
    END
    ELSE IF @Accion = 'MODIFICAR'
    BEGIN
        IF @Id = 0
            THROW 50006, N'MODIFICAR requiere @Id.', 1;

        SELECT @set = @set + N', ' + QUOTENAME(c.name) + N' = ' +
                   CASE WHEN f.[type] = 0 THEN N'NULL'
                        ELSE N'(SELECT [value] FROM OPENJSON(@Datos) WHERE [key] = N'''
                             + REPLACE(c.name, N'''', N'''''') + N''')'
                   END
        FROM OPENJSON(@Datos) f
        JOIN sys.columns c ON c.object_id = @obj AND c.name COLLATE Latin1_General_BIN2 = f.[key];

        IF @set = N''
            THROW 50007, N'MODIFICAR requiere @Datos.', 1;

        SET @sql = N'UPDATE ' + @t + N' SET ' + STUFF(@set, 1, 2, N'') + N' OUTPUT INSERTED.* WHERE [id] = @Id;';
    END
    ELSE IF @Accion = 'ELIMINAR'
    BEGIN
        -- Sin Id ni Filtro se borraría toda la tabla: no se permite.
        IF @where = N''
            THROW 50008, N'ELIMINAR requiere @Id o @Filtro.', 1;

        SET @sql = N'DELETE FROM ' + @t + N' OUTPUT DELETED.[id] WHERE 1 = 1' + @where + N';';
    END
    ELSE
    BEGIN
        SET @msg = N'Accion no válida: ' + ISNULL(@Accion, N'(vacía)');
        THROW 50009, @msg, 1;
    END

    EXEC sys.sp_executesql @sql,
        N'@Id INT, @Filtro NVARCHAR(MAX), @Datos NVARCHAR(MAX)',
        @Id = @Id, @Filtro = @Filtro, @Datos = @Datos;
END
GO
