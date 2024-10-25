from jinja2 import Environment, FileSystemLoader
from logger import Logger

class TemplateManager:
    """
    Manages template loading and rendering using the Jinja2 library.
    """
    def __init__(self, template_dirs=None):
        """
        Initializes the TemplateManager with specified template directories.

        :param template_dirs: A list of directories containing Jinja2 templates, defaults to empty.
        :type template_dirs: list, optional
        """
        self.log = Logger(self.__class__.__name__)
        self.template_dirs = template_dirs if template_dirs is not None else []
        self.templates_env = None
        self.templates = []

    def load_templates(self):
        """
        Loads templates from the configured directories and initializes the Jinja environment.
        """
        if not self.template_dirs:
            self.log.error("No template directories specified.")
            raise ValueError("Template directories not specified.")

        self.templates_env = Environment(loader=FileSystemLoader(self.template_dirs), autoescape=True)
        self.templates = self.templates_env.list_templates()

        if not self.templates:
            self.log.warning("No templates found in the specified directories.")
        else:
            self.log.info(f"Loaded templates: {self.templates}")

    def render_template(self, template_name, **kwargs):
        """
        Renders a template with the given parameters.

        :param template_name: The name of the template to render.
        :type template_name: str
        :param kwargs: Keyword arguments to pass to the template for rendering.
        :return: The rendered template as a string.
        :rtype: str
        """
        if template_name not in self.templates:
            self.log.error(f"Template '{template_name}' not found.")
            raise FileNotFoundError(f"Template '{template_name}' not found.")

        template = self.templates_env.get_template(template_name)
        return template.render(**kwargs)
