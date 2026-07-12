from jinja2 import Environment, FileSystemLoader
import os

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "prompts")
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))


def render_prompt(template_name: str, **kwargs) -> str:
    """Load a .jinja prompt template and render it with the given variables."""
    template = env.get_template(template_name)
    return template.render(**kwargs)