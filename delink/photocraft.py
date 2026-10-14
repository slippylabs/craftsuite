"""PhotoCraft without the ArtCraft promo links.

The title bar's Discord button; the start screen's and About dialog's "Join
us on Discord" button and website/GitHub/ArtCraft link row; the Help menu's
Discord, website, ArtCraft website, GitHub and Report an Issue entries (and
the separator that set them apart from System Info and About).
"""
from _patch import cut, scrub, sub

# The title bar's Discord button: everything from its comment up to the line
# that closes the controls group.
cut("crates/ui-egui/src/panels.rs",
    "                    // The community Discord, one click away while the bar has room for it\n",
    "                    if rtl { ui.min_rect().right() } else { ui.min_rect().left() }\n")
sub("crates/ui-egui/src/dialogs.rs", """            ui.add_space(12.0);
            ui.vertical_centered(|ui| {
                crate::links::discord_button(app, ui, 220.0);
                ui.add_space(8.0);
                crate::links::link_row(app, ui);
            });
""", "")
sub("crates/ui-egui/src/canvas.rs", """            ui.add_space(26.0);
            crate::links::discord_button(app, ui, 190.0);
            ui.add_space(10.0);
            crate::links::link_row(app, ui);
""", "")
sub("crates/ui-egui/src/menus.rs", """    ("help.discord", "Join the ArtCraft Discord…", &["Help"], None),
    ("help.website", "PhotoCraft Website", &["Help"], None),
    ("help.artcraftWebsite", "ArtCraft Website", &["Help"], None),
    ("help.github", "PhotoCraft on GitHub", &["Help"], None),
    ("help.reportIssue", "Report an Issue…", &["Help"], None),
""", "")
sub("crates/ui-egui/src/menus.rs", """    // Help: the link items, a separator, then System Info and About.
    if let Some(at) = items.iter().position(|i| i.id == "help.systemInfo" || i.id == "help.about") {
        items.insert(
            at,
            MenuItem { id: "---".into(), label: "---".into(), path: vec!["Help".into()], shortcut: None, enabled: false, checked: None, color: None },
        );
    }
""", "")
sub("crates/ui-egui/src/links.rs", """pub const COMMANDS: &[(&str, &str)] =
    &[("help.discord", DISCORD), ("help.website", APP_PAGE), ("help.artcraftWebsite", ARTCRAFT_WEBSITE), ("help.github", GITHUB), ("help.reportIssue", ISSUES)];""",
    "pub const COMMANDS: &[(&str, &str)] = &[];")
# About > Contributors: names stay, the link to each GitHub profile goes.
sub("crates/ui-egui/src/credits.rs", """    let url = format!("https://github.com/{}", c.login);
    let r = ui.add(egui::Link::new(c.name(names))).on_hover_text(c.summary());
    if r.clicked() {
        crate::links::open(app, ui.ctx(), &url);
    }
    r""", """    let _ = app;
    ui.label(c.name(names)).on_hover_text(c.summary())""")
scrub()
