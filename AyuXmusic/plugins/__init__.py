from pathlib import Path


def __list_all_modules():
    work_dir = Path(__file__).parent
    all_modules = []

    for module_path in work_dir.glob("*/*.py"):
        if module_path.name == "__init__.py":
            continue
        module = "." + ".".join(module_path.relative_to(work_dir).with_suffix("").parts)
        all_modules.append(module)

    return all_modules


ALL_MODULES = sorted(__list_all_modules())
__all__ = ALL_MODULES + ["ALL_MODULES"]
