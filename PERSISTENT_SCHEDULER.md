# Persistent Scheduler Implementation

## Resumen

Se ha implementado un sistema de scheduling persistente que garantiza que los spiders se ejecuten **al menos cada 4 horas**, incluso cuando el contenedor Docker se detiene y reinicia, o cuando el PC se apaga o suspende.

## Problema Identificado

El sistema anterior tenía las siguientes limitaciones:

1. **APScheduler no persiste estado**: Usaba `IntervalTrigger(hours=4)` que solo cuenta desde que el scheduler está activo. Si el contenedor se detenía, no había memoria de cuándo fue la última ejecución.

2. **Sin verificación de tiempo transcurrido**: Al reiniciar, el scheduler esperaba 4 horas completas antes de ejecutar, sin importar cuánto tiempo había pasado desde la última ejecución real.

3. **Docker restart policy insuficiente**: `restart: unless-stopped` solo reinicia el contenedor si falla, no cuando el PC se apaga.

### Ejemplo del Problema

**Escenario anterior**:
- Última ejecución: Lunes 10:00 AM
- PC se apaga: Lunes 11:00 AM
- PC se enciende: Lunes 6:00 PM (7 horas después)
- **Resultado**: Scheduler espera hasta Lunes 10:00 PM para ejecutar (4 horas desde reinicio)
- **Total sin ejecutar**: 12 horas ❌

## Solución Implementada

### 1. Persistencia en PostgreSQL

Se creó una tabla `scheduler_state` que registra cada ejecución:

```sql
CREATE TABLE scheduler_state (
    id SERIAL PRIMARY KEY,
    last_run_at TIMESTAMP WITH TIME ZONE NOT NULL,
    spider_count INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL,  -- 'running', 'completed', 'failed'
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
```

### 2. Lógica de Verificación al Inicio

El scheduler ahora:

1. **Consulta la base de datos** al iniciar para obtener `last_run_at`
2. **Calcula el tiempo transcurrido** desde la última ejecución exitosa
3. **Ejecuta inmediatamente** si han pasado ≥ 4 horas
4. **Espera el tiempo restante** si han pasado < 4 horas

### 3. Script de Migración Automática

Se agregó `docker-entrypoint.sh` que:
- Espera a que PostgreSQL esté disponible
- Ejecuta migraciones SQL automáticamente
- Inicia el scheduler

## Archivos Modificados/Creados

### Modificados

1. **`src/jobsearchtools/scheduler.py`**
   - Añadido `_get_db_connection()`: Maneja conexión a PostgreSQL
   - Añadido `_get_last_run_time()`: Lee última ejecución de la BD
   - Añadido `_update_last_run_time()`: Persiste estado de ejecución
   - Añadido `_should_run_now()`: Verifica si debe ejecutar inmediatamente
   - Modificado `run_spiders()`: Registra estado (running/completed/failed)
   - Modificado `start()`: Usa lógica de verificación de tiempo
   - Modificado `shutdown()`: Cierra conexión a BD

2. **`Dockerfile`**
   - Añadido `postgresql-client` para ejecutar migraciones
   - Copiado `docker-entrypoint.sh`
   - Cambiado `CMD` a `ENTRYPOINT` para usar script personalizado

### Creados

3. **`src/jobsearchtools/job_scraper/job_scraper/migrations/001_create_scheduler_state.sql`**
   - Migración para crear tabla `scheduler_state`
   - Crea índice en `last_run_at` para optimizar consultas
   - Inserta estado inicial (hace 5 horas para forzar primera ejecución)

4. **`docker-entrypoint.sh`**
   - Script de inicialización del contenedor
   - Espera a PostgreSQL
   - Ejecuta migraciones automáticamente
   - Inicia el scheduler

5. **`tests/test_scheduler_persistence.py`**
   - Suite completa de tests unitarios
   - Cobertura de todos los nuevos métodos
   - Tests de casos edge (sin ejecución previa, exactamente en threshold, etc.)

## Flujo de Ejecución

```
┌─────────────────────────────────────────┐
│ Contenedor Docker Inicia                │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ docker-entrypoint.sh                    │
│ - Espera PostgreSQL                     │
│ - Ejecuta migraciones SQL               │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ SpiderScheduler.__init__()              │
│ - Crea conexión a BD                    │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ SpiderScheduler.start()                 │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ _should_run_now()                       │
│ ¿Han pasado ≥ 4 horas?                  │
└──────┬──────────────────────┬───────────┘
       │ SÍ                   │ NO
       ▼                      ▼
┌────────────┐      ┌──────────────────┐
│ Ejecutar   │      │ Esperar según    │
│ AHORA      │      │ schedule (4h)    │
└────────────┘      └──────────────────┘
       │                      │
       ▼                      ▼
┌─────────────────────────────────────────┐
│ run_spiders()                           │
│ 1. UPDATE status='running'              │
│ 2. Ejecutar spiders                     │
│ 3. UPDATE status='completed' o 'failed' │
└─────────────────────────────────────────┘
```

## Casos de Uso Probados

### Caso 1: Primera Ejecución
- **Estado**: No hay registros en `scheduler_state`
- **Resultado**: Ejecuta inmediatamente ✅

### Caso 2: PC Apagado Durante Mucho Tiempo
- **Estado**: Última ejecución hace 8 horas
- **Threshold**: 4 horas
- **Resultado**: Ejecuta inmediatamente al reiniciar ✅

### Caso 3: Reinicio Rápido
- **Estado**: Última ejecución hace 2 horas
- **Threshold**: 4 horas
- **Resultado**: Espera 2 horas más antes de ejecutar ✅

### Caso 4: Exactamente en el Threshold
- **Estado**: Última ejecución hace exactamente 4 horas
- **Resultado**: Ejecuta inmediatamente ✅

### Caso 5: Falla en Ejecución
- **Estado**: Spider falla durante ejecución
- **Resultado**: Registra estado `failed` en BD, scheduler continúa operando ✅

## Cómo Probar

### 1. Construir y Levantar Contenedores

```powershell
# Construir imagen
docker-compose build

# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f scheduler
```

### 2. Verificar Migración

```powershell
# Conectarse a PostgreSQL
docker-compose exec postgres psql -U postgres -d jobsearchtools

# Verificar tabla
\d scheduler_state

# Ver registros
SELECT * FROM scheduler_state ORDER BY last_run_at DESC LIMIT 5;
```

### 3. Simular Apagado/Reinicio

```powershell
# Detener contenedor
docker-compose stop scheduler

# Esperar X minutos/horas

# Reiniciar contenedor
docker-compose start scheduler

# Verificar logs - debe calcular tiempo transcurrido
docker-compose logs scheduler | Select-String "Last run was"
```

### 4. Ejecutar Tests

```powershell
# Activar entorno virtual
.venv\Scripts\Activate.ps1

# Ejecutar tests del scheduler
.venv\Scripts\pytest.exe tests/test_scheduler_persistence.py -v

# Con coverage
.venv\Scripts\pytest.exe tests/test_scheduler_persistence.py --cov=jobsearchtools.scheduler --cov-report=html
```

## Configuración

### Variables de Entorno (`.env`)

```bash
# Scheduler Configuration
SCHEDULER_ENABLED=True
SCHEDULER_INTERVAL_HOURS=4  # Mínimo de horas entre ejecuciones
SCHEDULER_TIMEZONE=America/Bogota
SCHEDULER_MAX_INSTANCES=1

# Database Configuration (requerido para persistencia)
DB_HOST=postgres
DB_PORT=5432
DB_NAME=jobsearchtools
DB_USER=postgres
DB_PASSWORD=your_password
```

## Monitoreo

### Consultas Útiles de PostgreSQL

```sql
-- Última ejecución exitosa
SELECT last_run_at, spider_count, status
FROM scheduler_state
WHERE status = 'completed'
ORDER BY last_run_at DESC
LIMIT 1;

-- Historial de ejecuciones (últimas 24 horas)
SELECT
    last_run_at,
    spider_count,
    status,
    EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - last_run_at))/3600 AS hours_ago
FROM scheduler_state
WHERE last_run_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'
ORDER BY last_run_at DESC;

-- Contar ejecuciones por estado (último mes)
SELECT
    status,
    COUNT(*) as count,
    MIN(last_run_at) as first_run,
    MAX(last_run_at) as last_run
FROM scheduler_state
WHERE last_run_at > CURRENT_TIMESTAMP - INTERVAL '30 days'
GROUP BY status;

-- Verificar intervalos entre ejecuciones
SELECT
    last_run_at,
    LAG(last_run_at) OVER (ORDER BY last_run_at) as previous_run,
    EXTRACT(EPOCH FROM (
        last_run_at - LAG(last_run_at) OVER (ORDER BY last_run_at)
    ))/3600 AS hours_between
FROM scheduler_state
WHERE status = 'completed'
ORDER BY last_run_at DESC
LIMIT 10;
```

### Logs a Monitorear

```
# Inicio del scheduler
"Starting scheduler with 4 hour interval"

# Verificación de tiempo
"Last run was X.XX hours ago (required: 4 hours)"

# Decisión de ejecución
"Time threshold met or exceeded, running spiders immediately"
# o
"Recent run detected, skipping immediate execution"

# Estado de ejecución
"Starting spider run for N spider(s)"
"Spider run completed successfully"
```

## Notas Importantes

### Sincronización de Timezone

- Todos los timestamps se guardan en **UTC** en la base de datos
- El scheduler usa el timezone configurado en `SCHEDULER_TIMEZONE`
- Las comparaciones de tiempo se hacen correctamente considerando zonas horarias

### Manejo de Errores

- Si la consulta a la BD falla, el scheduler **asume que debe ejecutar** (comportamiento seguro)
- Si una ejecución falla, se registra como `failed` pero el scheduler continúa
- Las conexiones a la BD se reutilizan cuando es posible

### Rendimiento

- Conexión a BD se mantiene abierta durante la vida del scheduler (reutilización)
- Consultas optimizadas con índice en `last_run_at`
- Solo se consulta la BD al inicio y en cada ejecución (no polling constante)

## Próximos Pasos (Opcional)

1. **Alertas**: Implementar notificaciones si no hay ejecución exitosa en X horas
2. **Dashboard**: Visualizar historial de ejecuciones
3. **Limpieza automática**: Job para eliminar registros antiguos (> 90 días)
4. **Métricas**: Exportar datos a Prometheus/Grafana

## Créditos

- **Problema identificado**: Scheduling en entornos con interrupciones frecuentes
- **Solución**: Persistencia de estado en PostgreSQL + verificación inteligente
- **Fecha**: Noviembre 2025
