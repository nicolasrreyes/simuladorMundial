# Simulador Mundial 2026

Aplicacion FastAPI + frontend HTML/CSS/JavaScript para simular un Mundial 2026 con sorteo de grupos, fase de grupos, eliminacion directa, dashboard ejecutivo y estadisticas avanzadas.

## Funcionalidades

- ABM de equipos y jugadores.
- Seed automatico de 32 selecciones clasificadas priorizadas por ranking FIFA.
- Sorteo de grupos con restriccion de confederaciones.
- Simulacion completa: fase de grupos, octavos, cuartos, semifinal y final.
- Estadisticas de goleadores, asistidores, penales y mejor jugador del torneo.
- Dashboard ejecutivo con campeon, Botin de Oro y promedio de goles.
- Frontend servido por FastAPI.

## Requisitos

```bash
python -m pip install -r requirements.txt
```

## Ejecutar

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Abrir:

```text
http://127.0.0.1:8000/
```

## Tests

```bash
python -m pytest -q
```

## Informe QA

El informe ejecutivo de QA esta disponible en:

```text
reports/qa_report.html
```
