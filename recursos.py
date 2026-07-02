from __future__ import annotations

import os
import sys
from pathlib import Path


def caminho_recurso(*partes: str) -> Path:
    """Retorna caminho de arquivo em execução normal ou bundle PyInstaller."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base.joinpath(*partes)


def caminho_configuracoes_usuario() -> Path:
    """Mantém preferências persistentes fora do bundle quando empacotado."""
    if not getattr(sys, "frozen", False):
        return caminho_recurso("configuracoes.json")

    pasta_base = os.environ.get("APPDATA")
    pasta = (
        Path(pasta_base) / "PyCalc"
        if pasta_base
        else Path.home() / ".pycalc"
    )
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta / "configuracoes.json"
