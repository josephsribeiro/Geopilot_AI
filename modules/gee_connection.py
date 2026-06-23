"""
GeoPilot AI — Utilitários de conexão GEE
"""


def is_gee_connected() -> bool:
    """Verifica se o GEE está inicializado e funcional."""
    try:
        import ee  # type: ignore
        result = ee.Number(1).add(1).getInfo()
        return result == 2
    except Exception:
        return False


def get_gee_asset_list(asset_path: str = "users") -> list:
    """Lista assets disponíveis no GEE para o usuário."""
    try:
        import ee  # type: ignore
        assets = ee.data.listAssets({"parent": f"projects/{asset_path}"})
        return assets.get("assets", [])
    except Exception:
        return []
