"""SoundCraft without the ArtCraft promo links (About: app page, Discord)."""
from _patch import plain_credits, scrub, sub

sub("crates/ui-egui/src/panels.rs", """                ui.hyperlink_to("getartcraft.com/apps/soundcraft", "https://getartcraft.com/apps/soundcraft");
                ui.hyperlink_to("Join us on Discord", "https://discord.gg/artcraft");
""", "")
plain_credits()
scrub()
