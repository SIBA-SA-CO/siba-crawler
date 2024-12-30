# src/scrapers/__init__.py
import pkgutil
import inspect
import importlib
from .base_scraper import BaseScraper

def discover_scrapers():
    """
    Detecta automáticamente todas las clases de scrapers en el módulo `scrapers`
    que heredan de `BaseScraper`.
    """
    scrapers = {}
    package = __name__  # Nombre del paquete actual (src.scrapers)

    # Explora todos los módulos en el paquete
    for _, module_name, _ in pkgutil.iter_modules(__path__):
        # Importa el módulo dinámicamente
        module = importlib.import_module(f"{package}.{module_name}")
        # Busca todas las clases dentro del módulo
        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Verifica que la clase hereda de BaseScraper y pertenece al módulo actual
            if issubclass(obj, BaseScraper) and obj.__module__ == module.__name__:
                # Usa el nombre del canal como clave (ej: "bvn", "npo", etc.)
                scrapers[obj.__name__.lower()] = obj

    return scrapers
