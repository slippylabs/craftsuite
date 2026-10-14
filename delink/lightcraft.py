"""LightCraft without the ArtCraft promo links.

The top bar's Discord icon; the About dialog's Discord button and
website/GitHub/ArtCraft links; the Help menu's Discord, Send Feedback
(GitHub issues), website, GitHub and ArtCraft Website entries; and F1
LightCraft Help, which only opened the docs folder on GitHub.
"""
from _patch import scrub, sub

sub("crates/ui-egui/src/panels/topbar.rs", """                ("discord", Icon::Chat, "Join the ArtCraft community on Discord", "app.discord"),
""", "")
sub("crates/ui-egui/src/panels/dialogs.rs", """                            ui.add_space(10.0);
                            let discord = egui::Button::new(egui::RichText::new(crate::i18n::tr("Join the ArtCraft Discord")).font(t.semibold(15.0)).color(egui::Color32::WHITE))
                                .fill(t.accent)
                                .min_size(egui::vec2(260.0, 34.0));
                            let r = ui.add(discord).on_hover_text(crate::links::DISCORD);
                            crate::widgets::register(ui.ctx(), "button:aboutDiscord", r.rect);
                            if r.clicked() {
                                let _ = crate::links::open(app, crate::links::DISCORD);
                            }
                            ui.add_space(6.0);
                            for (label, url) in [
                                ("LightCraft website", crate::links::APP_PAGE),
                                ("Source code on GitHub", crate::links::GITHUB),
                                ("ArtCraft — more creative apps", crate::links::WEBSITE),
                            ] {
                                let r = ui.link(crate::i18n::tr(label)).on_hover_text(url);
                                if r.clicked() {
                                    let _ = crate::links::open(app, url);
                                }
                            }
""", "")
sub("crates/ui-egui/src/menubar.rs", """            "app.discord",
            "app.feedback",
            "---",
            "app.website",
            "app.github",
            "app.artcraft",
            "---",
            "app.whatsNew",""", """            "app.whatsNew",""")
sub("crates/ui-egui/src/menus.rs", """    ("app.help", "LightCraft Help", Some("F1"), "Help"),
    ("app.discord", "Join the ArtCraft Discord…", None, "Help"),
    ("app.feedback", "Send Feedback…", None, "Help"),
    ("app.website", "LightCraft Website", None, "Help"),
    ("app.github", "LightCraft on GitHub", None, "Help"),
    ("app.artcraft", "ArtCraft Website", None, "Help"),
""", "")
sub("crates/ui-egui/src/links.rs", """pub const LINKS: &[(&str, &str, &str)] = &[
    ("app.help", "LightCraft Help", HELP),
    ("app.discord", "Join the ArtCraft Discord…", DISCORD),
    ("app.website", "LightCraft Website", APP_PAGE),
    ("app.github", "LightCraft on GitHub", GITHUB),
    ("app.artcraft", "ArtCraft Website", WEBSITE),
    ("app.feedback", "Send Feedback…", FEEDBACK),
];""", "pub const LINKS: &[(&str, &str, &str)] = &[];")
# About > Contributors: names stay, the link to each GitHub profile goes.
sub("crates/ui-egui/src/credits.rs", """    if ui.link(c.name(names)).on_hover_text(c.summary()).clicked() {
        let _ = crate::links::open(app, &profile_url(c));
    }""", """    let _ = app;
    ui.label(c.name(names)).on_hover_text(c.summary());""")
scrub()
