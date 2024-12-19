# SIBA CRAWLER

Este proyecto crea una herramienta para recuperar los datos de la programación de canales para la empresa SIBA S.A.


# Ejecutar El Proyecto

```
$ docker exec -it siba-crawler /bin/bash -c "source /var/www/app/.venv/bin/activate && python main.py --initial_date '[YYYY-MM-DD]' --days_range [number] --channel '[channel_id]'"
```