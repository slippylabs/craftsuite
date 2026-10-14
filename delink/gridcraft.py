"""GridCraft without the ArtCraft promo links (About: app page, Discord)."""
from _patch import plain_credits, scrub, sub

sub("crates/ui-egui/src/dialogs.rs", """            ui.hyperlink_to("getartcraft.com/apps/gridcraft", "https://getartcraft.com/apps/gridcraft");
            ui.hyperlink_to("Join the ArtCraft Discord", "https://discord.gg/artcraft");
""", "")
plain_credits()
scrub()
