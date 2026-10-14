"""EffectCraft without the ArtCraft promo links.

The header's Discord pill and GitHub/website icons; the Home screen's
Community links and "More ArtCraft apps" buttons; the About dialog's
Discord/website/home page/GitHub buttons; the Help menu's Discord, Provide
Feedback (GitHub issues), ArtCraft Website, Home Page, GitHub and Online
Tutorials entries, and the four help.docs entries (F1 and the references),
which only opened the docs on GitHub -- and the commands behind them all.
The demo project's Lower Third read "Built with EffectCraft"; it now holds a
placeholder caption.
"""
from _patch import cut, plain_credits, scrub, sub

cut("crates/ui-egui/src/header.rs", """    // The pill fits its label (icon, gap, text) with even padding""",
    """    // Appearance: Sync with System, Light, Dark""")
cut("crates/ui-egui/src/panels/home.rs", """    // Community links at the foot (below the pages when the window is short).""",
    """}

/// The Home page: the welcome, quick-start tiles and the recent projects table.""")
sub("crates/ui-egui/src/panels/dialogs.rs", """    ui.add_space(14.0);
    let links: [(Icon, &str, &str, &'static str); 4] = [
        (Icon::Chat, "Join the ArtCraft Discord", effectcraft_engine::links::DISCORD, "help.discord"),
        (Icon::Globe, "ArtCraft website", effectcraft_engine::links::WEBSITE, "help.website"),
        (Icon::Sparkle, "EffectCraft home page", effectcraft_engine::links::APP_PAGE, "help.appPage"),
        (Icon::Code, "Source code on GitHub", effectcraft_engine::links::GITHUB, "help.github"),
    ];
    for (icon, label, url, c) in links {""", """    let links: [(Icon, &str, &str, &'static str); 0] = [];
    for (icon, label, url, c) in links {""")
sub("crates/engine/src/menus.rs", """Help
  EffectCraft Help... | help.docs {"page":"help"} | F1
  Scripting Help... | help.docs {"page":"scripting"}
  Expression Reference... | help.docs {"page":"expressions"}
  Effect Reference... | help.docs {"page":"effects"}
  Animation Presets... | anim.browsePresets""", """Help
  Animation Presets... | anim.browsePresets""")
sub("crates/engine/src/menus.rs", """  In-App Tutorials... | help.inAppTutorials
  Online Tutorials... | help.onlineTutorials
""", """  In-App Tutorials... | help.inAppTutorials
""")
sub("crates/engine/src/menus.rs", """  Reveal Logging File | help.revealLogFile
  ---
  Join the ArtCraft Discord... | help.discord
  Provide Feedback... | help.reportIssue
  ---
  ArtCraft Website | help.website
  EffectCraft Home Page | help.appPage
  EffectCraft on GitHub | help.github
  Open Demo Project""", """  Reveal Logging File | help.revealLogFile
  ---
  Open Demo Project""")
sub("crates/engine/src/commands/help.rs", """        cmd!("help.docs", "EffectCraft Help...", [], Some("F1"), "{page?: help|scripting|expressions|effects|agents}", always, docs),
        cmd!("help.discord", "Join the ArtCraft Discord...", ["Help"], None, "{}", always, |s, _| open(s, links::DISCORD.into())),
        cmd!("help.website", "ArtCraft Website", ["Help"], None, "{}", always, |s, _| open(s, links::WEBSITE.into())),
        cmd!("help.appPage", "EffectCraft Home Page", ["Help"], None, "{}", always, |s, _| open(s, links::APP_PAGE.into())),
        cmd!("help.github", "EffectCraft on GitHub", ["Help"], None, "{}", always, |s, _| open(s, links::GITHUB.into())),
        cmd!("help.onlineTutorials", "Online Tutorials...", ["Help"], None, "{}", always, |s, _| open(s, links::APP_PAGE.into())),
""", "")
cut("crates/engine/src/commands/help.rs", """        cmd!("help.reportIssue", "Provide Feedback...", ["Help"], None, "{}", always, |s, _| open(s, links::ISSUES.into())),""",
    """    ]
}""")
sub("crates/engine/src/demo.rs", '"Built with EffectCraft"', '"Your Title Here"', count=2)
plain_credits()
scrub()
