from app.data.species_data import get_species_info


def test_get_species_info_known():
    info = get_species_info("mirlo_comun")
    assert info["especie"] == "Mirlo Común"
    assert info["nombre_cientifico"] == "Turdus merula"
    assert len(info["datos_curiosos"]) == 3


def test_get_species_info_unknown_returns_fallback():
    info = get_species_info("nonexistent_bird")
    assert "no identificada" in info["especie"]


def test_classify_response_schema():
    from app.schemas.classify import ClassifyResponse, Metrics
    resp = ClassifyResponse(
        especie="Mirlo Común",
        nombre_cientifico="Turdus merula",
        confianza=0.91,
        descripcion="Descripción de prueba.",
        datos_curiosos=["Hecho 1", "Hecho 2"],
        metrics=Metrics(latency_ms=142, ram_mb=48.2, cpu_percent=12.4),
    )
    assert resp.confianza == 0.91
    assert resp.metrics.latency_ms == 142
