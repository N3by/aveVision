SPECIES_DATA: dict[str, dict] = {
    "canary": {
        "especie": "Canario",
        "nombre_cientifico": "Serinus canaria",
        "descripcion": (
            "El canario es un ave paseriforme originaria de las Islas Canarias, Azores y Madeira. "
            "Es famoso por su melodioso canto y su plumaje amarillo brillante, aunque también existen "
            "variedades de otros colores producto de la cría selectiva."
        ),
        "datos_curiosos": [
            "Los canarios machos son los principales cantores; las hembras rara vez cantan.",
            "Pueden aprender a imitar melodías complejas y se han usado históricamente en minas para detectar gases tóxicos.",
            "Su esperanza de vida en cautividad es de 10 a 15 años.",
        ],
    },
    "magpie": {
        "especie": "Urraca",
        "nombre_cientifico": "Pica pica",
        "descripcion": (
            "La urraca es un ave de la familia Corvidae, reconocible por su plumaje blanco y negro con "
            "reflejos iridiscentes azul-verdosos. Es una de las aves más inteligentes del mundo y la única "
            "ave no mamífera que supera la prueba del espejo de reconocimiento propio."
        ),
        "datos_curiosos": [
            "Las urracas construyen nidos con techo para protegerse de depredadores.",
            "Tienen memoria excepcional y pueden reconocer rostros humanos individuales.",
            "Son omnívoras y acumulan alimento enterrándolo para consumirlo posteriormente.",
        ],
    },
    "mockingbird": {
        "especie": "Sinsonte",
        "nombre_cientifico": "Mimus polyglottos",
        "descripcion": (
            "El sinsonte norteño es célebre por su extraordinaria capacidad de imitar los cantos de otras aves "
            "y sonidos del entorno. Un solo individuo puede reproducir más de 200 cantos distintos a lo largo "
            "de su vida, cantando incluso de noche durante la temporada de reproducción."
        ),
        "datos_curiosos": [
            "Un macho adulto puede imitar hasta 200 tipos de sonidos diferentes, incluyendo ranas y grillos.",
            "Defienden su territorio agresivamente y no dudan en atacar a animales mucho más grandes.",
            "Inspiraron el título de la novela clásica 'To Kill a Mockingbird' de Harper Lee.",
        ],
    },
    "nightingale": {
        "especie": "Ruiseñor",
        "nombre_cientifico": "Luscinia megarhynchos",
        "descripcion": (
            "El ruiseñor es un pequeño paseriforme famoso por su canto nocturno excepcionalmente rico y melodioso. "
            "A pesar de su apariencia discreta — plumaje pardo y cola rojiza —, su voz ha inspirado poetas, "
            "compositores y escritores durante siglos en toda Europa y Asia."
        ),
        "datos_curiosos": [
            "Solo los machos cantan, principalmente de noche para atraer hembras durante la migración.",
            "Su canto incluye más de 1000 variaciones de frases y puede escucharse a 1 km de distancia.",
            "Migra anualmente desde Europa hasta África subsahariana, un viaje de más de 5000 km.",
        ],
    },
    "robin": {
        "especie": "Petirrojo",
        "nombre_cientifico": "Erithacus rubecula",
        "descripcion": (
            "El petirrojo europeo es uno de los pájaros más reconocibles y queridos de Europa, famoso por su "
            "característico pecho naranja-rojizo. Es un ave territorial y valiente que no duda en enfrentarse "
            "a intrusos mucho mayores para defender su zona."
        ),
        "datos_curiosos": [
            "Los petirrojos utilizan campos magnéticos de la Tierra para orientarse durante la migración.",
            "Son una de las pocas aves que cantan durante el invierno, incluyendo de noche en zonas urbanas.",
            "Tienen fama de acercarse a jardineros en busca de lombrices recién expuestas por la tierra removida.",
        ],
    },
    "tanager": {
        "especie": "Tángara",
        "nombre_cientifico": "Thraupidae spp.",
        "descripcion": (
            "Las tángaras son una familia de aves neotropicales conocidas por su extraordinaria variedad de "
            "colores. Con más de 370 especies, representan una de las familias de aves más diversas del "
            "Neotrópico y son un indicador clave de la salud de los ecosistemas boscosos."
        ),
        "datos_curiosos": [
            "Muchas especies presentan dimorfismo sexual marcado: los machos tienen colores vibrantes y las hembras son más discretas.",
            "Se alimentan principalmente de frutas, siendo importantes dispersores de semillas en bosques tropicales.",
            "La tángara escarlata puede recorrer miles de kilómetros en su migración anual entre Norteamérica y Sudamérica.",
        ],
    },
}

_FALLBACK = {
    "especie": "Ave no identificada",
    "nombre_cientifico": "Especie desconocida",
    "descripcion": "Esta especie no se encuentra en la base de datos actual.",
    "datos_curiosos": ["Agrega esta especie al diccionario SPECIES_DATA."],
}


def get_species_info(class_label: str) -> dict:
    return SPECIES_DATA.get(class_label, _FALLBACK)
