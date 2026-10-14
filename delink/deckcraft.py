"""DeckCraft without the ArtCraft promo links.

About: Discord, app page and GitHub. Start screen: the Discord link. Slide
Show ribbon: "Learn More" (the app page). The "Community Links" command.
The sample deck plugged the app on its closing slide and in the first
slide's speaker notes; the slide now just says goodbye, the note just welcomes.
"""
from _patch import plain_credits, scrub, sub

sub("crates/ui-egui/src/dialogs.rs", """        ui.hyperlink_to("Join our community on Discord", deckcraft_engine::links::DISCORD);
        ui.hyperlink_to("getartcraft.com/apps/deckcraft", deckcraft_engine::links::APP_PAGE);
        ui.hyperlink_to("Source on GitHub", deckcraft_engine::links::GITHUB);
        ui.add_space(6.0);
""", "")
sub("crates/ui-egui/src/dialogs.rs", """        ui.add_space(30.0);
        ui.horizontal(|ui| {
            ui.add_space(40.0);
            ui.hyperlink_to("Join the ArtCraft community on Discord", deckcraft_engine::links::DISCORD);
        });
""", "")
sub("crates/ui-egui/src/ribbon.rs", """    group(ui, |ui| {
        if big_button(ui, Icon::Help, "Learn\\nMore", true).clicked() {
            app.open_url(deckcraft_engine::links::APP_PAGE);
        }
    });
""", "")
sub("crates/ui-egui/src/lib.rs", """    ("app.links", "Community Links", None, "{}"),
""", "")
sub("crates/ui-egui/src/lib.rs", """            "app.links" => {
                use deckcraft_engine::links::*;
                return Ok(json!({"discord": DISCORD, "website": WEBSITE, "apps": APPS, "appPage": APP_PAGE, "github": GITHUB}));
            }
""", "")
sub("crates/engine/src/sample.rs", '"body": "Made with DeckCraft — free and open source"', '"body": "Thanks for watching"')
sub("crates/engine/src/sample.rs", '"Welcome everyone. This deck was made in DeckCraft."', '"Welcome everyone."')
plain_credits()
scrub()
