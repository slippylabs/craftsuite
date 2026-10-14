"""DesignCraft without the ArtCraft promo links.

The toolbar's Discord pill; the start screen's "Join the ArtCraft community"
card; the About window's Discord button, page/GitHub/website/issue links and
"More ArtCraft apps" row; the Help menu's Discord, website, GitHub, Report an
Issue, ArtCraft Website and App Page entries and their ui: commands.
"""
from _patch import cut, plain_credits, scrub, sub

sub("crates/ui-egui/src/chrome.rs", """                        ui.add_space(8.0);
                        // Always one click away: the ArtCraft community Discord.
                        if crate::about::discord_button(ui, "Discord", vec2(78.0, 22.0)) {
                            let _ = app.run("help.discord", json!({}));
                        }
""", "")
sub("crates/ui-egui/src/chrome.rs", """            ui.add_space(20.0);
            community_card(app, ui);
""", "")
cut("crates/ui-egui/src/about.rs", """            ui.add_space(16.0);
            if discord_button(ui, "Join the ArtCraft Discord", vec2(300.0, 40.0)) {""",
    """            ui.add_space(12.0);
            ui.label(crate::rtl::widget(
                ui,
                egui::RichText::new(crate::i18n::tr(&app.ui.language, "Open source. No telemetry.")).size(11.0).color(t.text_dim),""",
    "            ui.add_space(4.0);\n")
sub("crates/ui-egui/src/menus.rs", """    ("help.discord", "Join the ArtCraft Discord…", None, "{} — opens https://discord.gg/artcraft in the browser"),
    ("help.appPage", "DesignCraft Website…", None, "{} — opens https://getartcraft.com/apps/designcraft"),
    ("help.github", "DesignCraft on GitHub…", None, "{} — opens https://github.com/storytold/designcraft"),
    ("help.issues", "Report an Issue…", None, "{} — opens the GitHub issue tracker"),
    ("help.website", "ArtCraft Website…", None, "{} — opens https://getartcraft.com"),
    ("help.app", "ArtCraft App Page…", None, "{app} — opens https://getartcraft.com/apps/{app} (e.g. photocraft)"),
""", "")
sub("crates/ui-egui/src/menus.rs", """            "ui:help.discord",
            "-",
            "ui:help.appPage",
            "ui:help.github",
            "ui:help.issues",
            "ui:help.website",
            "-",
            "cmd:file.newSample",""", """            "cmd:file.newSample",""")
plain_credits()
scrub()
