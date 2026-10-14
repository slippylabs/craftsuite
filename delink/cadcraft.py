"""CADCraft without the ArtCraft promo links (About: app page, Discord)."""
from _patch import plain_credits, scrub, sub

sub("crates/ui-egui/src/dialogs.rs", """                    ui.hyperlink_to("getartcraft.com/apps/cadcraft", "https://getartcraft.com/apps/cadcraft");
                    ui.hyperlink_to(crate::tl!("Join us on Discord"), "https://discord.gg/artcraft");
""", "")
plain_credits()
scrub()
