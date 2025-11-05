from typing import Any, Dict, List, Tuple  # (inchangé)
import math  # (inchangé)
import random  # (inchangé)


def is_vege(recipe: Dict[str, Any]) -> bool:  # (inchangé)
    return "tags" in recipe and any(t.lower() == "vege" for t in recipe["tags"])  # (inchangé)


def fits_time(recipe: Dict[str, Any], max_time: int | None) -> bool:  # (inchangé)
    if max_time is None:  # (inchangé)
        return True  # (inchangé)
    return int(recipe.get("time_min", 9999)) <= max_time  # (inchangé)


def within_budget_avg(
    selected: List[Dict[str, Any]],
    avg_target: float,
    tolerance: float = 0.2,
) -> bool:  # (inchangé)
    if not selected:  # (inchangé)
        return True  # (inchangé)
    cur_avg = sum(float(r.get("budget_eur", 0.0)) for r in selected) / len(selected)  # (inchangé)
    return (avg_target * (1 - tolerance)) <= cur_avg <= (avg_target * (1 + tolerance))  # (inchangé)


def select_menu(
    recipes: List[Dict[str, Any]],
    days: int = 7,
    min_vege: int = 2,
    max_time: int | None = None,
    avg_budget: float | None = None,
    tolerance: float = 0.2,
    seed: int | None = 42,
    no_duplicates: bool = False,  # AJOUT : flag pour interdire les doublons dans le menu
) -> List[Dict[str, Any]]:
    """
    Sélection simple et déterministe (via seed) :
    - Filtre par temps.
    - Tire au sort jusqu'à avoir 'days' recettes (avec ou sans doublons).
    - Vérifie min_vege et budget moyen (si fourni).
    Réessaie quelques fois.
    Le paramètre no_duplicates permet d'éviter d'avoir deux fois la même recette.
    """  # AJOUT : commentaire de doc expliquant no_duplicates

    pool = [r for r in recipes if fits_time(r, max_time)]  # (inchangé : filtrage par temps)

    if seed is not None:  # (inchangé)
        random.seed(seed)  # (inchangé)

    attempts = 200  # (inchangé)
    best: List[Dict[str, Any]] = []  # (inchangé)

    for _ in range(attempts):  # (inchangé)
        if not pool:  # AJOUT : si aucune recette ne passe le filtre temps, on sort proprement
            break  # AJOUT : évite des erreurs plus loin si pool est vide

        if no_duplicates:  # AJOUT : branche spécifique quand on ne veut pas de doublons
            # On ne tire que des recettes uniques, au maximum min(days, len(pool))
            k = min(days, len(pool))  # AJOUT : nombre max de recettes uniques possibles
            cand = random.sample(pool, k=k)  # AJOUT : tirage sans répétition
            # Pas de boucle de complétion ici : on accepte d'avoir moins de 'days' si pas assez de recettes uniques  # AJOUT
        else:
            # Comportement historique : on complète avec des doublons si besoin
            if len(pool) >= days:  # (inchangé fonctionnellement)
                cand = random.sample(pool, k=days)  # (inchangé fonctionnellement)
            else:
                cand = pool[:]  # (inchangé fonctionnellement)
                # Si pas assez, on complète en re-piochant (permet petit dataset)
                while len(cand) < days and pool:  # (inchangé fonctionnellement)
                    cand.append(random.choice(pool))  # (inchangé fonctionnellement)

        # Contraintes
        vege_count = sum(1 for r in cand if is_vege(r))  # (inchangé)
        if vege_count < min_vege:  # (inchangé)
            continue  # (inchangé)

        if avg_budget is not None and not within_budget_avg(cand, avg_budget, tolerance):  # (inchangé)
            continue  # (inchangé)

        best = cand  # (inchangé)
        break  # (inchangé)

    if not best:
        # Dernier recours si aucune combinaison ne respecte toutes les contraintes
        if no_duplicates:  # AJOUT : fallback spécifique quand on ne veut pas de doublons
            # On renvoie au maximum min(days, len(pool)) recettes uniques
            best = pool[: min(days, len(pool))]  # AJOUT : tronque la liste sans doublons
        else:
            # Comportement historique : on duplique si besoin pour remplir tous les jours
            best = pool[:days] if len(pool) >= days else (pool + pool)[:days]  # (inchangé)

    return best  # (inchangé)


def consolidate_shopping_list(menu: List[Dict[str, Any]]) -> List[Dict[str, Any]]:  # (inchangé)
    """
    Agrège par (name, unit).
    Ne gère pas la conversion d’unités (simple au départ).
    """  # (inchangé)
    agg: Dict[Tuple[str, str], float] = {}  # (inchangé)
    for r in menu:  # (inchangé)
        for ing in r.get("ingredients", []):  # (inchangé)
            key = (ing["name"].strip().lower(), ing.get("unit", "").strip().lower())  # (inchangé)
            agg[key] = agg.get(key, 0.0) + float(ing.get("qty", 0.0))  # (inchangé)

    items = [
        {"name": name, "qty": round(qty, 2), "unit": unit}
        for (name, unit), qty in sorted(agg.items())
    ]  # (inchangé)
    return items  # (inchangé)


def plan_menu(
    recipes: List[Dict[str, Any]],
    days: int = 7,
    min_vege: int = 2,
    max_time: int | None = None,
    avg_budget: float | None = None,
    tolerance: float = 0.2,
    seed: int | None = 42,
    no_duplicates: bool = False,  # AJOUT : on propage l'option no_duplicates jusqu'à select_menu
) -> Dict[str, Any]:
    menu = select_menu(
        recipes,
        days=days,
        min_vege=min_vege,
        max_time=max_time,
        avg_budget=avg_budget,
        tolerance=tolerance,
        seed=seed,
        no_duplicates=no_duplicates,  # AJOUT : on transmet le flag à la fonction de sélection
    )
    shopping = consolidate_shopping_list(menu)  # (inchangé)
    return {"days": days, "menu": menu, "shopping_list": shopping}  # (inchangé)
