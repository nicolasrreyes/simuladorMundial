# Deploy y Publicacion en GitHub

Este documento describe la configuracion y el flujo recomendado para publicar el proyecto **Simulador Mundial 2026** en GitHub y compartir cada actualizacion.

## Repositorio remoto

```text
https://github.com/nicolasrreyes/simuladorMundial.git
```

Remote local esperado:

```bash
git remote -v
```

Debe mostrar:

```text
origin  https://github.com/nicolasrreyes/simuladorMundial.git (fetch)
origin  https://github.com/nicolasrreyes/simuladorMundial.git (push)
```

## Rama principal

La rama principal del proyecto es:

```text
main
```

## Primer deploy a GitHub

Si el repositorio local ya tiene commits y el remote configurado:

```bash
git push -u origin main
```

## Flujo para publicar actualizaciones

Cada vez que hagas cambios en el proyecto:

```bash
git status
git add .
git commit -m "Descripcion breve del cambio"
git push origin main
```

Ejemplo:

```bash
git add .
git commit -m "Actualiza dashboard de metricas del Mundial"
git push origin main
```

## Verificacion antes de publicar

Antes de subir cambios, ejecutar:

```bash
python -m pytest -q
```

Resultado esperado:

```text
12 passed
```

Tambien se puede validar que la app levante localmente:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Abrir:

```text
http://127.0.0.1:8000/
```

## Compartir el proyecto

Una vez publicado, compartir:

```text
https://github.com/nicolasrreyes/simuladorMundial
```

## Notas importantes

- GitHub aloja el codigo fuente del proyecto.
- Este proyecto es una aplicacion FastAPI, por lo que GitHub Pages no ejecuta el backend.
- Para compartir una demo ejecutable en la web se recomienda desplegar en un servicio compatible con Python/FastAPI, por ejemplo Render, Railway, Fly.io o Azure App Service.
- El informe QA queda versionado en `reports/qa_report.html`.
