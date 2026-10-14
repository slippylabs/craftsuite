"""FilmCraft without the ArtCraft promo links.

The header's Discord button; the Import screen's Community row (Discord,
website, app page, GitHub); the About tab's Discord button and website, app
page, GitHub and Report an Issue links; the Help menu's Discord, website,
app page, GitHub and Report an Issue entries; F1 FilmCraft Help and the
Settings window's Help button, which only opened docs on GitHub. The
Credits roll template ended "Made with FilmCraft"; that line goes.
"""
from _patch import cut, plain_credits, scrub, sub

HEADER = "crates/ui-egui/src/header.rs"
sub(HEADER, """    // Community: a labelled Discord button, always one click away.
    {
""", """    {
""")
cut(HEADER, """        let label = "Discord";
""", """        // Localized menus and user titles can be wider than English. Use the actual gap.
""")
sub(HEADER, "        let right = r.min.x - 12.0;\n", "        let right = wr.min.x - 12.0;\n")
sub(HEADER, """
        if resp.clicked() {
            crate::links::open(app, ui.ctx(), crate::links::DISCORD);
        }
""", "")
cut("crates/ui-egui/src/panels/import_mode.rs", """    // Community and project links.
    let y = 90.0 + 150.0 + 36.0;""", """        x = r.max.x + 12.0;
    }
""")
sub("crates/ui-egui/src/panels/import_mode.rs", """        x = r.max.x + 12.0;
    }
""", "")
cut("crates/ui-egui/src/panels/dialogs.rs", """    ui.add_space(10.0);
    let mut link = |ui: &mut egui::Ui, id: &str, icon: Icon, label: &str, url: &str, primary: bool| {""",
    """    ui.add_space(10.0);
    ui.label(egui::RichText::new(tl!("MIT OR Apache-2.0.""")
sub("crates/ui-egui/src/panels/dialogs.rs", """    use crate::icons::{self, Icon};
    use crate::links;
    let t = app.tokens;""", """    let t = app.tokens;""")
sub("crates/ui-egui/src/menus.rs", """    uic!("help.discord", "Join the ArtCraft Discord…", ["Help"], None),
    uic!("help.website", "ArtCraft Website", ["Help"], None),
    uic!("help.appPage", "FilmCraft on getartcraft.com", ["Help"], None),
    uic!("help.github", "FilmCraft on GitHub", ["Help"], None),
    uic!("help.reportIssue", "Report an Issue…", ["Help"], None),
""", "")
sub("crates/ui-egui/src/links.rs", """pub const ALL: [(&str, &str, &str); 5] = [
    ("help.discord", "Join the ArtCraft Discord…", DISCORD),
    ("help.website", "ArtCraft Website", WEBSITE),
    ("help.appPage", "FilmCraft on getartcraft.com", APP_PAGE),
    ("help.github", "FilmCraft on GitHub", GITHUB),
    ("help.reportIssue", "Report an Issue…", ISSUES),
];""", "pub const ALL: [(&str, &str, &str); 0] = [];")
sub("crates/ui-egui/src/panels/keyboard.rs", """    uic!("help.filmcraftHelp", "FilmCraft Help…", ["Help"], Some("F1")),
""", "")
sub("crates/ui-egui/src/panels/settings.rs", """            if button(app, ui, "settings.help", tl!("Help"), false) {
                crate::links::open(app, ctx, &format!("{}/blob/main/docs/project-files.md#settings", crate::links::GITHUB));
            }
""", "")
sub("crates/project/src/gtemplate.rs", "\\nHana Kobayashi\\n\\nMade with FilmCraft\";", "\\nHana Kobayashi\";")
plain_credits()
scrub()
