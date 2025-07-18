# WARNING: DO NOT EDIT!
#
# This file was generated by plugin_template, and is managed by it. Please use
# './plugin-template --github pulp_hugging_face' to update this file.
#
# For more info visit https://github.com/pulp/plugin_template

import tomllib
import warnings
from packaging.requirements import Requirement


CHECK_MATRIX = [
    ("pyproject.toml", True, True, True),
    ("requirements.txt", True, True, True),
    ("dev_requirements.txt", False, True, False),
    ("ci_requirements.txt", False, True, True),
    ("doc_requirements.txt", False, True, False),
    ("lint_requirements.txt", False, True, True),
    ("unittest_requirements.txt", False, True, True),
    ("functest_requirements.txt", False, True, True),
    ("clitest_requirements.txt", False, True, True),
]


def iterate_file(filename):
    if filename == "pyproject.toml":
        with open(filename, "rb") as fd:
            pyproject_toml = tomllib.load(fd)
            if "project" in pyproject_toml:
                for nr, line in enumerate(pyproject_toml["project"]["dependencies"]):
                    yield nr, line
    else:
        with open(filename, "r") as fd:
            for nr, line in enumerate(fd.readlines()):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "#" in line:
                    line = line.split("#", maxsplit=1)[0]
                yield nr, line.strip()


def main():
    errors = []

    for filename, check_upperbound, check_prereleases, check_r in CHECK_MATRIX:
        try:
            for nr, line in iterate_file(filename):
                try:
                    req = Requirement(line)
                except ValueError:
                    if line.startswith("git+"):
                        # The single exception...
                        if "pulp-smash" not in line:
                            errors.append(f"{filename}:{nr}: Invalid source requirement: {line}")
                    elif line.startswith("-r "):
                        if check_r:
                            errors.append(f"{filename}:{nr}: Invalid deferred requirement: {line}")
                    else:
                        errors.append(f"{filename}:{nr}: Unreadable requirement {line}")
                else:
                    if check_prereleases and req.specifier.prereleases:
                        # Do not even think about begging for more exceptions!
                        if (
                            not req.name.startswith("opentelemetry")
                            and req.name != "pulp-hugging-face-client"
                        ):
                            errors.append(f"{filename}:{nr}: Prerelease versions found in {line}.")
                    ops = [spec.operator for spec in req.specifier]
                    if "~=" in ops:
                        warnings.warn(f"{filename}:{nr}: Please avoid using ~= on {req.name}!")
                    elif "<" not in ops and "<=" not in ops and "==" not in ops:
                        if check_upperbound:
                            errors.append(f"{filename}:{nr}: Upper bound missing in {line}.")
        except FileNotFoundError:
            # skip this test for plugins that don't use this requirements.txt
            pass

    if errors:
        print("Dependency issues found:")
        print("\n".join(errors))
        exit(1)


if __name__ == "__main__":
    main()
