"""PdfCraft without the ArtCraft promo links.

The header's Discord button, the Home screen's "Join the ArtCraft community"
card, the About dialog's link pills, and the Help menu's Discord, web page,
GitHub, ArtCraft website and Check for updates (which, on the web, only
opened the GitHub releases page) entries.
"""
from _patch import plain_credits, scrub, sub

sub("crates/engine/src/links.rs", """pub const LINKS: &[Link] = &[
    Link { command: "help.discord", label: "Join the ArtCraft Discord", url: DISCORD, icon: "messages-square" },
    Link { command: "help.app_page", label: "PdfCraft web page", url: APP_PAGE, icon: "globe" },
    Link { command: "help.github", label: "PdfCraft on GitHub", url: GITHUB, icon: "code-xml" },
    Link { command: "help.website", label: "ArtCraft website", url: WEBSITE, icon: "external-link" },
];""", "pub const LINKS: &[Link] = &[];")
sub("crates/engine/src/commands.rs", """    c("help.discord", "Join the ArtCraft Discord", HELP, None, Nothing, "messages-square"),
    c("help.app_page", "PdfCraft web page", HELP, None, Nothing, "globe"),
    c("help.github", "PdfCraft on GitHub", HELP, None, Nothing, "code-xml"),
    c("help.website", "ArtCraft website", HELP, None, Nothing, "external-link"),
    c("help.check_updates", "Check for updates…", HELP, None, Nothing, "cloud"),
""", "")
sub("crates/ui-egui/src/chrome.rs", """                // Keep the two 28-point buttons, Discord's text/padding and three gaps outside the scrolling tabs.
                let controls_width = ui.fonts_mut(|f| f.layout_no_wrap("Discord".into(), theme::medium(13.0), t.text).size().x) + 106.0;""",
    """                // Keep the two 28-point buttons and their gaps outside the scrolling tabs.
                let controls_width = 2.0 * 28.0 + 3.0 * 8.0;""")
sub("crates/ui-egui/src/chrome.rs", """                    // One click to the community, from anywhere in the app.
                    if widgets::ghost_button(ui, "messages-square", "Discord").on_hover_text(pdfcraft_engine::links::DISCORD).clicked() {
                        app.execute("help.discord");
                    }
""", "")
sub("crates/ui-egui/src/dialogs.rs", """                        ui.add_space(6.0);
                        if let Some(cmd) = widgets::community_links(ui) {
                            link_command = Some(cmd);
                        }
""", "")
sub("crates/ui-egui/src/home.rs", """            egui::Frame::NONE
                .fill(t.card)
                .stroke(Stroke::new(1.0, t.border))
                .corner_radius(CornerRadius::same(12))
                .inner_margin(egui::Margin::same(14))
                .show(ui, |ui| {
                    ui.set_width(ui.available_width());
                    ui.horizontal(|ui| {
                        widgets::artcraft_mark(ui, 28.0);
                        ui.vertical(|ui| {
                            ui.label(egui::RichText::new(tl!("Join the ArtCraft community")).font(theme::semibold(15.0)));
                            ui.label(egui::RichText::new(tl!("Get help, share feedback and follow development on Discord.")).color(t.text_muted));
                        });
                    });
                    ui.add_space(8.0);
                    if let Some(cmd) = widgets::community_links(ui) {
                        app.execute(cmd);
                    }
                });
            ui.add_space(22.0);

""", "")
plain_credits()
scrub()
