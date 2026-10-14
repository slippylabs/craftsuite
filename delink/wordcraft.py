"""WordCraft without the ArtCraft promo links.

The title bar's Discord button (and its Options checkbox); the File
backstage's "Discord community" item; the Help ribbon's
"Community Discord" button and its key tip; the ui.discord command; the
About dialog's app page, Discord and GitHub links. The sample document's
"community board" link pointed at getartcraft.com; it is plain text now.
LaTeX export no longer writes the app page's URL into every file.
"""
from _patch import cut, plain_credits, scrub, sub

cut("crates/ui-egui/src/chrome.rs", """                    if app.ui.show_discord {""", """                    // Search ("Tell me").""")
sub("crates/ui-egui/src/backstage.rs", """[("About", "about"), ("Discord community", "discord")]""", """[("About", "about")]""")
sub("crates/ui-egui/src/backstage.rs", """    ui.checkbox(&mut app.ui.show_discord, tl!("Show the community button in the title bar"));
""", "")
sub("crates/ui-egui/src/ribbon.rs", """        big(ui, app, "discord", "Community\\nDiscord", "ui.discord", json!({}), false);
""", "")
sub("crates/ui-egui/src/keytips.rs", """c("Community Discord", "ui.discord"), """, "")
sub("crates/ui-egui/src/lib.rs", """            "ui.discord" => {
                self.canvas.open_url = Some("https://discord.gg/artcraft".into());
                json!({})
            }
""", "")
sub("crates/ui-egui/src/dialogs.rs", """                    ui.add_space(6.0);
                    ui.hyperlink_to(tl!("getartcraft.com/apps/wordcraft"), "https://getartcraft.com/apps/wordcraft");
                    ui.hyperlink_to(tl!("Join us on Discord: discord.gg/artcraft"), "https://discord.gg/artcraft");
                    ui.hyperlink_to(tl!("Source code: github.com/storytold/wordcraft"), "https://github.com/storytold/wordcraft");
""", "")
sub("crates/engine/src/sample.rs", """CharProps { style: Some("Hyperlink".into()), link: Some("https://getartcraft.com/".into()), ..Default::default() },""",
    "CharProps::default(),")
sub("crates/formats/src/latex.rs", """"% Written by WordCraft (https://getartcraft.com/apps/wordcraft).\\n\"""", """"% Written by WordCraft.\\n\"""")
plain_credits()
scrub()
