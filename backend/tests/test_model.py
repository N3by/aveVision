from app.data.species_data import get_species_info


def test_get_species_info_known():
    info = get_species_info("mirlo_comun")
    assert info["especie"] == "Mirlo Común"
    assert info["nombre_cientifico"] == "Turdus merula"
    assert len(info["datos_curiosos"]) == 3


def test_get_species_info_unknown_returns_fallback():
    info = get_species_info("nonexistent_bird")
    assert "no identificada" in info["especie"]
