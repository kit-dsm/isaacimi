blueprint_schema = {
    "app": {
        "type": "dict",
        "required": True,
        "schema": {
            "headless": {"type": "boolean", "required": True},
            "renderer": {
                "type": "string",
                "allowed": ["RayTracedLighting", "PathTracing"],
                "required": True
            }
        },
    },
    "world": {
        "type": "dict",
        "required": True,
        "schema": {
            "stage_units_in_meters": {"type": "float", "required": True},
            "physics_dt": {"type": "float", "required": True},
            "rendering_dt": {"type": "float", "required": True}
        },
    },
    "scene": {
        "type": "dict",
        "required": True,
        "schema": {
            "environment": {
                "type": "dict",
                "required": True,
                "schema": {
                    "usd_path": {"type": "string", "required": True},
                    "prim_path": {"type": "string", "required": True},
                },
            },
            "robots": {
                "type": "list",
                "required": True,
                "schema": {
                    "type": "dict",
                    "schema": {
                        "name": {"type": "string", "required": True},
                        "usd_path": {"type": "string", "required": True},
                        "prim_path": {"type": "string", "required": True},
                        "position": {
                            "type": "list",
                            "required": True,
                            "schema": {"type": "float"},
                            "minlength": 3,
                            "maxlength": 3,
                        },
                        "orientation": {
                            "type": "list",
                            "required": True,
                            "schema": {"type": "float"},
                            "minlength": 4,
                            "maxlength": 4,
                        },
                        "plugins": { # optional plugins
                            "type": "list",
                            "required": False,
                            "schema": {
                                "type": "dict",
                                "schema": {
                                    "class": {"type": "string", "required": True},
                                    "params": {"type": "dict", "required": False}
                                },
                            },
                        },
                    },
                },
            },
        },
    },
    "robot_plugins": {
        "type": "list",
        "required": False,
        "schema": {
            "type": "dict",
            "schema": {
                "filepath": {"type": "string", "required": True},
                "classes": {
                    "type": "list",
                    "required": True,
                    'schema': {'type': 'string', 'empty': False},
                },
            },
        },
    },
}