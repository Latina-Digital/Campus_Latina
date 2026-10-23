// =====================================================================
// CAMPUS LATINA (versión nueva) - código para agregar a la API Syspro
// ---------------------------------------------------------------------
// Son 3 partes. Cada una va en un lugar distinto del proyecto de la API:
//   1. La clase CampusDatosDto      -> junto a los otros DTO (CategoriaDto, ModuloDto, ...)
//   2. El método del controlador    -> en el controlador, junto a GestionConfiguracion
//   3. El método de datos           -> en la clase SalesOrder, junto a GestionarConfiguracionAsync
//
// Antes, ejecutar 01_campus_nuevo.sql en la base CAMPUS.
// No cambia nada de lo que ya existe: el campus anterior sigue funcionando igual.
// =====================================================================


// ---------------------------------------------------------------------
// 1. DTO
// ---------------------------------------------------------------------
public class CampusDatosDto
{
    public string ApiKey { get; set; }
    public string Accion { get; set; }   // CONSULTAR, CREAR, MODIFICAR, ELIMINAR
    public string tabla { get; set; }    // tabla sin el prefijo CV_, ej: "Cursos" -> dbo.CV_Cursos
    public int id { get; set; }
    public string filtro { get; set; }   // texto JSON, ej: "{\"user_id\":5}"
    public string datos { get; set; }    // texto JSON, ej: "{\"title\":\"Duralin\"}"
}


// ---------------------------------------------------------------------
// 2. CONTROLADOR
// ---------------------------------------------------------------------
[HttpPost]
[Route("api/syspro/campus/datos")]
public async Task<IActionResult> GestionDatosCampus([FromBody] CampusDatosDto req)
{
    try
    {
        var apiKey = integration.ApiKeys?
        .Where(e => e.Id == req.ApiKey)
        .FirstOrDefault();

        if (apiKey == null)
            return Unauthorized(new { mensaje = "Acceso no autorizado. API Key inválida." });

        var _campusData = new SalesOrder();

        var resultado = await _campusData.GestionarDatosCampusAsync(req);
        return Ok(resultado);
    }
    catch (DbException ex)
    {
        // Errores de datos (tabla o columna no válida, registro duplicado, etc.):
        // se devuelven como 400 con el mensaje de SQL Server para que el campus lo muestre.
        _logger.LogWarning(ex, "Error de datos en api/syspro/campus/datos ({Tabla} {Accion})", req?.tabla, req?.Accion);
        return BadRequest(new { mensaje = ex.Message });
    }
    catch (Exception ex)
    {
        _logger.LogError(ex, "Error en api/syspro/campus/datos");
        return this.Problem(ex.Message);
    }
}


// ---------------------------------------------------------------------
// 3. CLASE SalesOrder
// ---------------------------------------------------------------------
// Devuelve las filas como lista de diccionarios (columna -> valor), así sirve
// para cualquier tabla sin crear una clase por cada una.
// Requiere: using System.Data; using System.Data.Common;  (ya los usan los otros métodos)
public async Task<List<Dictionary<string, object>>> GestionarDatosCampusAsync(CampusDatosDto req)
{
    var lista = new List<Dictionary<string, object>>();
    DbConnection conn = dbc.Database.GetDbConnection();
    bool cerrarAlFinal = conn.State != ConnectionState.Open;
    if (cerrarAlFinal) await conn.OpenAsync();

    try
    {
        await using DbCommand cmd = conn.CreateCommand();
        cmd.CommandText = "dbo.spCampus_Datos";
        cmd.CommandType = CommandType.StoredProcedure;
        cmd.CommandTimeout = 120;

        AddParam(cmd, "@Accion", DbType.AnsiString, req.Accion ?? "CONSULTAR");
        AddParam(cmd, "@Tabla", DbType.String, req.tabla ?? "");
        AddParam(cmd, "@Id", DbType.Int32, req.id);
        AddParam(cmd, "@Filtro", DbType.String, req.filtro);
        AddParam(cmd, "@Datos", DbType.String, req.datos);

        await using DbDataReader rdr = await cmd.ExecuteReaderAsync();
        while (await rdr.ReadAsync())
        {
            var fila = new Dictionary<string, object>(rdr.FieldCount);
            for (int i = 0; i < rdr.FieldCount; i++)
                fila[rdr.GetName(i)] = rdr.IsDBNull(i) ? null : rdr.GetValue(i);
            lista.Add(fila);
        }
    }
    finally
    {
        if (cerrarAlFinal) await conn.CloseAsync();
    }
    return lista;
}
