from cerberus import Validator
class BlueprintValidator(Validator):
    def _validate___description(self, constraint, field, value):
        """ A description of the value. This rule was created to generate documentation for the schema using the script docs/scripts/gen_schema_ref_pages.py

        The rule's arguments are validated against this schema:
        {'type': 'string'}
        """
        pass

blueprint_schema = {
    "app": {
        "__description": "All settings relating to the simulation app that is launched.",
        "type": "dict",
        "required": True,
        "schema": {
            "headless": {
                "__description": "Whether to run the simulation in headless mode or not.",
                "type": "boolean",
                "required": True
            },
            "renderer": {
                "__description": "Specify which renderer to use in the simulation.",
                "type": "string",
                "allowed": ["RayTracedLighting", "PathTracing"],
                "required": True
            },
            "livestream": {
                "__description": "Whether to enable a livestream server for streaming clients to connect to.",
                "type": "boolean",
                "default": False   
            }
        },
    },
    "world": {
        "__description": "All settings related to the world in the simulation.",
        "type": "dict",
        "required": True,
        "schema": {
            "stage_units_in_meters": {
                "__description": "The size in meters of one unit length in the simulation.",
                "type": "float",
                "required": True
            },
            "physics_dt": {
                "__description": "Physics timestep in seconds.",
                "type": "float",
                "required": True,
            },
            "rendering_dt": {
                "__description": "Render timestep in seconds.",
                "type": "float",
                "required": True
            },
        },
    },
    "scene": {
        "__description": "All settings related to the scene that will take place in the simulation.",
        "type": "dict",
        "required": True,
        "schema": {
            "environment": {
                "__description": "The environment of the scene.",
                "type": "dict",
                "required": True,
                "schema": {
                    "usd_path": {
                        "__description": "Path to a .usd file containing the environment.",
                        "type": "string",
                        "required": True
                    },
                    "prim_path": {
                        "__description": "Path of the environment prim in the simulation.",
                        "type": "string",
                        "required": True
                    },
                },
            },
            "robots": {
                "__description": "A list of all robots that will spawn into the environment.",
                "type": "list",
                "required": True,
                "schema": {
                    "type": "dict",
                    "schema": {
                        "name": {
                            "__description": "The name of the robot, must be unique.",
                            "type": "string",
                            "required": True
                        },
                        "usd_path": {
                            "__description": "Path to a .usd file containing the robot.",
                            "type": "string",
                            "required": True
                        },
                        "prim_path": {
                            "__description": "Path to the robot prim in the simulation.",
                            "type": "string",
                            "required": True
                        },
                        "position": {
                            "__description": "The position of the robot (relative to the parent prim) when spawned.",
                            "type": "list",
                            "required": True,
                            "schema": {"type": "float"},
                            "minlength": 3,
                            "maxlength": 3,
                        },
                        "orientation": {
                            "__description": "The orientation of the robot (relative to the parent prim) when spawned.",
                            "type": "list",
                            "required": True,
                            "schema": {"type": "float"},
                            "minlength": 4,
                            "maxlength": 4,
                        },
                        "plugins": { # optional plugins
                            "__description": "A list of optional plugins to load on the robot.",
                            "type": "list",
                            "required": False,
                            "schema": {
                                "type": "dict",
                                "schema": {
                                    "class": {
                                        "__description": "The name of the custom plugin class.",
                                        "type": "string",
                                        "required": True
                                    },
                                    "params": {
                                        "__description": "The parameters to pass to the plugin, if required.",
                                        "type": "dict",
                                        "required": False
                                    }
                                },
                            },
                        },
                    },
                },
            },
        },
    },
    "robot_plugins": {
        "__description": "A list of all user defined plugins to be used in the simulation.",
        "type": "list",
        "required": False,
        "schema": {
            "type": "dict",
            "schema": {
                "filepath": {
                    "__description": "Path to the .py file that defines the custom plugins.",
                    "type": "string",
                    "required": True
                },
                "classes": {
                    "__description": "A list of all plugins to import from the .py file.",
                    "type": "list",
                    "required": True,
                    'schema': {'type': 'string', 'empty': False},
                },
            },
        },
    },
}