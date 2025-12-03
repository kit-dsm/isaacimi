"""Generate the code reference pages."""

from pathlib import Path

import mkdocs_gen_files

def cerberus_to_markdown(schema, indent=0):
    space_char = "&nbsp;&nbsp;"
    tab_size = 4
    tab_char = space_char * tab_size

    md = ""
    prefix = space_char * indent

    for name, rules in schema.items():
        req = rules.get("required", False)
        typ = rules.get("type", "—")
        body = ""

        if "__description" in rules:
            body += f"{prefix}{tab_char}<sub><sup>*{rules['__description']}*</sup></sub><br>"
        
        # Constraints (minlength, maxlength, etc.)
        extras = {k: v for k, v in rules.items() if k not in ("type", "required", "schema", "__description")}
        if extras:
            for k, v in extras.items():
                body += f"{prefix}{tab_char}{k}: `{v}`<br>"
        
        # if the item is a list, get the type of the list item if specified
        if typ == "list" and "schema" in rules:
            if "type" in rules["schema"]:
                typ+=f"[{rules['schema']['type']}]"
            if "schema" in rules["schema"]:
                body += f"{prefix}{tab_char}list_item:<br>"
                body += cerberus_to_markdown(rules["schema"]["schema"], indent + 2 * tab_size)

        # For dict fields
        if typ == "dict" and "schema" in rules:
            body += cerberus_to_markdown(rules["schema"], indent + tab_size)
        
        md += f"{prefix}**{name}** `{typ}`{' *(required)*' if req else ''}<br>"  
        md += body

    return md


root = Path(__file__).parent.parent.parent
src = root / "src"

from isaacimi.blueprint_schema import blueprint_schema

path = next(src.rglob("blueprint_schema.py"), None)

if path:
    # full_doc_path = Path("reference", "schema", path.with_suffix(".md").name)
    full_doc_path = Path("reference", "simulation-blueprint.md")

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        fd.write(cerberus_to_markdown(blueprint_schema))

    mkdocs_gen_files.set_edit_path(full_doc_path, path.relative_to(root))


