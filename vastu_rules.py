import json
with open("vastu_data.json", encoding="utf-8") as f:
    DATA = json.load(f)

def check_vastu(rooms: dict, plot_facing: str, plot_shape: str, family_sit: str, is_rented: bool) -> dict:
    results = []
    total_pts = 0
    max_pts = len(rooms) * 3

    for room_type, direction in rooms.items():
        if room_type not in DATA["room_rules"]:
            continue
        rule = DATA["room_rules"][room_type]
        direction = direction.upper()

        if direction in rule["ideal"]:
            status = "EXCELLENT"; severity = "good"; pts = 3
        elif direction in rule["acceptable"]:
            status = "ACCEPTABLE"; severity = "warn"; pts = 2
        elif direction in rule["forbidden"]:
            status = "CRITICAL VIOLATION"; severity = "critical"; pts = 0
        else:
            status = "NOT IDEAL"; severity = "bad"; pts = 1

        total_pts += pts
        remedies = rule.get("remedies", {})
        remedy_text = remedies.get(direction, rule.get("tip", "Apply general Vastu principles."))
        dir_info = DATA["directions"].get(direction, {})
        colors = dir_info.get("colors", ["#888888"] * 5)

        results.append({
            "room": room_type.replace("_", " ").title(),
            "room_type": room_type,
            "direction": direction,
            "dir_meaning": dir_info.get("meaning", ""),
            "dir_element": dir_info.get("element", ""),
            "status": status,
            "severity": severity,
            "pts": pts,
            "tip": rule.get("tip", ""),
            "remedy": remedy_text,
            "ideal_zones": rule["ideal"],
            "colors": colors,
        })

    overall = round((total_pts / max_pts) * 100) if max_pts > 0 else 0
    grade = "A" if overall >= 80 else "B" if overall >= 60 else "C" if overall >= 40 else "D"

    pred_pts = total_pts
    for r in results:
        if r["severity"] == "critical":
            pred_pts += 3
    predicted = min(100, round((pred_pts / max_pts) * 100)) if max_pts > 0 else 0

    violated = [r for r in results if r["severity"] in ("critical", "bad")]
    violated.sort(key=lambda x: x["pts"])
    priority = [r["room"] for r in violated[:3]]

    bhuta_bal = {}
    for elem, info in DATA["pancha_bhuta"].items():
        dirs = info["dirs"]
        relevant = [r for r in results if r["direction"] in dirs]
        good_count = [r for r in relevant if r["severity"] == "good"]
        bhuta_bal[elem] = {
            "pct": round((len(good_count)/len(relevant))*100) if relevant else 0,
            "color": info["color"],
            "tip": info["balance_tip"]
        }

    shape_info = DATA["plot_shapes"].get(plot_shape, {})

    if is_rented:
        for r in results:
            if "move" in r["remedy"].lower() or "relocate" in r["remedy"].lower():
                r["remedy"] = "Rented mode: " + r.get("tip", "Apply Vastu remedies without structural changes.")

    return {
        "rooms": results,
        "overall_score": overall,
        "predicted_score": predicted,
        "grade": grade,
        "plot_facing": plot_facing,
        "plot_shape": plot_shape,
        "shape_info": shape_info,
        "family_situation": family_sit,
        "is_rented": is_rented,
        "priority_fixes": priority,
        "pancha_bhuta": bhuta_bal,
        "total_rooms": len(results),
        "critical_count": sum(1 for r in results if r["severity"] == "critical"),
        "warn_count": sum(1 for r in results if r["severity"] in ("warn","bad")),
        "good_count": sum(1 for r in results if r["severity"] == "good"),
    }
