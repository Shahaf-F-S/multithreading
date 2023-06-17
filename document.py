# document.py

import os
import inspect
from importlib.machinery import SourceFileLoader
from pathlib import Path
from typing import Optional

from multithreading.base import validate_requirement, suppress

validate_requirement("pdoc", path="pdoc3")

from pdoc.cli import main as document, parser

from build import collect_files

def generate_md(
        package: str,
        destination: Optional[str] = None,
        reload: Optional[bool] = False
) -> None:
    """
    Generates the documentation for the package.

    :param package: The package to document.
    :param destination: The documentation destination.
    :param reload: The value to rewrite the documentation.
    """

    if destination is None:
        destination = "docs"
    # end if

    if reload or not (Path(destination)).is_dir():
        documentation_files = [
            file for file in collect_files(location=package)
            if file.endswith("document.py")
        ]

        for file in documentation_files:
            path = Path(file)
            module_name = ".".join(Path(file).parts).replace(".py", "")

            module = SourceFileLoader(
                module_name, str(path)
            ).load_module()

            content = ""

            for i, name in enumerate(dir(module)):
                attribute = getattr(module, name)

                try:
                    if (
                        (attribute.__module__ == module.__name__) or
                        name.startswith("_") or
                        (name == "document")
                    ):
                        continue
                    # end if

                except AttributeError:
                    continue
                # end try

                if i == 0:
                    content += ("#### `" + attribute.__module__ + "`\n\n")

                    path = attribute.__module__.replace('.', '/') + ".md"
                # end if

                content += (
                    "## " + attribute.__module__ + "." +
                    attribute.__name__ + "\n\n"
                )

                signature = inspect.signature(
                    attribute.__init__ if inspect.isclass(attribute) else attribute
                )

                initializer = (str(signature)[1:] + "\n").replace(")\n", "")

                for argument in signature.parameters:
                    if f"{argument}:" in str(signature):
                        argument = f"{argument}:"
                    # end if

                    if argument not in ("self", "cls", "mls"):
                        replacement = f"\n{argument}"

                    else:
                        replacement = ""
                    # end if

                    initializer = initializer.replace(argument, replacement)
                # end for

                if initializer.startswith("\n"):
                    initializer = initializer[1:]
                # end if

                end = initializer.rfind(")")

                if ")" in initializer:
                    initializer = (
                        initializer[:end] + "\nreturns:\n" + initializer[end + 1:]
                    )
                # end if

                initializer = (
                    "\n````python\n" + initializer.replace(", \n", "\n") + "\n````\n"
                ).replace("**kw\nargs", "\n**kwargs")

                doc = "\n".join(str(attribute.__doc__).splitlines())
                example = "\n".join(
                    line for line in doc.split("\n") if line.startswith("    >>>")
                )
                doc = "\n".join(
                    line for line in doc.split("\n") if not line.startswith("    >>>")
                )
                doc = "\n".join(
                    line.replace("    ", "") if line.replace(" ", "") else line
                    for line in doc.split("\n")
                )
                example = (
                    "\n````python\n" + example.replace("    >>>", "") + "\n````\n"
                )
                content += (
                    "\n### arguments:\n" + initializer +
                    "\n### documentation:\n" + doc +
                    "\n### examples:\n" + example
                ).replace("\n ", "\n")
            # end for

            directory = Path(destination) / Path("/".join(Path(path).parts[:-1]))

            os.makedirs(directory, exist_ok=True)

            file_path = str(directory / Path("README.md"))

            with open(file_path, "w") as f:
                f.write(content)
            # end open
        # end for
    # end if
# end generate_md

def generate_html(
        package: str,
        destination: Optional[str] = None,
        reload: Optional[bool] = False,
        show: Optional[bool] = True
) -> None:
    """
    Generates the documentation for the package.

    :param reload: The value to rewrite the documentation.
    :param show: The value to show the documentation.
    :param package: The package to document.
    :param destination: The documentation destination.
    """

    if destination is None:
        destination = "docs"
    # end if

    main_index_file = Path(destination) / Path(package) / Path("index.html")

    if reload or not main_index_file.is_dir():
        with suppress():
            document(
                parser.parse_args(
                    [
                        "--html", "--force", "--output-dir",
                        str(destination), str(package)
                    ]
                )
            )
        # end suppress
    # end if

    if show:
        os.system(f'start {main_index_file}')
    # end if

def main(
        location: str,
        destination: Optional[str] = "docs",
        reload: Optional[bool] = True,
        show: Optional[bool] = False
) -> None:
    """
    Shows the documentation of the project.

    :param location of The location of the package.
    :param destination: The documentation destination.
    :param reload: The value to rewrite the documentation.
    :param show: The value to show the documentation.
    """

    generate_md(location, destination=destination, reload=reload)
    generate_html(location, destination=destination, reload=reload, show=show)
# end main

if __name__ == "__main__":
    main(location="multithreading", reload=True, show=False)
# end if