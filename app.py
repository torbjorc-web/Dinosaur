from flask import Flask, render_template, abort, request, url_for
import random
from catalog import CATEGORIES, DINOSAURS as DINOSAUR_DATA, QUIZ_TEXT, TEXT, localized_dinosaurs, localized_other_reptiles

app = Flask(__name__)

DINOSAURS = [
    {
        "slug": "tyrannosaurus-rex",
        "name": "Tyrannosaurus rex",
        "nickname": "T. rex",
        "period": "Sen kritt · ca. 68–66 millioner år siden",
        "diet": "Kjøtteter",
        "length": "Opptil 12 meter",
        "weight": "Opptil 8 tonn",
        "emoji": "🦖",
        "color": "coral",
        "description": "T. rex var en av de største landlevende rovdyrene. Den hadde kraftige bakbein, små armer og et enormt bitt. Fossiler viser at den levde i det som i dag er Nord-Amerika.",
        "fact": "Navnet betyr «kongeøglen» — selv om dinosaurer ikke var øgler."
    },
    {
        "slug": "triceratops",
        "name": "Triceratops",
        "nickname": "Den tret hornede",
        "period": "Sen kritt · ca. 68–66 millioner år siden",
        "diet": "Planteeter",
        "length": "Opptil 9 meter",
        "weight": "Opptil 12 tonn",
        "emoji": "🦕",
        "color": "sage",
        "description": "Triceratops hadde tre horn i ansiktet og en stor nakkekrage. Det kraftige nebbet hjalp den med å spise planter. Den levde samtidig med T. rex.",
        "fact": "Nakkekragen kan ha beskyttet nakken eller hjulpet dinosaurene med å kjenne igjen hverandre."
    },
    {
        "slug": "stegosaurus",
        "name": "Stegosaurus",
        "nickname": "Ryggplatene",
        "period": "Sen jura · ca. 155–150 millioner år siden",
        "diet": "Planteeter",
        "length": "Opptil 9 meter",
        "weight": "Opptil 5 tonn",
        "emoji": "🦕",
        "color": "gold",
        "description": "Stegosaurus er lett å kjenne igjen på de store platene langs ryggen og piggene på halen. Den hadde et lite hode og gikk på fire bein.",
        "fact": "Platene sto i to rekker langs ryggen, men forskere diskuterer fortsatt nøyaktig hva de ble brukt til."
    },
    {
        "slug": "brachiosaurus",
        "name": "Brachiosaurus",
        "nickname": "Den langhalsede kjempen",
        "period": "Sen jura · ca. 154–150 millioner år siden",
        "diet": "Planteeter",
        "length": "Opptil 26 meter",
        "weight": "Opptil 50 tonn",
        "emoji": "🦕",
        "color": "blue",
        "description": "Brachiosaurus var en enorm planteeter med lang hals og forbein som var lengre enn bakbeina. Den kunne nå blader høyt oppe i trærne.",
        "fact": "Navnet betyr «armøgle» og viser til de lange forbeina."
    },
    {
        "slug": "velociraptor",
        "name": "Velociraptor",
        "nickname": "Den raske jegeren",
        "period": "Sen kritt · ca. 75–71 millioner år siden",
        "diet": "Kjøtteter",
        "length": "Ca. 2 meter",
        "weight": "Ca. 15 kilo",
        "emoji": "🦖",
        "color": "lavender",
        "description": "Velociraptor var mye mindre enn mange tror, omtrent på størrelse med en stor kalkun. Den var rask, hadde skarpe tenner og en stor klo på hver fot.",
        "fact": "Fossiler tyder på at Velociraptor hadde fjær."
    },
    {
        "slug": "ankylosaurus",
        "name": "Ankylosaurus",
        "nickname": "Den pansrede",
        "period": "Sen kritt · ca. 68–66 millioner år siden",
        "diet": "Planteeter",
        "length": "Opptil 8 meter",
        "weight": "Opptil 8 tonn",
        "emoji": "🦕",
        "color": "mint",
        "description": "Ankylosaurus var dekket av beinplater som et naturlig panser. Halen endte i en tung klubbe, og den lave kroppen gjorde den vanskelig å velte.",
        "fact": "Den pansrede halen kunne brukes til å slå fra seg rovdyr."
    },
]


@app.get("/")
def index():
    lang = request.args.get("lang", "no")
    if lang not in ("no", "en"):
        lang = "no"
    return render_template("home.html", dinosaurs=localized_dinosaurs(lang), lang=lang, t=TEXT[lang], categories=CATEGORIES[lang])


@app.get("/kategori/<slug>")
def category_page(slug):
    lang = request.args.get("lang", "no")
    if lang not in ("no", "en"):
        lang = "no"
    categories = CATEGORIES[lang]
    if slug not in categories:
        abort(404)
    category = categories[slug]
    dinosaurs = localized_dinosaurs(lang)
    if category["kind"] == "plant":
        items = [dino for dino in dinosaurs if dino["diet_kind"] == "plant"]
    elif category["kind"] == "meat":
        items = [dino for dino in dinosaurs if dino["diet_kind"] == "meat"]
    elif category["kind"] == "land":
        items = dinosaurs
    else:
        items = localized_other_reptiles(category["kind"], lang)
    return render_template("category.html", items=items, slug=slug, category=category,
                           categories=categories, lang=lang, t=TEXT[lang])


@app.get("/dinosaur/<slug>")
def dinosaur_detail(slug):
    lang = request.args.get("lang", "no")
    if lang not in ("no", "en"):
        lang = "no"
    dinosaur = next((item for item in localized_dinosaurs(lang) if item["slug"] == slug), None)
    if dinosaur is None:
        for kind in ("sea", "air"):
            dinosaur = next((item for item in localized_other_reptiles(kind, lang) if item["slug"] == slug), None)
            if dinosaur is not None:
                break
    if dinosaur is None:
        abort(404)
    return render_template("dino.html", dinosaur=dinosaur, lang=lang, t=TEXT[lang])


def make_quiz_bank(lang):
    rng = random.SystemRandom()
    animals = localized_dinosaurs(lang)
    animals += localized_other_reptiles("sea", lang)
    animals += localized_other_reptiles("air", lang)
    names = [animal["name"] for animal in animals]
    diets = list(dict.fromkeys(animal["diet"] for animal in animals))
    periods = list(dict.fromkeys(animal["period"] for animal in animals))
    groups = list(dict.fromkeys(animal["group"] for animal in animals))
    text = QUIZ_TEXT[lang]
    questions = []

    def add(question_id, prompt, answer, pool, explanation, challenge=False):
        choices = [choice for choice in dict.fromkeys(pool) if choice != answer]
        rng.shuffle(choices)
        options = choices[:3] + [answer]
        rng.shuffle(options)
        questions.append({"id": question_id, "prompt": prompt, "options": options,
                          "answer": answer, "explanation": explanation,
                          "challenge": challenge})

    for animal in animals:
        add(animal["slug"] + "-diet", text["diet_q"].format(name=animal["name"]),
            animal["diet"], diets, animal["description"])
        add(animal["slug"] + "-period", text["period_q"].format(name=animal["name"]),
            animal["period"], periods, animal["dates_display"] + ". " + animal["description"])
        add(animal["slug"] + "-group", text["group_q"].format(name=animal["name"]),
            animal["group"], groups, animal["features"], challenge=True)
        add(animal["slug"] + "-feature",
            text["feature_q"] + " “" + animal["features"] + "”",
            animal["name"], names, animal["description"], challenge=True)
        add(animal["slug"] + "-fact",
            text["fact_q"] + " “" + animal["fact"] + "”",
            animal["name"], names, animal["description"], challenge=True)
    rng.shuffle(questions)
    return questions


@app.get("/quiz")
def quiz_page():
    lang = request.args.get("lang", "no")
    if lang not in ("no", "en"):
        lang = "no"
    response = app.make_response(render_template("quiz.html", lang=lang,
                                t=TEXT[lang], q=QUIZ_TEXT[lang],
                                question_bank=make_quiz_bank(lang)))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response


if __name__ == "__main__":
    app.run(debug=True)
