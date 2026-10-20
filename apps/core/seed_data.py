"""
Contenido inicial de ejemplo del campus.

Los textos son material de partida pensado para que el equipo de Capacitación
lo revise y ajuste con los datos oficiales de las fichas técnicas.
El curso de Duralin conserva el banco de 10 preguntas de la versión anterior.
"""

CATEGORIES = [
    ("Pinturas y Acabados", "paint-bucket", "Látex, satinados y recubrimientos para interiores y exteriores."),
    ("Empastes", "layers", "Preparación y nivelación de superficies."),
    ("Preparación / Selladores", "shield-check", "Selladores e imprimantes para que la pintura dure."),
    ("Morteros y Adhesivos", "brick-wall", "Pegado de cerámica y reparaciones."),
    ("Siliconas", "droplets", "Sellado de juntas, ventanas y baños."),
    ("Techos y Cubiertas", "house", "Cubiertas metálicas y su instalación."),
    ("Clavos y Fijaciones", "hammer", "Fijación correcta para cada material."),
    ("Habilidades Comerciales", "handshake", "Técnicas de venta y atención al cliente."),
]

PRODUCT_LINES = [
    ("Pinturas", "paint-bucket"),
    ("Empastes", "layers"),
    ("Selladores", "shield-check"),
    ("Siliconas", "droplets"),
    ("Cubiertas", "house"),
    ("Clavos y fijaciones", "hammer"),
]

# image = archivo en apps/core/seed_assets (prod-<image>.jpg)
PRODUCTS = [
    {
        "name": "Duralin Premium Forte", "brand": "latina", "line": "Pinturas", "image": "duralin",
        "summary": "Pintura de alto cubrimiento y acabado fino. Mate, lavable, para interiores y exteriores.",
        "description": "Pintura látex de calidad Tipo 1 con acabado mate. Su gran poder cubriente y su lavabilidad la hacen ideal para proyectos residenciales y comerciales.",
        "features": "Máximo cubrimiento\nAlto rendimiento\nAcabado profesional mate\nAltamente lavable\nCalidad Tipo 1",
        "uses": "Paredes interiores y exteriores\nTumbados (disimula imperfecciones)\nProyectos residenciales y comerciales",
        "presentations": "Galón · Caneca",
    },
    {
        "name": "Satinado Latina", "brand": "latina", "line": "Pinturas", "image": "satinado",
        "summary": "Acabado fino y especial con un ligero brillo que facilita la limpieza.",
        "description": "Pintura de acabado satinado para espacios que se limpian con frecuencia y donde se busca un aspecto elegante.",
        "features": "Acabado satinado elegante\nFácil de limpiar\nResistente al uso diario",
        "uses": "Cocinas y baños\nPasillos y áreas de alto tránsito\nPuertas y molduras",
        "presentations": "Galón · Caneca",
    },
    {
        "name": "Elastomérico Latina", "brand": "latina", "line": "Pinturas", "image": "elastomerico",
        "summary": "Recubrimiento acrílico hidrorepelente y flexible para fachadas y techos.",
        "description": "Recubrimiento elastomérico que forma una película flexible capaz de acompañar los movimientos de la superficie y repeler el agua de lluvia.",
        "features": "Hidrorepelente\nFlexible\nRecubrimiento acrílico\nPuentea microfisuras",
        "uses": "Fachadas expuestas a lluvia\nLosas y techos\nParedes con microfisuras",
        "presentations": "Galón · Caneca",
    },
    {
        "name": "Silicón Induless", "brand": "induless", "line": "Siliconas", "image": "silicon",
        "summary": "Silicón para sellar juntas en vidrio, aluminio, cerámica y baños.",
        "description": "Sellador de silicón en cartucho para aplicar con pistola. Forma un cordón flexible y duradero.",
        "features": "Cordón flexible\nAdhiere a superficies no porosas\nPráctico cartucho para pistola",
        "uses": "Ventanas y vidrios\nJuntas de baños y cocinas\nSellado de canaletas y uniones",
        "presentations": "Cartucho",
    },
    {
        "name": "Induzinc", "brand": "induless", "line": "Cubiertas", "image": "induzinc",
        "summary": "Planchas onduladas de acero galvanizado para cubiertas livianas y resistentes.",
        "description": "Cubierta metálica ondulada con recubrimiento de zinc que protege el acero frente a la corrosión.",
        "features": "Acero galvanizado\nLiviana y resistente\nInstalación rápida",
        "uses": "Techos de viviendas\nGalpones y bodegas\nCubiertas de patios y parqueaderos",
        "presentations": "Planchas en varias longitudes",
    },
    {
        "name": "Clavos Induless", "brand": "induless", "line": "Clavos y fijaciones", "image": "clavos",
        "summary": "Clavos para construcción y carpintería en distintas medidas.",
        "description": "Clavos de acero para trabajos de construcción, encofrado y carpintería.",
        "features": "Acero de calidad\nVariedad de medidas\nCaja práctica",
        "uses": "Encofrados\nCarpintería\nFijación de cubiertas (con arandela)",
        "presentations": "Caja",
    },
    {
        "name": "Empaste Latina", "brand": "latina", "line": "Empastes", "image": None,
        "summary": "Empaste para nivelar y alisar paredes antes de pintar.",
        "description": "Pasta para corregir imperfecciones y dejar la superficie lisa y uniforme.",
        "features": "Fácil de lijar\nBuena adherencia\nAcabado liso",
        "uses": "Paredes interiores\nCorrección de imperfecciones",
        "presentations": "Galón · Caneca",
    },
    {
        "name": "Sellador Acrílico Latina", "brand": "latina", "line": "Selladores", "image": None,
        "summary": "Sellador para preparar superficies nuevas y mejorar el rendimiento de la pintura.",
        "description": "Sella la porosidad del enlucido, uniformiza la absorción y mejora la adherencia y el rendimiento de la pintura.",
        "features": "Sella la porosidad\nMejora la adherencia\nAhorra pintura",
        "uses": "Enlucidos nuevos (después del curado)\nSuperficies porosas",
        "presentations": "Galón · Caneca",
    },
]

DURALIN_QUESTIONS = [
    ("¿Cuál es la principal diferencia explicada al inicio?", ["Pintura lavable satinada y mate", "Pintura de aceite y agua", "Empaste y sellador", "Colores cálidos y fríos"], 0, "La lección compara el acabado satinado con el acabado mate."),
    ("¿Cómo se llama la pintura de acabado mate presentada?", ["Sellador Blanco Profesional", "Duralin Premium Forte", "Satinado de Industrial Latina", "Empaste Monocomponente"], 1, ""),
    ("¿A qué categoría de calidad pertenece Duralin Premium Forte?", ["Tipo 3", "Tipo 2", "Tipo 1", "Económica"], 2, "Duralin Premium Forte es calidad Tipo 1."),
    ("¿Cuál de las siguientes características define a Duralin Premium Forte?", ["No se puede lavar", "Es altamente lavable", "Es exclusivamente para madera", "Tiene un acabado brillante"], 1, ""),
    ("¿Para qué tipo de ambientes es ideal Duralin Premium Forte?", ["Solo interiores", "Solo exteriores", "Interiores y exteriores", "Pisos y techos"], 2, ""),
    ("¿Qué gran ventaja ofrece el acabado mate de esta pintura?", ["Resalta los errores de la pared", "Ayuda a disimular imperfecciones", "Cambia de color con el sol", "Seca en 5 minutos"], 1, "El acabado mate no refleja la luz, por eso disimula imperfecciones."),
    ("¿En qué superficie se recomienda usar pintura mate para ocultar imperfecciones?", ["Pisos de cerámica", "Tumbados", "Mesones", "Tejas"], 1, ""),
    ("Para que la pintura dure y perdure en el tiempo, ¿qué se debe hacer primero?", ["Aplicar tres capas de pintura", "Preparar la superficie correctamente", "Pintar directamente sobre el ladrillo", "Mezclar la pintura con sellador"], 1, ""),
    ("¿Cuántos días se debe esperar para tratar una pared después de enlucirla?", ["De 5 a 10 días", "De 15 a 20 días", "De 28 a 31 días", "De 40 a 50 días"], 2, "El enlucido necesita cerca de un mes de curado."),
    ("Una vez transcurrido el tiempo de curado del enlucido, ¿cuál es el primer paso?", ["Aplicar empaste", "Sellar la pared con un sellador acrílico", "Pintar con Duralin", "Lijar agresivamente"], 1, "Primero se sella la pared para controlar la porosidad."),
]

COURSES = [
    {
        "title": "Duralin Premium Forte: la pintura mate Tipo 1",
        "brand": "latina", "category": "Pinturas y Acabados", "level": "basico", "featured": True, "mandatory": True,
        "image": "duralin", "products": ["Duralin Premium Forte", "Sellador Acrílico Latina", "Empaste Latina"],
        "summary": "Conoce a fondo Duralin Premium Forte, cuándo recomendar un acabado mate y cómo preparar la superficie para que la pintura dure.",
        "description": "Este curso te prepara para asesorar a tus clientes sobre Duralin Premium Forte, nuestra pintura de calidad Tipo 1 con acabado mate.\n\nAprenderás la diferencia entre acabados satinado y mate, las características que hacen única a Duralin y el proceso correcto de preparación de superficies.",
        "outcomes": "Diferenciar un acabado satinado de uno mate\nExplicar por qué Duralin Premium Forte es calidad Tipo 1\nRecomendar el producto según el ambiente y la superficie\nGuiar al cliente en la preparación correcta de la pared",
        "modules": [
            ("Conociendo Duralin Premium Forte", [
                ("Pintura satinada vs. pintura mate", 6, """
<p>Antes de recomendar una pintura, el cliente necesita entender <strong>qué acabado</strong> quiere. Las dos opciones más comunes en pinturas lavables son el acabado <strong>satinado</strong> y el acabado <strong>mate</strong>.</p>
<h2>Acabado satinado</h2>
<ul><li>Tiene un brillo suave que refleja parte de la luz.</li><li>Es muy fácil de limpiar.</li><li>Al reflejar la luz, <strong>resalta las imperfecciones</strong> de la pared.</li></ul>
<h2>Acabado mate</h2>
<ul><li>No tiene brillo: absorbe la luz.</li><li>Da un aspecto sobrio y uniforme.</li><li><strong>Ayuda a disimular imperfecciones</strong>, por eso es el preferido para <strong>tumbados</strong>.</li></ul>
<blockquote>Tip de venta: si el cliente menciona paredes o techos con pequeñas irregularidades, el acabado mate es tu mejor aliado.</blockquote>"""),
                ("Duralin Premium Forte: características clave", 7, """
<p><strong>Duralin Premium Forte</strong> es la pintura de acabado mate de Industrial Latina. Pertenece a la <strong>calidad Tipo 1</strong>, la categoría más alta en pinturas arquitectónicas.</p>
<h2>¿Qué la hace diferente?</h2>
<ul><li><strong>Máximo cubrimiento:</strong> cubre mejor con menos manos.</li><li><strong>Alto rendimiento:</strong> rinde más metros cuadrados por galón.</li><li><strong>Altamente lavable:</strong> las manchas se limpian sin perder el color.</li><li><strong>Interiores y exteriores:</strong> un solo producto para toda la obra.</li><li><strong>Acabado profesional:</strong> superficie uniforme y fina.</li></ul>
<p>Cuando un cliente pregunta “¿por qué cuesta más que una pintura económica?”, la respuesta está en el rendimiento y la durabilidad: pinta menos veces y gasta menos a largo plazo.</p>"""),
            ]),
            ("Aplicación que perdura", [
                ("Preparación de la superficie", 8, """
<p>Una pintura de excelente calidad solo dura si la superficie está bien preparada. <strong>El primer paso siempre es preparar la superficie correctamente.</strong></p>
<h2>Paredes recién enlucidas</h2>
<ol><li><strong>Esperar el curado:</strong> el enlucido debe curar entre <strong>28 y 31 días</strong> antes de tratarlo.</li><li><strong>Sellar:</strong> una vez curado, el primer paso es aplicar un <strong>sellador acrílico</strong> que controla la porosidad y mejora la adherencia.</li><li><strong>Empastar</strong> (si se necesita una superficie lisa) y lijar suavemente.</li><li><strong>Limpiar el polvo</strong> y aplicar Duralin Premium Forte.</li></ol>
<blockquote>Error común: pintar directamente sobre el enlucido fresco. La humedad y la alcalinidad dañan la pintura y aparecen manchas.</blockquote>"""),
                ("Cómo recomendar Duralin en el punto de venta", 5, """
<p>Usa estas preguntas para asesorar mejor:</p>
<ul><li>¿Es para interior, exterior o ambos? <em>(Duralin sirve para los dos)</em></li><li>¿La superficie es nueva o ya estaba pintada?</li><li>¿Tiene imperfecciones o es un tumbado? <em>(el acabado mate las disimula)</em></li><li>¿Cuántos metros cuadrados va a pintar?</li></ul>
<h2>Venta completa</h2>
<p>Una buena recomendación incluye el <strong>sellador acrílico</strong> y, si hace falta, el <strong>empaste</strong>. Así el cliente obtiene un resultado profesional y tú aumentas el valor de la venta.</p>"""),
            ]),
        ],
        "questions": DURALIN_QUESTIONS,
    },
    {
        "title": "Satinado Latina: acabado fino y especial",
        "brand": "latina", "category": "Pinturas y Acabados", "level": "basico", "featured": True,
        "image": "satinado", "products": ["Satinado Latina", "Sellador Acrílico Latina"],
        "summary": "Aprende cuándo recomendar un acabado satinado y cómo aplicarlo para lograr un resultado elegante y fácil de limpiar.",
        "description": "El acabado satinado combina elegancia y practicidad. En este curso verás sus ventajas, en qué espacios conviene y los cuidados para aplicarlo sin marcas.",
        "outcomes": "Identificar los espacios ideales para un acabado satinado\nExplicar sus ventajas de limpieza\nPrevenir marcas y empalmes durante la aplicación\nPreparar la superficie para un brillo uniforme",
        "modules": [
            ("El acabado satinado", [
                ("¿Qué es un acabado satinado?", 5, """
<p>El acabado <strong>satinado</strong> tiene un brillo suave, intermedio entre el mate y el brillante. Su superficie es más cerrada, por eso <strong>repele mejor la suciedad y se limpia con facilidad</strong>.</p>
<p>Como refleja parte de la luz, <strong>hace más visibles las imperfecciones</strong>: la pared debe estar bien preparada.</p>"""),
                ("Dónde recomendarlo", 5, """
<ul><li><strong>Cocinas y baños:</strong> se limpian con frecuencia.</li><li><strong>Pasillos y escaleras:</strong> zonas de alto tránsito y roce.</li><li><strong>Habitaciones de niños:</strong> resiste mejor la limpieza de manchas.</li><li><strong>Puertas y molduras:</strong> resalta los detalles.</li></ul>
<blockquote>Para tumbados o paredes con irregularidades, recomienda mejor un acabado mate como Duralin Premium Forte.</blockquote>"""),
            ]),
            ("Aplicación sin marcas", [
                ("Aplicación paso a paso", 7, """
<ol><li>Preparar la superficie: limpia, seca, sellada y, si es necesario, empastada y lijada.</li><li>Mezclar bien el producto hasta que sea homogéneo.</li><li>Usar rodillo de pelo corto y brocha para los bordes.</li><li>Aplicar en paños completos, de esquina a esquina, sin detenerse a la mitad.</li><li>No repasar zonas que ya empezaron a secar: eso deja marcas de brillo.</li><li>Respetar el tiempo entre manos indicado en la ficha técnica y aplicar la segunda mano.</li></ol>"""),
            ]),
        ],
        "questions": [
            ("¿Qué caracteriza a un acabado satinado?", ["No tiene ningún brillo", "Tiene un brillo suave y se limpia con facilidad", "Solo sirve para exteriores", "Es un tipo de empaste"], 1, ""),
            ("¿Qué efecto tiene el brillo satinado sobre las imperfecciones de la pared?", ["Las disimula por completo", "Las hace más visibles", "No tiene ningún efecto", "Las elimina"], 1, "Al reflejar la luz, el satinado resalta las irregularidades."),
            ("¿Cuál es un espacio ideal para recomendar satinado?", ["Un tumbado irregular", "Una cocina", "Un piso de cemento", "Un techo de zinc"], 1, ""),
            ("¿Qué herramienta se recomienda para aplicar satinado en paredes?", ["Rodillo de pelo corto", "Espátula", "Llana dentada", "Pistola de silicón"], 0, ""),
            ("¿Qué debes evitar para no dejar marcas de brillo?", ["Mezclar la pintura", "Repasar zonas que ya empezaron a secar", "Aplicar una segunda mano", "Usar brocha en los bordes"], 1, ""),
            ("Para un tumbado con imperfecciones, ¿qué acabado conviene más?", ["Satinado", "Brillante", "Mate", "Ninguno"], 2, ""),
        ],
    },
    {
        "title": "Elastomérico: protección hidrorepelente para fachadas y techos",
        "brand": "latina", "category": "Pinturas y Acabados", "level": "intermedio",
        "image": "elastomerico", "products": ["Elastomérico Latina"],
        "summary": "Entiende cómo funciona un recubrimiento elastomérico y cómo asesorar a tus clientes en la protección de fachadas y techos.",
        "description": "Los recubrimientos elastoméricos protegen superficies expuestas a la lluvia y a cambios de temperatura. Aprende sus ventajas y su correcta aplicación.",
        "outcomes": "Explicar qué es un recubrimiento elastomérico\nDiferenciarlo de una pintura convencional\nRecomendarlo para fachadas, losas y techos\nGuiar una aplicación por capas",
        "modules": [
            ("Conceptos clave", [
                ("¿Qué es un recubrimiento elastomérico?", 6, """
<p>Un recubrimiento <strong>elastomérico</strong> forma una película acrílica <strong>flexible</strong>: se estira y se contrae junto con la superficie cuando cambia la temperatura.</p>
<ul><li><strong>Hidrorepelente:</strong> repele el agua de lluvia.</li><li><strong>Flexible:</strong> acompaña los movimientos de dilatación.</li><li><strong>Puentea microfisuras:</strong> cubre fisuras finas sin que se abran en la pintura.</li></ul>"""),
                ("Ventajas frente a una pintura convencional", 5, """
<p>Una pintura convencional forma una película rígida que puede agrietarse cuando la pared se mueve. El elastomérico, en cambio, <strong>se estira</strong> y mantiene la protección.</p>
<blockquote>Argumento de venta: “Protege su fachada de la lluvia y evita que las fisuras finas vuelvan a aparecer”.</blockquote>"""),
            ]),
            ("Aplicación", [
                ("Aplicación en techos y fachadas", 8, """
<ol><li>Limpiar la superficie: sin polvo, grasa, hongos ni partes sueltas.</li><li>Reparar previamente las fisuras grandes y las grietas.</li><li>Preparar o sellar la superficie según la ficha técnica.</li><li>Aplicar en capas, cruzando la dirección entre una mano y otra.</li><li>Respetar el tiempo de secado y no aplicar si se espera lluvia.</li></ol>"""),
            ]),
        ],
        "questions": [
            ("¿Qué propiedad describe mejor a un recubrimiento elastomérico?", ["Es rígido", "Es flexible", "Es un solvente", "Es un empaste"], 1, ""),
            ("¿Qué significa que sea hidrorepelente?", ["Que atrae la humedad", "Que repele el agua", "Que se diluye con agua", "Que seca bajo el agua"], 1, ""),
            ("¿Qué hace el elastomérico con las microfisuras?", ["Las agranda", "Las puentea o cubre", "No las afecta", "Las rellena de cemento"], 1, ""),
            ("¿En qué superficies se recomienda?", ["Fachadas y techos", "Muebles de madera", "Vidrios", "Pisos interiores"], 0, ""),
            ("¿Qué se debe hacer con las fisuras grandes antes de aplicar?", ["Nada", "Repararlas previamente", "Pintarlas de otro color", "Cubrirlas con silicón"], 1, ""),
            ("¿Cuándo NO se debe aplicar el producto?", ["En la mañana", "Cuando se espera lluvia", "Sobre una superficie limpia", "Después de reparar fisuras"], 1, ""),
        ],
    },
    {
        "title": "Siliconas Induless: sellado profesional",
        "brand": "induless", "category": "Siliconas", "level": "basico", "featured": True,
        "image": "silicon", "products": ["Silicón Induless"],
        "summary": "Aprende a recomendar y aplicar silicón Induless para lograr juntas limpias, flexibles y duraderas.",
        "description": "El sellado de juntas es una de las consultas más frecuentes en ferretería. Este curso te enseña a orientar al cliente y a explicar la aplicación paso a paso.",
        "outcomes": "Identificar los usos más comunes del silicón\nExplicar la preparación de la junta\nGuiar la aplicación de un cordón continuo\nEvitar los errores más frecuentes",
        "modules": [
            ("Conociendo el silicón", [
                ("Usos del silicón en obra y hogar", 5, """
<p>El silicón forma un <strong>cordón flexible</strong> que sella uniones entre materiales y evita el paso de agua y aire.</p>
<ul><li>Ventanas y vidrios.</li><li>Juntas de lavamanos, duchas y mesones.</li><li>Uniones en canaletas y cubiertas.</li></ul>
<p>Pregunta siempre <strong>qué materiales</strong> va a unir el cliente y si la junta estará expuesta al agua; así recomiendas el producto adecuado.</p>"""),
            ]),
            ("Aplicación", [
                ("Cómo lograr un cordón perfecto", 7, """
<ol><li>La superficie debe estar <strong>limpia y seca</strong>, sin restos de silicón viejo.</li><li>Colocar <strong>cinta de enmascarar</strong> a ambos lados de la junta para un acabado recto.</li><li>Cortar la boquilla en diagonal (45°) al ancho de la junta.</li><li>Aplicar con pistola un <strong>cordón continuo</strong>, con presión constante.</li><li>Alisar el cordón y <strong>retirar la cinta</strong> antes de que el silicón forme piel.</li><li>Respetar el tiempo de curado antes de exponerlo al agua.</li></ol>"""),
            ]),
        ],
        "questions": [
            ("¿Cuál es la función principal del silicón?", ["Pegar ladrillos", "Sellar juntas de forma flexible", "Pintar paredes", "Nivelar pisos"], 1, ""),
            ("¿Cómo debe estar la superficie antes de aplicar silicón?", ["Húmeda", "Limpia y seca", "Con polvo", "Recién pintada"], 1, ""),
            ("¿Para qué sirve la cinta de enmascarar?", ["Para acelerar el secado", "Para lograr un acabado recto y limpio", "Para reemplazar el silicón", "No tiene utilidad"], 1, ""),
            ("¿Cómo se corta la boquilla del cartucho?", ["Recta y muy pequeña", "En diagonal al ancho de la junta", "No se corta", "En forma de cruz"], 1, ""),
            ("¿Cuándo se retira la cinta de enmascarar?", ["Al día siguiente", "Antes de que el silicón forme piel", "Nunca", "Antes de aplicar el silicón"], 1, ""),
            ("¿Qué pregunta ayuda a recomendar el silicón correcto?", ["¿Qué materiales va a unir?", "¿De qué color es su casa?", "¿Cuántos años tiene?", "¿Dónde compró la pistola?"], 0, ""),
        ],
    },
    {
        "title": "Induzinc: cubiertas metálicas e instalación",
        "brand": "induless", "category": "Techos y Cubiertas", "level": "intermedio",
        "image": "induzinc", "products": ["Induzinc", "Clavos Induless"],
        "summary": "Conoce las planchas Induzinc de acero galvanizado y las buenas prácticas de instalación que debes explicar al cliente.",
        "description": "Las cubiertas metálicas son una solución liviana y rápida. Aprende sus ventajas y los puntos clave de una instalación correcta.",
        "outcomes": "Explicar qué es el acero galvanizado\nDescribir las ventajas de una cubierta metálica\nIndicar dónde y cómo fijar las planchas\nRecomendar accesorios complementarios",
        "modules": [
            ("Cubiertas metálicas", [
                ("Qué es Induzinc y por qué el galvanizado", 6, """
<p>Induzinc son planchas onduladas de <strong>acero galvanizado</strong>. El galvanizado es un <strong>recubrimiento de zinc</strong> que protege al acero contra la corrosión.</p>
<ul><li>Son <strong>livianas</strong>: requieren estructuras más sencillas.</li><li>Se instalan <strong>rápido</strong>.</li><li>Son ideales para viviendas, bodegas, galpones y patios.</li></ul>"""),
            ]),
            ("Instalación", [
                ("Buenas prácticas de instalación", 8, """
<ol><li>Respetar la <strong>pendiente mínima</strong> indicada por el fabricante para que el agua escurra.</li><li>Instalar las planchas en sentido contrario al viento predominante.</li><li>Respetar los <strong>traslapes</strong> laterales y longitudinales.</li><li>Fijar siempre en la <strong>cresta de la onda</strong> (parte alta), nunca en el valle, usando fijaciones con arandela.</li><li>Complementar con <strong>silicón</strong> en uniones y remates.</li></ol>
<blockquote>Venta cruzada: planchas + clavos o tornillos con arandela + silicón Induless.</blockquote>"""),
            ]),
        ],
        "questions": [
            ("¿Qué protege al acero en una plancha galvanizada?", ["Una capa de pintura", "Un recubrimiento de zinc", "Un plástico", "Nada"], 1, ""),
            ("¿Cuál es una ventaja de las cubiertas metálicas?", ["Son muy pesadas", "Son livianas y rápidas de instalar", "No necesitan fijación", "Solo sirven en interiores"], 1, ""),
            ("¿Dónde se debe fijar la plancha ondulada?", ["En el valle de la onda", "En la cresta de la onda", "En cualquier parte", "Solo en los bordes"], 1, "Fijar en la cresta evita que el agua se filtre por la perforación."),
            ("¿Por qué es importante la pendiente del techo?", ["Para que el agua escurra", "Por estética únicamente", "No es importante", "Para ahorrar clavos"], 0, ""),
            ("¿Qué tipo de fijación se recomienda?", ["Sin arandela", "Con arandela", "Pegamento escolar", "Cinta adhesiva"], 1, ""),
            ("¿Qué producto complementa la instalación en uniones y remates?", ["Silicón", "Empaste", "Pintura mate", "Sellador acrílico"], 0, ""),
        ],
    },
    {
        "title": "Venta consultiva en el punto de venta",
        "brand": "corporativo", "category": "Habilidades Comerciales", "level": "basico", "featured": True,
        "image": None, "products": [],
        "summary": "Técnicas prácticas para descubrir necesidades, convertir características en beneficios y cerrar más ventas en ferreterías y distribuidores.",
        "description": "Vender no es recitar características: es entender el problema del cliente y ofrecerle la mejor solución. Este curso te da herramientas simples para hacerlo todos los días.",
        "outcomes": "Hacer preguntas que descubren la necesidad real\nTransformar características en beneficios\nResponder objeciones de precio\nAumentar el ticket con venta cruzada",
        "modules": [
            ("Escuchar antes de vender", [
                ("Las preguntas que abren la venta", 6, """
<p>Un buen asesor <strong>pregunta más de lo que habla</strong>. Usa preguntas abiertas para entender la situación:</p>
<ul><li><strong>Situación:</strong> ¿qué va a pintar o sellar?, ¿interior o exterior?</li><li><strong>Problema:</strong> ¿qué le pasó con el producto anterior?</li><li><strong>Necesidad:</strong> ¿qué resultado espera?, ¿cuánto tiempo quiere que dure?</li></ul>"""),
                ("De la característica al beneficio", 6, """
<p>El cliente no compra características, compra <strong>beneficios</strong>. Usa la fórmula <strong>Característica → Ventaja → Beneficio</strong>:</p>
<blockquote>“Duralin es <strong>altamente lavable</strong> (característica), las manchas salen con un paño húmedo (ventaja), así su pared se ve como nueva por más tiempo y no tiene que volver a pintar pronto (beneficio)”.</blockquote>"""),
            ]),
            ("Cerrar y fidelizar", [
                ("Manejo de objeciones de precio", 6, """
<p>Cuando el cliente dice “está caro”, no bajes el precio de inmediato. Habla de <strong>valor</strong>:</p>
<ul><li>Compara el <strong>rendimiento</strong>: un producto que cubre más necesita menos galones.</li><li>Compara la <strong>duración</strong>: pintar menos veces es ahorrar.</li><li>Pregunta: “¿Qué es lo más importante para usted en este trabajo?”.</li></ul>"""),
                ("Venta cruzada inteligente", 5, """
<p>La venta cruzada ayuda al cliente a lograr un mejor resultado:</p>
<ul><li>Pintura + <strong>sellador</strong> + empaste + rodillos.</li><li>Cubierta Induzinc + <strong>fijaciones con arandela</strong> + silicón.</li></ul>
<p>Recomienda solo lo que el trabajo realmente necesita: así generas confianza y el cliente regresa.</p>"""),
            ]),
        ],
        "questions": [
            ("¿Qué debe hacer primero un buen asesor?", ["Hablar del precio", "Hacer preguntas para entender la necesidad", "Ofrecer el producto más caro", "Mostrar el catálogo completo"], 1, ""),
            ("¿Qué compra realmente el cliente?", ["Características", "Beneficios", "Envases", "Marcas"], 1, ""),
            ("En la fórmula C-V-B, ¿qué significa la B?", ["Bodega", "Beneficio", "Brillo", "Base"], 1, ""),
            ("Ante la objeción “está caro”, ¿qué es recomendable?", ["Bajar el precio de inmediato", "Hablar del valor: rendimiento y duración", "Terminar la conversación", "Recomendar otra tienda"], 1, ""),
            ("¿Cuál es un ejemplo de venta cruzada correcta?", ["Pintura + sellador", "Pintura + juguete", "Silicón + comida", "Clavos + perfume"], 0, ""),
            ("¿Por qué recomendar solo lo que el trabajo necesita?", ["Para vender menos", "Para generar confianza y que el cliente regrese", "Porque es obligatorio", "No importa"], 1, ""),
        ],
    },
]

PATHS = [
    {
        "title": "Asesor experto en pinturas Latina", "brand": "latina",
        "summary": "Domina la línea de pinturas de Industrial Latina: acabados, preparación de superficies y protección de fachadas.",
        "description": "Recomendada para ejecutivos que atienden ferreterías y distribuidores de pintura.",
        "courses": [0, 1, 2],
    },
    {
        "title": "Especialista Induless", "brand": "induless",
        "summary": "Siliconas, cubiertas Induzinc y fijaciones: todo lo que necesitas para asesorar en techos y sellado.",
        "description": "Ideal para el equipo que atiende la línea de construcción liviana.",
        "courses": [3, 4],
    },
    {
        "title": "Vendedor estrella", "brand": "corporativo",
        "summary": "Combina técnicas de venta consultiva con el producto estrella de la marca.",
        "description": "Un programa corto para mejorar la conversión en el punto de venta.",
        "courses": [5, 0],
    },
]

DEMO_SUPERVISORS = [("fabarca", "Fernando", "Abarca"), ("pmolina", "Patricia", "Molina")]
DEMO_USERS = [
    ("mcevallos", "María José", "Cevallos", "Fernando Abarca", "Guayaquil"),
    ("cmora", "Carlos Andrés", "Mora", "Fernando Abarca", "Guayaquil"),
    ("dparedes", "Daniela", "Paredes", "Fernando Abarca", "Machala"),
    ("lvera", "Luis Fernando", "Vera", "Fernando Abarca", "Manta"),
    ("asalazar", "Andrea", "Salazar", "Patricia Molina", "Quito"),
    ("jintriago", "Jorge Luis", "Intriago", "Patricia Molina", "Portoviejo"),
    ("gtorres", "Gabriela", "Torres", "Patricia Molina", "Cuenca"),
    ("kzambrano", "Kevin", "Zambrano", "Patricia Molina", "Quito"),
]
