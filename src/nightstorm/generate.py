"""Theme generation."""

import math
import re
from importlib.resources import files
import nightstorm
from nightstorm.color_manipulation import oklab_adjust, deopacify

# Create an Oklab rainbow palette.
n = 15  # pylint: disable=invalid-name
ts = [float(x)/(n) for x in range(n)]  # np.linspace(0, 1, n)
base_chromatic_palette = [oklab_adjust("#cc8080", hue_addend=t*2*math.pi) for t in ts]


def generate_theme_variant(accent_color, variant_name):
    """Generate a theme variant with the given accent color index."""

    def deepen(hex_color):
        return oklab_adjust(hex_color, lightness_factor=0.85, chroma_factor=1.9)

    def soften(hex_color):
        return oklab_adjust(hex_color, lightness_factor=1.15, chroma_factor=0.9)

    def vividify(hex_color):
        return oklab_adjust(hex_color, lightness_factor=1.05, chroma_factor=1.2)

    def saturate(hex_color):
        return oklab_adjust(hex_color, lightness_factor=1.1, chroma_factor=2.5)

    def dim(hex_color):
        return oklab_adjust(hex_color, lightness_factor=0.6, chroma_factor=0.7)

    color_map = {f"${i:02}$": color for i, color in enumerate(base_chromatic_palette)}
    color_map.update({
        # accent
        "$accent$": base_chromatic_palette[accent_color],
        "$deep_accent$": deepen(base_chromatic_palette[accent_color]),
        "$highlighted_deep_accent$": soften(deepen(base_chromatic_palette[accent_color])),
        "$dimmed_accent$": dim(base_chromatic_palette[accent_color]),
        "$vivid_accent$": vividify(base_chromatic_palette[accent_color]),

        # achromatic
        "$pure_white$": "#ffffff",
        "$sidebar_foreground$": "#e0e0e0",
        "$ansi_bright_white$": "#cccccc",
        "$white$": "#bbbbbb",
        "$opaque_statusbar_foreground$": "#a0a0a0",  # actual fg /w alpha for better hover
        "$gray$": "#808080",
        "$word_highlight$": "#777777",
        "$ansi_bright_black$": "#666666",
        "$scrollbar$": "#505050",
        "$linenumber$": "#505050",
        "$active_background$": "#505050",
        "$menu_border$": "#444444",
        "$border$": "#3c3c3c",
        "$indent_guide$": "#343434",
        "$sidebar_background$": "#2c2c2c",
        "$line_highlight$": "#282828",
        "$editor_background$": "#202020",
        "$pure_black$": "#000000",

        # terminal
        "$ansi_bright_red$": soften(deepen(base_chromatic_palette[0])),
        "$ansi_bright_yellow$": soften(deepen(base_chromatic_palette[3])),
        "$ansi_bright_green$": soften(deepen(base_chromatic_palette[6])),
        "$ansi_bright_cyan$": soften(deepen(base_chromatic_palette[8])),
        "$ansi_bright_blue$": soften(deepen(base_chromatic_palette[9])),
        "$ansi_bright_magenta$": soften(deepen(base_chromatic_palette[13])),
        "$ansi_red$": deepen(base_chromatic_palette[0]),
        "$ansi_yellow$": deepen(base_chromatic_palette[3]),
        "$ansi_green$": deepen(base_chromatic_palette[6]),
        "$ansi_cyan$": deepen(base_chromatic_palette[8]),
        "$ansi_blue$": deepen(base_chromatic_palette[9]),
        "$ansi_magenta$": deepen(base_chromatic_palette[13]),

        # source control graph
        "$gitgraph_1$": saturate(base_chromatic_palette[6]),
        "$gitgraph_2$": saturate(base_chromatic_palette[3]),
        "$gitgraph_3$": saturate(base_chromatic_palette[0]),
        "$gitgraph_4$": saturate(base_chromatic_palette[8]),
        "$gitgraph_5$": saturate(base_chromatic_palette[13]),
        "$gitgraph_ref$": saturate(base_chromatic_palette[10]),
        "$gitgraph_remoteref$": base_chromatic_palette[12],
        "$gitgraph_baseref$": deepen(base_chromatic_palette[1]),
        "$gitgraph_additions$": soften(base_chromatic_palette[5]),
        "$gitgraph_deletions$": soften(base_chromatic_palette[0]),

        # editor error/warning/info squiggly underlines
        "$underlined_error$": saturate(base_chromatic_palette[0]),
        "$underlined_warning$": saturate(base_chromatic_palette[3]),
        "$underlined_info$": saturate(base_chromatic_palette[10]),

        # minimap error/warning/info
        "$minimap_error$": soften(deepen(base_chromatic_palette[0])),
        "$minimap_warning$": soften(deepen(base_chromatic_palette[3])),
        "$minimap_info$": soften(deepen(base_chromatic_palette[10])),

        # explorer/tab filenames
        "$file_error$": vividify(base_chromatic_palette[0]),
        "$file_warning$": vividify(base_chromatic_palette[3]),
        "$file_modified$": vividify(base_chromatic_palette[9]),
        "$file_added$": vividify(base_chromatic_palette[5]),
        "$file_untracked$": vividify(base_chromatic_palette[1]),
        "$file_renamed$": vividify(base_chromatic_palette[8]),

        # editor gutter
        "$editorgutter_added$": soften(dim(base_chromatic_palette[5])),
        "$editorgutter_modified$": soften(dim(base_chromatic_palette[9])),
        "$editorgutter_deleted$": soften(dim(base_chromatic_palette[0])),

        # diff
        "$diff_inserted$": dim(base_chromatic_palette[5]),
        "$diff_removed$": dim(base_chromatic_palette[0]),

        # merge
        "$merge_current$": dim(base_chromatic_palette[1]),
        "$merge_current_header$": vividify(base_chromatic_palette[1]),
        "$merge_incoming$": dim(base_chromatic_palette[8]),
        "$merge_incoming_header$": vividify(base_chromatic_palette[8]),
        "$merge_editor_change$": dim(base_chromatic_palette[14]),
        "$merge_editor_change_word$": base_chromatic_palette[14],

        # match highlights
        "$word_highlight_strong$": deepen(base_chromatic_palette[9]),
        "$findmatch$": soften(deepen(base_chromatic_palette[6])),
        "$repeating_selection$": dim(base_chromatic_palette[6]),

        # miscellaneous
        "$fold_background$": dim(base_chromatic_palette[9]),
        "$breakpoint_foreground$": deepen(base_chromatic_palette[1]),
    })
    color_map["$transparent_statusbar_foreground$"] = deopacify(
        color="#ffffff",
        background=color_map["$sidebar_background$"],
        target=color_map["$opaque_statusbar_foreground$"],
    )

    # Replace.
    content = (files(nightstorm)/"template.json").read_text()
    translation_map = color_map | {"$variant$": variant_name.capitalize()}
    pattern = re.compile("|".join(map(re.escape, translation_map.keys())))  # safely match any key
    content = pattern.sub(lambda match: translation_map[match.group(0)], content)

    # Save.
    output_dir = files(nightstorm).parent.parent/"themes"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir/f"Nightstorm-{variant_name}.json").write_text(content)


def main():
    """Main function."""
    variants = (
        ("orange", 2),
        ("turquoise", 7),
        ("cyan", 8),
        ("blue", 10),
        ("magenta", 13),
    )
    for variant_name, accent_color in variants:
        generate_theme_variant(accent_color, variant_name)


if __name__ == "__main__":
    main()
