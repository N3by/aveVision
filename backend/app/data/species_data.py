# Map model output class labels → species display info.
# Populate this dict with your actual classes once the model is trained.
# Keys must exactly match what model.predict() returns.
SPECIES_DATA: dict[str, dict] = {
    "mirlo_comun": {
        "especie": "Mirlo Común",
        "nombre_cientifico": "Turdus merula",
        "descripcion": (
            "El mirlo común es un ave paseriforme de la familia Turdidae, "
            "conocida por su plumaje negro brillante en los machos y su melodioso canto."
        ),
        "datos_curiosos": [
            "El macho adulto tiene un pico y anillo orbital de color amarillo-naranja intenso.",
            "Es capaz de imitar los sonidos de otras aves e incluso sonidos artificiales.",
            "Puede vivir hasta 5 años en estado salvaje y más de 20 en cautividad.",
        ],
    },
    # Add more species here matching your model's class labels
}

_FALLBACK = {
    "especie": "Ave no identificada",
    "nombre_cientifico": "Especie desconocida",
    "descripcion": "Esta especie no se encuentra en la base de datos actual.",
    "datos_curiosos": ["Agrega esta especie al diccionario SPECIES_DATA."],
}


def get_species_info(class_label: str) -> dict:
    return SPECIES_DATA.get(class_label, _FALLBACK)
