"""Terminal visuals, theme cards, and procedural ASCII art."""

from stemclaw.visuals.ascii_art import (
    STEMCLAW_LOGO,
    ASCII_DNA_HELIX,
    ASCII_ATOM_LATTICE,
    ASCII_CIRCUIT_GEAR,
    ASCII_GLOBE_WAVE,
    ASCII_CONSTELLATION,
    get_category_ascii,
)
from stemclaw.visuals.banner import (
    print_banner,
    print_category_prompt,
    print_loadout_summary,
)
from stemclaw.visuals.animations import (
    render_data_flowing_animation,
    install_visual_hooks,
)

__all__ = [
    "STEMCLAW_LOGO",
    "ASCII_DNA_HELIX",
    "ASCII_ATOM_LATTICE",
    "ASCII_CIRCUIT_GEAR",
    "ASCII_GLOBE_WAVE",
    "ASCII_CONSTELLATION",
    "get_category_ascii",
    "print_banner",
    "print_category_prompt",
    "print_loadout_summary",
    "render_data_flowing_animation",
    "install_visual_hooks",
]
