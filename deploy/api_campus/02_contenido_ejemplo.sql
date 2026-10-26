/* =====================================================================
   CAMPUS LATINA - contenido de ejemplo
   ---------------------------------------------------------------------
   Ejecutar en SQL Server Management Studio sobre la base CAMPUS,
   DESPUÉS de 01_campus_nuevo.sql.

   Carga 6 cursos con lecciones y evaluaciones, 8 productos, 3 rutas de
   aprendizaje y un anuncio de bienvenida:
     LineasProducto        6 filas
     Productos             8 filas
     Categorias            8 filas
     Cursos                6 filas
     CursoProductos        9 filas
     Modulos              12 filas
     Lecciones            18 filas
     Rutas                 3 filas
     RutaCursos            7 filas
     Evaluaciones          6 filas
     Preguntas            40 filas
     Opciones            160 filas
     Anuncios              1 filas

   - Solo se ejecuta si las tablas del campus están vacías (no duplica nada).
   - Todo va en una transacción: si algo falla, no queda nada a medias.
   - Las portadas y fotos de producto son archivos: copiar la carpeta
     deploy\api_campus\media_ejemplo\ dentro de la carpeta media\ del campus.
   - Después, reiniciar el sitio del campus para que cargue los datos.

   Revisar los textos con las fichas técnicas oficiales antes de publicarlos.
   Generado a partir de apps/core/seed_data.py.
   ===================================================================== */

USE [CAMPUS];
GO

SET NOCOUNT ON;
SET XACT_ABORT ON;

IF EXISTS (SELECT 1 FROM dbo.CV_Cursos) OR EXISTS (SELECT 1 FROM dbo.CV_Productos)
   OR EXISTS (SELECT 1 FROM dbo.CV_Categorias) OR EXISTS (SELECT 1 FROM dbo.CV_LineasProducto)
   OR EXISTS (SELECT 1 FROM dbo.CV_Rutas) OR EXISTS (SELECT 1 FROM dbo.CV_Anuncios)
BEGIN
    RAISERROR(N'Las tablas del campus ya tienen datos: no se carga el contenido de ejemplo.', 16, 1);
    RETURN;
END

BEGIN TRANSACTION;

    -- LineasProducto: 6
    SET IDENTITY_INSERT dbo.CV_LineasProducto ON;
    INSERT INTO dbo.CV_LineasProducto ([id], [name], [slug], [icon], [order]) VALUES
        (1, N'Pinturas', N'pinturas', N'paint-bucket', 0),
        (2, N'Empastes', N'empastes', N'layers', 1),
        (3, N'Selladores', N'selladores', N'shield-check', 2),
        (4, N'Siliconas', N'siliconas', N'droplets', 3),
        (5, N'Cubiertas', N'cubiertas', N'house', 4),
        (6, N'Clavos y fijaciones', N'clavos-y-fijaciones', N'hammer', 5);
    SET IDENTITY_INSERT dbo.CV_LineasProducto OFF;

    -- Productos: 8
    SET IDENTITY_INSERT dbo.CV_Productos ON;
    INSERT INTO dbo.CV_Productos ([id], [brand], [line_id], [name], [slug], [summary], [description], [features], [uses], [presentations], [image], [datasheet], [is_active], [order], [created_at]) VALUES
        (1, N'latina', 1, N'Duralin Premium Forte', N'duralin-premium-forte', N'Pintura de alto cubrimiento y acabado fino. Mate, lavable, para interiores y exteriores.', N'Pintura látex de calidad Tipo 1 con acabado mate. Su gran poder cubriente y su lavabilidad la hacen ideal para proyectos residenciales y comerciales.', N'Máximo cubrimiento
Alto rendimiento
Acabado profesional mate
Altamente lavable
Calidad Tipo 1', N'Paredes interiores y exteriores
Tumbados (disimula imperfecciones)
Proyectos residenciales y comerciales', N'Galón · Caneca', N'products/duralin.jpg', N'', 1, 0, N'2026-10-24T13:57:44.358808'),
        (2, N'latina', 1, N'Satinado Latina', N'satinado-latina', N'Acabado fino y especial con un ligero brillo que facilita la limpieza.', N'Pintura de acabado satinado para espacios que se limpian con frecuencia y donde se busca un aspecto elegante.', N'Acabado satinado elegante
Fácil de limpiar
Resistente al uso diario', N'Cocinas y baños
Pasillos y áreas de alto tránsito
Puertas y molduras', N'Galón · Caneca', N'products/satinado.jpg', N'', 1, 1, N'2026-10-24T13:57:44.425823'),
        (3, N'latina', 1, N'Elastomérico Latina', N'elastomerico-latina', N'Recubrimiento acrílico hidrorepelente y flexible para fachadas y techos.', N'Recubrimiento elastomérico que forma una película flexible capaz de acompañar los movimientos de la superficie y repeler el agua de lluvia.', N'Hidrorepelente
Flexible
Recubrimiento acrílico
Puentea microfisuras', N'Fachadas expuestas a lluvia
Losas y techos
Paredes con microfisuras', N'Galón · Caneca', N'products/elastomerico.jpg', N'', 1, 2, N'2026-10-24T13:57:44.481310'),
        (4, N'induless', 4, N'Silicón Induless', N'silicon-induless', N'Silicón para sellar juntas en vidrio, aluminio, cerámica y baños.', N'Sellador de silicón en cartucho para aplicar con pistola. Forma un cordón flexible y duradero.', N'Cordón flexible
Adhiere a superficies no porosas
Práctico cartucho para pistola', N'Ventanas y vidrios
Juntas de baños y cocinas
Sellado de canaletas y uniones', N'Cartucho', N'products/silicon.jpg', N'', 1, 3, N'2026-10-24T13:57:44.527807'),
        (5, N'induless', 5, N'Induzinc', N'induzinc', N'Planchas onduladas de acero galvanizado para cubiertas livianas y resistentes.', N'Cubierta metálica ondulada con recubrimiento de zinc que protege el acero frente a la corrosión.', N'Acero galvanizado
Liviana y resistente
Instalación rápida', N'Techos de viviendas
Galpones y bodegas
Cubiertas de patios y parqueaderos', N'Planchas en varias longitudes', N'products/induzinc.jpg', N'', 1, 4, N'2026-10-24T13:57:44.583133'),
        (6, N'induless', 6, N'Clavos Induless', N'clavos-induless', N'Clavos para construcción y carpintería en distintas medidas.', N'Clavos de acero para trabajos de construcción, encofrado y carpintería.', N'Acero de calidad
Variedad de medidas
Caja práctica', N'Encofrados
Carpintería
Fijación de cubiertas (con arandela)', N'Caja', N'products/clavos.jpg', N'', 1, 5, N'2026-10-24T13:57:44.624644'),
        (7, N'latina', 2, N'Empaste Latina', N'empaste-latina', N'Empaste para nivelar y alisar paredes antes de pintar.', N'Pasta para corregir imperfecciones y dejar la superficie lisa y uniforme.', N'Fácil de lijar
Buena adherencia
Acabado liso', N'Paredes interiores
Corrección de imperfecciones', N'Galón · Caneca', N'', N'', 1, 6, N'2026-10-24T13:57:44.631234'),
        (8, N'latina', 3, N'Sellador Acrílico Latina', N'sellador-acrilico-latina', N'Sellador para preparar superficies nuevas y mejorar el rendimiento de la pintura.', N'Sella la porosidad del enlucido, uniformiza la absorción y mejora la adherencia y el rendimiento de la pintura.', N'Sella la porosidad
Mejora la adherencia
Ahorra pintura', N'Enlucidos nuevos (después del curado)
Superficies porosas', N'Galón · Caneca', N'', N'', 1, 7, N'2026-10-24T13:57:44.641682');
    SET IDENTITY_INSERT dbo.CV_Productos OFF;

    -- Categorias: 8
    SET IDENTITY_INSERT dbo.CV_Categorias ON;
    INSERT INTO dbo.CV_Categorias ([id], [name], [slug], [description], [icon], [order]) VALUES
        (1, N'Pinturas y Acabados', N'pinturas-y-acabados', N'Látex, satinados y recubrimientos para interiores y exteriores.', N'paint-bucket', 0),
        (2, N'Empastes', N'empastes', N'Preparación y nivelación de superficies.', N'layers', 1),
        (3, N'Preparación / Selladores', N'preparacion-selladores', N'Selladores e imprimantes para que la pintura dure.', N'shield-check', 2),
        (4, N'Morteros y Adhesivos', N'morteros-y-adhesivos', N'Pegado de cerámica y reparaciones.', N'brick-wall', 3),
        (5, N'Siliconas', N'siliconas', N'Sellado de juntas, ventanas y baños.', N'droplets', 4),
        (6, N'Techos y Cubiertas', N'techos-y-cubiertas', N'Cubiertas metálicas y su instalación.', N'house', 5),
        (7, N'Clavos y Fijaciones', N'clavos-y-fijaciones', N'Fijación correcta para cada material.', N'hammer', 6),
        (8, N'Habilidades Comerciales', N'habilidades-comerciales', N'Técnicas de venta y atención al cliente.', N'handshake', 7);
    SET IDENTITY_INSERT dbo.CV_Categorias OFF;

    -- Cursos: 6
    SET IDENTITY_INSERT dbo.CV_Cursos ON;
    INSERT INTO dbo.CV_Cursos ([id], [title], [slug], [brand], [category_id], [level], [summary], [description], [outcomes], [cover], [instructor_name], [instructor_title], [is_published], [is_featured], [is_mandatory], [order], [created_at], [updated_at]) VALUES
        (1, N'Duralin Premium Forte: la pintura mate Tipo 1', N'duralin-premium-forte-la-pintura-mate-tipo-1', N'latina', 1, N'basico', N'Conoce a fondo Duralin Premium Forte, cuándo recomendar un acabado mate y cómo preparar la superficie para que la pintura dure.', N'Este curso te prepara para asesorar a tus clientes sobre Duralin Premium Forte, nuestra pintura de calidad Tipo 1 con acabado mate.

Aprenderás la diferencia entre acabados satinado y mate, las características que hacen única a Duralin y el proceso correcto de preparación de superficies.', N'Diferenciar un acabado satinado de uno mate
Explicar por qué Duralin Premium Forte es calidad Tipo 1
Recomendar el producto según el ambiente y la superficie
Guiar al cliente en la preparación correcta de la pared', N'courses/covers/cover-1.jpg', N'Equipo de Capacitación Latina', N'Industrial Latina S.A.', 1, 1, 1, 0, N'2026-10-24T13:57:44.713993', N'2026-10-24T13:57:44.714006'),
        (2, N'Satinado Latina: acabado fino y especial', N'satinado-latina-acabado-fino-y-especial', N'latina', 1, N'basico', N'Aprende cuándo recomendar un acabado satinado y cómo aplicarlo para lograr un resultado elegante y fácil de limpiar.', N'El acabado satinado combina elegancia y practicidad. En este curso verás sus ventajas, en qué espacios conviene y los cuidados para aplicarlo sin marcas.', N'Identificar los espacios ideales para un acabado satinado
Explicar sus ventajas de limpieza
Prevenir marcas y empalmes durante la aplicación
Preparar la superficie para un brillo uniforme', N'courses/covers/cover-2.jpg', N'Equipo de Capacitación Latina', N'Industrial Latina S.A.', 1, 1, 0, 1, N'2026-10-24T13:57:45.261586', N'2026-10-24T13:57:45.261607'),
        (3, N'Elastomérico: protección hidrorepelente para fachadas y techos', N'elastomerico-proteccion-hidrorepelente-para-fachadas-y-techos', N'latina', 1, N'intermedio', N'Entiende cómo funciona un recubrimiento elastomérico y cómo asesorar a tus clientes en la protección de fachadas y techos.', N'Los recubrimientos elastoméricos protegen superficies expuestas a la lluvia y a cambios de temperatura. Aprende sus ventajas y su correcta aplicación.', N'Explicar qué es un recubrimiento elastomérico
Diferenciarlo de una pintura convencional
Recomendarlo para fachadas, losas y techos
Guiar una aplicación por capas', N'courses/covers/cover-3.jpg', N'Equipo de Capacitación Latina', N'Industrial Latina S.A.', 1, 0, 0, 2, N'2026-10-24T13:57:45.650173', N'2026-10-24T13:57:45.650186'),
        (4, N'Siliconas Induless: sellado profesional', N'siliconas-induless-sellado-profesional', N'induless', 5, N'basico', N'Aprende a recomendar y aplicar silicón Induless para lograr juntas limpias, flexibles y duraderas.', N'El sellado de juntas es una de las consultas más frecuentes en ferretería. Este curso te enseña a orientar al cliente y a explicar la aplicación paso a paso.', N'Identificar los usos más comunes del silicón
Explicar la preparación de la junta
Guiar la aplicación de un cordón continuo
Evitar los errores más frecuentes', N'courses/covers/cover-4.jpg', N'Equipo de Capacitación Latina', N'Industrial Latina S.A.', 1, 1, 0, 3, N'2026-10-24T13:57:45.994033', N'2026-10-24T13:57:45.994045'),
        (5, N'Induzinc: cubiertas metálicas e instalación', N'induzinc-cubiertas-metalicas-e-instalacion', N'induless', 6, N'intermedio', N'Conoce las planchas Induzinc de acero galvanizado y las buenas prácticas de instalación que debes explicar al cliente.', N'Las cubiertas metálicas son una solución liviana y rápida. Aprende sus ventajas y los puntos clave de una instalación correcta.', N'Explicar qué es el acero galvanizado
Describir las ventajas de una cubierta metálica
Indicar dónde y cómo fijar las planchas
Recomendar accesorios complementarios', N'courses/covers/cover-5.jpg', N'Equipo de Capacitación Latina', N'Industrial Latina S.A.', 1, 0, 0, 4, N'2026-10-24T13:57:46.328531', N'2026-10-24T13:57:46.328551'),
        (6, N'Venta consultiva en el punto de venta', N'venta-consultiva-en-el-punto-de-venta', N'corporativo', 8, N'basico', N'Técnicas prácticas para descubrir necesidades, convertir características en beneficios y cerrar más ventas en ferreterías y distribuidores.', N'Vender no es recitar características: es entender el problema del cliente y ofrecerle la mejor solución. Este curso te da herramientas simples para hacerlo todos los días.', N'Hacer preguntas que descubren la necesidad real
Transformar características en beneficios
Responder objeciones de precio
Aumentar el ticket con venta cruzada', N'courses/covers/cover-6.jpg', N'Equipo de Capacitación Latina', N'Industrial Latina S.A.', 1, 1, 0, 5, N'2026-10-24T13:57:46.647405', N'2026-10-24T13:57:46.647418');
    SET IDENTITY_INSERT dbo.CV_Cursos OFF;

    -- CursoProductos: 9
    SET IDENTITY_INSERT dbo.CV_CursoProductos ON;
    INSERT INTO dbo.CV_CursoProductos ([id], [course_id], [product_id]) VALUES
        (1, 1, 8),
        (2, 1, 1),
        (3, 1, 7),
        (4, 2, 8),
        (5, 2, 2),
        (6, 3, 3),
        (7, 4, 4),
        (8, 5, 5),
        (9, 5, 6);
    SET IDENTITY_INSERT dbo.CV_CursoProductos OFF;

    -- Modulos: 12
    SET IDENTITY_INSERT dbo.CV_Modulos ON;
    INSERT INTO dbo.CV_Modulos ([id], [course_id], [title], [description], [order]) VALUES
        (1, 1, N'Conociendo Duralin Premium Forte', N'', 1),
        (2, 1, N'Aplicación que perdura', N'', 2),
        (3, 2, N'El acabado satinado', N'', 1),
        (4, 2, N'Aplicación sin marcas', N'', 2),
        (5, 3, N'Conceptos clave', N'', 1),
        (6, 3, N'Aplicación', N'', 2),
        (7, 4, N'Conociendo el silicón', N'', 1),
        (8, 4, N'Aplicación', N'', 2),
        (9, 5, N'Cubiertas metálicas', N'', 1),
        (10, 5, N'Instalación', N'', 2),
        (11, 6, N'Escuchar antes de vender', N'', 1),
        (12, 6, N'Cerrar y fidelizar', N'', 2);
    SET IDENTITY_INSERT dbo.CV_Modulos OFF;

    -- Lecciones: 18
    SET IDENTITY_INSERT dbo.CV_Lecciones ON;
    INSERT INTO dbo.CV_Lecciones ([id], [module_id], [title], [kind], [order], [duration_minutes], [video], [youtube_url], [document], [content], [require_full_watch]) VALUES
        (1, 1, N'Pintura satinada vs. pintura mate', N'lectura', 1, 6, N'', N'', N'', N'<p>Antes de recomendar una pintura, el cliente necesita entender <strong>qué acabado</strong> quiere. Las dos opciones más comunes en pinturas lavables son el acabado <strong>satinado</strong> y el acabado <strong>mate</strong>.</p>
<h2>Acabado satinado</h2>
<ul><li>Tiene un brillo suave que refleja parte de la luz.</li><li>Es muy fácil de limpiar.</li><li>Al reflejar la luz, <strong>resalta las imperfecciones</strong> de la pared.</li></ul>
<h2>Acabado mate</h2>
<ul><li>No tiene brillo: absorbe la luz.</li><li>Da un aspecto sobrio y uniforme.</li><li><strong>Ayuda a disimular imperfecciones</strong>, por eso es el preferido para <strong>tumbados</strong>.</li></ul>
<blockquote>Tip de venta: si el cliente menciona paredes o techos con pequeñas irregularidades, el acabado mate es tu mejor aliado.</blockquote>', 1),
        (2, 1, N'Duralin Premium Forte: características clave', N'lectura', 2, 7, N'', N'', N'', N'<p><strong>Duralin Premium Forte</strong> es la pintura de acabado mate de Industrial Latina. Pertenece a la <strong>calidad Tipo 1</strong>, la categoría más alta en pinturas arquitectónicas.</p>
<h2>¿Qué la hace diferente?</h2>
<ul><li><strong>Máximo cubrimiento:</strong> cubre mejor con menos manos.</li><li><strong>Alto rendimiento:</strong> rinde más metros cuadrados por galón.</li><li><strong>Altamente lavable:</strong> las manchas se limpian sin perder el color.</li><li><strong>Interiores y exteriores:</strong> un solo producto para toda la obra.</li><li><strong>Acabado profesional:</strong> superficie uniforme y fina.</li></ul>
<p>Cuando un cliente pregunta “¿por qué cuesta más que una pintura económica?”, la respuesta está en el rendimiento y la durabilidad: pinta menos veces y gasta menos a largo plazo.</p>', 1),
        (3, 2, N'Preparación de la superficie', N'lectura', 1, 8, N'', N'', N'', N'<p>Una pintura de excelente calidad solo dura si la superficie está bien preparada. <strong>El primer paso siempre es preparar la superficie correctamente.</strong></p>
<h2>Paredes recién enlucidas</h2>
<ol><li><strong>Esperar el curado:</strong> el enlucido debe curar entre <strong>28 y 31 días</strong> antes de tratarlo.</li><li><strong>Sellar:</strong> una vez curado, el primer paso es aplicar un <strong>sellador acrílico</strong> que controla la porosidad y mejora la adherencia.</li><li><strong>Empastar</strong> (si se necesita una superficie lisa) y lijar suavemente.</li><li><strong>Limpiar el polvo</strong> y aplicar Duralin Premium Forte.</li></ol>
<blockquote>Error común: pintar directamente sobre el enlucido fresco. La humedad y la alcalinidad dañan la pintura y aparecen manchas.</blockquote>', 1),
        (4, 2, N'Cómo recomendar Duralin en el punto de venta', N'lectura', 2, 5, N'', N'', N'', N'<p>Usa estas preguntas para asesorar mejor:</p>
<ul><li>¿Es para interior, exterior o ambos? <em>(Duralin sirve para los dos)</em></li><li>¿La superficie es nueva o ya estaba pintada?</li><li>¿Tiene imperfecciones o es un tumbado? <em>(el acabado mate las disimula)</em></li><li>¿Cuántos metros cuadrados va a pintar?</li></ul>
<h2>Venta completa</h2>
<p>Una buena recomendación incluye el <strong>sellador acrílico</strong> y, si hace falta, el <strong>empaste</strong>. Así el cliente obtiene un resultado profesional y tú aumentas el valor de la venta.</p>', 1),
        (5, 3, N'¿Qué es un acabado satinado?', N'lectura', 1, 5, N'', N'', N'', N'<p>El acabado <strong>satinado</strong> tiene un brillo suave, intermedio entre el mate y el brillante. Su superficie es más cerrada, por eso <strong>repele mejor la suciedad y se limpia con facilidad</strong>.</p>
<p>Como refleja parte de la luz, <strong>hace más visibles las imperfecciones</strong>: la pared debe estar bien preparada.</p>', 1),
        (6, 3, N'Dónde recomendarlo', N'lectura', 2, 5, N'', N'', N'', N'<ul><li><strong>Cocinas y baños:</strong> se limpian con frecuencia.</li><li><strong>Pasillos y escaleras:</strong> zonas de alto tránsito y roce.</li><li><strong>Habitaciones de niños:</strong> resiste mejor la limpieza de manchas.</li><li><strong>Puertas y molduras:</strong> resalta los detalles.</li></ul>
<blockquote>Para tumbados o paredes con irregularidades, recomienda mejor un acabado mate como Duralin Premium Forte.</blockquote>', 1),
        (7, 4, N'Aplicación paso a paso', N'lectura', 1, 7, N'', N'', N'', N'<ol><li>Preparar la superficie: limpia, seca, sellada y, si es necesario, empastada y lijada.</li><li>Mezclar bien el producto hasta que sea homogéneo.</li><li>Usar rodillo de pelo corto y brocha para los bordes.</li><li>Aplicar en paños completos, de esquina a esquina, sin detenerse a la mitad.</li><li>No repasar zonas que ya empezaron a secar: eso deja marcas de brillo.</li><li>Respetar el tiempo entre manos indicado en la ficha técnica y aplicar la segunda mano.</li></ol>', 1),
        (8, 5, N'¿Qué es un recubrimiento elastomérico?', N'lectura', 1, 6, N'', N'', N'', N'<p>Un recubrimiento <strong>elastomérico</strong> forma una película acrílica <strong>flexible</strong>: se estira y se contrae junto con la superficie cuando cambia la temperatura.</p>
<ul><li><strong>Hidrorepelente:</strong> repele el agua de lluvia.</li><li><strong>Flexible:</strong> acompaña los movimientos de dilatación.</li><li><strong>Puentea microfisuras:</strong> cubre fisuras finas sin que se abran en la pintura.</li></ul>', 1),
        (9, 5, N'Ventajas frente a una pintura convencional', N'lectura', 2, 5, N'', N'', N'', N'<p>Una pintura convencional forma una película rígida que puede agrietarse cuando la pared se mueve. El elastomérico, en cambio, <strong>se estira</strong> y mantiene la protección.</p>
<blockquote>Argumento de venta: “Protege su fachada de la lluvia y evita que las fisuras finas vuelvan a aparecer”.</blockquote>', 1),
        (10, 6, N'Aplicación en techos y fachadas', N'lectura', 1, 8, N'', N'', N'', N'<ol><li>Limpiar la superficie: sin polvo, grasa, hongos ni partes sueltas.</li><li>Reparar previamente las fisuras grandes y las grietas.</li><li>Preparar o sellar la superficie según la ficha técnica.</li><li>Aplicar en capas, cruzando la dirección entre una mano y otra.</li><li>Respetar el tiempo de secado y no aplicar si se espera lluvia.</li></ol>', 1),
        (11, 7, N'Usos del silicón en obra y hogar', N'lectura', 1, 5, N'', N'', N'', N'<p>El silicón forma un <strong>cordón flexible</strong> que sella uniones entre materiales y evita el paso de agua y aire.</p>
<ul><li>Ventanas y vidrios.</li><li>Juntas de lavamanos, duchas y mesones.</li><li>Uniones en canaletas y cubiertas.</li></ul>
<p>Pregunta siempre <strong>qué materiales</strong> va a unir el cliente y si la junta estará expuesta al agua; así recomiendas el producto adecuado.</p>', 1),
        (12, 8, N'Cómo lograr un cordón perfecto', N'lectura', 1, 7, N'', N'', N'', N'<ol><li>La superficie debe estar <strong>limpia y seca</strong>, sin restos de silicón viejo.</li><li>Colocar <strong>cinta de enmascarar</strong> a ambos lados de la junta para un acabado recto.</li><li>Cortar la boquilla en diagonal (45°) al ancho de la junta.</li><li>Aplicar con pistola un <strong>cordón continuo</strong>, con presión constante.</li><li>Alisar el cordón y <strong>retirar la cinta</strong> antes de que el silicón forme piel.</li><li>Respetar el tiempo de curado antes de exponerlo al agua.</li></ol>', 1),
        (13, 9, N'Qué es Induzinc y por qué el galvanizado', N'lectura', 1, 6, N'', N'', N'', N'<p>Induzinc son planchas onduladas de <strong>acero galvanizado</strong>. El galvanizado es un <strong>recubrimiento de zinc</strong> que protege al acero contra la corrosión.</p>
<ul><li>Son <strong>livianas</strong>: requieren estructuras más sencillas.</li><li>Se instalan <strong>rápido</strong>.</li><li>Son ideales para viviendas, bodegas, galpones y patios.</li></ul>', 1),
        (14, 10, N'Buenas prácticas de instalación', N'lectura', 1, 8, N'', N'', N'', N'<ol><li>Respetar la <strong>pendiente mínima</strong> indicada por el fabricante para que el agua escurra.</li><li>Instalar las planchas en sentido contrario al viento predominante.</li><li>Respetar los <strong>traslapes</strong> laterales y longitudinales.</li><li>Fijar siempre en la <strong>cresta de la onda</strong> (parte alta), nunca en el valle, usando fijaciones con arandela.</li><li>Complementar con <strong>silicón</strong> en uniones y remates.</li></ol>
<blockquote>Venta cruzada: planchas + clavos o tornillos con arandela + silicón Induless.</blockquote>', 1),
        (15, 11, N'Las preguntas que abren la venta', N'lectura', 1, 6, N'', N'', N'', N'<p>Un buen asesor <strong>pregunta más de lo que habla</strong>. Usa preguntas abiertas para entender la situación:</p>
<ul><li><strong>Situación:</strong> ¿qué va a pintar o sellar?, ¿interior o exterior?</li><li><strong>Problema:</strong> ¿qué le pasó con el producto anterior?</li><li><strong>Necesidad:</strong> ¿qué resultado espera?, ¿cuánto tiempo quiere que dure?</li></ul>', 1),
        (16, 11, N'De la característica al beneficio', N'lectura', 2, 6, N'', N'', N'', N'<p>El cliente no compra características, compra <strong>beneficios</strong>. Usa la fórmula <strong>Característica → Ventaja → Beneficio</strong>:</p>
<blockquote>“Duralin es <strong>altamente lavable</strong> (característica), las manchas salen con un paño húmedo (ventaja), así su pared se ve como nueva por más tiempo y no tiene que volver a pintar pronto (beneficio)”.</blockquote>', 1),
        (17, 12, N'Manejo de objeciones de precio', N'lectura', 1, 6, N'', N'', N'', N'<p>Cuando el cliente dice “está caro”, no bajes el precio de inmediato. Habla de <strong>valor</strong>:</p>
<ul><li>Compara el <strong>rendimiento</strong>: un producto que cubre más necesita menos galones.</li><li>Compara la <strong>duración</strong>: pintar menos veces es ahorrar.</li><li>Pregunta: “¿Qué es lo más importante para usted en este trabajo?”.</li></ul>', 1),
        (18, 12, N'Venta cruzada inteligente', N'lectura', 2, 5, N'', N'', N'', N'<p>La venta cruzada ayuda al cliente a lograr un mejor resultado:</p>
<ul><li>Pintura + <strong>sellador</strong> + empaste + rodillos.</li><li>Cubierta Induzinc + <strong>fijaciones con arandela</strong> + silicón.</li></ul>
<p>Recomienda solo lo que el trabajo realmente necesita: así generas confianza y el cliente regresa.</p>', 1);
    SET IDENTITY_INSERT dbo.CV_Lecciones OFF;

    -- Rutas: 3
    SET IDENTITY_INSERT dbo.CV_Rutas ON;
    INSERT INTO dbo.CV_Rutas ([id], [title], [slug], [summary], [description], [brand], [cover], [is_published], [order], [created_at]) VALUES
        (1, N'Asesor experto en pinturas Latina', N'asesor-experto-en-pinturas-latina', N'Domina la línea de pinturas de Industrial Latina: acabados, preparación de superficies y protección de fachadas.', N'Recomendada para ejecutivos que atienden ferreterías y distribuidores de pintura.', N'latina', N'', 1, 0, N'2026-10-24T13:57:46.869857'),
        (2, N'Especialista Induless', N'especialista-induless', N'Siliconas, cubiertas Induzinc y fijaciones: todo lo que necesitas para asesorar en techos y sellado.', N'Ideal para el equipo que atiende la línea de construcción liviana.', N'induless', N'', 1, 1, N'2026-10-24T13:57:46.894221'),
        (3, N'Vendedor estrella', N'vendedor-estrella', N'Combina técnicas de venta consultiva con el producto estrella de la marca.', N'Un programa corto para mejorar la conversión en el punto de venta.', N'corporativo', N'', 1, 2, N'2026-10-24T13:57:46.912162');
    SET IDENTITY_INSERT dbo.CV_Rutas OFF;

    -- RutaCursos: 7
    SET IDENTITY_INSERT dbo.CV_RutaCursos ON;
    INSERT INTO dbo.CV_RutaCursos ([id], [path_id], [course_id], [order]) VALUES
        (1, 1, 1, 1),
        (2, 1, 2, 2),
        (3, 1, 3, 3),
        (4, 2, 4, 1),
        (5, 2, 5, 2),
        (6, 3, 6, 1),
        (7, 3, 1, 2);
    SET IDENTITY_INSERT dbo.CV_RutaCursos OFF;

    -- Evaluaciones: 6
    SET IDENTITY_INSERT dbo.CV_Evaluaciones ON;
    INSERT INTO dbo.CV_Evaluaciones ([id], [course_id], [title], [instructions], [time_limit_minutes], [questions_per_attempt], [passing_score], [max_attempts], [show_review]) VALUES
        (1, 1, N'Evaluación final', N'', 10, 10, 70, 0, 1),
        (2, 2, N'Evaluación final', N'', 10, 10, 70, 0, 1),
        (3, 3, N'Evaluación final', N'', 10, 10, 70, 0, 1),
        (4, 4, N'Evaluación final', N'', 10, 10, 70, 0, 1),
        (5, 5, N'Evaluación final', N'', 10, 10, 70, 0, 1),
        (6, 6, N'Evaluación final', N'', 10, 10, 70, 0, 1);
    SET IDENTITY_INSERT dbo.CV_Evaluaciones OFF;

    -- Preguntas: 40
    SET IDENTITY_INSERT dbo.CV_Preguntas ON;
    INSERT INTO dbo.CV_Preguntas ([id], [quiz_id], [text], [explanation], [order]) VALUES
        (1, 1, N'¿Cuál es la principal diferencia explicada al inicio?', N'La lección compara el acabado satinado con el acabado mate.', 1),
        (2, 1, N'¿Cómo se llama la pintura de acabado mate presentada?', N'', 2),
        (3, 1, N'¿A qué categoría de calidad pertenece Duralin Premium Forte?', N'Duralin Premium Forte es calidad Tipo 1.', 3),
        (4, 1, N'¿Cuál de las siguientes características define a Duralin Premium Forte?', N'', 4),
        (5, 1, N'¿Para qué tipo de ambientes es ideal Duralin Premium Forte?', N'', 5),
        (6, 1, N'¿Qué gran ventaja ofrece el acabado mate de esta pintura?', N'El acabado mate no refleja la luz, por eso disimula imperfecciones.', 6),
        (7, 1, N'¿En qué superficie se recomienda usar pintura mate para ocultar imperfecciones?', N'', 7),
        (8, 1, N'Para que la pintura dure y perdure en el tiempo, ¿qué se debe hacer primero?', N'', 8),
        (9, 1, N'¿Cuántos días se debe esperar para tratar una pared después de enlucirla?', N'El enlucido necesita cerca de un mes de curado.', 9),
        (10, 1, N'Una vez transcurrido el tiempo de curado del enlucido, ¿cuál es el primer paso?', N'Primero se sella la pared para controlar la porosidad.', 10),
        (11, 2, N'¿Qué caracteriza a un acabado satinado?', N'', 1),
        (12, 2, N'¿Qué efecto tiene el brillo satinado sobre las imperfecciones de la pared?', N'Al reflejar la luz, el satinado resalta las irregularidades.', 2),
        (13, 2, N'¿Cuál es un espacio ideal para recomendar satinado?', N'', 3),
        (14, 2, N'¿Qué herramienta se recomienda para aplicar satinado en paredes?', N'', 4),
        (15, 2, N'¿Qué debes evitar para no dejar marcas de brillo?', N'', 5),
        (16, 2, N'Para un tumbado con imperfecciones, ¿qué acabado conviene más?', N'', 6),
        (17, 3, N'¿Qué propiedad describe mejor a un recubrimiento elastomérico?', N'', 1),
        (18, 3, N'¿Qué significa que sea hidrorepelente?', N'', 2),
        (19, 3, N'¿Qué hace el elastomérico con las microfisuras?', N'', 3),
        (20, 3, N'¿En qué superficies se recomienda?', N'', 4),
        (21, 3, N'¿Qué se debe hacer con las fisuras grandes antes de aplicar?', N'', 5),
        (22, 3, N'¿Cuándo NO se debe aplicar el producto?', N'', 6),
        (23, 4, N'¿Cuál es la función principal del silicón?', N'', 1),
        (24, 4, N'¿Cómo debe estar la superficie antes de aplicar silicón?', N'', 2),
        (25, 4, N'¿Para qué sirve la cinta de enmascarar?', N'', 3),
        (26, 4, N'¿Cómo se corta la boquilla del cartucho?', N'', 4),
        (27, 4, N'¿Cuándo se retira la cinta de enmascarar?', N'', 5),
        (28, 4, N'¿Qué pregunta ayuda a recomendar el silicón correcto?', N'', 6),
        (29, 5, N'¿Qué protege al acero en una plancha galvanizada?', N'', 1),
        (30, 5, N'¿Cuál es una ventaja de las cubiertas metálicas?', N'', 2),
        (31, 5, N'¿Dónde se debe fijar la plancha ondulada?', N'Fijar en la cresta evita que el agua se filtre por la perforación.', 3),
        (32, 5, N'¿Por qué es importante la pendiente del techo?', N'', 4),
        (33, 5, N'¿Qué tipo de fijación se recomienda?', N'', 5),
        (34, 5, N'¿Qué producto complementa la instalación en uniones y remates?', N'', 6),
        (35, 6, N'¿Qué debe hacer primero un buen asesor?', N'', 1),
        (36, 6, N'¿Qué compra realmente el cliente?', N'', 2),
        (37, 6, N'En la fórmula C-V-B, ¿qué significa la B?', N'', 3),
        (38, 6, N'Ante la objeción “está caro”, ¿qué es recomendable?', N'', 4),
        (39, 6, N'¿Cuál es un ejemplo de venta cruzada correcta?', N'', 5),
        (40, 6, N'¿Por qué recomendar solo lo que el trabajo necesita?', N'', 6);
    SET IDENTITY_INSERT dbo.CV_Preguntas OFF;

    -- Opciones: 160
    SET IDENTITY_INSERT dbo.CV_Opciones ON;
    INSERT INTO dbo.CV_Opciones ([id], [question_id], [text], [is_correct], [order]) VALUES
        (1, 1, N'Pintura lavable satinada y mate', 1, 0),
        (2, 1, N'Pintura de aceite y agua', 0, 1),
        (3, 1, N'Empaste y sellador', 0, 2),
        (4, 1, N'Colores cálidos y fríos', 0, 3),
        (5, 2, N'Sellador Blanco Profesional', 0, 0),
        (6, 2, N'Duralin Premium Forte', 1, 1),
        (7, 2, N'Satinado de Industrial Latina', 0, 2),
        (8, 2, N'Empaste Monocomponente', 0, 3),
        (9, 3, N'Tipo 3', 0, 0),
        (10, 3, N'Tipo 2', 0, 1),
        (11, 3, N'Tipo 1', 1, 2),
        (12, 3, N'Económica', 0, 3),
        (13, 4, N'No se puede lavar', 0, 0),
        (14, 4, N'Es altamente lavable', 1, 1),
        (15, 4, N'Es exclusivamente para madera', 0, 2),
        (16, 4, N'Tiene un acabado brillante', 0, 3),
        (17, 5, N'Solo interiores', 0, 0),
        (18, 5, N'Solo exteriores', 0, 1),
        (19, 5, N'Interiores y exteriores', 1, 2),
        (20, 5, N'Pisos y techos', 0, 3),
        (21, 6, N'Resalta los errores de la pared', 0, 0),
        (22, 6, N'Ayuda a disimular imperfecciones', 1, 1),
        (23, 6, N'Cambia de color con el sol', 0, 2),
        (24, 6, N'Seca en 5 minutos', 0, 3),
        (25, 7, N'Pisos de cerámica', 0, 0),
        (26, 7, N'Tumbados', 1, 1),
        (27, 7, N'Mesones', 0, 2),
        (28, 7, N'Tejas', 0, 3),
        (29, 8, N'Aplicar tres capas de pintura', 0, 0),
        (30, 8, N'Preparar la superficie correctamente', 1, 1),
        (31, 8, N'Pintar directamente sobre el ladrillo', 0, 2),
        (32, 8, N'Mezclar la pintura con sellador', 0, 3),
        (33, 9, N'De 5 a 10 días', 0, 0),
        (34, 9, N'De 15 a 20 días', 0, 1),
        (35, 9, N'De 28 a 31 días', 1, 2),
        (36, 9, N'De 40 a 50 días', 0, 3),
        (37, 10, N'Aplicar empaste', 0, 0),
        (38, 10, N'Sellar la pared con un sellador acrílico', 1, 1),
        (39, 10, N'Pintar con Duralin', 0, 2),
        (40, 10, N'Lijar agresivamente', 0, 3),
        (41, 11, N'No tiene ningún brillo', 0, 0),
        (42, 11, N'Tiene un brillo suave y se limpia con facilidad', 1, 1),
        (43, 11, N'Solo sirve para exteriores', 0, 2),
        (44, 11, N'Es un tipo de empaste', 0, 3),
        (45, 12, N'Las disimula por completo', 0, 0),
        (46, 12, N'Las hace más visibles', 1, 1),
        (47, 12, N'No tiene ningún efecto', 0, 2),
        (48, 12, N'Las elimina', 0, 3),
        (49, 13, N'Un tumbado irregular', 0, 0),
        (50, 13, N'Una cocina', 1, 1),
        (51, 13, N'Un piso de cemento', 0, 2),
        (52, 13, N'Un techo de zinc', 0, 3),
        (53, 14, N'Rodillo de pelo corto', 1, 0),
        (54, 14, N'Espátula', 0, 1),
        (55, 14, N'Llana dentada', 0, 2),
        (56, 14, N'Pistola de silicón', 0, 3),
        (57, 15, N'Mezclar la pintura', 0, 0),
        (58, 15, N'Repasar zonas que ya empezaron a secar', 1, 1),
        (59, 15, N'Aplicar una segunda mano', 0, 2),
        (60, 15, N'Usar brocha en los bordes', 0, 3),
        (61, 16, N'Satinado', 0, 0),
        (62, 16, N'Brillante', 0, 1),
        (63, 16, N'Mate', 1, 2),
        (64, 16, N'Ninguno', 0, 3),
        (65, 17, N'Es rígido', 0, 0),
        (66, 17, N'Es flexible', 1, 1),
        (67, 17, N'Es un solvente', 0, 2),
        (68, 17, N'Es un empaste', 0, 3),
        (69, 18, N'Que atrae la humedad', 0, 0),
        (70, 18, N'Que repele el agua', 1, 1),
        (71, 18, N'Que se diluye con agua', 0, 2),
        (72, 18, N'Que seca bajo el agua', 0, 3),
        (73, 19, N'Las agranda', 0, 0),
        (74, 19, N'Las puentea o cubre', 1, 1),
        (75, 19, N'No las afecta', 0, 2),
        (76, 19, N'Las rellena de cemento', 0, 3),
        (77, 20, N'Fachadas y techos', 1, 0),
        (78, 20, N'Muebles de madera', 0, 1),
        (79, 20, N'Vidrios', 0, 2),
        (80, 20, N'Pisos interiores', 0, 3),
        (81, 21, N'Nada', 0, 0),
        (82, 21, N'Repararlas previamente', 1, 1),
        (83, 21, N'Pintarlas de otro color', 0, 2),
        (84, 21, N'Cubrirlas con silicón', 0, 3),
        (85, 22, N'En la mañana', 0, 0),
        (86, 22, N'Cuando se espera lluvia', 1, 1),
        (87, 22, N'Sobre una superficie limpia', 0, 2),
        (88, 22, N'Después de reparar fisuras', 0, 3),
        (89, 23, N'Pegar ladrillos', 0, 0),
        (90, 23, N'Sellar juntas de forma flexible', 1, 1),
        (91, 23, N'Pintar paredes', 0, 2),
        (92, 23, N'Nivelar pisos', 0, 3),
        (93, 24, N'Húmeda', 0, 0),
        (94, 24, N'Limpia y seca', 1, 1),
        (95, 24, N'Con polvo', 0, 2),
        (96, 24, N'Recién pintada', 0, 3),
        (97, 25, N'Para acelerar el secado', 0, 0),
        (98, 25, N'Para lograr un acabado recto y limpio', 1, 1),
        (99, 25, N'Para reemplazar el silicón', 0, 2),
        (100, 25, N'No tiene utilidad', 0, 3),
        (101, 26, N'Recta y muy pequeña', 0, 0),
        (102, 26, N'En diagonal al ancho de la junta', 1, 1),
        (103, 26, N'No se corta', 0, 2),
        (104, 26, N'En forma de cruz', 0, 3),
        (105, 27, N'Al día siguiente', 0, 0),
        (106, 27, N'Antes de que el silicón forme piel', 1, 1),
        (107, 27, N'Nunca', 0, 2),
        (108, 27, N'Antes de aplicar el silicón', 0, 3),
        (109, 28, N'¿Qué materiales va a unir?', 1, 0),
        (110, 28, N'¿De qué color es su casa?', 0, 1),
        (111, 28, N'¿Cuántos años tiene?', 0, 2),
        (112, 28, N'¿Dónde compró la pistola?', 0, 3),
        (113, 29, N'Una capa de pintura', 0, 0),
        (114, 29, N'Un recubrimiento de zinc', 1, 1),
        (115, 29, N'Un plástico', 0, 2),
        (116, 29, N'Nada', 0, 3),
        (117, 30, N'Son muy pesadas', 0, 0),
        (118, 30, N'Son livianas y rápidas de instalar', 1, 1),
        (119, 30, N'No necesitan fijación', 0, 2),
        (120, 30, N'Solo sirven en interiores', 0, 3),
        (121, 31, N'En el valle de la onda', 0, 0),
        (122, 31, N'En la cresta de la onda', 1, 1),
        (123, 31, N'En cualquier parte', 0, 2),
        (124, 31, N'Solo en los bordes', 0, 3),
        (125, 32, N'Para que el agua escurra', 1, 0),
        (126, 32, N'Por estética únicamente', 0, 1),
        (127, 32, N'No es importante', 0, 2),
        (128, 32, N'Para ahorrar clavos', 0, 3),
        (129, 33, N'Sin arandela', 0, 0),
        (130, 33, N'Con arandela', 1, 1),
        (131, 33, N'Pegamento escolar', 0, 2),
        (132, 33, N'Cinta adhesiva', 0, 3),
        (133, 34, N'Silicón', 1, 0),
        (134, 34, N'Empaste', 0, 1),
        (135, 34, N'Pintura mate', 0, 2),
        (136, 34, N'Sellador acrílico', 0, 3),
        (137, 35, N'Hablar del precio', 0, 0),
        (138, 35, N'Hacer preguntas para entender la necesidad', 1, 1),
        (139, 35, N'Ofrecer el producto más caro', 0, 2),
        (140, 35, N'Mostrar el catálogo completo', 0, 3),
        (141, 36, N'Características', 0, 0),
        (142, 36, N'Beneficios', 1, 1),
        (143, 36, N'Envases', 0, 2),
        (144, 36, N'Marcas', 0, 3),
        (145, 37, N'Bodega', 0, 0),
        (146, 37, N'Beneficio', 1, 1),
        (147, 37, N'Brillo', 0, 2),
        (148, 37, N'Base', 0, 3),
        (149, 38, N'Bajar el precio de inmediato', 0, 0),
        (150, 38, N'Hablar del valor: rendimiento y duración', 1, 1),
        (151, 38, N'Terminar la conversación', 0, 2),
        (152, 38, N'Recomendar otra tienda', 0, 3),
        (153, 39, N'Pintura + sellador', 1, 0),
        (154, 39, N'Pintura + juguete', 0, 1),
        (155, 39, N'Silicón + comida', 0, 2),
        (156, 39, N'Clavos + perfume', 0, 3),
        (157, 40, N'Para vender menos', 0, 0),
        (158, 40, N'Para generar confianza y que el cliente regrese', 1, 1),
        (159, 40, N'Porque es obligatorio', 0, 2),
        (160, 40, N'No importa', 0, 3);
    SET IDENTITY_INSERT dbo.CV_Opciones OFF;

    -- Anuncios: 1
    SET IDENTITY_INSERT dbo.CV_Anuncios ON;
    INSERT INTO dbo.CV_Anuncios ([id], [title], [body], [tone], [link_url], [link_label], [is_active], [created_at]) VALUES
        (1, N'¡Te damos la bienvenida al nuevo Campus Latina!', N'Ahora puedes aprender a tu ritmo, rendir evaluaciones, ganar puntos y descargar certificados verificables. Empieza por el curso obligatorio de Duralin Premium Forte.', N'nuevo', N'/aprender/explorar/', N'Explorar cursos', 1, N'2026-10-24T13:57:46.929557');
    SET IDENTITY_INSERT dbo.CV_Anuncios OFF;

COMMIT TRANSACTION;

PRINT N'Contenido de ejemplo cargado. Reinicia el sitio del campus (o ejecuta manage.py cargar_api).';
GO
