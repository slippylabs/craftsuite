"""VectorCraft without the ArtCraft promo links.

The app bar's Discord pill; the About dialog's and Home screen's Discord
button and website/app page/GitHub links; the Help menu's (and the macOS
app menu's) Discord, ArtCraft website, app page and GitHub entries, and the
help.* commands behind them.
"""
from _patch import scrub, sub

sub("crates/engine/src/cmd/help.rs", """        cmd!(query "help.discord", "Join Our Discord", ["Help"], None, "{} → {url} the ArtCraft community Discord", always, |_, _| url(DISCORD_URL.into())),
        cmd!(query "help.website", "ArtCraft Website", ["Help"], None, "{} → {url}", always, |_, _| url(WEBSITE_URL.into())),
        cmd!(query "help.appPage", "VectorCraft on getartcraft.com", ["Help"], None, "{} → {url} this app's page", always, |_, _| url(app_page_url())),
        cmd!(query "help.github", "VectorCraft on GitHub", ["Help"], None, "{} → {url} source code, issues and releases", always, |_, _| url(github_url())),
        cmd!(query "help.links", "Links", [], None, "{} → {discord, website, appPage, github}", always, |_, _| {
            Ok(json!({ "discord": DISCORD_URL, "website": WEBSITE_URL, "appPage": app_page_url(), "github": github_url() }))
        }),
""", "")
sub("crates/ui-egui/src/menus.rs", """            vec![c("About VectorCraft", "help.about"), c("Join Our Discord", "help.discord")],""",
    """            vec![c("About VectorCraft", "help.about")],""")
sub("crates/ui-egui/src/menus.rs", """                c("Join Our Discord", "help.discord"),
                c("ArtCraft Website", "help.website"),
                c("VectorCraft on getartcraft.com", "help.appPage"),
                c("VectorCraft on GitHub", "help.github"),
                Sep,
                c("Search Commands…", "help.commandPalette"),""", """                c("Search Commands…", "help.commandPalette"),""")
sub("crates/ui-egui/src/chrome.rs", """            let discord = search && room >= ws_w + 8.0 + gap + icon + 10.0 + gap + crate::community::discord_width(ui, false);
""", "")
sub("crates/ui-egui/src/chrome.rs", """            if discord {
                ui.add_space(10.0);
                crate::community::discord_button(app, ui, false);
            }
""", "")
sub("crates/ui-egui/src/dialogs/about.rs", """    ui.add_space(12.0);
    crate::community::links(app, ui);
""", "")
sub("crates/ui-egui/src/canvas.rs", """    ui.add_space(28.0);
    ui.label(egui::RichText::new(tl!("Community")).font(theme::semibold(14.0)).color(t.text));
    ui.add_space(10.0);
    crate::community::links(app, ui);
""", "")
# About > Contributors: names stay, the link to each GitHub profile goes.
sub("crates/ui-egui/src/credits.rs", """    let url = format!("https://github.com/{}", c.login);
    let r = ui.add(egui::Link::new(c.name(names))).on_hover_text(c.summary());
    if r.clicked() {
        app.open_url(&url);
    }
    r""", """    let _ = app;
    ui.label(c.name(names)).on_hover_text(c.summary())""")
scrub()
