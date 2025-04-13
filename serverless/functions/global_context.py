"""
Module: global_context

This module defines a global dictionary to store shared context information that can be
accessed and updated across different parts of the application. It is primarily used for
storing metadata such as batch IDs, image fingerprints, and debug flags, which are useful
for logging and debugging purposes.

Attributes:
    global_context (dict): A global dictionary to store shared context information.
        - batch_id (str or None): The ID of the current batch being processed.
        - img_fprint (str or None): The fingerprint (hash) of the current image being processed.
        - is_debug (bool): A flag indicating whether the application is running in debug mode.

Usage:
    This module is imported wherever shared context information needs to be accessed or updated.

Example:
    # Access the global context
    batch_id = global_context["batch_id"]

    # Update the global context
    global_context["is_debug"] = True

    # Log the current context
    LOG.info("Current context: %s", global_context)
"""

# Global dictionary to store shared context (for atexit logging)
global_context = {
    "batch_id": None,
    "img_fprint": None,
    "is_debug": False,
}
