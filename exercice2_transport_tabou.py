"""Compatibilité : l'implémentation est désormais dans :mod:`td2`."""

from td2.exercice2_transport_tabou import *  # noqa: F401,F403

if __name__ == "__main__":
    import runpy
    runpy.run_module("td2.exercice2_transport_tabou", run_name="__main__")
